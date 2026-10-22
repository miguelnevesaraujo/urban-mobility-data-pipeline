import requests
from datetime import datetime, timezone

GBFS_URL = "https://gbfs.citibikenyc.com/gbfs/2.3/gbfs.json"

response = requests.get(GBFS_URL, timeout=20)
response.raise_for_status()

feeds = response.json()["data"]["en"]["feeds"]

status_url = next(
    feed["url"]
    for feed in feeds
    if feed["name"] == "station_status"
)

response = requests.get(status_url, timeout=20)
response.raise_for_status()

data = response.json()
stations = data["data"]["stations"]

updated_at = datetime.fromtimestamp(
    data["last_updated"],
    tz=timezone.utc
)

print("Feed updated (UTC):", updated_at)
print("Total stations:", len(stations))

print("\nAvailable fields:")
print(list(stations[0].keys()))

print("\nSample of 3 stations:")

for station in stations[:3]:
    print({
        "station_id": station.get("station_id"),
        "num_bikes_available": station.get("num_bikes_available"),
        "num_docks_available": station.get("num_docks_available"),
        "is_installed": station.get("is_installed"),
        "is_renting": station.get("is_renting"),
        "is_returning": station.get("is_returning"),
    })