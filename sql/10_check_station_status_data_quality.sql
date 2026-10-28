SELECT
    COUNT(*) AS total_observations,
    COUNT(*) FILTER (
        WHERE num_bikes_available < 0
           OR num_docks_available < 0
    ) AS negative_counts,
    COUNT(*) FILTER (
        WHERE is_installed NOT IN (0, 1)
           OR is_renting NOT IN (0, 1)
           OR is_returning NOT IN (0, 1)
    ) AS invalid_operational_flags,
    COUNT(*) FILTER (
        WHERE num_bikes_available IS NULL
           OR num_docks_available IS NULL
    ) AS missing_availability_counts,
    COUNT(*) FILTER (
        WHERE last_reported_unix IS NULL
           OR last_reported_unix <= 0
    ) AS missing_or_invalid_report_time,
    COUNT(*) FILTER (
        WHERE source_file IS NULL
           OR TRIM(source_file) = ''
    ) AS missing_source_file
FROM raw.station_status;