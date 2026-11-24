from datetime import date, datetime
from pydantic import BaseModel, Field


class KPISummary(BaseModel):
    current_week_avg_rating: float = 0.0
    previous_week_avg_rating: float = 0.0
    rating_change: float = 0.0
    total_reviews_count: int = 0
    current_week_reviews_count: int = 0
    previous_week_reviews_count: int = 0
    positive_review_percentage: float = 0.0
    negative_review_percentage: float = 0.0
    mixed_review_percentage: float = 0.0
    neutral_review_percentage: float = 0.0
    period_start: str = ""
    period_end: str = ""
    previous_period_start: str = ""
    previous_period_end: str = ""
    timezone: str = "Australia/Sydney"


class WeeklyTrendPoint(BaseModel):
    week_label: str  # e.g., "Week 46 (11 Nov)"
    week_start: str
    week_end: str
    average_rating: float
    total_reviews: int
    positive_count: int
    negative_count: int
    mixed_count: int


class PropertyComparison(BaseModel):
    property_id: int
    property_name: str
    average_rating: float
    total_reviews: int
    positive_percentage: float
    negative_percentage: float
    weekly_rating_change: float
    top_negative_topic: str | None = None


class TopicDistribution(BaseModel):
    topic: str
    positive_count: int = 0
    negative_count: int = 0
    total_mentions: int = 0
    negative_percentage_of_negative_reviews: float = 0.0
    positive_percentage_of_positive_reviews: float = 0.0


class RecurringIssue(BaseModel):
    topic: str
    negative_mentions: int
    percentage_of_negative_reviews: float
    change_vs_previous_week: float
    trend: str  # "worsening", "improving", "stable"
    most_affected_properties: list[str] = Field(default_factory=list)
    sample_reviews: list[dict] = Field(default_factory=list)


class OperationalInsight(BaseModel):
    headline: str
    topic: str
    category: str  # "warning", "positive", "trend"
    negative_reviews_percentage_current: float
    negative_reviews_percentage_previous: float
    percentage_change: float
    affected_properties: list[str]
    supporting_reviews: list[dict]
    interpretation: str
