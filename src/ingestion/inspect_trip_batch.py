from pathlib import Path
from zipfile import ZipFile

import pandas as pd

ZIP_PATH = Path("data/raw/202604-citibike-tripdata.zip")

with ZipFile(ZIP_PATH, "r") as archive:

    csv_files = sorted(
        file for file in archive.namelist()
        if file.lower().endswith(".csv")
    )

    with archive.open(csv_files[0]) as csv:
        df = pd.read_csv(
            csv,
            nrows=10000,
            dtype={
                "ride_id": "string",
                "start_station_id": "string",
                "end_station_id": "string"
            }
        )

print("CSV file:", csv_files[0])
print("Rows loaded:", len(df))

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("\nSample records:")
print(df.head(3).to_string(index=False))