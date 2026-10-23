from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ZIP_PATH = Path("data/raw/202604-citibike-tripdata.zip")
OUTPUT_DIR = Path("data/bronze/trips/year=2026/month=04")
CHUNK_SIZE = 50_000

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

string_columns = [
    "ride_id",
    "rideable_type",
    "started_at",
    "ended_at",
    "start_station_name",
    "start_station_id",
    "end_station_name",
    "end_station_id",
    "member_casual",
]

schema = pa.schema([
    pa.field("ride_id", pa.string()),
    pa.field("rideable_type", pa.string()),
    pa.field("started_at", pa.string()),
    pa.field("ended_at", pa.string()),
    pa.field("start_station_name", pa.string()),
    pa.field("start_station_id", pa.string()),
    pa.field("end_station_name", pa.string()),
    pa.field("end_station_id", pa.string()),
    pa.field("start_lat", pa.float64()),
    pa.field("start_lng", pa.float64()),
    pa.field("end_lat", pa.float64()),
    pa.field("end_lng", pa.float64()),
    pa.field("member_casual", pa.string()),
])

with ZipFile(ZIP_PATH, "r") as archive:
    for part in range(1, 5):
        csv_name = next(
            name for name in archive.namelist()
            if name.endswith(f"part{part}.csv")
        )

        output_path = OUTPUT_DIR / f"trips_part{part}.parquet"

        if output_path.exists():
            print(f"Part {part}: already exists, skipping.")
            continue

        temp_path = OUTPUT_DIR / f"trips_part{part}.tmp"
        writer = None
        total_rows = 0

        print(f"\nProcessing part {part}...")

        try:
            with archive.open(csv_name) as file:
                chunks = pd.read_csv(
                    file,
                    dtype={col: "string" for col in string_columns},
                    chunksize=CHUNK_SIZE,
                )

                for chunk_number, chunk in enumerate(chunks, 1):

                    table = pa.Table.from_pandas(
                        chunk,
                        schema=schema,
                        preserve_index=False,
                    )

                    if writer is None:
                        writer = pq.ParquetWriter(
                            temp_path,
                            schema,
                            compression="snappy",
                        )

                    writer.write_table(table)
                    total_rows += len(chunk)

                    print(
                        f"Part {part} | Chunk {chunk_number} "
                        f"| Total rows: {total_rows}"
                    )

            if writer is not None:
                writer.close()
                writer = None
                temp_path.replace(output_path)

            print(f"Part {part} completed: {total_rows} rows")

        except Exception:
            if writer is not None:
                writer.close()

            temp_path.unlink(missing_ok=True)
            raise

print("\nAll available trip parts processed!")