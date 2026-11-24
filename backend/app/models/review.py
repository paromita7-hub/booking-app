from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    external_id = Column(String(255), nullable=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(512), nullable=True)
    positive_text = Column(Text, nullable=True)
    negative_text = Column(Text, nullable=True)
    rating = Column(Float, nullable=False)
    review_date = Column(Date, nullable=False, index=True)
    stay_date = Column(Date, nullable=True)
    reviewer_country = Column(String(100), nullable=True, index=True)
    traveler_type = Column(String(100), nullable=True, index=True)
    room_type = Column(String(255), nullable=True)
    language = Column(String(20), default="en", nullable=False)
    source = Column(String(50), nullable=False, default="csv_import")
    content_fingerprint = Column(String(64), nullable=False, unique=True, index=True)
    is_demo = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    property = relationship("Property", back_populates="reviews")
    topics = relationship("ReviewTopic", back_populates="review", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_reviews_property_date", "property_id", "review_date"),
        Index("ix_reviews_rating", "rating"),
    )
