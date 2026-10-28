import json
import os
from collections import defaultdict
from pathlib import Path
import psycopg
from dotenv import load_dotenv

load_dotenv("infra/.env")

RAW_DIR = Path("data/raw")
SNAPSHOT_DIR = RAW_DIR / "gbfs/station_status"

database_stations = defaultdict(set)

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
            FROM raw.station_status;
        """)

        for source_file, station_id in cursor:
            database_stations[source_file].add(station_id)

snapshot_files = sorted(
    SNAPSHOT_DIR.rglob("station_status_*.json")
)

valid_snapshots = 0
invalid_snapshots = []

for file_path in snapshot_files:
    with open(file_path, "r", encoding="utf-8") as file:
        snapshot = json.load(file)

    stations = snapshot["payload"]["data"]["stations"]

    expected_ids = [
        str(station["station_id"])
        for station in stations
    ]

    source_file = file_path.relative_to(RAW_DIR).as_posix()
    actual_ids = database_stations.get(source_file, set())
    no_duplicates = len(expected_ids) == len(set(expected_ids))

    is_complete = (
        len(expected_ids) > 0
        and no_duplicates
        and set(expected_ids) == actual_ids
    )
    if is_complete:
        valid_snapshots += 1
    else:
        invalid_snapshots.append(source_file)

print("Snapshots checked:", len(snapshot_files))
print("Valid snapshots:", valid_snapshots)
print("Invalid snapshots:", len(invalid_snapshots))

for source_file in invalid_snapshots[:10]:
    print("INVALID:", source_file)