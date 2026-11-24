import json
from app.services.ingestion_service import IngestionService, CSVIngestionAdapter, JSONIngestionAdapter
from app.models.review import Review


def test_csv_adapter_parsing():
    adapter = CSVIngestionAdapter()
    sample_csv = """property_name,rating,review_date,title,positive_text,negative_text
Olympic Hotel Paddington,8.5,2026-11-20,Great Stay,Clean room,A bit noisy
"""
    records = adapter.parse(sample_csv)
    assert len(records) == 1
    assert records[0]["property_name"] == "Olympic Hotel Paddington"
    assert records[0]["rating"] == "8.5"
    assert records[0]["positive_text"] == "Clean room"


def test_json_adapter_parsing():
    adapter = JSONIngestionAdapter()
    sample_json = json.dumps([
        {
            "property_name": "Potts Point",
            "rating": 7.0,
            "review_date": "2026-11-18",
            "title": "Decent place",
            "positive_text": "Good bed",
            "negative_text": "Slow lift",
        }
    ])
    records = adapter.parse(sample_json)
    assert len(records) == 1
    assert records[0]["property_name"] == "Potts Point"
    assert records[0]["rating"] == 7.0


def test_duplicate_prevention(db_session):
    """Test duplicate detection via fingerprint and external_id."""
    service = IngestionService(db_session)
    record = {
        "external_id": "REV-DUP-100",
        "property_id": 1,
        "rating": 8.0,
        "review_date": "2026-11-20",
        "title": "Good stay",
        "positive_text": "Very clean",
        "negative_text": "None",
    }

    # First ingestion
    log1 = service.ingest_records([record], source_name="test_csv")
    assert log1.records_added == 1
    assert log1.records_skipped == 0
    assert db_session.query(Review).count() == 1

    # Second ingestion of identical record
    log2 = service.ingest_records([record], source_name="test_csv")
    assert log2.records_added == 0
    assert log2.records_skipped == 1
    assert db_session.query(Review).count() == 1


def test_invalid_rating_and_missing_property_handling(db_session):
    """Ensure invalid ratings or unknown properties are safely rejected without crashing."""
    service = IngestionService(db_session)
    invalid_records = [
        {"property_id": 1, "rating": 15.0, "title": "Invalid high rating"},  # Rating > 10
        {"property_id": 1, "rating": -2.0, "title": "Negative rating"},       # Rating < 1
        {"property_id": 999, "rating": 8.0, "title": "Non-existent property"}, # Missing property
    ]
    log = service.ingest_records(invalid_records, source_name="test_invalid")
    assert log.records_added == 0
    assert log.records_skipped == 3
