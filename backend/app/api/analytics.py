from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    KPISummary,
    WeeklyTrendPoint,
    PropertyComparison,
    TopicDistribution,
    OperationalInsight,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=KPISummary)
def get_analytics_overview(
    property_id: int | None = Query(None, description="Optional property filter"),
    db: Session = Depends(get_db),
):
    """Retrieve top-level operational KPIs calculated using Sydney timezone calendar weeks."""
    service = AnalyticsService(db)
    return service.get_kpi_summary(property_id=property_id)


@router.get("/weekly", response_model=list[WeeklyTrendPoint])
def get_weekly_trends(
    property_id: int | None = Query(None, description="Optional property filter"),
    weeks: int = Query(8, ge=2, le=24, description="Number of historical weeks"),
    db: Session = Depends(get_db),
):
    """Retrieve historical weekly trend points."""
    service = AnalyticsService(db)
    return service.get_weekly_trends(property_id=property_id, weeks_count=weeks)


@router.get("/properties", response_model=list[PropertyComparison])
def get_property_analytics(db: Session = Depends(get_db)):
    """Retrieve side-by-side performance comparison across all hotel properties."""
    service = AnalyticsService(db)
    return service.get_property_comparisons()


@router.get("/topics", response_model=list[TopicDistribution])
def get_topics_analytics(
    property_id: int | None = Query(None, description="Optional property filter"),
    db: Session = Depends(get_db),
):
    """Retrieve operational issue and positive topic distribution across reviews."""
    service = AnalyticsService(db)
    return service.get_topic_distributions(property_id=property_id)


@router.get("/operational-insights", response_model=list[OperationalInsight])
def get_operational_insights(
    property_id: int | None = Query(None, description="Optional property filter"),
    db: Session = Depends(get_db),
):
    """Retrieve actionable operational insights comparing current vs previous periods with supporting review evidence."""
    service = AnalyticsService(db)
    return service.get_operational_insights(property_id=property_id)
