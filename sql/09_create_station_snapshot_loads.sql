CREATE TABLE IF NOT EXISTS raw.station_snapshot_loads (
    source_file TEXT PRIMARY KEY,
    expected_rows INTEGER NOT NULL CHECK (expected_rows > 0),
    loaded_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
