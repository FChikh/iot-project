# Grafana Dashboard for Admin Room Monitoring
The Grafana dashboard implementation provides administrators with a centralized, 
real-time view of room metrics, combining **time-series sensor data** (InfluxDB) and **static room data**  (PostgreSQL). 
Designed for scalability and usability, it enables quick anomaly detection and room-specific analysis. 
Below is a detailed breakdown of the design choices, features, and challenges.

## Design Choices & Key Features

### Dual Data Source Integration
- InfluxDB: Handles time-series sensor data (temperature, CO2, humidity, PM2.5/PM10).
- PostgreSQL: Stores static room metadata (equipment availability, capacity).
    This separation ensures efficient querying—real-time metrics from InfluxDB and structural details from PostgreSQL.

### Two-Tier Dashboard Design
- Overall Metrics Dashboard:
    - Displays averages (e.g., mean temperature across all rooms).
    - Highlights anomalies (e.g., rooms with highest CO2 levels).
    - Uses InfluxDB aggregations (MEAN(), MAX(), MIN()) for summary statistics.

- Room-Specific Dashboard:
    - Features a dynamic dropdown of rooms, auto-populated from PostgreSQL and sorted alphabetically.
    - Combines real-time sensor graphs with static equipment/capacity tables.

- Automatic Room Discovery
    - The dropdown menu queries PostgreSQL dynamically, ensuring new rooms or sensors added to the simulation are instantly available in Grafana without manual configuration.

- Admin-Centric Visualizations
    - Anomaly Detection: Color-coded thresholds (e.g., red for PM2.5 > 50 μg/m³).
    - Equipment Status: Boolean indicators (e.g., green checkmark for projectors).
    - Time-Range Selection: Allows admins to analyze trends over hours, days, or weeks.

## Key Challenges
### Combining Time-Series and Relational Data
- Joining InfluxDB (time-series) and PostgreSQL (relational) data in Grafana required careful synchronization.

### Dynamic Dropdown Population
- Ensuring the dropdown list updated in real-time as rooms were added demanded frequent PostgreSQL queries.

### Schema Flexibility
- Adding new sensors (e.g., noise, VOC) required updating Grafana panels and InfluxDB queries.
- Future-Proofing: Designed reusable panel templates to simplify adding metrics.


