from datetime import date
from app.models.property import Property
from app.models.review import Review
from app.models.review_topic import ReviewTopic
from app.services.ingestion_service import generate_content_fingerprint


def test_property_and_review_relationships(db_session):
    """Test property and review model relations and cascades."""
    prop = db_session.query(Property).filter(Property.id == 1).first()
    assert prop is not None
    assert prop.name == "Olympic Hotel Paddington"

    fp = generate_content_fingerprint(1, date(2026, 11, 20), 8.5, "Great", "Loved it", "None")
    review = Review(
        external_id="REV-TEST-001",
        property_id=prop.id,
        title="Great",
        positive_text="Loved it",
        negative_text="None",
        rating=8.5,
        review_date=date(2026, 11, 20),
        content_fingerprint=fp,
        is_demo=True,
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    topic = ReviewTopic(
        review_id=review.id,
        topic="Cleanliness",
        sentiment="Positive",
        confidence=0.9,
        matched_keywords=["clean"],
    )
    db_session.add(topic)
    db_session.commit()

    # Verify relationships
    assert len(prop.reviews) == 1
    assert prop.reviews[0].id == review.id
    assert len(review.topics) == 1
    assert review.topics[0].topic == "Cleanliness"
    assert review.property.name == "Olympic Hotel Paddington"
