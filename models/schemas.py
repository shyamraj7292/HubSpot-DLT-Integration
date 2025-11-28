"""
Data models and schemas
"""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class DealProperty(BaseModel):
    """HubSpot deal property"""
    name: str
    value: Any
    source: Optional[str] = None


class HubSpotDeal(BaseModel):
    """HubSpot deal model"""
    id: str
    properties: dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    archived: bool = False


class DealRecord(BaseModel):
    """Deal record with ETL metadata"""
    deal_id: str
    properties: dict[str, Any]
    _extracted_at: datetime
    _scan_id: str
    _tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    archived: bool = False

