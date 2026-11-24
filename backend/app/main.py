from datetime import datetime
import pytz
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database import get_db
from app.api.properties import router as properties_router
from app.api.reviews import router as reviews_router
from app.api.analytics import router as analytics_router
from app.api.ingestion import router as ingestion_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Operational Review Insights & Performance Analytics for Azzurro Hotels.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits frontend dev and docker networking
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(properties_router, prefix=settings.API_V1_STR)
app.include_router(reviews_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(ingestion_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Health check validating application state, database connection, and Sydney timezone."""
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    tz = pytz.timezone(settings.APP_TIMEZONE)
    current_sydney_time = datetime.now(tz).isoformat()

    return {
        "status": "healthy" if db_ok else "degraded",
        "database_connected": db_ok,
        "version": settings.VERSION,
        "sydney_time": current_sydney_time,
        "automated_scraping_enabled": settings.ALLOW_AUTOMATED_SCRAPING,
    }
