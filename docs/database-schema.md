# Database Schema Documentation

## Overview

This document describes the PostgreSQL database schema for storing HubSpot deals data with ETL metadata and multi-tenant support.

## Schema: hubspot_deals

All tables are created in the `hubspot_deals` schema.

## Table: deals

Stores HubSpot deal records with ETL metadata.

### CREATE TABLE Statement

```sql
CREATE SCHEMA IF NOT EXISTS hubspot_deals;

CREATE TABLE IF NOT EXISTS hubspot_deals.deals (
    -- Primary Key
    deal_id VARCHAR(255) NOT NULL,
    
    -- ETL Metadata
    _extracted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    _scan_id VARCHAR(255) NOT NULL,
    _tenant_id VARCHAR(255) NOT NULL DEFAULT 'default',
    
    -- Deal Properties
    deal_name VARCHAR(500),
    amount NUMERIC(15, 2),
    deal_stage VARCHAR(255),
    pipeline VARCHAR(255),
    close_date VARCHAR(255),
    description TEXT,
    deal_type VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    archived BOOLEAN DEFAULT FALSE,
    
    -- Flexible Properties Storage
    properties_json JSONB,
    
    -- Primary Key Constraint
    PRIMARY KEY (deal_id, _tenant_id, _scan_id)
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_deals_tenant_id ON hubspot_deals.deals(_tenant_id);
CREATE INDEX IF NOT EXISTS idx_deals_scan_id ON hubspot_deals.deals(_scan_id);
CREATE INDEX IF NOT EXISTS idx_deals_extracted_at ON hubspot_deals.deals(_extracted_at);
CREATE INDEX IF NOT EXISTS idx_deals_deal_stage ON hubspot_deals.deals(deal_stage);
CREATE INDEX IF NOT EXISTS idx_deals_created_at ON hubspot_deals.deals(created_at);
CREATE INDEX IF NOT EXISTS idx_deals_updated_at ON hubspot_deals.deals(updated_at);
CREATE INDEX IF NOT EXISTS idx_deals_tenant_scan ON hubspot_deals.deals(_tenant_id, _scan_id);
CREATE INDEX IF NOT EXISTS idx_deals_properties_json ON hubspot_deals.deals USING GIN(properties_json);
```

## Column Descriptions

### Primary Key Fields

- **deal_id** (VARCHAR(255)): HubSpot deal identifier
- **_tenant_id** (VARCHAR(255)): Tenant identifier for multi-tenant isolation
- **_scan_id** (VARCHAR(255)): Extraction scan identifier

### ETL Metadata Fields

- **_extracted_at** (TIMESTAMP WITH TIME ZONE): Timestamp when the record was extracted
- **_scan_id** (VARCHAR(255)): Unique identifier for the extraction scan
- **_tenant_id** (VARCHAR(255)): Tenant identifier for data isolation

### Deal Property Fields

- **deal_name** (VARCHAR(500)): Name of the deal
- **amount** (NUMERIC(15, 2)): Deal amount in currency
- **deal_stage** (VARCHAR(255)): Current stage of the deal
- **pipeline** (VARCHAR(255)): Pipeline name
- **close_date** (VARCHAR(255)): Expected or actual close date
- **description** (TEXT): Deal description
- **deal_type** (VARCHAR(255)): Type of deal (newbusiness, existingbusiness, etc.)

### Timestamp Fields

- **created_at** (TIMESTAMP WITH TIME ZONE): Deal creation timestamp from HubSpot
- **updated_at** (TIMESTAMP WITH TIME ZONE): Last modification timestamp from HubSpot
- **archived** (BOOLEAN): Whether the deal is archived

### Flexible Storage

- **properties_json** (JSONB): All deal properties stored as JSON for flexibility and future extensibility

## Property Type Mappings

### HubSpot to PostgreSQL Type Mapping

| HubSpot Type | PostgreSQL Type | Notes |
|--------------|----------------|-------|
| string | VARCHAR(500) | Deal names, stages, etc. |
| number | NUMERIC(15, 2) | Amounts, quantities |
| date | VARCHAR(255) | Stored as string, can be parsed to TIMESTAMP |
| datetime | TIMESTAMP WITH TIME ZONE | Created/updated timestamps |
| bool | BOOLEAN | Archived status |
| enum | VARCHAR(255) | Deal stages, types |
| text | TEXT | Descriptions, notes |
| json | JSONB | Complex nested properties |

