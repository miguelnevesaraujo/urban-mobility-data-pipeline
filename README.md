# Urban Mobility Data Engineering Pipeline

## Project Overview

An end-to-end Data Engineering project designed to build an automated data pipeline using **Python, PostgreSQL, Docker, Parquet, dbt, and Apache Airflow**.

The project integrates historical trip records and station availability data from the Citi Bike bicycle-sharing system in New York City.

The objective is to develop a reliable data pipeline covering data ingestion, storage, transformation, quality validation, orchestration, and analytical reporting.

**Project Status:** In Development — Phase 2: Data Ingestion & Raw Data Layer.

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
| dbt | SQL transformations and data quality tests (planned) |
| Apache Airflow | Pipeline orchestration (planned) |
| GitHub Actions | Continuous Integration (planned) |
| Streamlit | Analytical dashboard (planned) |

## Data Architecture

The target architecture follows these stages:

**Data Sources → Python Ingestion → Raw Storage → PostgreSQL & dbt → Analytics Dashboard**

Data quality checks, incremental processing, and orchestration will be integrated throughout the pipeline.

## Current Implementation

- Configured Docker-based PostgreSQL and Azurite services.
- Developed a Python collector for Citi Bike station availability snapshots.
- Implemented recurring snapshot collection with a 15-minute interval while Docker is running.
- Integrated JSON snapshot storage with Azurite.
- Implemented duplicate upload protection.
- Processed **965,093 trip records** from a historical CSV using chunk-based processing.
- Converted the records into compressed Parquet format.
- Validated row counts and column structure between CSV and Parquet.
- Documented initial data quality rules in `docs/data_contract.md`.

## Development Roadmap

1. Project Setup & Architecture — Completed
2. Data Ingestion & Raw Data Layer — In Progress
3. Data Warehouse & dbt
4. Incremental Processing & Data Quality
5. Airflow & Pipeline Orchestration
6. Cloud Integration & Portfolio

## Documentation

- [Data Contract](docs/data_contract.md)

Additional architecture diagrams, technical decisions, testing results, and performance measurements will be added as the project progresses.

## Project Goal

This project is being developed to demonstrate practical Data Engineering skills, including reliable data ingestion, data modeling, automation, data quality, and maintainable pipeline development.