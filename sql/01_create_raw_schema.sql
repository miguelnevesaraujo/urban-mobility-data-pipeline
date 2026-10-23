CREATE SCHEMA IF NOT EXISTS raw;

COMMENT ON SCHEMA raw IS
'Landing tables for ingested Citi Bike source data';

SELECT schema_name
FROM information_schema.schemata
WHERE schema_name = 'raw';