CREATE TABLE IF NOT EXISTS raw.station_information (
    station_id TEXT PRIMARY KEY,
    name TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    capacity INTEGER,
    loaded_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE raw.station_information IS
'Station reference information from the Citi Bike GBFS API';

SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'raw'
  AND table_name = 'station_information'
ORDER BY ordinal_position;