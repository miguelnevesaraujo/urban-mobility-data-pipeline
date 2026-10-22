import requests

GBFS_URL = "https://gbfs.citibikenyc.com/gbfs/2.3/gbfs.json"

response = requests.get(GBFS_URL, timeout=20)
response.raise_for_status()

feeds = response.json()["data"]["en"]["feeds"]

info_url = next(
    feed["url"]
    for feed in feeds
    if feed["name"] == "station_information"
)

response = requests.get(info_url, timeout=20)
response.raise_for_status()

stations = response.json()["data"]["stations"]

print("Total stations:", len(stations))

print("\nAvailable fields:")
print(list(stations[0].keys()))

print("\nSample of 3 stations:")

for station in stations[:3]:
    print({
        "station_id": station.get("station_id"),
        "name": station.get("name"),
        "latitude": station.get("lat"),
        "longitude": station.get("lon"),
        "capacity": station.get("capacity")
    })