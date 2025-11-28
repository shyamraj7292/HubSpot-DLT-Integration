"""
Extraction endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import logging

from services.extraction_service import ExtractionService

logger = logging.getLogger(__name__)
router = APIRouter()


class ExtractionRequest(BaseModel):
    """Request model for starting an extraction"""
    access_token: str
    tenant_id: Optional[str] = "default"
    limit: Optional[int] = 100
    properties: Optional[list[str]] = None


class ExtractionResponse(BaseModel):
    """Response model for extraction"""
    scan_id: str
    status: str
    message: str


class ScanStatusResponse(BaseModel):
    """Response model for scan status"""
    scan_id: str
    status: str
    progress: Optional[dict] = None
    error: Optional[str] = None


@router.post("/extractions", response_model=ExtractionResponse)
async def start_extraction(request: ExtractionRequest, background_tasks: BackgroundTasks):
    """Start a new extraction scan"""
    try:
        extraction_service = ExtractionService()
        scan_id = await extraction_service.start_extraction(
            access_token=request.access_token,
            tenant_id=request.tenant_id,
            limit=request.limit,
            properties=request.properties
        )
        
        return ExtractionResponse(
            scan_id=scan_id,
            status="started",
            message=f"Extraction started with scan_id: {scan_id}"
        )
    except Exception as e:
        logger.error(f"Error starting extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/extractions/{scan_id}/status", response_model=ScanStatusResponse)
async def get_extraction_status(scan_id: str):
    """Get the status of an extraction scan"""
    try:
        extraction_service = ExtractionService()
        status = await extraction_service.get_extraction_status(scan_id)
        
        return ScanStatusResponse(**status)
    except Exception as e:
        logger.error(f"Error getting extraction status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/extractions/{scan_id}/results")
async def get_extraction_results(scan_id: str, limit: int = 100, offset: int = 0):
    """Get results from a completed extraction"""
    try:
        extraction_service = ExtractionService()
        results = await extraction_service.get_extraction_results(
            scan_id=scan_id,
            limit=limit,
            offset=offset
        )
        
        return results
    except Exception as e:
        logger.error(f"Error getting extraction results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

