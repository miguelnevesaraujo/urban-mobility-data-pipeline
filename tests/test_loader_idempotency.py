import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
import psycopg
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_PORT = os.getenv("TEST_POSTGRES_PORT")

@pytest.mark.skipif(
    not TEST_PORT,
    reason="Isolated PostgreSQL test database not configured"
)
def test_station_status_loader_idempotency(tmp_path):

    if int(TEST_PORT) == 5432:
        pytest.fail("Refusing to use the production PostgreSQL port.")

    def get_counts():
        with psycopg.connect(
            host="127.0.0.1",
            port=int(TEST_PORT),
            dbname="mobility",
            user="mobility",
            password="test_password",
            connect_timeout=5
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        (SELECT COUNT(*) FROM raw.station_status),
                        (SELECT COUNT(*) FROM raw.station_snapshot_loads)
                """)
                return cursor.fetchone()

    fixture_path = (
        PROJECT_ROOT
        / "tests/fixtures/raw/gbfs/station_status/2026/10/30"
        / "station_status_20261030T120000000000Z.json"
    )

    snapshot = json.loads(fixture_path.read_text(encoding="utf-8"))

    unique_id = uuid.uuid4().hex
    snapshot["collected_at_utc"] = datetime.now(timezone.utc).isoformat()

    for index, station in enumerate(snapshot["payload"]["data"]["stations"]):
        station["station_id"] = f"test_{unique_id}_{index}"

    raw_dir = tmp_path / "raw"
    snapshot_dir = raw_dir / "gbfs" / "station_status"
    snapshot_dir.mkdir(parents=True)

    snapshot_file = snapshot_dir / f"station_status_{unique_id}.json"
    snapshot_file.write_text(json.dumps(snapshot), encoding="utf-8")

    env = {
        **os.environ,
        "POSTGRES_HOST": "127.0.0.1",
        "POSTGRES_PORT": TEST_PORT,
        "POSTGRES_DB": "mobility",
        "POSTGRES_PASSWORD": "test_password",
        "STATION_SNAPSHOT_DIR": str(snapshot_dir),
        "RAW_DATA_DIR": str(raw_dir),
    }

    command = [
        sys.executable,
        str(PROJECT_ROOT / "src/warehouse/load_station_status.py")
    ]

    before = get_counts()

    subprocess.run(command, cwd=PROJECT_ROOT, env=env, check=True)

    after_first = get_counts()

    assert after_first == (before[0] + 2, before[1] + 1)

    second_run = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True
    )

    assert "Pending snapshots: 0" in second_run.stdout
    assert get_counts() == after_first