SELECT
    station_name,
    eligible_snapshots,
    zero_bike_snapshots,
    unavailability_rate_pct
FROM dbt_mobility.mart_station_unavailability
WHERE has_minimum_sample = TRUE

ORDER BY
    unavailability_rate_pct DESC,
    zero_bike_snapshots DESC,
    station_id
LIMIT 10;