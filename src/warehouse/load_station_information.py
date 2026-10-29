import os
from pathlib import Path
import psycopg
import requests
from dotenv import load_dotenv

load_dotenv(Path("infra/.env"))

DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")

GBFS_URL = "https://gbfs.citibikenyc.com/gbfs/2.3/gbfs.json"

if not DB_PASSWORD:
    raise ValueError("POSTGRES_PASSWORD not found.")

response = requests.get(GBFS_URL, timeout=30)
response.raise_for_status()

feeds = response.json()["data"]["en"]["feeds"]

station_url = next(
    feed["url"]
    for feed in feeds
    if feed["name"] == "station_information"
)

response = requests.get(station_url, timeout=30)
response.raise_for_status()

stations = response.json()["data"]["stations"]

print("Stations received from API:", len(stations))

records = [
    (
        str(station["station_id"]),
        station.get("name"),
        station.get("lat"),
        station.get("lon"),
        station.get("capacity"),
    )
    for station in stations
]

station_ids = [record[0] for record in records]

if len(station_ids) != len(set(station_ids)):
    raise ValueError("Duplicate station IDs detected in API data.")

insert_query = """
INSERT INTO raw.station_information (
    station_id,
    name,
    lat,
    lon,
    capacity
)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (station_id)
DO UPDATE SET
    name = EXCLUDED.name,
    lat = EXCLUDED.lat,
    lon = EXCLUDED.lon,
    capacity = EXCLUDED.capacity,
    loaded_at = NOW()
WHERE (
    raw.station_information.name,
    raw.station_information.lat,
    raw.station_information.lon,
    raw.station_information.capacity
) IS DISTINCT FROM (
    EXCLUDED.name,
    EXCLUDED.lat,
    EXCLUDED.lon,
    EXCLUDED.capacity
);
"""

with psycopg.connect(
    host=DB_HOST,
    port=5432,
    dbname="mobility",
    user="mobility",
    password=DB_PASSWORD,
) as connection:

    with connection.cursor() as cursor:

        cursor.executemany(insert_query, records)

        cursor.execute(
            "SELECT COUNT(*) FROM raw.station_information;"
        )

        total_stations = cursor.fetchone()[0]

print("Stations stored in PostgreSQL:", total_stations)
print("Station information loading completed!")