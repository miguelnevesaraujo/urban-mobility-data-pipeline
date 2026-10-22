from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ZIP_PATH = Path("data/raw/202604-citibike-tripdata.zip")

OUTPUT_PATH = Path(
    "data/bronze/trips/year=2026/month=04/trips_part1.parquet"
)

CHUNK_SIZE = 50_000

SCHEMA = pa.schema([
    ("ride_id", pa.string()),
    ("rideable_type", pa.string()),
    ("started_at", pa.string()),
    ("ended_at", pa.string()),
    ("start_station_name", pa.string()),
    ("start_station_id", pa.string()),
    ("end_station_name", pa.string()),
    ("end_station_id", pa.string()),
    ("start_lat", pa.float64()),
    ("start_lng", pa.float64()),
    ("end_lat", pa.float64()),
    ("end_lng", pa.float64()),
    ("member_casual", pa.string()),
])

STRING_COLUMNS = {
    field.name: "string"
    for field in SCHEMA
    if pa.types.is_string(field.type)
}

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

total_rows = 0
total_chunks = 0

with ZipFile(ZIP_PATH, "r") as archive:

    csv_name = next(
        name for name in archive.namelist()
        if name.endswith("part1.csv")
    )

    print("Processing:", csv_name)

    with archive.open(csv_name) as csv_file:
        with pq.ParquetWriter(
            OUTPUT_PATH,
            SCHEMA,
            compression="snappy"
        ) as writer:

            for chunk in pd.read_csv(
                csv_file,
                chunksize=CHUNK_SIZE,
                dtype=STRING_COLUMNS
            ):
                table = pa.Table.from_pandas(
                    chunk,
                    schema=SCHEMA,
                    preserve_index=False
                )

                writer.write_table(table)

                total_rows += len(chunk)
                total_chunks += 1

                print(
                    f"Chunk {total_chunks}: "
                    f"{len(chunk)} rows processed"
                )

metadata = pq.ParquetFile(OUTPUT_PATH).metadata

print("\nConversion completed!")
print("Total chunks:", total_chunks)
print("Total rows:", total_rows)
print("Parquet rows:", metadata.num_rows)
print(
    "Parquet size (MB):",
    round(OUTPUT_PATH.stat().st_size / (1024 ** 2), 2)
)
print("Saved to:", OUTPUT_PATH)