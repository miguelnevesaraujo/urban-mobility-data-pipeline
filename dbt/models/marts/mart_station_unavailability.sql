{{ config(materialized='table') }}

WITH eligible_observations AS (
    SELECT
        station_id,
        station_name,
        latitude,
        longitude,
        capacity,
        num_bikes_available

    FROM {{ ref('int_station_availability') }}

    WHERE is_eligible = TRUE
),

station_metrics AS (
    SELECT
        station_id,
        station_name,
        latitude,
        longitude,
        capacity,
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

    GROUP BY
        station_id,
        station_name,
        latitude,
        longitude,
        capacity
)

SELECT
    *,
    eligible_snapshots >= 10 AS has_minimum_sample
FROM station_metrics