WITH invalid_station_metrics AS (
    SELECT
        'station_mart' AS model_name,
        station_id AS record_id
    FROM {{ ref('mart_station_unavailability') }}
    WHERE eligible_snapshots <= 0
       OR zero_bike_snapshots < 0
       OR zero_bike_snapshots > eligible_snapshots
       OR unavailability_rate_pct NOT BETWEEN 0 AND 100
),

invalid_hourly_metrics AS (
    SELECT
        'hourly_mart' AS model_name,
        hour_of_day::TEXT AS record_id
    FROM {{ ref('mart_hourly_unavailability') }}
    WHERE hour_of_day NOT BETWEEN 0 AND 23
       OR eligible_observations <= 0
       OR zero_bike_observations < 0
       OR zero_bike_observations > eligible_observations
       OR unavailability_rate_pct NOT BETWEEN 0 AND 100
)

SELECT *
FROM invalid_station_metrics

UNION ALL

SELECT *
FROM invalid_hourly_metrics