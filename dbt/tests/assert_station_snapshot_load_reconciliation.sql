WITH actual_counts AS (
    SELECT
        source_file,
        COUNT(*) AS actual_rows
    FROM {{ source('citi_bike', 'station_status') }}
    WHERE source_file IS NOT NULL
    GROUP BY source_file
),

reconciliation AS (
    SELECT
        COALESCE(
            loads.source_file,
            actual.source_file
        ) AS source_file,

        loads.expected_rows,

        COALESCE(actual.actual_rows, 0) AS actual_rows,

        CASE
            WHEN loads.source_file IS NULL
                THEN 'unregistered_snapshot'

            WHEN actual.source_file IS NULL
                THEN 'missing_observations'

            WHEN loads.expected_rows <> actual.actual_rows
                THEN 'row_count_mismatch'

            ELSE NULL
        END AS issue
    FROM {{ source('citi_bike', 'station_snapshot_loads') }}
        AS loads

    FULL OUTER JOIN actual_counts AS actual
        ON loads.source_file = actual.source_file
)

SELECT
    source_file,
    expected_rows,
    actual_rows,
    issue
FROM reconciliation
WHERE issue IS NOT NULL