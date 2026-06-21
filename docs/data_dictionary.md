# Data Dictionary

## raw.ev_stations
Raw EV charging station data ingested directly from the NLR (National Renewable Energy Lab) API.
76 columns total; key columns listed below.

| Column | Type | Description |
|--------|------|--------------|
| id | text | Unique station identifier from NLR |
| station_name | text | Name of the charging station |
| city | text | City where station is located |
| state | text | State (CA for this project) |
| latitude | text | Station latitude |
| longitude | text | Station longitude |
| ev_network | text | Charging network operator (e.g. ChargePoint, Tesla) |
| ev_level1_evse_num | text | Number of Level 1 charging ports |
| ev_level2_evse_num | text | Number of Level 2 charging ports |
| ev_dc_fast_num | text | Number of DC Fast charging ports |
| status_code | text | E = available, T = temporarily unavailable |
| open_date | text | Date the station opened |
| ingested_at | text | Timestamp when this row was loaded |

## staging.stg_stations
Cleaned and type-cast version of raw.ev_stations. Filters to public, active EV stations only.

| Column | Type | Description |
|--------|------|--------------|
| station_id | integer | Unique station ID |
| station_name | text | Station name |
| city | text | City |
| state | text | State |
| zip | text | ZIP code |
| latitude | numeric(9,6) | Latitude, cast from text |
| longitude | numeric(9,6) | Longitude, cast from text |
| ev_network | text | Charging network |
| ev_connector_types | text | Connector types available |
| level1_ports | integer | Level 1 port count |
| level2_ports | integer | Level 2 port count |
| dc_fast_ports | integer | DC Fast port count |
| facility_type | text | Type of location (mall, workplace, etc) |
| access_code | text | Public or private access |
| status_code | text | Station status |
| open_date | date | Date station opened |
| date_last_confirmed | date | Last data confirmation date |
| ingested_at | timestamptz | Load timestamp |

## mart.fct_hourly_demand
Aggregated city-network combinations with port capacity metrics. 3,057 rows.

| Column | Type | Description |
|--------|------|--------------|
| city | text | City |
| state | text | State |
| ev_network | text | Charging network |
| total_stations | bigint | Count of stations in this city-network combo |
| total_level1_ports | bigint | Total Level 1 ports |
| total_level2_ports | bigint | Total Level 2 ports |
| total_dc_fast_ports | bigint | Total DC Fast ports |
| total_ports | bigint | Sum of all port types |
| avg_ports_per_station | numeric | Average ports per station |
| dc_fast_pct | numeric | % of total ports that are DC Fast |
| level2_pct | numeric | % of total ports that are Level 2 |
| created_at | timestamp | Table generation timestamp |

## mart.station_growth
Monthly time series of station openings, derived from open_date. Covers 1995-2026.

| Column | Type | Description |
|--------|------|--------------|
| month | timestamptz | Month of station openings |
| state | text | State |
| ev_network | text | Charging network |
| stations_opened | bigint | Stations opened that month |
| ports_opened | bigint | Total ports opened that month |
| dc_fast_opened | bigint | DC Fast ports opened that month |
| level2_opened | bigint | Level 2 ports opened that month |
| cumulative_stations | bigint | Running total of stations |
| cumulative_ports | bigint | Running total of ports |

## mart.model_metrics
Evaluation results for each trained Prophet model.

| Column | Type | Description |
|--------|------|--------------|
| label | text | City_Network identifier |
| city | text | City |
| ev_network | text | Charging network |
| total_ports | integer | Port count used for training |
| mae | numeric | Mean Absolute Error |
| rmse | numeric | Root Mean Squared Error |
| evaluated_at | text | Evaluation timestamp |

## raw.dq_log
Data quality check results logged on each pipeline run.

| Column | Type | Description |
|--------|------|--------------|
| check_name | text | Name of the quality check |
| status | text | PASS or FAIL |
| detail | text | Check result detail |
| checked_at | timestamptz | When the check ran |
