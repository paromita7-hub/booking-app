"""Pluggable Review Ingestion Service.

Supports CSV, JSON imports, duplicate detection via content fingerprinting,
source tracking, and source-adapter pattern with safe access authorization gates.
"""

from abc import ABC, abstractmethod
import csv
import io
import json
import hashlib
from datetime import datetime, date, timezone
from typing import Any
from dateutil import parser as date_parser
from sqlalchemy.orm import Session

from app.models.property import Property
from app.models.review import Review
from app.models.review_topic import ReviewTopic
from app.models.ingestion_log import IngestionLog
from app.services.analysis_engine import classifier
from app.config import settings


class IngestionError(Exception):
    pass


class AuthorizationError(IngestionError):
    pass


def generate_content_fingerprint(
    property_id: int,
    review_date: date,
    rating: float,
    title: str | None,
    positive_text: str | None,
    negative_text: str | None,
) -> str:
    """Computes a deterministic SHA-256 content fingerprint for deduplication."""
    clean_title = (title or "").strip().lower()
    clean_pos = (positive_text or "").strip().lower()
    clean_neg = (negative_text or "").strip().lower()
    payload = f"{property_id}|{review_date.isoformat()}|{rating:.1f}|{clean_title}|{clean_pos}|{clean_neg}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class BaseSourceAdapter(ABC):
    @abstractmethod
    def parse(self, raw_data: Any) -> list[dict[str, Any]]:
        pass


class CSVIngestionAdapter(BaseSourceAdapter):
    COLUMN_ALIASES = {
        "property_id": ["property_id", "property", "hotel_id"],
        "property_name": ["property_name", "hotel_name", "hotel"],
        "external_id": ["external_id", "review_id", "id"],
        "title": ["title", "headline", "review_title"],
        "positive_text": ["positive_text", "positive", "pros", "liked"],
        "negative_text": ["negative_text", "negative", "cons", "disliked"],
        "rating": ["rating", "score", "review_score", "overall_rating"],
        "review_date": ["review_date", "date", "publication_date", "posted_date"],
        "stay_date": ["stay_date", "date_of_stay", "stayed"],
        "reviewer_country": ["reviewer_country", "country", "guest_country"],
        "traveler_type": ["traveler_type", "trip_type", "traveller_type"],
        "room_type": ["room_type", "room"],
        "language": ["language", "lang"],
        "is_demo": ["is_demo", "demo"],
    }

    def parse(self, raw_data: str | bytes) -> list[dict[str, Any]]:
        if isinstance(raw_data, bytes):
            text = raw_data.decode("utf-8", errors="replace")
        else:
            text = raw_data

        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            return []

        # Build map from lower header to standard field name
        header_map = {}
        for col in reader.fieldnames:
            clean_col = col.strip().lower()
            for std_field, aliases in self.COLUMN_ALIASES.items():
                if clean_col in aliases:
                    header_map[col] = std_field
                    break

        records = []
        for row in reader:
            record: dict[str, Any] = {}
            for col, val in row.items():
                if col in header_map and val is not None:
                    record[header_map[col]] = val.strip()
            if record:
                records.append(record)
        return records


class JSONIngestionAdapter(BaseSourceAdapter):
    def parse(self, raw_data: str | bytes | list | dict) -> list[dict[str, Any]]:
        if isinstance(raw_data, (bytes, str)):
            data = json.loads(raw_data)
        else:
            data = raw_data

        if isinstance(data, dict):
            # Check for wrapper key such as {"reviews": [...]}
            if "reviews" in data and isinstance(data["reviews"], list):
                return data["reviews"]
            return [data]
        elif isinstance(data, list):
            return data
        return []


class PlaywrightScraperAdapter(BaseSourceAdapter):
    """Safe adapter that strictly respects access boundaries and authorized collection conditions."""

    def parse(self, raw_data: Any) -> list[dict[str, Any]]:
        if not settings.ALLOW_AUTOMATED_SCRAPING:
            raise AuthorizationError(
                "Automated web collection is disabled. Direct access requires explicit written "
                "client authorization, terms compliance, and ALLOW_AUTOMATED_SCRAPING=true."
            )
        # Note: Playwright scraping is only engaged when authorized
        return []


