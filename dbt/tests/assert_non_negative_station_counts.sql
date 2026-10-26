SELECT
    station_id,
    collected_at_utc,
    num_bikes_available,
    num_docks_available

FROM {{ ref('stg_station_status') }}

WHERE num_bikes_available < 0
   OR num_docks_available < 0