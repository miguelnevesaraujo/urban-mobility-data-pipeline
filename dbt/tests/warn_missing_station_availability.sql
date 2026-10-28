{{ config(severity='warn') }}

SELECT
    station_id,
    collected_at_utc,
    source_file
FROM {{ source('citi_bike', 'station_status') }}
WHERE
    num_bikes_available IS NULL
    OR num_docks_available IS NULL