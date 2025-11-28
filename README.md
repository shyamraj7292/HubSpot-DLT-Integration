# HubSpot Deals ETL Integration

A production-ready ETL service for extracting HubSpot deals data using DLT (Data Load Tool) and storing it in PostgreSQL.

## Features

- ✅ HubSpot CRM API v3 integration
- ✅ DLT-based data pipeline with checkpointing
- ✅ Multi-tenant data isolation
- ✅ RESTful API for extraction management
- ✅ Rate limiting and error handling
- ✅ PostgreSQL destination with optimized schema
- ✅ Docker Compose setup for easy deployment
- ✅ Comprehensive documentation

## Project Structure

```
.
├── api/                    # API routes and endpoints
│   └── routes/
│       ├── extraction.py   # Extraction endpoints
│       └── health.py       # Health check endpoints
├── config/                 # Configuration
│   └── settings.py         # Application settings
├── docs/                   # Documentation
│   ├── api-integration.md  # HubSpot API integration docs
│   ├── database-schema.md   # Database schema documentation
│   └── api-documentation.md # API endpoint documentation
├── models/                 # Data models
│   └── schemas.py          # Pydantic models
├── services/               # Business logic
│   ├── hubspot_api_service.py  # HubSpot API client
│   ├── data_source.py      # DLT data source
│   └── extraction_service.py   # Extraction orchestration
├── utils/                  # Utilities
│   └── database.py         # Database utilities
├── main.py                 # FastAPI application
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile             # Docker image definition
├── requirements.txt       # Python dependencies
└── config.json            # Project configuration
```

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- HubSpot Developer Account with Private App access token
- PostgreSQL (included in Docker Compose)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd HubSpot-DLT-Integration

# Create environment file
cp .env.example .env

# Edit .env and add your HubSpot access token
# HUBSPOT_ACCESS_TOKEN=pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 2. Start Services with Docker Compose

```bash
# Start PostgreSQL and API services
docker-compose up -d --build

# Check service health
curl http://localhost:5200/health
```

### 3. Start an Extraction

```bash
curl -X POST "http://localhost:5200/api/v1/extractions" \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "tenant_id": "tenant1"
  }'
```

### 4. Check Extraction Status

```bash
# Replace {scan_id} with the scan_id from the previous response
curl "http://localhost:5200/api/v1/extractions/{scan_id}/status"
```

## Local Development Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start PostgreSQL

```bash
docker-compose up -d postgres
```

### 3. Configure Environment

Create a `.env` file:

```env
ENV=dev
HUBSPOT_API_BASE_URL=https://api.hubapi.com
HUBSPOT_API_TIMEOUT=30
HUBSPOT_ACCESS_TOKEN=your_token_here

DLT_PIPELINE_NAME=hubspot_deals
DLT_DATABASE_SCHEMA=hubspot_deals

DATABASE_URL=postgresql://user:password@localhost:5432/hubspot_deals_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hubspot_deals_db
DB_USER=user
DB_PASSWORD=password

SERVICE_PORT=5200
LOG_LEVEL=INFO
```

### 4. Run the Application

```bash
uvicorn main:app --host 0.0.0.0 --port 5200 --reload
```

## API Endpoints

### Health Check

- `GET /health` - Service health status
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check

### Extraction

- `POST /api/v1/extractions` - Start a new extraction
- `GET /api/v1/extractions/{scan_id}/status` - Get extraction status
- `GET /api/v1/extractions/{scan_id}/results` - Get extraction results

See [API Documentation](docs/api-documentation.md) for detailed endpoint documentation.

## HubSpot Setup

### 1. Create Developer Account

1. Go to [https://developers.hubspot.com/](https://developers.hubspot.com/)
2. Create a free developer account
3. Create a test account within the developer portal

### 2. Create Private App

1. Navigate to **Settings → Integrations → Private Apps**
2. Create a new private app called "DLT Deals Extractor"
3. Configure the required scope: `crm.objects.deals.read`
4. Generate and save the access token securely

### 3. Add Test Data

Create 5 different test deals in your HubSpot test account with:
- Different deal stages: qualified, presentation scheduled, closed won, closed lost
- Different amounts: $5K, $25K, $50K, $75K, $100K
- Meaningful descriptions and close dates

See [API Integration Documentation](docs/api-integration.md) for more details.

## Database Schema

The service creates a PostgreSQL schema `hubspot_deals` with a `deals` table.

Key features:
- Multi-tenant support with `_tenant_id`
- ETL metadata: `_extracted_at`, `_scan_id`
- Optimized indexes for performance
- JSONB column for flexible property storage

See [Database Schema Documentation](docs/database-schema.md) for complete schema details.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment (dev/stage/prod) | `dev` |
| `HUBSPOT_API_BASE_URL` | HubSpot API base URL | `https://api.hubapi.com` |
| `HUBSPOT_API_TIMEOUT` | API request timeout (seconds) | `30` |
| `HUBSPOT_ACCESS_TOKEN` | HubSpot access token | - |
| `DLT_PIPELINE_NAME` | DLT pipeline name | `hubspot_deals` |
| `DLT_DATABASE_SCHEMA` | Database schema name | `hubspot_deals` |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `SERVICE_PORT` | API service port | `5200` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Ports

- **Development**: 5200
- **Staging**: 5201
- **Production**: 5202

## Testing

### Manual Testing

1. **Health Check**
   ```bash
   curl http://localhost:5200/health
   ```

2. **Start Extraction**
   ```bash
   curl -X POST "http://localhost:5200/api/v1/extractions" \
     -H "Content-Type: application/json" \
     -d '{"access_token": "your_token", "tenant_id": "test"}'
   ```

3. **Check Status**
   ```bash
   curl http://localhost:5200/api/v1/extractions/{scan_id}/status
   ```

4. **Verify Database**
   ```bash
   docker-compose exec postgres psql -U user -d hubspot_deals_db -c "SELECT COUNT(*) FROM hubspot_deals.deals;"
   ```

### Test Checklist

- [ ] Health endpoint returns 200
- [ ] Extraction starts successfully
- [ ] All 5 test deals are extracted
- [ ] Database records match expected format
- [ ] Checkpoint functionality works (interrupt and resume)
- [ ] API documentation accessible at `/docs`

## Documentation

- [HubSpot API Integration](docs/api-integration.md) - API integration details
- [Database Schema](docs/database-schema.md) - Database design and schema
- [API Documentation](docs/api-documentation.md) - REST API endpoints

## Rate Limiting

HubSpot API rate limits:
- **Limit**: 150 requests per 10 seconds
- **Window**: 10 seconds rolling window

The service automatically handles rate limiting with exponential backoff.

## Error Handling

The service handles common HubSpot API errors:
- 401 Unauthorized - Invalid access token
- 403 Forbidden - Insufficient permissions
- 429 Too Many Requests - Rate limit exceeded
- 500 Internal Server Error - Retry with backoff

## Multi-Tenant Support

The service supports multi-tenant data isolation:
- Each extraction is tagged with a `tenant_id`
- Database schema includes `_tenant_id` in primary key
- Queries are filtered by tenant for data isolation

## Development

### Project Phases

- **Phase 1**: Generate Structure & Update Documentation ✅
- **Phase 2**: Data Addition Tasks (HubSpot setup) ⏳
- **Phase 3**: Implementation Tasks ✅

### Adding New Features

1. Create feature branch
2. Implement changes
3. Update documentation
4. Test thoroughly
5. Submit pull request

## License

[Add your license here]

## Support

For issues and questions, please open an issue in the repository.
