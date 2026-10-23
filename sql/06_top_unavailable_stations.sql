WITH eligible_observations AS (
    SELECT
        s.station_id,
        i.name AS station_name,
        s.num_bikes_available

    FROM raw.station_status AS s

    INNER JOIN raw.station_information AS i
        ON s.station_id = i.station_id

    WHERE s.is_installed = 1
      AND s.is_renting = 1
      AND i.capacity > 0
      AND s.num_bikes_available IS NOT NULL
      AND s.last_reported_unix IS NOT NULL
      AND EXTRACT(EPOCH FROM s.collected_at_utc)
          - s.last_reported_unix BETWEEN 0 AND 900
)

SELECT
    station_id,
    station_name,

    COUNT(*) AS eligible_snapshots,

    COUNT(*) FILTER (
        WHERE num_bikes_available = 0
    ) AS zero_bike_snapshots,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE num_bikes_available = 0
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS unavailability_rate_pct

FROM eligible_observations

GROUP BY station_id, station_name

HAVING COUNT(*) >= 10

ORDER BY
    unavailability_rate_pct DESC,
    zero_bike_snapshots DESC,
    station_id

LIMIT 10;