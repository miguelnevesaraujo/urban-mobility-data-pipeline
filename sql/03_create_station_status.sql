CREATE TABLE IF NOT EXISTS raw.station_status (
    collected_at_utc TIMESTAMPTZ NOT NULL,
    station_id TEXT NOT NULL,

    num_bikes_available INTEGER,
    num_docks_available INTEGER,

    is_installed INTEGER,
    is_renting INTEGER,
    is_returning INTEGER,

    last_reported_unix BIGINT,
    source_file TEXT NOT NULL,

    loaded_at TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (collected_at_utc, station_id)
);

COMMENT ON TABLE raw.station_status IS
'Historical Citi Bike station availability snapshots';

SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'raw'
  AND table_name = 'station_status'
ORDER BY ordinal_position;