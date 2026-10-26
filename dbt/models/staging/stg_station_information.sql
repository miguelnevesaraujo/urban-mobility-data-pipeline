WITH source_stations AS (

    SELECT
        station_id,
        NULLIF(TRIM(name), '') AS station_name,
        lat AS latitude,
        lon AS longitude,
        capacity,
        loaded_at

    FROM {{ source('citi_bike', 'station_information') }}
)

SELECT *
FROM source_stations