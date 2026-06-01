-- stg_stations.sql
-- Cleans raw.ev_stations and loads into staging.stg_stations
-- Keeps only EV-relevant columns, casts types, filters nulls

DROP TABLE IF EXISTS staging.stg_stations;

CREATE TABLE staging.stg_stations AS
SELECT
    id::INTEGER                                                         AS station_id,
    station_name,
    city,
    state,
    zip,
    street_address,
    latitude::NUMERIC(9,6)                                             AS latitude,
    longitude::NUMERIC(9,6)                                            AS longitude,
    ev_network,
    ev_connector_types,
    CASE WHEN ev_level1_evse_num IN ('None','nan','') THEN 0
         ELSE ev_level1_evse_num::FLOAT::INTEGER END                   AS level1_ports,
    CASE WHEN ev_level2_evse_num IN ('None','nan','') THEN 0
         ELSE ev_level2_evse_num::FLOAT::INTEGER END                   AS level2_ports,
    CASE WHEN ev_dc_fast_num IN ('None','nan','') THEN 0
         ELSE ev_dc_fast_num::FLOAT::INTEGER END                       AS dc_fast_ports,
    facility_type,
    access_code,
    status_code,
    CASE WHEN open_date IN ('None','nan','') THEN NULL
         ELSE open_date::DATE END                                      AS open_date,
    CASE WHEN date_last_confirmed IN ('None','nan','') THEN NULL
         ELSE date_last_confirmed::DATE END                            AS date_last_confirmed,
    ingested_at::TIMESTAMPTZ                                           AS ingested_at
FROM raw.ev_stations
WHERE
    id IS NOT NULL
    AND id != 'None'
    AND latitude IS NOT NULL
    AND latitude != 'None'
    AND longitude IS NOT NULL
    AND longitude != 'None'
    AND status_code = 'E';
