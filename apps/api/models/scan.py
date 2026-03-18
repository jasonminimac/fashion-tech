from pydantic import BaseModel
from typing import Optional


class ScanRequest(BaseModel):
    user_id: Optional[str] = None
    notes: Optional[str] = None


class ScanResponse(BaseModel):
    scan_id: str
    status: str
