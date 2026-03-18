from fastapi import APIRouter
from models.scan import ScanRequest, ScanResponse

router = APIRouter(prefix="/scan", tags=["scans"])


@router.post("", response_model=ScanResponse, status_code=200)
async def create_scan(payload: ScanRequest):
    """Stub: accept a scan submission and return a placeholder scan_id."""
    return ScanResponse(scan_id="stub-uuid", status="received")
