import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

COLLECTOR = (
    PROJECT_ROOT
    / "src"
    / "ingestion"
    / "collect_station_snapshot.py"
)

INTERVAL_SECONDS = 15 * 60


def run_collection():
    timestamp = datetime.now(timezone.utc).isoformat()

    print(f"\n[{timestamp}] Starting collection...", flush=True)

    try:
        subprocess.run(
            [sys.executable, str(COLLECTOR)],
            cwd=PROJECT_ROOT,
            check=True
        )
        print("Collection completed successfully.", flush=True)

    except subprocess.CalledProcessError as error:
        print(
            f"Collection failed with exit code {error.returncode}.",
            flush=True
        )


if __name__ == "__main__":
    print("Citi Bike Collector started.")
    print("Collection interval: 15 minutes.")

    try:
        while True:
            run_collection()
            time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nCollector stopped.")