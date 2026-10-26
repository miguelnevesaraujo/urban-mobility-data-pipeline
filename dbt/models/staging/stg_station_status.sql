WITH source_status AS (
    SELECT
        station_id,
        collected_at_utc,

        num_bikes_available,
        num_docks_available,

        is_installed,
        is_renting,
        is_returning,

        last_reported_unix,
        source_file,
        loaded_at

    FROM {{ source('citi_bike', 'station_status') }}
)

SELECT
    station_id,
    collected_at_utc,
    num_bikes_available,
    num_docks_available,
    CASE
        WHEN is_installed = 1 THEN TRUE
        WHEN is_installed = 0 THEN FALSE
        ELSE NULL
    END AS is_installed,

    CASE
        WHEN is_renting = 1 THEN TRUE
        WHEN is_renting = 0 THEN FALSE
        ELSE NULL
    END AS is_renting,

    CASE
        WHEN is_returning = 1 THEN TRUE
        WHEN is_returning = 0 THEN FALSE
        ELSE NULL
    END AS is_returning,

    TO_TIMESTAMP(last_reported_unix)
        AS station_reported_at_utc,

    source_file,
    loaded_at

FROM source_status