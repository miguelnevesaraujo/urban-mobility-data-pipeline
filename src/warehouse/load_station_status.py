import json
import os
from datetime import datetime
from pathlib import Path
import psycopg
from dotenv import load_dotenv

load_dotenv("infra/.env")

DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "mobility")

SNAPSHOT_DIR = Path(
    os.getenv("STATION_SNAPSHOT_DIR", "data/raw/gbfs/station_status")
)
RAW_DIR = Path(
    os.getenv("RAW_DATA_DIR", "data/raw")
)

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
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user="mobility",
    password=DB_PASSWORD,
) as connection:

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT source_file
            FROM raw.station_snapshot_loads;
        """)

        loaded_files = {
            row[0] for row in cursor.fetchall()
        }

    pending_files = [
        file_path
        for file_path in snapshot_files
        if file_path.relative_to(RAW_DIR).as_posix()
        not in loaded_files
    ]

    print("Already loaded:", len(snapshot_files) - len(pending_files))
    print("Pending snapshots:", len(pending_files))

    for file_number, file_path in enumerate(pending_files, 1):

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
            expected_ids = [
                str(station["station_id"])
                for station in stations
            ]
            cursor.execute("""
                SELECT station_id
                FROM raw.station_status
                WHERE source_file = %s;
            """, (source_file,))

            actual_ids = [
                row[0] for row in cursor.fetchall()
            ]
            is_complete = (
                len(expected_ids) > 0
                and len(expected_ids) == len(set(expected_ids))
                and len(expected_ids) == len(actual_ids)
                and set(expected_ids) == set(actual_ids)
            )

            if not is_complete:
                raise ValueError(
                    f"Incomplete snapshot: {source_file}"
                )

            cursor.execute("""
                INSERT INTO raw.station_snapshot_loads (
                    source_file,
                    expected_rows
                )
                VALUES (%s, %s)
                ON CONFLICT (source_file) DO NOTHING;
            """, (source_file, len(expected_ids)))

        connection.commit()

        print(
            f"Snapshot {file_number}/{len(pending_files)} "
            f"| Stations: {len(records)}"
        )

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM raw.station_status;")
        total_rows = cursor.fetchone()[0]

print("\nTotal station status rows:", total_rows)
print("Historical station status loading completed!")