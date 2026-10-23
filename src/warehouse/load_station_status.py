import json
import os
from datetime import datetime
from pathlib import Path
import psycopg
from dotenv import load_dotenv

load_dotenv("infra/.env")

DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

SNAPSHOT_DIR = Path("data/raw/gbfs/station_status")
RAW_DIR = Path("data/raw")

if not DB_PASSWORD:
    raise ValueError("POSTGRES_PASSWORD not found.")

insert_query = """
INSERT INTO raw.station_status (
    collected_at_utc,
    station_id,
    num_bikes_available,
    num_docks_available,
    is_installed,
    is_renting,
    is_returning,
    last_reported_unix,
    source_file
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (collected_at_utc, station_id)
DO NOTHING;
"""

snapshot_files = sorted(
    SNAPSHOT_DIR.rglob("station_status_*.json")
)

if not snapshot_files:
    raise ValueError("No station status snapshots found.")

print("Snapshot files found:", len(snapshot_files))

with psycopg.connect(
    host="127.0.0.1",
    port=5432,
    dbname="mobility",
    user="mobility",
    password=DB_PASSWORD,
) as connection:

    for file_number, file_path in enumerate(snapshot_files, 1):

        with open(file_path, "r", encoding="utf-8") as file:
            snapshot = json.load(file)

        collected_at = datetime.fromisoformat(
            snapshot["collected_at_utc"].replace("Z", "+00:00")
        )

        if collected_at.utcoffset() is None:
            raise ValueError(f"Missing timezone: {file_path}")

        stations = snapshot["payload"]["data"]["stations"]

        source_file = file_path.relative_to(RAW_DIR).as_posix()

        records = [
            (
                collected_at,
                str(station["station_id"]),
                station.get("num_bikes_available"),
                station.get("num_docks_available"),
                station.get("is_installed"),
                station.get("is_renting"),
                station.get("is_returning"),
                station.get("last_reported"),
                source_file,
            )
            for station in stations
        ]

        with connection.cursor() as cursor:
            cursor.executemany(insert_query, records)

        connection.commit()

        print(
            f"Snapshot {file_number}/{len(snapshot_files)} "
            f"| Stations: {len(records)}"
        )

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM raw.station_status;")
        total_rows = cursor.fetchone()[0]

print("\nTotal station status rows:", total_rows)
print("Historical station status loading completed!")