"""
Test script for HubSpot Deals Extraction
Run this script to test the extraction functionality
"""
import asyncio
import os
from services.hubspot_api_service import HubSpotAPIService
from services.extraction_service import ExtractionService


async def test_hubspot_api():
    """Test HubSpot API service"""
    print("Testing HubSpot API Service...")
    
    # Get access token from environment
    access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
    if not access_token:
        print("ERROR: HUBSPOT_ACCESS_TOKEN not set in environment")
        return False
    
    try:
        # Initialize API service
        api_service = HubSpotAPIService(access_token)
        
        # Validate credentials
        print("Validating credentials...")
        is_valid = await api_service.validate_credentials()
        if not is_valid:
            print("ERROR: Invalid credentials")
            return False
        print("✓ Credentials validated")
        
        # Get first page of deals
        print("Fetching deals...")
        deals_data = await api_service.get_deals(limit=5)
        deals = deals_data.get("results", [])
        print(f"✓ Retrieved {len(deals)} deals")
        
        if deals:
            print(f"Sample deal: {deals[0].get('properties', {}).get('dealname', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


async def test_extraction_service():
    """Test extraction service"""
    print("\nTesting Extraction Service...")
    
    access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
    if not access_token:
        print("ERROR: HUBSPOT_ACCESS_TOKEN not set in environment")
        return False
    
    try:
        extraction_service = ExtractionService()
        
        # Start extraction
        print("Starting extraction...")
        scan_id = await extraction_service.start_extraction(
            access_token=access_token,
            tenant_id="test",
            properties=["dealname", "amount", "dealstage"]
        )
        print(f"✓ Extraction started with scan_id: {scan_id}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Check status
        print("Checking extraction status...")
        status = await extraction_service.get_extraction_status(scan_id)
        print(f"✓ Status: {status['status']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("=" * 50)
    print("HubSpot Deals ETL - Test Script")
    print("=" * 50)
    
    # Test API service
    api_test = await test_hubspot_api()
    
    if api_test:
        # Test extraction service (requires database)
        print("\nNote: Extraction service test requires database connection")
        # extraction_test = await test_extraction_service()
    
    print("\n" + "=" * 50)
    if api_test:
        print("Tests completed successfully!")
    else:
        print("Some tests failed. Check the errors above.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())

