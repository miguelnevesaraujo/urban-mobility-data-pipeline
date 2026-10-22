from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import pyarrow.parquet as pq

ZIP_PATH = Path("data/raw/202604-citibike-tripdata.zip")

PARQUET_PATH = Path(
    "data/bronze/trips/year=2026/month=04/trips_part1.parquet"
)

with ZipFile(ZIP_PATH, "r") as archive:

    csv_name = next(
        name for name in archive.namelist()
        if name.endswith("part1.csv")
    )

    with archive.open(csv_name) as file:
        csv_columns = pd.read_csv(file, nrows=0).columns.tolist()

    csv_rows = 0

    with archive.open(csv_name) as file:
        for chunk in pd.read_csv(
            file,
            usecols=["ride_id"],
            chunksize=50_000
        ):
            csv_rows += len(chunk)

parquet = pq.ParquetFile(PARQUET_PATH)

parquet_rows = parquet.metadata.num_rows
parquet_columns = parquet.schema_arrow.names

print("CSV rows:", csv_rows)
print("Parquet rows:", parquet_rows)
print("Row counts match:", csv_rows == parquet_rows)

print("\nCSV columns:", len(csv_columns))
print("Parquet columns:", len(parquet_columns))
print("Column names match:", csv_columns == parquet_columns)

if csv_rows != parquet_rows:
    raise ValueError("Row count mismatch!")

if csv_columns != parquet_columns:
    raise ValueError("Column mismatch!")

print("\nStructural validation passed!")