{{ config(materialized='table') }}
WITH classified_observations AS (
    SELECT
        CASE
            WHEN is_eligible IS TRUE
                THEN 'Eligible'

            WHEN report_age_seconds > 900
                THEN 'Stale report'

            WHEN report_age_seconds < 0
                THEN 'Future report'

            WHEN report_age_seconds IS NULL
                THEN 'Unknown report age'

            WHEN capacity IS NULL OR capacity <= 0
                THEN 'Invalid station capacity'

            WHEN is_installed IS DISTINCT FROM TRUE
                THEN 'Station not installed'

            WHEN is_renting IS DISTINCT FROM TRUE
                THEN 'Renting disabled'

            WHEN num_bikes_available IS NULL
                THEN 'Missing bike availability'

            ELSE 'Other reason'
        END AS quality_category
    FROM {{ ref('int_station_availability') }}
),

category_counts AS (
    SELECT
        quality_category,
        COUNT(*) AS observation_count
    FROM classified_observations
    GROUP BY quality_category
)

SELECT
    quality_category,
    observation_count,
    ROUND(
        100.0 * observation_count
        / NULLIF(SUM(observation_count) OVER (), 0),
        2
    ) AS percentage_of_total
FROM category_counts