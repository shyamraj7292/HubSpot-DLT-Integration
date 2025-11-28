# Setup Instructions

## Phase 2: HubSpot Developer Account Setup

### Task 2.1: Set Up HubSpot Developer Account

1. Go to [https://developers.hubspot.com/](https://developers.hubspot.com/)
2. Create a free developer account
3. Create a test account within the developer portal
4. Navigate to **Settings → Integrations → Private Apps**
5. Create a new private app called "DLT Deals Extractor"
6. Configure the required scopes: `crm.objects.deals.read`
7. Generate and save the access token securely

### Task 2.2: Add Test Deal Records

1. Create 5 different test deals in your HubSpot test account
2. Include variety in deal stages, amounts, and types:
   - **Deal Stages**: qualified, presentation scheduled, closed won, closed lost
   - **Amounts**: $5K, $25K, $50K, $75K, $100K
   - Add meaningful descriptions and close dates
3. Note down the deal IDs for verification later

## Phase 3: Testing and Validation

### Task 3.4: Test and Validate

1. **Start the Docker services:**
   ```bash
   docker-compose up -d --build
   ```

2. **Test health endpoint:**
   ```bash
   curl http://localhost:5200/health
   ```

3. **Create test extraction request:**
   ```bash
   curl -X POST "http://localhost:5200/api/v1/extractions" \
     -H "Content-Type: application/json" \
     -d '{
       "access_token": "your_hubspot_access_token_here",
       "tenant_id": "test"
     }'
   ```

4. **Start a scan and monitor the status:**
   ```bash
   # Get scan_id from previous response, then:
   curl http://localhost:5200/api/v1/extractions/{scan_id}/status
   ```

5. **Verify all 5 test deals are extracted correctly:**
   ```bash
   # Check database
   docker-compose exec postgres psql -U user -d hubspot_deals_db -c "SELECT deal_id, deal_name, amount, deal_stage FROM hubspot_deals.deals;"
   ```

6. **Check database records match expected format:**
   ```bash
   docker-compose exec postgres psql -U user -d hubspot_deals_db -c "SELECT * FROM hubspot_deals.deals LIMIT 1;"
   ```

7. **Test checkpoint functionality** by interrupting and resuming (requires manual testing)

8. **Verify API documentation** at `/docs` endpoint:
   - Open browser: http://localhost:5200/docs

## Environment Configuration

### Create .env file

Copy `.env.example` to `.env` and update with your values:

```env
ENV=dev
HUBSPOT_API_BASE_URL=https://api.hubapi.com
HUBSPOT_API_TIMEOUT=30
HUBSPOT_ACCESS_TOKEN=pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

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

### DLT Secrets (Optional)

If you prefer to use DLT secrets file instead of environment variables:

1. Create `.dlt/secrets.toml`:
   ```bash
   mkdir -p .dlt
   cp .dlt/secrets.toml.example .dlt/secrets.toml
   ```

2. Update `.dlt/secrets.toml` with your database credentials

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running: `docker-compose ps`
- Check database logs: `docker-compose logs postgres`
- Verify connection string in `.env`

### HubSpot API Issues

- Verify access token is valid
- Check token has `crm.objects.deals.read` scope
- Verify rate limits are not exceeded

### DLT Pipeline Issues

- Check DLT logs in console output
- Verify DATABASE_URL is set correctly
- Ensure PostgreSQL schema exists

