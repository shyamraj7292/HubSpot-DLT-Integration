"""
DLT Data Source for HubSpot Deals
"""
import dlt
import logging
import asyncio
from typing import Iterator, Dict, Any, Optional, List
from datetime import datetime
import uuid

from services.hubspot_api_service import HubSpotAPIService

logger = logging.getLogger(__name__)


@dlt.resource(
    name="deals",
    write_disposition="merge",
    primary_key="deal_id"
)
def hubspot_deals_resource(
    access_token: str,
    tenant_id: str = "default",
    properties: Optional[List[str]] = None,
    archived: bool = False,
    checkpoint_interval: int = 10
):
    """
    DLT resource for HubSpot deals
    
    Args:
        access_token: HubSpot access token
        tenant_id: Tenant identifier for multi-tenant isolation
        properties: List of deal properties to retrieve
        archived: Whether to include archived deals
        checkpoint_interval: Number of pages between checkpoints
    
    Yields:
        Deal records with ETL metadata
    """
    api_service = HubSpotAPIService(access_token)
    scan_id = str(uuid.uuid4())
    page_count = 0
    
    logger.info(f"Starting deals extraction - scan_id: {scan_id}, tenant_id: {tenant_id}")
    
    async def _async_generator():
        """Async generator that fetches deals"""
        async for page_data in api_service.get_all_deals(
            properties=properties,
            archived=archived
        ):
            yield page_data
    
    try:
        # Run async generator in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async_gen = _async_generator()
            
            while True:
                try:
                    page_data = loop.run_until_complete(async_gen.__anext__())
                    
                    results = page_data.get("results", [])
                    
                    for deal in results:
                        # Transform HubSpot deal to our schema
                        deal_record = transform_deal_record(
                            deal=deal,
                            scan_id=scan_id,
                            tenant_id=tenant_id
                        )
                        yield deal_record
                    
                    page_count += 1
                    
                    # Create checkpoint every N pages
                    if page_count % checkpoint_interval == 0:
                        logger.info(f"Checkpoint: Processed {page_count} pages")
                        # DLT will handle checkpointing automatically
                    
                    # Log progress
                    if page_count % 10 == 0:
                        logger.info(f"Extracted {page_count} pages of deals")
                        
                except StopAsyncIteration:
                    break
                    
        finally:
            loop.close()
        
        logger.info(f"Extraction completed - scan_id: {scan_id}, pages: {page_count}")
        
    except Exception as e:
        logger.error(f"Error in deals extraction: {str(e)}")
        raise


def transform_deal_record(
    deal: Dict[str, Any],
    scan_id: str,
    tenant_id: str
) -> Dict[str, Any]:
    """
    Transform HubSpot deal to our database schema
    
    Args:
        deal: Raw deal data from HubSpot API
        scan_id: Extraction scan identifier
        tenant_id: Tenant identifier
    
    Returns:
        Transformed deal record
    """
    deal_id = deal.get("id")
    properties = deal.get("properties", {})
    
    # Extract timestamps
    created_at = None
    updated_at = None
    
    if "createdate" in properties:
        try:
            created_at = datetime.fromtimestamp(int(properties["createdate"]) / 1000)
        except (ValueError, TypeError):
            pass
    
    if "hs_lastmodifieddate" in properties:
        try:
            updated_at = datetime.fromtimestamp(int(properties["hs_lastmodifieddate"]) / 1000)
        except (ValueError, TypeError):
            pass
    
    # Transform amount to numeric
    amount = None
    if "amount" in properties and properties["amount"]:
        try:
            amount = float(properties["amount"])
        except (ValueError, TypeError):
            pass
    
    # Build record
    record = {
        "deal_id": deal_id,
        "tenant_id": tenant_id,
        "scan_id": scan_id,
        "extracted_at": datetime.utcnow(),
        
        # Deal properties
        "deal_name": properties.get("dealname"),
        "amount": amount,
        "deal_stage": properties.get("dealstage"),
        "pipeline": properties.get("pipeline"),
        "close_date": properties.get("closedate"),
        "description": properties.get("description"),
        "deal_type": properties.get("dealtype"),
        
        # Timestamps
        "created_at": created_at,
        "updated_at": updated_at,
        "archived": deal.get("archived", False),
        
        # Store all properties as JSON for flexibility
        "properties_json": properties
    }
    
    return record

