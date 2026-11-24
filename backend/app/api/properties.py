from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.property import Property
from app.models.review import Review
from app.models.review_topic import ReviewTopic
from app.schemas.property import PropertyResponse, PropertyStats

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.get("", response_model=list[PropertyStats])
def get_properties(db: Session = Depends(get_db)):
    """List all hotel properties with operational summary statistics."""
    properties = db.query(Property).order_by(Property.id).all()
    stats_list = []

    for prop in properties:
        reviews = db.query(Review).filter(Review.property_id == prop.id).all()
        total = len(reviews)
        avg_rating = round(sum(r.rating for r in reviews) / total, 2) if total > 0 else 0.0

        pos_count = sum(1 for r in reviews if r.rating >= 7.0)
        neg_count = sum(1 for r in reviews if r.rating <= 5.5)
        pos_pct = round((pos_count / total) * 100, 1) if total > 0 else 0.0
        neg_pct = round((neg_count / total) * 100, 1) if total > 0 else 0.0

        # Top negative topic
        top_topic = (
            db.query(ReviewTopic.topic, func.count(ReviewTopic.id).label("count"))
            .join(Review, Review.id == ReviewTopic.review_id)
            .filter(Review.property_id == prop.id, ReviewTopic.sentiment.in_(["Negative", "Mixed"]))
            .group_by(ReviewTopic.topic)
            .order_by(func.count(ReviewTopic.id).desc())
            .first()
        )

        stats_list.append(
            PropertyStats(
                id=prop.id,
                name=prop.name,
                booking_url=prop.booking_url,
                location=prop.location,
                created_at=prop.created_at,
                total_reviews=total,
                average_rating=avg_rating,
                positive_percentage=pos_pct,
                negative_percentage=neg_pct,
                weekly_rating_change=0.0,
                top_negative_topic=top_topic[0] if top_topic else None,
            )
        )

    return stats_list


@router.get("/{property_id}", response_model=PropertyStats)
def get_property(property_id: int, db: Session = Depends(get_db)):
    """Retrieve details and operational statistics for a specific property."""
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Property with ID {property_id} not found",
        )

    reviews = db.query(Review).filter(Review.property_id == prop.id).all()
    total = len(reviews)
    avg_rating = round(sum(r.rating for r in reviews) / total, 2) if total > 0 else 0.0
    pos_count = sum(1 for r in reviews if r.rating >= 7.0)
    neg_count = sum(1 for r in reviews if r.rating <= 5.5)

    top_topic = (
        db.query(ReviewTopic.topic, func.count(ReviewTopic.id).label("count"))
        .join(Review, Review.id == ReviewTopic.review_id)
        .filter(Review.property_id == prop.id, ReviewTopic.sentiment.in_(["Negative", "Mixed"]))
        .group_by(ReviewTopic.topic)
        .order_by(func.count(ReviewTopic.id).desc())
        .first()
    )

    return PropertyStats(
        id=prop.id,
        name=prop.name,
        booking_url=prop.booking_url,
        location=prop.location,
        created_at=prop.created_at,
        total_reviews=total,
        average_rating=avg_rating,
        positive_percentage=round((pos_count / total) * 100, 1) if total > 0 else 0.0,
        negative_percentage=round((neg_count / total) * 100, 1) if total > 0 else 0.0,
        weekly_rating_change=0.0,
        top_negative_topic=top_topic[0] if top_topic else None,
    )
