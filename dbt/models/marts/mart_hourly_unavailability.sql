{{ config(materialized='table') }}

WITH eligible_observations AS (
    SELECT
        station_id,
        collected_at_utc,
        EXTRACT(
            HOUR FROM (
                collected_at_utc AT TIME ZONE 'America/New_York'
            )
        )::INTEGER AS hour_of_day,

        num_bikes_available
    FROM {{ ref('int_station_availability') }}
    WHERE is_eligible = TRUE
),

hourly_metrics AS (
    SELECT
        hour_of_day,
        COUNT(DISTINCT collected_at_utc)
            AS total_snapshots,

        COUNT(*) AS eligible_observations,

        COUNT(*) FILTER (
            WHERE num_bikes_available = 0
        ) AS zero_bike_observations

    FROM eligible_observations
    GROUP BY hour_of_day
)

SELECT
    hour_of_day,
    total_snapshots,
    eligible_observations,
    zero_bike_observations,
    ROUND(
        100.0 * zero_bike_observations
        / NULLIF(eligible_observations, 0),
        2
    ) AS unavailability_rate_pct
FROM hourly_metrics