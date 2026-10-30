import os
from pathlib import Path
from dotenv import load_dotenv
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient

load_dotenv("infra/.env")

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

PARQUET_DIR = Path("data/bronze/trips/year=2026/month=04")
CONTAINER_NAME = os.getenv("AZURE_BRONZE_CONTAINER", "bronze")

if not CONNECTION_STRING:
    raise ValueError("Azure Storage connection string not found.")

blob_service = BlobServiceClient.from_connection_string(
    CONNECTION_STRING,
    api_version="2023-11-03"
)

try:
    container = blob_service.create_container(CONTAINER_NAME)
    print("Bronze container created.")
except ResourceExistsError:
    container = blob_service.get_container_client(CONTAINER_NAME)
    print("Bronze container already exists.")

parquet_files = sorted(PARQUET_DIR.glob("trips_part*.parquet"))

if len(parquet_files) != 4:
    raise ValueError(
        f"Expected 4 Parquet files, found {len(parquet_files)}."
    )

for file_path in parquet_files:

    blob_name = (
        f"trips/year=2026/month=04/{file_path.name}"
    )

    blob_client = container.get_blob_client(blob_name)

    print(f"\nProcessing: {file_path.name}")

    try:
        with open(file_path, "rb") as file:
            blob_client.upload_blob(
                file,
                overwrite=False
            )

        print("Upload completed.")

    except ResourceExistsError:
        print("Blob already exists, skipping upload.")

    local_size = file_path.stat().st_size
    blob_size = blob_client.get_blob_properties().size

    if local_size != blob_size:
        raise ValueError(
            f"File size mismatch: {file_path.name}"
        )

    print("File size verified.")

print("\nAll Parquet files are available in Blob Storage!")