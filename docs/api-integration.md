# HubSpot Deals API Integration Documentation

## Overview

This document describes the integration with HubSpot CRM API v3 for extracting deals data.

## Authentication

### Method: Private App Access Tokens

HubSpot uses private app access tokens for authentication. These tokens are generated through the HubSpot Developer Portal.

### Setup Steps

1. Navigate to `https://developers.hubspot.com/`
2. Create a free developer account
3. Create a test account within the developer portal
4. Navigate to **Settings → Integrations → Private Apps**
5. Create a new private app called "DLT Deals Extractor"
6. Configure the required scopes: `crm.objects.deals.read`
7. Generate and save the access token securely

### Authentication Header

All API requests must include the access token in the Authorization header:

```
Authorization: Bearer {access_token}
```

## API Endpoint

### Base URL

```
https://api.hubapi.com
```

### Deals Endpoint

```
GET /crm/v3/objects/deals
```

## Query Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of deals to return (max: 100) | 100 |
| `after` | string | No | Pagination cursor from previous response | - |
| `properties` | string | No | Comma-separated list of property names to retrieve | All properties |
| `archived` | boolean | No | Whether to include archived deals | false |

### Example Request

```bash
curl -X GET "https://api.hubapi.com/crm/v3/objects/deals?limit=100&properties=dealname,amount,dealstage" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Response Structure

### Success Response (200 OK)

```json
{
  "results": [
    {
      "id": "123456789",
      "properties": {
        "dealname": "Sample Deal",
        "amount": "50000",
        "dealstage": "qualifiedtobuy",
        "pipeline": "default",
        "closedate": "2024-12-31T00:00:00.000Z",
        "createdate": "2024-01-01T00:00:00.000Z",
        "hs_lastmodifieddate": "2024-01-15T00:00:00.000Z",
        "description": "Deal description",
        "dealtype": "newbusiness"
      },
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-01-15T00:00:00.000Z",
      "archived": false
    }
  ],
  "paging": {
    "next": {
      "after": "eyJsYXN0X2lkIjo0NzQwNDk5NjQsImxhc3RfdmFsdWUiOiI0NzQwNDk5NjQifQ=="
    }
  }
}
```

### Response Fields

- **results**: Array of deal objects
  - **id**: Unique deal identifier
  - **properties**: Object containing deal properties
  - **createdAt**: ISO 8601 timestamp of creation
  - **updatedAt**: ISO 8601 timestamp of last update
  - **archived**: Boolean indicating if deal is archived

- **paging**: Pagination information
  - **next.after**: Cursor for next page (if available)

## Pagination

HubSpot uses cursor-based pagination. To retrieve the next page:

1. Check if `paging.next.after` exists in the response
2. Include the `after` parameter in the next request with the cursor value
3. Continue until `paging.next.after` is null

### Example Pagination Flow

```python
after = None
while True:
    response = get_deals(after=after)
    deals = response['results']
    # Process deals...
    
    if not response.get('paging', {}).get('next', {}).get('after'):
        break
    after = response['paging']['next']['after']
```

## Available Deal Properties

Common deal properties available from HubSpot:

- `dealname` - Deal name
- `amount` - Deal amount (numeric)
- `dealstage` - Current deal stage
- `pipeline` - Pipeline name
- `closedate` - Expected close date
- `createdate` - Creation timestamp
- `hs_lastmodifieddate` - Last modification timestamp
- `description` - Deal description
- `dealtype` - Type of deal (newbusiness, existingbusiness, etc.)

For a complete list, refer to [HubSpot Deal Properties Documentation](https://developers.hubspot.com/docs/api/crm/deals).

## Rate Limits

HubSpot API rate limits:

- **Limit**: 150 requests per 10 seconds per access token
- **Window**: 10 seconds rolling window

### Rate Limit Headers

When approaching rate limits, HubSpot includes these headers:

- `X-HubSpot-RateLimit-Daily`: Daily limit remaining
- `X-HubSpot-RateLimit-DailyLimit`: Daily limit total
- `Retry-After`: Seconds to wait before retrying (on 429 errors)

### Handling Rate Limits

1. Track request timestamps
2. Implement exponential backoff
3. Respect `Retry-After` header on 429 responses
4. Batch requests when possible

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "status": "error",
  "message": "Invalid access token"
}
```
**Solution**: Verify access token is valid and not expired

#### 403 Forbidden
```json
{
  "status": "error",
  "message": "Insufficient permissions"
}
```
**Solution**: Verify private app has `crm.objects.deals.read` scope

#### 429 Too Many Requests
```json
{
  "status": "error",
  "message": "Rate limit exceeded"
}
```
**Solution**: Wait for the duration specified in `Retry-After` header

#### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Internal server error"
}
```
**Solution**: Retry after a delay, contact HubSpot support if persistent

### Error Handling Best Practices

1. Implement retry logic with exponential backoff
2. Log all errors with context
3. Handle rate limits gracefully
4. Validate responses before processing
5. Use timeouts to prevent hanging requests

## Data Type Conversions

### Timestamps

HubSpot returns timestamps in milliseconds since epoch. Convert to datetime:

```python
timestamp_ms = properties.get("createdate")
timestamp = datetime.fromtimestamp(int(timestamp_ms) / 1000)
```

### Amounts

Deal amounts are returned as strings. Convert to numeric:

```python
amount = float(properties.get("amount", 0))
```

### Booleans

Boolean properties are returned as strings ("true"/"false"). Convert:

```python
archived = properties.get("archived", "false").lower() == "true"
```

## References

- [HubSpot CRM API v3 Documentation](https://developers.hubspot.com/docs/api/crm/deals)
- [HubSpot Authentication Guide](https://developers.hubspot.com/docs/api/working-with-oauth)
- [HubSpot Rate Limits](https://developers.hubspot.com/docs/api/working-with-apis)

