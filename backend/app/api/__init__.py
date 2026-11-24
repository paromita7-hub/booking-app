from app.api.properties import router as properties_router
from app.api.reviews import router as reviews_router
from app.api.analytics import router as analytics_router
from app.api.ingestion import router as ingestion_router

__all__ = [
    "properties_router",
    "reviews_router",
    "analytics_router",
    "ingestion_router",
]
