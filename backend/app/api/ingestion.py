from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.ingestion_log import IngestionLog
from app.schemas.ingestion import IngestionLogResponse, IngestionStatusResponse
from app.services.ingestion_service import IngestionService
from app.config import settings

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


@router.get("/status", response_model=IngestionStatusResponse)
def get_ingestion_status(db: Session = Depends(get_db)):
    """Check current review collection status, permissions, and history."""
    total_logs = db.query(IngestionLog).count()
    last_log = db.query(IngestionLog).order_by(desc(IngestionLog.started_at)).first()

    return IngestionStatusResponse(
        automated_scraping_enabled=settings.ALLOW_AUTOMATED_SCRAPING,
        allowed_sources=["csv_import", "json_import"] + (["playwright_scraper"] if settings.ALLOW_AUTOMATED_SCRAPING else []),
        total_imports_run=total_logs,
        last_import_timestamp=last_log.started_at if last_log else None,
        last_import_status=last_log.status if last_log else None,
    )


@router.get("/history", response_model=list[IngestionLogResponse])
def get_ingestion_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Browse historical ingestion runs, records added, skipped, and errors."""
    logs = db.query(IngestionLog).order_by(desc(IngestionLog.started_at)).limit(limit).all()
    results = []
    for l in logs:
        results.append(
            IngestionLogResponse(
                id=l.id,
                source=l.source,
                property_id=l.property_id,
                property_name=l.property.name if l.property else None,
                status=l.status,
                records_processed=l.records_processed,
                records_added=l.records_added,
                records_skipped=l.records_skipped,
                error_message=l.error_message,
                started_at=l.started_at,
                completed_at=l.completed_at,
            )
        )
    return results


@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    property_id: int | None = None,
    is_demo: bool = False,
    db: Session = Depends(get_db),
):
    """Trigger manual data ingestion from CSV or JSON file."""
    content = await file.read()
    filename = file.filename or "import_data"
    service = IngestionService(db)

    if filename.endswith(".json"):
        records = service.json_adapter.parse(content)
        source = f"json_upload:{filename}"
    else:
        records = service.csv_adapter.parse(content)
        source = f"csv_upload:{filename}"

    if not records:
        raise HTTPException(status_code=400, detail="Uploaded file contained no valid review records")

    log = service.ingest_records(
        raw_records=records,
        source_name=source,
        default_property_id=property_id,
        is_demo=is_demo,
    )

    return {
        "status": log.status,
        "records_processed": log.records_processed,
        "records_added": log.records_added,
        "records_skipped": log.records_skipped,
        "error_message": log.error_message,
        "log_id": log.id,
    }
