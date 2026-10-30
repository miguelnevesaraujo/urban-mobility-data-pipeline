# Architecture Decisions

This document summarizes the main technical decisions behind the Urban Mobility Data Engineering Pipeline.

## 1. Independent Data Collection

**Decision:** Run the Python collector every 15 minutes, independently of the hourly Airflow DAG.

**Rationale:** Data collection should continue even when warehouse transformations or Airflow are temporarily unavailable. Airflow orchestrates incremental loading and dbt processing separately.

**Trade-off:** Collection and processing require separate scheduling and monitoring.

## 2. PostgreSQL and dbt

**Decision:** Use PostgreSQL for relational storage and dbt for analytical transformations.

**Rationale:** PostgreSQL provides structured storage and SQL querying, while dbt supports modular models, automated data quality tests and lineage documentation.

**Trade-off:** The local PostgreSQL environment requires infrastructure management.

## 3. Parquet for Historical Trip Data

**Decision:** Convert historical Citi Bike CSV datasets into compressed Parquet files.

**Rationale:** Parquet provides efficient columnar storage and supports analytical processing.

**Trade-off:** Historical trip data remains separate from the current PostgreSQL/dbt station availability pipeline.

## 4. Azurite for Object Storage

**Decision:** Use Azurite with the Azure Blob Storage SDK.

**Rationale:** Azurite enables cost-free local development while using Azure-compatible storage APIs for Raw JSON and Bronze Parquet files.

**Trade-off:** Local emulation does not validate deployment, authentication or operational behavior in Azure Cloud.

## 5. Incremental and Idempotent Loading

**Decision:** Track processed snapshots using a PostgreSQL ingestion ledger and transactions.

**Rationale:** This prevents duplicate processing and supports recovery from incomplete or interrupted loads.

**Trade-off:** The ingestion process requires additional metadata and reconciliation logic.