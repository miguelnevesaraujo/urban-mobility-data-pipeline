WITH station_status AS (
    SELECT *
    FROM {{ ref('stg_station_status') }}
),

station_information AS (
    SELECT *
    FROM {{ ref('stg_station_information') }}
),

joined_data AS (
    SELECT
        s.station_id,
        i.station_name,
        i.latitude,
        i.longitude,
        i.capacity,
        s.collected_at_utc,
        s.station_reported_at_utc,
        EXTRACT(
            EPOCH FROM (
                s.collected_at_utc - s.station_reported_at_utc
            )
        ) AS report_age_seconds,
        s.num_bikes_available,
        s.num_docks_available,
        s.is_installed,
        s.is_renting,
        s.is_returning,
        s.source_file
    FROM station_status AS s

    LEFT JOIN station_information AS i
        ON s.station_id = i.station_id
)

SELECT
    *,
    CASE
        WHEN is_installed IS TRUE
         AND is_renting IS TRUE
         AND capacity > 0
         AND num_bikes_available IS NOT NULL
         AND report_age_seconds BETWEEN 0 AND 900
        THEN TRUE
        ELSE FALSE
    END AS is_eligible,
    num_bikes_available = 0 AS is_zero_bike

FROM joined_data