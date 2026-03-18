from pydantic import BaseModel
from typing import Any, List


class Garment(BaseModel):
    id: str
    name: str
    brand: str | None = None
    category: str | None = None


class GarmentListResponse(BaseModel):
    garments: List[Any]
    total: int
