from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq

DATA_DIR = Path("data/bronze/trips/year=2026/month=04")

all_ride_ids = []
total_rows = 0
reference_columns = None

for part in range(1, 5):
    file_path = DATA_DIR / f"trips_part{part}.parquet"

    parquet = pq.ParquetFile(file_path)

    rows = parquet.metadata.num_rows
    columns = parquet.schema_arrow.names

    if reference_columns is None:
        reference_columns = columns

    if columns != reference_columns:
        raise ValueError(f"Column mismatch in part {part}")

    ride_ids = pd.read_parquet(
        file_path,
        columns=["ride_id"]
    )["ride_id"]

    if len(ride_ids) != rows:
        raise ValueError(f"Row count mismatch in part {part}")

    all_ride_ids.append(ride_ids)
    total_rows += rows

    print(f"Part {part}: {rows:,} rows")


combined_ids = pd.concat(
    all_ride_ids,
    ignore_index=True
)

missing_ids = int(combined_ids.isna().sum())

duplicate_ids = int(
    combined_ids.dropna().duplicated().sum()
)

print("\n--- DATA VALIDATION RESULTS ---")

print("Total rows:", total_rows)
print("Number of columns:", len(reference_columns))
print("Missing ride IDs:", missing_ids)
print("Duplicate ride IDs:", duplicate_ids)

if missing_ids == 0 and duplicate_ids == 0:
    print("\nData integrity checks passed!")
else:
    print("\nData quality issues detected!")