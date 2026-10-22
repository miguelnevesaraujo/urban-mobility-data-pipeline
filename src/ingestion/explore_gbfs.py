import requests

GBFS_URL = "https://gbfs.citibikenyc.com/gbfs/2.3/gbfs.json"

response = requests.get(GBFS_URL, timeout=20)
response.raise_for_status()

data = response.json()

print("GBFS Version:", data["version"])
print("\nAvailable data sources:")

feeds = data["data"]["en"]["feeds"]

for feed in feeds:
    if feed["name"] in ["station_information", "station_status"]:
        print(f"{feed['name']}: {feed['url']}")