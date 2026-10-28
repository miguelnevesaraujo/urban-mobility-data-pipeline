import json
import os
from collections import defaultdict
from pathlib import Path
import psycopg
from dotenv import load_dotenv

load_dotenv("infra/.env")

RAW_DIR = Path("data/raw")
SNAPSHOT_DIR = RAW_DIR / "gbfs/station_status"

snapshot_files = sorted(
    SNAPSHOT_DIR.rglob("station_status_*.json")
)

with psycopg.connect(
    host="127.0.0.1",
    port=5432,
    dbname="mobility",
    user="mobility",
    password=os.environ["POSTGRES_PASSWORD"],
) as connection:
    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT source_file, station_id
            FROM raw.station_status
            WHERE source_file IS NOT NULL;
        """)

        database_stations = defaultdict(list)

        for source_file, station_id in cursor:
            database_stations[source_file].append(station_id)

        registered = 0
        skipped = 0

        for file_path in snapshot_files:

            with open(file_path, "r", encoding="utf-8") as file:
                snapshot = json.load(file)

            source_file = file_path.relative_to(RAW_DIR).as_posix()

            expected_ids = [
                str(station["station_id"])
                for station in snapshot["payload"]["data"]["stations"]
            ]

            actual_ids = database_stations.get(source_file, [])
            is_complete = (
                len(expected_ids) > 0
                and len(expected_ids) == len(set(expected_ids))
                and len(expected_ids) == len(actual_ids)
                and set(expected_ids) == set(actual_ids)
            )

            if not is_complete:
                skipped += 1
                print("SKIPPED:", source_file)
                continue

            cursor.execute("""
                INSERT INTO raw.station_snapshot_loads (
                    source_file,
                    expected_rows
                )
                VALUES (%s, %s)
                ON CONFLICT (source_file) DO NOTHING;
            """, (
                source_file,
                len(expected_ids)
            ))
            registered += cursor.rowcount

        cursor.execute("""
            SELECT COUNT(*)
            FROM raw.station_snapshot_loads;
        """)
        total_registered = cursor.fetchone()[0]

print("Snapshots checked:", len(snapshot_files))
print("New registrations:", registered)
print("Skipped snapshots:", skipped)
print("Total registered snapshots:", total_registered)