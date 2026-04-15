from typing import Optional
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import uuid


class ImageDTO(BaseModel):
    """Image metadata"""
    uid: uuid.UUID
    metadata_: Dict
    image_path: Optional[str] = None

class SearchResultDTO(BaseModel):
    id: str
    match_percentage: float
    uid: str
    meta: Optional[Dict] = None  # Changed from str to Dict to support metadata


class SearchByImageResponseDTO(BaseModel):
    calculated_hash: str
    total_matches: int
    results: list[SearchResultDTO]


class SearchByHashResponseDTO(BaseModel):
    query_hash: str
    total_matches: int
    results: list[SearchResultDTO]