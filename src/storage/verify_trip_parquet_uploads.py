import os
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv("infra/.env")

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
PARQUET_DIR = Path("data/bronze/trips/year=2026/month=04")

if not CONNECTION_STRING:
    raise ValueError("Azure Storage connection string not found.")

blob_service = BlobServiceClient.from_connection_string(
    CONNECTION_STRING,
    api_version="2023-11-03"
)

container = blob_service.get_container_client("bronze")
parquet_files = sorted(PARQUET_DIR.glob("trips_part*.parquet"))

if len(parquet_files) != 4:
    raise ValueError("Expected exactly 4 Parquet files.")

for file_path in parquet_files:
    blob_name = f"trips/year=2026/month=04/{file_path.name}"

    local_hash = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            local_hash.update(chunk)

    remote_hash = hashlib.sha256()

    blob_client = container.get_blob_client(blob_name)

    for chunk in blob_client.download_blob().chunks():
        remote_hash.update(chunk)

    if local_hash.digest() != remote_hash.digest():
        raise ValueError(
            f"Integrity check failed: {file_path.name}"
        )

    print(f"{file_path.name}: SHA-256 MATCH")

print("\nAll 4 Parquet files passed integrity verification!")