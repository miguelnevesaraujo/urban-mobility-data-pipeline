import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from airflow.sdk import dag, task
import logging

def log_task_failure(context):
    task_instance = context["task_instance"]
    logging.error(
        "URBAN_MOBILITY_TASK_FAILED | "
        "dag=%s | task=%s | run=%s",
        task_instance.dag_id,
        task_instance.task_id,
        context.get("run_id", "unknown")
    )

@dag(
    dag_id="urban_mobility_pipeline",
    start_date=datetime(2026, 10, 1, tzinfo=timezone.utc),
    schedule="0 * * * *",
    catchup=False,
    max_active_runs=1,
    tags=["urban-mobility", "data-engineering"],
    default_args={
        "on_failure_callback": log_task_failure
    },
)
def urban_mobility_pipeline():
    @task(
        retries=2,
        retry_delay=timedelta(seconds=30),
        execution_timeout=timedelta(minutes=5)
    )
    def load_station_information():
        print("Updating station reference information...")
        subprocess.run(
            [
                sys.executable,
                "src/warehouse/load_station_information.py"
            ],
            cwd="/opt/urban-mobility",
            check=True
        )
        print("Station information updated successfully!")

    @task(
        retries=2,
        retry_delay=timedelta(seconds=30),
        execution_timeout=timedelta(minutes=20)
    )
    def load_station_status():
        print("Starting incremental station status loading...")
        subprocess.run(
            [
                sys.executable,
                "src/warehouse/load_station_status.py"
            ],
            cwd="/opt/urban-mobility",
            check=True
        )
        print("Station status loading completed!")

    @task(
        retries=2,
        retry_delay=timedelta(seconds=30),
        execution_timeout=timedelta(minutes=10)
    )
    def build_dbt_models():
        print("Starting dbt build...", flush=True)
        subprocess.run(
            [
                "/opt/dbt-venv/bin/dbt",
                "build",
                "--project-dir",
                "/opt/urban-mobility/dbt",
                "--profiles-dir",
                "/opt/urban-mobility/dbt"
            ],
            cwd="/opt/urban-mobility",
            env={
                **os.environ,
                "DBT_ENGINE_MANAGE_STATE": "0"
            },
            check=True
        )
        print("dbt build completed successfully!", flush=True)

    station_information = load_station_information()
    station_status = load_station_status()
    dbt_build = build_dbt_models()
    station_information >> station_status >> dbt_build

urban_mobility_pipeline()