"""
Extraction Service
Orchestrates the ETL process using DLT
"""
import dlt
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from concurrent.futures import ThreadPoolExecutor

from config.settings import get_settings
from services.data_source import hubspot_deals_resource
import os

logger = logging.getLogger(__name__)

# Store extraction statuses (in production, use Redis or database)
extraction_statuses: Dict[str, Dict[str, Any]] = {}


class ExtractionService:
    """Service for managing extraction processes"""
    
    def __init__(self):
        self.settings = get_settings()
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    async def start_extraction(
        self,
        access_token: str,
        tenant_id: str = "default",
        limit: Optional[int] = None,
        properties: Optional[List[str]] = None
    ) -> str:
        """
        Start a new extraction process
        
        Args:
            access_token: HubSpot access token
            tenant_id: Tenant identifier
            limit: Optional limit on number of records
            properties: Optional list of properties to extract
        
        Returns:
            scan_id: Unique identifier for this extraction
        """
        scan_id = str(uuid.uuid4())
        
        # Initialize status
        extraction_statuses[scan_id] = {
            "scan_id": scan_id,
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "progress": {
                "pages_processed": 0,
                "records_processed": 0
            },
            "error": None
        }
        
        # Run extraction in background
        asyncio.create_task(self._run_extraction(
            scan_id=scan_id,
            access_token=access_token,
            tenant_id=tenant_id,
            properties=properties
        ))
        
        logger.info(f"Started extraction - scan_id: {scan_id}")
        return scan_id
    
    async def _run_extraction(
        self,
        scan_id: str,
        access_token: str,
        tenant_id: str,
        properties: Optional[List[str]] = None
    ):
        """Run the extraction process"""
        try:
            # Ensure DATABASE_URL is set for DLT
            if not os.environ.get("DATABASE_URL") and not self.settings.database_url:
                # Construct from components if not set
                db_url = (
                    f"postgresql://{self.settings.db_user}:{self.settings.db_password}"
                    f"@{self.settings.db_host}:{self.settings.db_port}/{self.settings.db_name}"
                )
                os.environ["DATABASE_URL"] = db_url
            elif self.settings.database_url:
                os.environ["DATABASE_URL"] = self.settings.database_url
            
            # Configure DLT pipeline
            # DLT will read database credentials from DATABASE_URL environment variable
            pipeline = dlt.pipeline(
                pipeline_name=self.settings.dlt_pipeline_name,
                destination="postgres",
                dataset_name=self.settings.dlt_database_schema
            )
            
            # Create data source
            deals_data = hubspot_deals_resource(
                access_token=access_token,
                tenant_id=tenant_id,
                properties=properties,
                archived=False,
                checkpoint_interval=10
            )
            
            # Run the pipeline
            load_info = pipeline.run(deals_data)
            
            # Update status
            extraction_statuses[scan_id].update({
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "load_info": {
                    "tables": list(load_info.keys()) if load_info else [],
                    "jobs": [job.asdict() for job in load_info.get("jobs", [])] if load_info else []
                }
            })
            
            logger.info(f"Extraction completed - scan_id: {scan_id}")
            
        except Exception as e:
            logger.error(f"Extraction failed - scan_id: {scan_id}, error: {str(e)}")
            extraction_statuses[scan_id].update({
                "status": "failed",
                "completed_at": datetime.utcnow().isoformat(),
                "error": str(e)
            })
    
    async def get_extraction_status(self, scan_id: str) -> Dict[str, Any]:
        """
        Get the status of an extraction
        
        Args:
            scan_id: Extraction scan identifier
        
        Returns:
            Status information
        """
        if scan_id not in extraction_statuses:
            raise ValueError(f"Extraction {scan_id} not found")
        
        return extraction_statuses[scan_id]
    
    async def get_extraction_results(
        self,
        scan_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get results from a completed extraction
        
        Args:
            scan_id: Extraction scan identifier
            limit: Maximum number of records to return
            offset: Offset for pagination
        
        Returns:
            Results data
        """
        # In a real implementation, query the database
        # For now, return a placeholder
        status = await self.get_extraction_status(scan_id)
        
        if status["status"] != "completed":
            raise ValueError(f"Extraction {scan_id} is not completed yet")
        
        return {
            "scan_id": scan_id,
            "status": status["status"],
            "records": [],  # Would query database here
            "total": 0,
            "limit": limit,
            "offset": offset
        }

