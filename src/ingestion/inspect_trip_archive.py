from pathlib import Path
from zipfile import ZipFile

ZIP_PATH = Path("data/raw/202604-citibike-tripdata.zip")

with ZipFile(ZIP_PATH, "r") as archive:

    csv_files = [
        file for file in archive.infolist()
        if file.filename.lower().endswith(".csv")
    ]

    print("CSV files found:", len(csv_files))

    total_size = sum(file.file_size for file in csv_files)

    print(
        "Uncompressed CSV size (MB):",
        round(total_size / (1024 ** 2), 2)
    )

    print("\nFiles inside the archive:")

    for file in csv_files[:10]:
        print(
            file.filename,
            "-",
            round(file.file_size / (1024 ** 2), 2),
            "MB"
        )

    if csv_files:
        with archive.open(csv_files[0]) as csv:
            header = csv.readline().decode("utf-8-sig").strip()

        print("\nCSV columns:")
        print(header)