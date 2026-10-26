SELECT
    station_id,
    collected_at_utc,
    COUNT(*) AS duplicate_count

FROM {{ ref('stg_station_status') }}

GROUP BY
    station_id,
    collected_at_utc

HAVING COUNT(*) > 1