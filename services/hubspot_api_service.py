"""
HubSpot API Service
Handles authentication and API calls to HubSpot CRM API v3
"""
import httpx
import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime

from config.settings import get_settings

logger = logging.getLogger(__name__)


class HubSpotAPIError(Exception):
    """Custom exception for HubSpot API errors"""
    pass


class RateLimitError(HubSpotAPIError):
    """Exception for rate limit errors"""
    pass


class HubSpotAPIService:
    """Service for interacting with HubSpot CRM API v3"""
    
    def __init__(self, access_token: str):
        """
        Initialize HubSpot API service
        
        Args:
            access_token: HubSpot private app access token
        """
        self.access_token = access_token
        self.settings = get_settings()
        self.base_url = self.settings.hubspot_api_base_url
        self.timeout = self.settings.hubspot_api_timeout
        
        # Rate limiting: HubSpot allows 150 requests per 10 seconds
        self.rate_limit_requests = 150
        self.rate_limit_window = 10  # seconds
        self.request_times = []
        
        # Headers
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        current_time = time.time()
        
        # Remove requests older than the rate limit window
        self.request_times = [
            req_time for req_time in self.request_times
            if current_time - req_time < self.rate_limit_window
        ]
        
        # If we've hit the limit, wait until we can make another request
        if len(self.request_times) >= self.rate_limit_requests:
            sleep_time = self.rate_limit_window - (current_time - self.request_times[0]) + 0.1
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                # Clean up again after sleep
                self.request_times = [
                    req_time for req_time in self.request_times
                    if time.time() - req_time < self.rate_limit_window
                ]
        
        # Record this request
        self.request_times.append(current_time)
    
    def _handle_error(self, response: httpx.Response):
        """Handle API errors"""
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 10))
            raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds")
        elif response.status_code == 401:
            raise HubSpotAPIError("Authentication failed. Check your access token.")
        elif response.status_code == 403:
            raise HubSpotAPIError("Access forbidden. Check your API scopes.")
        elif response.status_code >= 400:
            error_detail = response.text
            raise HubSpotAPIError(f"API error {response.status_code}: {error_detail}")
    
    async def validate_credentials(self) -> bool:
        """
        Validate HubSpot credentials
        
        Returns:
            True if credentials are valid
        """
        try:
            # Make a simple API call to validate credentials
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/crm/v3/objects/deals",
                    headers=self.headers,
                    params={"limit": 1}
                )
                
                if response.status_code == 200:
                    logger.info("HubSpot credentials validated successfully")
                    return True
                else:
                    self._handle_error(response)
                    return False
        except Exception as e:
            logger.error(f"Error validating credentials: {str(e)}")
            raise HubSpotAPIError(f"Failed to validate credentials: {str(e)}")
    
    async def get_deals(
        self,
        limit: int = 100,
        after: Optional[str] = None,
        properties: Optional[List[str]] = None,
        archived: bool = False
    ) -> Dict[str, Any]:
        """
        Get deals from HubSpot
        
        Args:
            limit: Maximum number of deals to return (default: 100, max: 100)
            after: Pagination cursor (from previous response)
            properties: List of deal properties to retrieve
            archived: Whether to include archived deals
        
        Returns:
            Dictionary with deals data and pagination info
        """
        self._check_rate_limit()
        
        # Default properties to retrieve
        if properties is None:
            properties = [
                "dealname", "amount", "dealstage", "pipeline", "closedate",
                "createdate", "hs_lastmodifieddate", "description", "dealtype"
            ]
        
        params = {
            "limit": min(limit, 100),  # HubSpot max is 100
            "archived": str(archived).lower()
        }
        
        if after:
            params["after"] = after
        
        if properties:
            params["properties"] = ",".join(properties)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/crm/v3/objects/deals",
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Retrieved {len(data.get('results', []))} deals")
                    return data
                else:
                    self._handle_error(response)
        except httpx.TimeoutException:
            raise HubSpotAPIError("Request timeout. HubSpot API did not respond in time.")
        except httpx.RequestError as e:
            raise HubSpotAPIError(f"Request error: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting deals: {str(e)}")
            raise HubSpotAPIError(f"Failed to get deals: {str(e)}")
    
    async def get_all_deals(
        self,
        properties: Optional[List[str]] = None,
        archived: bool = False,
        max_pages: Optional[int] = None
    ):
        """
        Generator that yields all deals with pagination
        
        Args:
            properties: List of deal properties to retrieve
            archived: Whether to include archived deals
            max_pages: Maximum number of pages to fetch (None for all)
        
        Yields:
            Dictionary with deals data for each page
        """
        page_count = 0
        after = None
        
        while True:
            if max_pages and page_count >= max_pages:
                break
            
            response_data = await self.get_deals(
                limit=100,
                after=after,
                properties=properties,
                archived=archived
            )
            
            yield response_data
            
            # Check if there are more pages
            paging = response_data.get("paging", {})
            after = paging.get("next", {}).get("after")
            
            if not after:
                break
            
            page_count += 1

