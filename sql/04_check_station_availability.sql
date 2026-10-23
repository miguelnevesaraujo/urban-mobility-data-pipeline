WITH observations AS (
    SELECT
        s.station_id,
        s.num_bikes_available,

        (
            s.is_installed = 1
            AND s.is_renting = 1
            AND i.capacity > 0
        ) AS is_operational,

        (
            s.last_reported_unix IS NOT NULL
            AND EXTRACT(EPOCH FROM s.collected_at_utc)
                - s.last_reported_unix
                BETWEEN 0 AND 900
        ) AS is_fresh

    FROM raw.station_status AS s

    LEFT JOIN raw.station_information AS i
        ON s.station_id = i.station_id
)

SELECT
    COUNT(*) AS total_observations,

    COUNT(*) FILTER (
        WHERE num_bikes_available = 0
    ) AS zero_bike_observations,

    COUNT(*) FILTER (
        WHERE is_operational AND is_fresh
    ) AS eligible_observations,

    COUNT(*) FILTER (
        WHERE is_operational
          AND is_fresh
          AND num_bikes_available = 0
    ) AS eligible_zero_bike_observations

FROM observations;