class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.csv_adapter = CSVIngestionAdapter()
        self.json_adapter = JSONIngestionAdapter()
        self.scraper_adapter = PlaywrightScraperAdapter()

    def _resolve_property_id(self, record: dict[str, Any], property_map: dict[str, int]) -> int | None:
        # Check direct property_id
        if "property_id" in record and record["property_id"]:
            try:
                pid = int(record["property_id"])
                if pid in property_map.values():
                    return pid
            except (ValueError, TypeError):
                pass

        # Check property_name
        prop_name = record.get("property_name")
        if prop_name:
            clean_name = prop_name.strip().lower()
            for name, pid in property_map.items():
                if clean_name in name.lower() or name.lower() in clean_name:
                    return pid

        return None

    def ingest_records(
        self,
        raw_records: list[dict[str, Any]],
        source_name: str,
        default_property_id: int | None = None,
        is_demo: bool = False,
    ) -> IngestionLog:
        """Processes, validates, deduplicates, classifies, and commits incoming reviews."""
        # 1. Initialize Ingestion Log
        log = IngestionLog(
            source=source_name,
            property_id=default_property_id,
            status="in_progress",
            records_processed=0,
            records_added=0,
            records_skipped=0,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        try:
            # Preload properties map
            properties = self.db.query(Property).all()
            property_map = {p.name: p.id for p in properties}
            if not property_map:
                raise IngestionError("No hotel properties found in database. Seed properties first.")

            # Preload existing fingerprints and external_ids for fast deduplication
            existing_fingerprints = set(
                fp for (fp,) in self.db.query(Review.content_fingerprint).all()
            )
            existing_external_ids = set(
                (p_id, ext_id)
                for p_id, ext_id in self.db.query(Review.property_id, Review.external_id)
                .filter(Review.external_id.isnot(None))
                .all()
            )

            records_processed = 0
            records_added = 0
            records_skipped = 0

            for record in raw_records:
                records_processed += 1

                # 1. Resolve Property
                prop_id = self._resolve_property_id(record, property_map) or default_property_id
                if not prop_id:
                    records_skipped += 1
                    continue

                # 2. Validate Rating
                try:
                    rating = float(record.get("rating", 0.0))
                    if not (1.0 <= rating <= 10.0):
                        records_skipped += 1
                        continue
                    rating = round(rating, 1)
                except (ValueError, TypeError):
                    records_skipped += 1
                    continue

                # 3. Parse Dates
                raw_rev_date = record.get("review_date")
                if not raw_rev_date:
                    rev_date = date.today()
                else:
                    try:
                        rev_date = date_parser.parse(str(raw_rev_date)).date()
                    except Exception:
                        rev_date = date.today()

                raw_stay_date = record.get("stay_date")
                stay_date = None
                if raw_stay_date:
                    try:
                        stay_date = date_parser.parse(str(raw_stay_date)).date()
                    except Exception:
                        stay_date = None

                # 4. Clean Fields
                title = record.get("title") or None
                pos_text = record.get("positive_text") or None
                neg_text = record.get("negative_text") or None
                ext_id = record.get("external_id") or None
                country = record.get("reviewer_country") or None
                traveler_type = record.get("traveler_type") or None
                room_type = record.get("room_type") or None
                language = record.get("language") or "en"
                rec_is_demo = is_demo or str(record.get("is_demo", "")).lower() in ("true", "1", "yes")

                # 5. Duplicate Detection
                # A) External ID check
                if ext_id and (prop_id, ext_id) in existing_external_ids:
                    records_skipped += 1
                    continue

                # B) Content Fingerprint check
                fingerprint = generate_content_fingerprint(
                    property_id=prop_id,
                    review_date=rev_date,
                    rating=rating,
                    title=title,
                    positive_text=pos_text,
                    negative_text=neg_text,
                )

                if fingerprint in existing_fingerprints:
                    records_skipped += 1
                    continue

                # 6. Run Analysis Engine
                analysis = classifier.analyze(
                    title=title,
                    positive_text=pos_text,
                    negative_text=neg_text,
                    rating=rating,
                )

                # 7. Create Review Record
                review = Review(
                    external_id=ext_id,
                    property_id=prop_id,
                    title=title,
                    positive_text=pos_text,
                    negative_text=neg_text,
                    rating=rating,
                    review_date=rev_date,
                    stay_date=stay_date,
                    reviewer_country=country,
                    traveler_type=traveler_type,
                    room_type=room_type,
                    language=language,
                    source=source_name,
                    content_fingerprint=fingerprint,
                    is_demo=rec_is_demo,
                )
                self.db.add(review)
                self.db.flush()  # obtain review.id

                # 8. Create Topic Classifications
                for topic_item in analysis["topics"]:
                    review_topic = ReviewTopic(
                        review_id=review.id,
                        topic=topic_item["topic"],
                        sentiment=topic_item["sentiment"],
                        confidence=topic_item["confidence"],
                        matched_keywords=topic_item["matched_keywords"],
                    )
                    self.db.add(review_topic)

                existing_fingerprints.add(fingerprint)
                if ext_id:
                    existing_external_ids.add((prop_id, ext_id))
                records_added += 1

            self.db.commit()

            # Update Log
            log.status = "completed" if records_skipped == 0 else "partial"
            log.records_processed = records_processed
            log.records_added = records_added
            log.records_skipped = records_skipped
            log.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(log)
            return log

        except Exception as e:
            self.db.rollback()
            log.status = "failed"
            log.error_message = str(e)
            log.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(log)
            raise e
