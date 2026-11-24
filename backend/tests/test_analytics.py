from datetime import date, timedelta
from app.services.analytics_service import AnalyticsService
from app.services.ingestion_service import IngestionService


def test_weekly_analytics_and_insights(db_session):
    service = AnalyticsService(db_session)
    ingestion = IngestionService(db_session)

    # 1. Test empty state handling (should not divide by zero or crash)
    summary = service.get_kpi_summary()
    assert summary["total_reviews_count"] == 0
    assert summary["current_week_avg_rating"] == 0.0

    # 2. Ingest reviews spanning current and previous weeks
    ref_date = date.today()
    reviews = [
        {
            "property_id": 1,
            "rating": 4.0,
            "review_date": (ref_date - timedelta(days=1)).isoformat(),
            "title": "Dirty sheets",
            "positive_text": "",
            "negative_text": "Housekeeping was terrible. Dirty bathroom and stained linen.",
        },
        {
            "property_id": 1,
            "rating": 8.0,
            "review_date": (ref_date - timedelta(days=2)).isoformat(),
            "title": "Nice room",
            "positive_text": "Clean and spacious room with friendly reception staff.",
            "negative_text": "",
        },
        {
            "property_id": 2,
            "rating": 5.0,
            "review_date": (ref_date - timedelta(days=9)).isoformat(),
            "title": "Slow check-in",
            "positive_text": "",
            "negative_text": "Waited forever at reception for check-in.",
        },
    ]
    ingestion.ingest_records(reviews, source_name="analytics_test")

    # 3. Test KPI summary
    summary_after = service.get_kpi_summary()
    assert summary_after["total_reviews_count"] == 3

    # 4. Test Property Comparisons
    comparisons = service.get_property_comparisons()
    assert len(comparisons) == 4

    # 5. Test Topic Distributions
    topic_dists = service.get_topic_distributions()
    cleanliness = next((t for t in topic_dists if t["topic"] == "Cleanliness"), None)
    assert cleanliness is not None
    assert cleanliness["negative_count"] >= 1
