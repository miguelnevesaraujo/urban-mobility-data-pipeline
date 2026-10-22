import os
from pathlib import Path

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

load_dotenv("infra/.env")

connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

blob_service = BlobServiceClient.from_connection_string(
    connection_string,
    api_version="2023-11-03"
)

container = blob_service.get_container_client("raw")

try:
    container.create_container()
    print("Container 'raw' created.")
except ResourceExistsError:
    print("Container 'raw' already exists.")

snapshot_dir = Path("data/raw/gbfs/station_status")

snapshot_files = list(snapshot_dir.rglob("*.json"))

if not snapshot_files:
    raise FileNotFoundError("No station snapshots found.")

latest_snapshot = max(snapshot_files, key=lambda p: p.name)

blob_name = latest_snapshot.relative_to(
    Path("data/raw")
).as_posix()

blob = container.get_blob_client(blob_name)

try:
    with open(latest_snapshot, "rb") as file:
        blob.upload_blob(file, overwrite=False)

    print("Snapshot uploaded successfully!")

except ResourceExistsError:
    print("Snapshot already exists in Azurite.")

properties = blob.get_blob_properties()

print("Container:", container.container_name)
print("Blob:", blob_name)
print("Size (bytes):", properties.size)