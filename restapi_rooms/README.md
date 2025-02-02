# RESTAPI (Input for Decision System)
The REST API developed for our IoT project serves as a critical interface 
for retrieving sensor data, managing room bookings, and providing equipment
details. Built with Flask and documented via Swagger (OpenAPI 3.0), 
it integrates seamlessly with InfluxDB for sensor data storage and
Google Calendar for booking management. Below is a breakdown of the design 
choices, key features, and challenges addressed during implementation.

## Design Choices & Key Features
### Modular Endpoint Structure
- **Global endpoints** `(e.g., /rooms/sensor, /rooms/pm2\_5)` to fetch aggregated data across all rooms.
- **Room-specific endpoints** (e.g., /rooms/{room\_id}/sensor, /rooms/{room\_id}/bookings) 
    to retrieve data for individual rooms. This design ensures scalability, 
    allowing users to query broad datasets or drill down into specific rooms as needed.

### Standardized Data Schema
All responses follow a consistent JSON schema defined in Swagger components (e.g., RoomData, RoomEquipment). 
For example:
```yaml
RoomTemperature:
  type: object
  properties:
    room: 
      type: string
    temperature:
      type: array
      items:
        $ref: '#/components/schemas/TemperatureReading'
```
Each sensor type (temperature, PM2.5, CO2, etc.) returns an array of timestamp-value pairs, 
ensuring predictability for both human users and the decision system.

### Booking Integration with Google Calendar
The `/book/rooms/{room\_id}` endpoint handles 30-minute slot bookings, 
checking for conflicts via Google Calendar. The API enforces:
- Validation of timestamp formats.
- Conflict detection (HTTP 409 if the slot is occupied).
- Synchronization with Google Calendar for persistent storage.

### Equipment Metadata
Endpoints like `/rooms/equipment` expose static room attributes (e.g., projector availability, 
seating capacity), enabling the decision system to rank rooms based on user requirements 
(e.g., "Find a room with a projector for 20 people")

### Comprehensive Error Handling
Responses include descriptive errors (e.g., 404 for missing data, 500 for server issues), 
aiding developers in troubleshooting.


## Most Interesting Aspects
1. Decision System Integration
    The API’s structured output allows the decision system to efficiently parse and rank rooms. For instance:
    - Sensor data (e.g., CO2 levels, temperature) is used to evaluate comfort.
    - Equipment metadata and booking availability enable filtering based on user preferences.
2. Swagger-Driven Development
    Swagger’s interactive documentation provides:
    - Auto-generated API specs for frontend/backend alignment.
    - Testability via the Swagger UI, reducing integration risks.
    - Clear schema definitions, ensuring consistency across endpoints.

3. Temporal Filtering for Bookings
    The `/rooms/bookings` endpoint supports optional `startDate` and `days` parameters,
    enabling users to fetch bookings within custom time windows. 
    This minimizes data transfer overhead and improves performance.


## Key Challenge: Data Structure Design
The most complex task was designing an intuitive yet machine-friendly data format. 
Requirements included:
- Consistency: Ensuring all sensor types followed the same nested structure (e.g., `temperature: [{timestamp: "...", value: 25}, ...]`).
- Accessibility: Balancing readability for developers with ease of parsing for the decision system.
- Extensibility: Structuring schemas (e.g., `RoomData`) to accommodate future sensors without breaking existing integrations.

By leveraging Swagger’s schema reuse and hierarchical modeling, the API achieves a balance between clarity and efficiency. 
For example, the RoomData schema aggregates multiple sensor arrays, 
while individual endpoints `(e.g., /rooms/temperature)` provide isolated datasets for specific metrics.
