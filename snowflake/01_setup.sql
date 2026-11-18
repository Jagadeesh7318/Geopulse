-- GeoPulse - Week 1: Snowflake setup and GEOGRAPHY conversion
CREATE DATABASE IF NOT EXISTS GEOPULSE;
USE DATABASE GEOPULSE;
CREATE SCHEMA IF NOT EXISTS RAW;
CREATE SCHEMA IF NOT EXISTS ANALYTICS;
USE SCHEMA GEOPULSE.RAW;

CREATE OR REPLACE TABLE raw_pings_stg (device_id STRING, lat FLOAT, lon FLOAT, ping_ts TIMESTAMP_NTZ);
CREATE OR REPLACE TABLE stores_stg (store_id INT, store_name STRING, lat FLOAT, lon FLOAT);
CREATE OR REPLACE TABLE raw_pings (device_id STRING, ping_ts TIMESTAMP_NTZ, geo GEOGRAPHY);
CREATE OR REPLACE TABLE stores (store_id INT, store_name STRING, lat FLOAT, lon FLOAT, geo GEOGRAPHY);

-- Load data/pings.csv into raw_pings_stg and data/stores.csv into stores_stg
-- using Snowsight: Add Data > Load data into a table.

-- Run each INSERT only once. ST_MAKEPOINT takes (longitude, latitude).
INSERT INTO raw_pings
SELECT device_id, ping_ts, ST_MAKEPOINT(lon, lat) FROM raw_pings_stg;

INSERT INTO stores
SELECT store_id, store_name, lat, lon, ST_MAKEPOINT(lon, lat) FROM stores_stg;

-- Check: busiest stores within a 500 m catchment
SELECT s.store_id, COUNT(DISTINCT p.device_id) AS devices_500m
FROM stores s
JOIN raw_pings p ON ST_DWITHIN(p.geo, s.geo, 500)
GROUP BY s.store_id
ORDER BY devices_500m DESC
LIMIT 10;