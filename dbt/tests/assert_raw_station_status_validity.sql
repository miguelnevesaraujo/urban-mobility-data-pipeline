SELECT
    station_id,
    collected_at_utc,
    source_file
FROM {{ source('citi_bike', 'station_status') }}
WHERE
    is_installed IS NULL
    OR is_installed NOT IN (0, 1)
    OR is_renting IS NULL
    OR is_renting NOT IN (0, 1)
    OR is_returning IS NULL
    OR is_returning NOT IN (0, 1)
    OR last_reported_unix IS NULL
    OR last_reported_unix <= 0
    OR source_file IS NULL
    OR TRIM(source_file) = ''