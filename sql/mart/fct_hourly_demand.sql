-- fct_hourly_demand.sql
-- Aggregates staging data to create a demand proxy per network per city
-- Since we don't have session logs, we use port counts as a demand capacity proxy

DROP TABLE IF EXISTS mart.fct_hourly_demand;

CREATE TABLE mart.fct_hourly_demand AS
WITH station_capacity AS (
    SELECT
        station_id,
        station_name,
        city,
        state,
        zip,
        latitude,
        longitude,
        ev_network,
        ev_connector_types,
        facility_type,
        level1_ports,
        level2_ports,
        dc_fast_ports,
        (level1_ports + level2_ports + dc_fast_ports)   AS total_ports,
        open_date,
        ingested_at
    FROM staging.stg_stations
    WHERE ev_network IS NOT NULL
    AND ev_network != 'None'
),
network_city_summary AS (
    SELECT
        city,
        state,
        ev_network,
        COUNT(station_id)                               AS total_stations,
        SUM(level1_ports)                               AS total_level1_ports,
        SUM(level2_ports)                               AS total_level2_ports,
        SUM(dc_fast_ports)                              AS total_dc_fast_ports,
        SUM(total_ports)                                AS total_ports,
        ROUND(AVG(total_ports), 2)                      AS avg_ports_per_station
    FROM station_capacity
    GROUP BY city, state, ev_network
)
SELECT
    city,
    state,
    ev_network,
    total_stations,
    total_level1_ports,
    total_level2_ports,
    total_dc_fast_ports,
    total_ports,
    avg_ports_per_station,
    ROUND(total_dc_fast_ports * 100.0 / NULLIF(total_ports, 0), 2)    AS dc_fast_pct,
    ROUND(total_level2_ports * 100.0 / NULLIF(total_ports, 0), 2)     AS level2_pct,
    NOW()                                                               AS created_at
FROM network_city_summary
ORDER BY total_ports DESC;
