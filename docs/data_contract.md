# Citi Bike Station Availability — Data Contract

## 1. Data Sources

The pipeline uses two Citi Bike GBFS 2.3 feeds:

- **station_information:** Station identifiers, names, locations, and capacity.
- **station_status:** Bicycle availability, operational status, and reporting timestamps.

Both datasets are linked through `station_id`.

Historical trip records will be integrated separately.

## 2. Data Granularity

Each availability record represents the observed state of one station at a specific snapshot timestamp.

The expected logical key is:

`station_id + snapshot_timestamp_utc`

All timestamps will be normalized to UTC.

## 3. Required Fields

| Field | Purpose |
|---|---|
| `station_id` | Identifies the station |
| `snapshot_timestamp_utc` | Identifies when the snapshot was collected |
| `num_bikes_available` | Available bicycles |
| `num_docks_available` | Available docking spaces |
| `is_installed` | Station installation status |
| `is_renting` | Whether rentals are enabled |
| `is_returning` | Whether returns are enabled |
| `last_reported` | Last station reporting timestamp |
| `capacity` | Reported station capacity |

Additional metadata, including the feed's `last_updated` timestamp, will be preserved.

## 4. Station Unavailability Definition

A station is classified as unavailable due to a lack of bicycles when:

- The station is installed (`is_installed = 1`).
- Rentals are enabled (`is_renting = 1`).
- Reported capacity is greater than zero.
- The station report is sufficiently recent.
- The station has zero available bicycles (`num_bikes_available = 0`).

The freshness threshold will be established after analyzing actual reporting delays.

Stations failing these eligibility conditions will not automatically be classified as lacking bicycles.

## 5. Data Quality Rules

The pipeline must verify:

- Uniqueness of station identifiers within each snapshot.
- Valid relationships between station information and station status.
- Non-negative bicycle and dock counts.
- Valid timestamps and reporting freshness.
- Detection of missing or duplicate snapshots.
- Identification of stations reporting zero capacity.

Stations with zero capacity will be flagged for investigation rather than automatically deleted.

## 6. Main Business KPI

**Station Unavailability Rate (%)**

Number of eligible station snapshots with zero available bicycles divided by the total number of eligible station snapshots, multiplied by 100.

This metric measures observed unavailability at collection times, not the exact percentage of elapsed time without bicycles.

## 7. Initial Data Validation

The initial API inspection returned:

| Check | Result |
|---|---:|
| Station information records | 2,519 |
| Station status records | 2,519 |
| Matching station identifiers | 2,519 |
| Unmatched station identifiers | 0 |
| Stations reporting zero capacity | 35 |

These values describe the initial inspection and may change as the source data is updated.

## 8. Collection Limitations

The station status API provides current snapshots rather than a complete historical availability dataset.

Snapshots will initially be collected every 15 minutes while the collection service is running.

Missed collection periods will be recorded as missing data and will not be reconstructed using invented observations.

Availability metrics must account for differences in data completeness between stations.