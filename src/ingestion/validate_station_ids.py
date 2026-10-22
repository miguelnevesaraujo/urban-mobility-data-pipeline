import requests

GBFS_URL = "https://gbfs.citibikenyc.com/gbfs/2.3/gbfs.json"

response = requests.get(GBFS_URL, timeout=20)
response.raise_for_status()

feeds = {
    feed["name"]: feed["url"]
    for feed in response.json()["data"]["en"]["feeds"]
}

def get_stations(feed_name):
    response = requests.get(feeds[feed_name], timeout=20)
    response.raise_for_status()
    return response.json()["data"]["stations"]

information = get_stations("station_information")
status = get_stations("station_status")

information_ids = {
    station["station_id"] for station in information
}

status_ids = {
    station["station_id"] for station in status
}

print("Station information records:", len(information))
print("Station status records:", len(status))

print("Matching stations:", len(information_ids & status_ids))
print("Stations without status:", len(information_ids - status_ids))
print("Status records without information:", len(status_ids - information_ids))

print(
    "Stations with zero capacity:",
    sum(station.get("capacity") == 0 for station in information)
)