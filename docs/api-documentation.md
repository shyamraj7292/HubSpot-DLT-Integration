# API Documentation

## Overview

This document describes the REST API endpoints exposed by the HubSpot Deals ETL Service.

## Base URL

- **Development**: `http://localhost:5200`
- **Staging**: `http://localhost:5201`
- **Production**: `http://localhost:5202`

## Authentication

Currently, authentication is handled via access tokens passed in request bodies. Future versions may implement API key authentication.

## Endpoints

### Health Check

#### GET /health

Check service health status.

**Response**: `200 OK`

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "hubspot_deals_etl"
}
```

#### GET /health/ready

Check if service is ready to accept requests.

**Response**: `200 OK`

```json
{
  "status": "ready",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### GET /health/live

Check if service is alive.

**Response**: `200 OK`

```json
{
  "status": "alive",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

### Extraction Endpoints

#### POST /api/v1/extractions

Start a new extraction scan.

**Request Body**:

```json
{
  "access_token": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenant_id": "default",
  "limit": 100,
  "properties": ["dealname", "amount", "dealstage"]
}
```

**Request Schema**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_token` | string | Yes | HubSpot private app access token |
| `tenant_id` | string | No | Tenant identifier (default: "default") |
| `limit` | integer | No | Maximum records per page (default: 100) |
| `properties` | array[string] | No | List of deal properties to extract |

**Response**: `200 OK`

```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "message": "Extraction started with scan_id: 550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses**:

- `400 Bad Request`: Invalid request body
- `500 Internal Server Error`: Server error

**Example Request**:

```bash
curl -X POST "http://localhost:5200/api/v1/extractions" \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "tenant_id": "tenant1",
    "properties": ["dealname", "amount", "dealstage"]
  }'
```

---

#### GET /api/v1/extractions/{scan_id}/status

Get the status of an extraction scan.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `scan_id` | string | Unique scan identifier |

**Response**: `200 OK`

```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": {
    "pages_processed": 5,
    "records_processed": 450
  },
  "started_at": "2024-01-15T10:30:00.000Z",
  "completed_at": null,
  "error": null
}
```

**Status Values**:

- `running`: Extraction is in progress
- `completed`: Extraction completed successfully
- `failed`: Extraction failed

**Error Responses**:

- `404 Not Found`: Scan ID not found
- `500 Internal Server Error`: Server error

**Example Request**:

```bash
curl "http://localhost:5200/api/v1/extractions/550e8400-e29b-41d4-a716-446655440000/status"
```

---

#### GET /api/v1/extractions/{scan_id}/results

Get results from a completed extraction.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `scan_id` | string | Unique scan identifier |

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Maximum records to return (default: 100) |
| `offset` | integer | No | Offset for pagination (default: 0) |

**Response**: `200 OK`

```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "records": [
    {
      "deal_id": "123456789",
      "deal_name": "Sample Deal",
      "amount": 50000.00,
      "deal_stage": "qualifiedtobuy",
      "created_at": "2024-01-01T00:00:00Z",
      "_extracted_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 450,
  "limit": 100,
  "offset": 0
}
```

**Error Responses**:

- `400 Bad Request`: Extraction not completed yet
- `404 Not Found`: Scan ID not found
- `500 Internal Server Error`: Server error

**Example Request**:

```bash
curl "http://localhost:5200/api/v1/extractions/550e8400-e29b-41d4-a716-446655440000/results?limit=50&offset=0"
```

---

## Error Responses

### Standard Error Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Bad Request - Invalid input |
| `404` | Not Found - Resource not found |
| `500` | Internal Server Error - Server error |

### Example Error Response

```json
{
  "detail": "Extraction 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

---

## Example Workflow

### 1. Start an Extraction

```bash
curl -X POST "http://localhost:5200/api/v1/extractions" \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "tenant_id": "tenant1"
  }'
```

**Response**:
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "message": "Extraction started with scan_id: 550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. Check Extraction Status

```bash
curl "http://localhost:5200/api/v1/extractions/550e8400-e29b-41d4-a716-446655440000/status"
```

**Response** (while running):
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": {
    "pages_processed": 3,
    "records_processed": 250
  }
}
```

**Response** (when completed):
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "completed_at": "2024-01-15T10:35:00.000Z"
}
```

### 3. Get Extraction Results

```bash
curl "http://localhost:5200/api/v1/extractions/550e8400-e29b-41d4-a716-446655440000/results"
```

---

## API Documentation (Swagger/OpenAPI)

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:5200/docs`
- **ReDoc**: `http://localhost:5200/redoc`
- **OpenAPI JSON**: `http://localhost:5200/openapi.json`

## Rate Limiting

Currently, no rate limiting is implemented at the API level. Rate limiting is handled internally for HubSpot API calls.

## Versioning

API versioning is handled through the URL path (`/api/v1/`). Future versions will use `/api/v2/`, etc.