## Indexes

### Performance Indexes

1. **idx_deals_tenant_id**: Fast tenant-based queries
2. **idx_deals_scan_id**: Fast scan-based queries
3. **idx_deals_extracted_at**: Time-based queries and filtering
4. **idx_deals_deal_stage**: Filtering by deal stage
5. **idx_deals_created_at**: Time-based analysis
6. **idx_deals_updated_at**: Recent updates tracking
7. **idx_deals_tenant_scan**: Composite index for tenant + scan queries
8. **idx_deals_properties_json**: GIN index for JSONB queries

### Index Usage Examples

```sql
-- Query by tenant
SELECT * FROM hubspot_deals.deals 
WHERE _tenant_id = 'tenant1';

-- Query by scan
SELECT * FROM hubspot_deals.deals 
WHERE _scan_id = 'scan-123';

-- Query by date range
SELECT * FROM hubspot_deals.deals 
WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31';

-- Query by deal stage
SELECT * FROM hubspot_deals.deals 
WHERE deal_stage = 'qualifiedtobuy';

-- JSON property query
SELECT * FROM hubspot_deals.deals 
WHERE properties_json->>'custom_field' = 'value';
```

## Multi-Tenant Data Isolation

### Strategy

Multi-tenant isolation is achieved through:

1. **Tenant ID in Primary Key**: Ensures uniqueness per tenant
2. **Tenant Index**: Fast tenant-based filtering
3. **Row-Level Security** (Optional): Can be implemented for additional security

### Example Queries

```sql
-- Get all deals for a tenant
SELECT * FROM hubspot_deals.deals 
WHERE _tenant_id = 'tenant1';

-- Get latest scan for a tenant
SELECT * FROM hubspot_deals.deals 
WHERE _tenant_id = 'tenant1' 
  AND _scan_id = (
    SELECT MAX(_scan_id) 
    FROM hubspot_deals.deals 
    WHERE _tenant_id = 'tenant1'
  );
```

## Data Retention and Cleanup

### Recommended Cleanup Strategy

```sql
-- Delete old scans (keep last N scans per tenant)
DELETE FROM hubspot_deals.deals
WHERE _scan_id NOT IN (
  SELECT DISTINCT _scan_id
  FROM hubspot_deals.deals
  WHERE _tenant_id = 'tenant1'
  ORDER BY _extracted_at DESC
  LIMIT 10
);
```

## DLT Pipeline Configuration

The DLT pipeline is configured with:

- **Pipeline Name**: `hubspot_deals`
- **Destination**: `postgres`
- **Dataset Name**: `hubspot_deals`
- **Write Disposition**: `merge` (updates existing records)
- **Primary Key**: `deal_id`

## Sample Queries

### Get Latest Deals by Tenant

```sql
SELECT 
    deal_id,
    deal_name,
    amount,
    deal_stage,
    created_at,
    _extracted_at
FROM hubspot_deals.deals
WHERE _tenant_id = 'tenant1'
  AND _scan_id = (
    SELECT MAX(_scan_id)
    FROM hubspot_deals.deals
    WHERE _tenant_id = 'tenant1'
  )
ORDER BY created_at DESC
LIMIT 100;
```

### Deal Stage Distribution

```sql
SELECT 
    deal_stage,
    COUNT(*) as count,
    SUM(amount) as total_amount
FROM hubspot_deals.deals
WHERE _tenant_id = 'tenant1'
  AND archived = FALSE
GROUP BY deal_stage
ORDER BY count DESC;
```

### Extraction Statistics

```sql
SELECT 
    _scan_id,
    _tenant_id,
    COUNT(*) as record_count,
    MIN(_extracted_at) as extraction_start,
    MAX(_extracted_at) as extraction_end
FROM hubspot_deals.deals
GROUP BY _scan_id, _tenant_id
ORDER BY extraction_start DESC;
```

