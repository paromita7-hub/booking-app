from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PropertyBase(BaseModel):
    name: str
    booking_url: str
    location: str


class PropertyCreate(PropertyBase):
    pass


class PropertyResponse(PropertyBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PropertyStats(PropertyResponse):
    total_reviews: int = 0
    average_rating: float = 0.0
    positive_percentage: float = 0.0
    negative_percentage: float = 0.0
    weekly_rating_change: float = 0.0
    top_negative_topic: str | None = None
