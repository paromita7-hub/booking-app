from datetime import datetime
from pydantic import BaseModel, ConfigDict


class IngestionLogResponse(BaseModel):
    id: int
    source: str
    property_id: int | None = None
    property_name: str | None = None
    status: str
    records_processed: int
    records_added: int
    records_skipped: int
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class IngestionStatusResponse(BaseModel):
    automated_scraping_enabled: bool
    allowed_sources: list[str]
    total_imports_run: int
    last_import_timestamp: datetime | None = None
    last_import_status: str | None = None
