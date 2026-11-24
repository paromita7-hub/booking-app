from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class ReviewTopicSchema(BaseModel):
    topic: str
    sentiment: str
    confidence: float = 1.0
    matched_keywords: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ReviewBase(BaseModel):
    external_id: str | None = None
    property_id: int
    title: str | None = None
    positive_text: str | None = None
    negative_text: str | None = None
    rating: float = Field(..., ge=1.0, le=10.0)
    review_date: date
    stay_date: date | None = None
    reviewer_country: str | None = None
    traveler_type: str | None = None
    room_type: str | None = None
    language: str = "en"
    source: str = "csv_import"
    is_demo: bool = False


class ReviewCreate(ReviewBase):
    content_fingerprint: str | None = None


class ReviewResponse(ReviewBase):
    id: int
    content_fingerprint: str
    created_at: datetime
    updated_at: datetime
    property_name: str | None = None
    topics: list[ReviewTopicSchema] = Field(default_factory=list)
    overall_sentiment: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedReviewsResponse(BaseModel):
    items: list[ReviewResponse]
    total: int
    page: int
    limit: int
    pages: int
