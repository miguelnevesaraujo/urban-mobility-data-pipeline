import json
from datetime import datetime, timezone
from pathlib import Path

import requests
import os

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError


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

payload = response.json()

collected_at = datetime.now(timezone.utc)

snapshot = {
    "collected_at_utc": collected_at.isoformat(),
    "source_url": status_url,
    "payload": payload
}

output_dir = (
    Path("data/raw/gbfs/station_status")
    / collected_at.strftime("%Y/%m/%d")
)

output_dir.mkdir(parents=True, exist_ok=True)

filename = (
    f"station_status_"
    f"{collected_at.strftime('%Y%m%dT%H%M%S%fZ')}.json"
)

output_path = output_dir / filename

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(snapshot, file, ensure_ascii=False)

print("Snapshot collected successfully!")
print("Stations:", len(payload["data"]["stations"]))
print("Collected at (UTC):", collected_at.isoformat())
print("Saved to:", output_path)

load_dotenv("infra/.env")

connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

blob_service = BlobServiceClient.from_connection_string(
    connection_string,
    api_version="2023-11-03"
)

container = blob_service.get_container_client("raw")

try:
    container.create_container()
except ResourceExistsError:
    pass

blob_name = output_path.relative_to(
    Path("data/raw")
).as_posix()

blob = container.get_blob_client(blob_name)

try:
    with open(output_path, "rb") as file:
        blob.upload_blob(file, overwrite=False)

    print("Snapshot uploaded to Azurite successfully!")

except ResourceExistsError:
    print("Snapshot already exists in Azurite.")

print("Blob:", blob_name)