from datetime import date
import io
import csv
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.database import get_db
from app.models.review import Review
from app.models.review_topic import ReviewTopic
from app.models.property import Property
from app.schemas.review import ReviewResponse, PaginatedReviewsResponse, ReviewTopicSchema
from app.services.ingestion_service import IngestionService, CSVIngestionAdapter, JSONIngestionAdapter
from app.services.analysis_engine import classifier

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("", response_model=PaginatedReviewsResponse)
def get_reviews(
    property_id: int | None = Query(None, description="Filter by property ID"),
    start_date: date | None = Query(None, description="Filter review date from"),
    end_date: date | None = Query(None, description="Filter review date to"),
    min_rating: float | None = Query(None, ge=1.0, le=10.0, description="Minimum rating"),
    max_rating: float | None = Query(None, ge=1.0, le=10.0, description="Maximum rating"),
    topic: str | None = Query(None, description="Filter by operational topic"),
    sentiment: str | None = Query(None, description="Filter by sentiment (Positive, Negative, Mixed, Neutral)"),
    search: str | None = Query(None, description="Text search in title, positive or negative text"),
    source: str | None = Query(None, description="Filter by source"),
    sort_by: str = Query("review_date", pattern="^(review_date|rating|created_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve paginated, filterable, searchable reviews with topic classifications."""
    query = db.query(Review)

    if property_id:
        query = query.filter(Review.property_id == property_id)
    if start_date:
        query = query.filter(Review.review_date >= start_date)
    if end_date:
        query = query.filter(Review.review_date <= end_date)
    if min_rating is not None:
        query = query.filter(Review.rating >= min_rating)
    if max_rating is not None:
        query = query.filter(Review.rating <= max_rating)
    if source:
        query = query.filter(Review.source == source)

    if topic or sentiment:
        query = query.join(ReviewTopic, ReviewTopic.review_id == Review.id)
        if topic:
            query = query.filter(ReviewTopic.topic == topic)
        if sentiment:
            query = query.filter(ReviewTopic.sentiment == sentiment)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            (Review.title.ilike(search_term))
            | (Review.positive_text.ilike(search_term))
            | (Review.negative_text.ilike(search_term))
        )

    # Distinct if joined
    if topic or sentiment:
        query = query.distinct()

    total = query.count()

    # Sorting
    order_col = getattr(Review, sort_by)
    query = query.order_by(desc(order_col) if sort_order == "desc" else asc(order_col))

    # Pagination
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    # Build response with sentiment and topic tags
    result_items = []
    for r in items:
        topics_schema = [
            ReviewTopicSchema(
                topic=t.topic,
                sentiment=t.sentiment,
                confidence=t.confidence,
                matched_keywords=t.matched_keywords or [],
            )
            for t in r.topics
        ]
        # Overall review sentiment
        analysis = classifier.analyze(r.title, r.positive_text, r.negative_text, r.rating)
        result_items.append(
            ReviewResponse(
                id=r.id,
                external_id=r.external_id,
                property_id=r.property_id,
                property_name=r.property.name if r.property else None,
                title=r.title,
                positive_text=r.positive_text,
                negative_text=r.negative_text,
                rating=r.rating,
                review_date=r.review_date,
                stay_date=r.stay_date,
                reviewer_country=r.reviewer_country,
                traveler_type=r.traveler_type,
                room_type=r.room_type,
                language=r.language,
                source=r.source,
                content_fingerprint=r.content_fingerprint,
                is_demo=r.is_demo,
                created_at=r.created_at,
                updated_at=r.updated_at,
                topics=topics_schema,
                overall_sentiment=analysis["overall_sentiment"],
            )
        )

    pages = (total + limit - 1) // limit if limit > 0 else 0
    return PaginatedReviewsResponse(
        items=result_items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/template")
def download_csv_template():
    """Generates a downloadable sample CSV template for review imports."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "property_name",
        "external_id",
        "title",
        "positive_text",
        "negative_text",
        "rating",
        "review_date",
        "stay_date",
        "reviewer_country",
        "traveler_type",
        "room_type",
        "language",
        "is_demo",
    ])
    # Add a sample reference row
    writer.writerow([
        "Olympic Hotel Paddington",
        "REV-AU-9901",
        "Great location and clean rooms",
        "The housekeeping staff was wonderful and the location in Paddington was perfect for walking.",
        "A bit noisy from the street traffic at night, but earplugs were provided.",
        "8.5",
        "2026-11-20",
        "2026-11-18",
        "Australia",
        "Couple",
        "Deluxe Queen Room",
        "en",
        "false",
    ])
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=booking_reviews_template.csv"},
    )


@router.get("/export")
def export_reviews_csv(
    property_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Exports reviews into a downloadable CSV format."""
    query = db.query(Review)
    if property_id:
        query = query.filter(Review.property_id == property_id)
    reviews = query.order_by(desc(Review.review_date)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID",
        "Property",
        "External ID",
        "Rating",
        "Review Date",
        "Stay Date",
        "Title",
        "Positive Feedback",
        "Negative Feedback",
        "Reviewer Country",
        "Traveler Type",
        "Room Type",
        "Source",
        "Is Demo",
    ])
    for r in reviews:
        writer.writerow([
            r.id,
            r.property.name if r.property else "",
            r.external_id or "",
            r.rating,
            r.review_date.isoformat(),
            r.stay_date.isoformat() if r.stay_date else "",
            r.title or "",
            r.positive_text or "",
            r.negative_text or "",
            r.reviewer_country or "",
            r.traveler_type or "",
            r.room_type or "",
            r.source,
            r.is_demo,
        ])
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=reviews_export.csv"},
    )


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single review."""
    r = db.query(Review).filter(Review.id == review_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Review not found")

    topics_schema = [
        ReviewTopicSchema(
            topic=t.topic,
            sentiment=t.sentiment,
            confidence=t.confidence,
            matched_keywords=t.matched_keywords or [],
        )
        for t in r.topics
    ]
    analysis = classifier.analyze(r.title, r.positive_text, r.negative_text, r.rating)

    return ReviewResponse(
        id=r.id,
        external_id=r.external_id,
        property_id=r.property_id,
        property_name=r.property.name if r.property else None,
        title=r.title,
        positive_text=r.positive_text,
        negative_text=r.negative_text,
        rating=r.rating,
        review_date=r.review_date,
        stay_date=r.stay_date,
        reviewer_country=r.reviewer_country,
        traveler_type=r.traveler_type,
        room_type=r.room_type,
        language=r.language,
        source=r.source,
        content_fingerprint=r.content_fingerprint,
        is_demo=r.is_demo,
        created_at=r.created_at,
        updated_at=r.updated_at,
        topics=topics_schema,
        overall_sentiment=analysis["overall_sentiment"],
    )


@router.post("/import")
async def import_reviews_file(
    file: UploadFile = File(...),
    property_id: int | None = None,
    is_demo: bool = False,
    db: Session = Depends(get_db),
):
    """Upload and ingest reviews via CSV or JSON file."""
    content = await file.read()
    filename = file.filename or "upload"

    service = IngestionService(db)
    if filename.endswith(".json"):
        records = service.json_adapter.parse(content)
        source_name = f"json_import:{filename}"
    else:
        records = service.csv_adapter.parse(content)
        source_name = f"csv_import:{filename}"

    if not records:
        raise HTTPException(status_code=400, detail="No valid review records found in uploaded file")

    log = service.ingest_records(
        raw_records=records,
        source_name=source_name,
        default_property_id=property_id,
        is_demo=is_demo,
    )

    return {
        "status": log.status,
        "records_processed": log.records_processed,
        "records_added": log.records_added,
        "records_skipped": log.records_skipped,
        "error_message": log.error_message,
        "log_id": log.id,
    }
