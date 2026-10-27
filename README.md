# Urban Mobility Data Engineering Pipeline

## Project Overview

An end-to-end Data Engineering project designed to build an automated data pipeline using **Python, PostgreSQL, Docker, Parquet, dbt and Apache Airflow**.

The project integrates historical trip records and station availability data from the Citi Bike bicycle-sharing system in New York City.

The objective is to develop a reliable data pipeline covering data ingestion, storage, transformation, quality validation, orchestration and analytical reporting.

## Business Objective

**Which Citi Bike stations experience the highest bicycle unavailability rates, and during which hours does this occur most frequently?**

The project aims to provide reliable historical data that can help identify patterns in bicycle availability and support potential station rebalancing decisions.

## Data Sources

- **Citi Bike GBFS API:** Station information and availability snapshots.
- **Citi Bike Trip Histories:** Historical bicycle trip records provided as compressed CSV files.

Source: https://citibikenyc.com/system-data

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data ingestion and processing |
| Pandas & PyArrow | Batch processing and Parquet conversion |
| Docker & Docker Compose | Containerization and local infrastructure |
| PostgreSQL | Data Warehouse |
| Azurite | Local Azure Blob Storage emulation |
| dbt | SQL transformations and data quality tests |
| Apache Airflow | Pipeline orchestration |
| GitHub Actions | Continuous Integration |
| Streamlit | Analytical dashboard |

## Data Architecture

The target architecture follows these stages:

**Data Sources → Python Ingestion → Raw Storage → PostgreSQL & dbt → Analytics Dashboard**

Data quality checks, incremental processing and orchestration will be integrated throughout the pipeline.

## Current Implementation

- Configured Docker-based PostgreSQL and Azurite services.
- Developed a Python collector for Citi Bike station availability snapshots.
- Implemented recurring snapshot collection with a 15-minute interval while Docker is running.
- Integrated JSON snapshot storage with Azurite.
- Implemented duplicate upload protection.
- Processed 3,860,371 historical Citi Bike trip records from four CSV files.
- Converted the datasets into compressed Parquet files using chunk-based processing.
- Implemented structural validation and verified that all 3,860,371 records have non-null, unique ride IDs across all four Parquet files.
- Documented initial data quality rules in `docs/data_contract.md`.
- Created PostgreSQL raw schemas and tables for station information and historical availability.
- Implemented Python-based loading of Citi Bike station information using psycopg.
- Loaded and validated 52,899 station availability records from 21 historical snapshots.
- Implemented idempotent loading using PostgreSQL conflict handling.
- Developed SQL queries to evaluate station availability, operational status, and data freshness.
- Calculated an initial station unavailability rate of 4.71% across eligible observations.
- Identified stations with the highest observed zero-bike rates, using a minimum sample threshold.

## Data Warehouse & dbt

The project uses PostgreSQL as its analytical data warehouse
and dbt Core to organize, transform, document, and validate data.

### Data Warehouse Architecture

The transformation layer follows a modular architecture:

Raw PostgreSQL Tables --> Staging Models --> Intermediate Model --> Analytical Marts

### dbt Models

**Staging Layer**
- `stg_station_information`: Cleans and standardizes station reference information.
- `stg_station_status`: Prepares historical availability observations and converts operational indicators and timestamps.

**Intermediate Layer**
- `int_station_availability`: Combines station reference data with historical snapshots and applies operational eligibility and data freshness rules.

**Analytical Marts**
- `mart_station_unavailability`: Calculates station-level zero-bike rates and observation counts.
- `mart_hourly_unavailability`: Calculates unavailability metrics by local hour in New York City.

### Data Quality

Automated dbt tests validate:

- Primary identifiers and required fields
- Unique station identifiers and composite observation keys
- Referential integrity between station models
- Non-negative bicycle and dock counts
- Valid metric ranges and observation counts
- Consistency between intermediate and analytical models

### Initial Analytical Results

Based on 21 historical station availability snapshots:

- 52,899 station observations processed
- 51,573 eligible observations
- 2,431 eligible observations with zero available bicycles
- 4.71% observed bicycle unavailability rate

These results represent the collected snapshots, not continuous
station downtime. The limited and discontinuous observation
period does not support conclusions about long-term patterns.

### dbt Documentation

dbt provides automatically generated model documentation
and a lineage graph illustrating the dependencies between
raw sources, staging models, intermediate transformations
and analytical marts.

## Development Roadmap

1. Project Setup & Architecture
2. Data Ingestion & Raw Data Layer
3. Data Warehouse & dbt
4. Incremental Processing & Data Quality
5. Airflow & Pipeline Orchestration
6. Cloud Integration & Portfolio

## Documentation

- [Data Contract](docs/data_contract.md)

## Project Goal

This project is being developed to demonstrate practical Data Engineering skills, including reliable data ingestion, data modeling, automation, data quality and maintainable pipeline development.