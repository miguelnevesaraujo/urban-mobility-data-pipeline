SELECT
    COALESCE(
        LPAD(hour_of_day::TEXT, 2, '0') || ':00',
        'TOTAL'
    ) AS local_hour,
    SUM(total_snapshots) AS total_snapshots,
    SUM(eligible_observations) AS eligible_observations,
    SUM(zero_bike_observations) AS zero_bike_observations,
    ROUND(
        100.0 * SUM(zero_bike_observations)
        / NULLIF(SUM(eligible_observations), 0),
        2
    ) AS unavailability_rate_pct
FROM dbt_mobility.mart_hourly_unavailability
GROUP BY ROLLUP(hour_of_day)
ORDER BY
    GROUPING(hour_of_day),
    hour_of_day;