WITH expected AS (
    SELECT
        COUNT(*) FILTER (
            WHERE is_eligible
        ) AS eligible_observations,
        COUNT(*) FILTER (
            WHERE is_eligible AND is_zero_bike
        ) AS zero_bike_observations,
        COUNT(DISTINCT collected_at_utc) FILTER (
            WHERE is_eligible
        ) AS total_snapshots
    FROM {{ ref('int_station_availability') }}
),

actual AS (
    SELECT
        COALESCE(SUM(eligible_observations), 0)
            AS eligible_observations,

        COALESCE(SUM(zero_bike_observations), 0)
            AS zero_bike_observations,

        COALESCE(SUM(total_snapshots), 0)
            AS total_snapshots
    FROM {{ ref('mart_hourly_unavailability') }}
)

SELECT
    expected.eligible_observations AS expected_eligible,
    actual.eligible_observations AS actual_eligible,

    expected.zero_bike_observations AS expected_zero_bike,
    actual.zero_bike_observations AS actual_zero_bike,

    expected.total_snapshots AS expected_snapshots,
    actual.total_snapshots AS actual_snapshots
FROM expected
CROSS JOIN actual
WHERE expected.eligible_observations
      <> actual.eligible_observations
   OR expected.zero_bike_observations
      <> actual.zero_bike_observations
   OR expected.total_snapshots
      <> actual.total_snapshots