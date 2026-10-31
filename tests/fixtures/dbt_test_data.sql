INSERT INTO raw.station_information (
    station_id,
    name,
    lat,
    lon,
    capacity
)
VALUES
    ('ci_station_001', 'CI Test Station A', 40.7500, -73.9900, 20),
    ('ci_station_002', 'CI Test Station B', 40.7600, -73.9800, 15);

INSERT INTO raw.station_status (
    collected_at_utc,
    station_id,
    num_bikes_available,
    num_docks_available,
    is_installed,
    is_renting,
    is_returning,
    last_reported_unix,
    source_file
)
VALUES
    (
        '2026-10-30 12:00:00+00',
        'ci_station_001',
        5, 15, 1, 1, 1,
        EXTRACT(EPOCH FROM TIMESTAMPTZ
            '2026-10-30 11:59:30+00')::BIGINT,
        'ci/station_status_20261030T120000Z.json'
    ),
    (
        '2026-10-30 12:00:00+00',
        'ci_station_002',
        0, 15, 1, 1, 1,
        EXTRACT(EPOCH FROM TIMESTAMPTZ
            '2026-10-30 11:59:30+00')::BIGINT,
        'ci/station_status_20261030T120000Z.json'
    );

-- Register the snapshot in the ingestion ledger
INSERT INTO raw.station_snapshot_loads (
    source_file,
    expected_rows
)
VALUES (
    'ci/station_status_20261030T120000Z.json',
    2
);