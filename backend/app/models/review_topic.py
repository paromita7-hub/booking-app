from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from app.database import Base


class ReviewTopic(Base):
    __tablename__ = "review_topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    sentiment = Column(String(50), nullable=False, index=True)  # Positive, Negative, Mixed, Neutral
    confidence = Column(Float, nullable=False, default=1.0)
    matched_keywords = Column(JSON, nullable=True)

    # Relationship
    review = relationship("Review", back_populates="topics")

    __table_args__ = (
        Index("ix_review_topics_topic_sentiment", "topic", "sentiment"),
    )
