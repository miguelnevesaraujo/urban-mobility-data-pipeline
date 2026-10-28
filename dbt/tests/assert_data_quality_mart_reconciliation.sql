WITH source_counts AS (
    SELECT
        COUNT(*) AS total_observations,
        COUNT(*) FILTER (
            WHERE is_eligible IS TRUE
        ) AS eligible_observations
    FROM {{ ref('int_station_availability') }}
),

mart_counts AS (
    SELECT
        COALESCE(
            SUM(observation_count), 0
        ) AS total_classified,
        COALESCE(
            SUM(observation_count) FILTER (
                WHERE quality_category = 'Eligible'
            ), 0
        ) AS eligible_classified
    FROM {{ ref('mart_station_data_quality') }}
)

SELECT
    s.total_observations,
    m.total_classified,
    s.eligible_observations,
    m.eligible_classified
FROM source_counts AS s
CROSS JOIN mart_counts AS m
WHERE
    s.total_observations <> m.total_classified
    OR s.eligible_observations <> m.eligible_classified