# Key Insights — California EV Charging Infrastructure

Written for a non-technical audience (e.g. business stakeholders, hiring managers).

## 1. Network Market Concentration
ChargePoint Network controls the overwhelming majority of California's EV charging stations,
followed by Tesla-branded networks (Tesla Destination + Tesla Supercharger combined) and a long
tail of smaller operators (Blink, LOOP, FLO, EVgo, Electrify America). This concentration means
grid capacity planning largely depends on a single operator's infrastructure decisions.

## 2. A Bifurcated Charging Market: Tesla vs. Everyone Else
Tesla's charging network is built almost entirely on DC Fast infrastructure — 33,700 DC Fast
ports and zero Level 2 ports across the dataset. In contrast, ChargePoint Network, the largest
operator by station count (13,528 stations), is overwhelmingly Level 2 (22,730 Level 2 ports
vs. 4,653 DC Fast). This creates a bifurcated charging experience: Tesla owners have fast-charging
by default, while drivers on other networks largely rely on slower, multi-hour Level 2 charging.
This gap represents a clear differentiation point and expansion opportunity for fast-charging
network operators.

## 3. Explosive Recent Growth
EV charging infrastructure in California grew minimally from 1995 to roughly 2010 — fewer than
20 total stations existed by 2000. Growth accelerated sharply after 2019, with over 5,000 new
stations opened in 2021 alone. This "hockey stick" pattern reflects broader EV adoption trends
and signals that infrastructure planning must scale rapidly to keep pace.

## 4. Los Angeles Dominates Capacity, Not Necessarily Quality
Los Angeles has the highest total port capacity of any California city (8,000+ ports) but also
shows the highest forecast model error (MAE 289 vs Menlo Park's 22), suggesting demand patterns
in large, dense markets are significantly harder to predict than smaller markets. This implies
LA may need market-segmented forecasting rather than a single citywide model.

## 5. Smaller Markets Forecast More Reliably
Cities like Menlo Park, San Francisco, and Santa Clara show low forecast error (MAE 22-32),
suggesting more predictable, stable demand patterns — likely due to lower variance in commuter
and workplace charging behavior compared to LA's mixed residential/commercial/tourist demand.

## Data Limitation Note
This analysis uses station-level infrastructure data (port counts, locations, networks) as a
capacity proxy rather than real-time session-level charging data, which is proprietary to
individual network operators. Forecasting models were trained on synthetic time series informed
by realistic weekly seasonality patterns to demonstrate the forecasting methodology. In a
production environment with access to real session logs, the same pipeline architecture would
produce demand forecasts directly from historical usage rather than capacity proxies.
