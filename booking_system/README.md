# Room Booking System – Feature Implementation Report

## 1. Overview
The room booking system is designed to rank available classrooms based on two sets of criteria:

1. **Environmental Sensor Data**: Measurements include CO₂, PM2.5, PM10, noise, lighting, humidity, VOC, and temperature. Each sensor’s data is checked against EU and international standards for compliance.
2. **Equipment Data**: This includes room features such as seating capacity, projector, smartboard, PC, whiteboard, and other relevant equipment.

User preferences for environmental conditions and room amenities are provided through a web interface built with Streamlit. The system processes sensor and equipment data using a decision-making logic based on the **TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)** method to rank rooms. REST API endpoints, documented with Swagger, facilitate the integration and testing of these services.

## 2. Execution Flow and Function Order

### A. Data Retrieval and Preprocessing

#### 1. Data Fetching (`data_fetcher.py`):
- **`fetch_api_data`**: This helper function manages GET requests with retries and exponential backoff to ensure reliable communication with the room_db REST API.
- **`download_sensor_data`**: Retrieves sensor-specific JSON data (e.g., for CO₂, temperature).
- **Other functions** (`fetch_room_bookings`, `fetch_rooms_and_equipments`, `fetch_rooms`, `fetch_equipment`): Collect booking information and equipment details for each room.

#### 2. Compliance Checking (`check_compliance.py`):
Each sensor type has a dedicated function to:
- Compute key statistics: Such as average, maximum, and the percentage of compliant or non-compliant readings.
- Evaluate compliance: The compliance checks are based on EU/German regulations. The German compliance rules were chosen, as they are stricter than Luxembourgish regulations and are well-documented. Also, there was limited information on Luxembourgish compliance regulations.

##### Compliance Standards:
1. **CO₂**: [German Committee on Indoor Air Guide Values](https://www.umweltbundesamt.de/en/topics/health/commissions-working-groups/german-committee-on-indoor-air-guide-values#german-committee-on-indoor-air-guide-values-air)
2. **PM2.5 & PM10**: [EU Air Quality Standards](https://environment.ec.europa.eu/topics/air/air-quality/eu-air-quality-standards_en)
3. **Acoustic**: EN ISO 3382-2:2008
4. **Light**: EN 12464-1
5. **Humidity**: EN ISO 773
6. **Temperature**: According to German ASR (Arbeitsstätten Regeln), an office workspace should have a minimum temperature of 19°C and a maximum temperature of 26°C (without ventilation/AC).

### B. Decision Logic and Room Ranking

#### 3. Primary Room Validations:
- **`check_seats`** and **`check_availability`**: Ensure that rooms have adequate seating and are free during the requested time slots.
- **`create_user_prefs`**: Consolidates user input regarding environmental and equipment preferences into a dictionary used to adjust the decision matrix.

#### 4. Decision Logic (`decision_logic.py`):
- **`perform_compliance_check`**: Iterates over the sensor data for each room and calls the corresponding compliance function.
- **`extract_sensor_attributes`**: Extracts average sensor attributes (like average CO₂ or temperature) from the compliance results, which are then used in the decision matrix.
- **`build_topsis_matrix`**:
  1. Compiles both sensor attributes and equipment data for each room (after validating seating capacity and environmental compliance) into a unified decision matrix.
  2. REST API Integration: A GET request is sent to the REST API endpoint (documented via Swagger) to trigger the ranking process. This endpoint calls functions like `get_ranking` that build the decision matrix and apply the TOPSIS algorithm.
- **`topsis_decision_logic`**:
  1. **Normalization and Weighting**: The decision matrix is normalized, and each attribute is weighted.
     - Weights are chosen such that equipment data (e.g., seating capacity, projector, PC) have higher importance relative to sensor data. This reflects the idea that equipment features directly impact room functionality.
  2. **Ideal Solutions Calculation**: The algorithm determines the positive ideal solution (PIS) and negative ideal solution (NIS), based on the user preferences. For criteria where lower values are preferable (such as CO₂ or noise levels), the ideal best is defined as the minimum value.
  3. **Closeness Coefficient Calculation**: Each room’s distance from the ideal solution is computed to derive a closeness coefficient, which is used to rank the rooms.

### C. Booking Interface

#### 5. Booking Interface (`booking_interface.py`):
- The **Streamlit interface** collects user details, desired booking times, and room preferences.
- **`fetch_room_ranking`**: This function builds the API URL with the appropriate query parameters and sends a GET request to the decision logic REST API endpoint. The endpoint is documented with Swagger for clarity and ease of testing.
- The **ranked list of rooms**, along with their environmental and equipment attributes, is then displayed. Users can trigger the booking process via a button that calls `send_booking`, which posts booking requests to the room service.
- The **Google Calendar** is displayed on the webpage to provide an overview of the booking schedule.

## 3. Why TOPSIS Was Chosen
Several Multi-Criteria Decision Making (MCDM) methods are available (such as AHP, ELECTRE, and PROMETHEE), but **TOPSIS was selected** for this system because:

- **Simplicity and Intuitiveness**: TOPSIS is straightforward to implement and understand. By measuring the Euclidean distance to an ideal solution, it allows for an intuitive ranking of alternatives.
- **Computational Efficiency**: The method scales well and is efficient, which is crucial given the multiple sensor and equipment parameters involved.
- **Effective Normalization and Weighting**: TOPSIS easily accommodates varying scales by normalizing data and applying weights. This is essential when combining continuous sensor data with binary equipment data.
- **Clear Outcome**: The algorithm produces a **closeness coefficient** for each room, allowing for a transparent and interpretable rank order based on both environmental and equipment criteria.

## 4. Motivation Behind the Weight Selection
The weights in the TOPSIS algorithm were carefully chosen based on the following priorities:

- **Higher Importance of Equipment Data**:
  - Equipment features such as seating capacity, projector availability, PC, smartboard, and other amenities were given **higher weights**. This is because the physical and functional aspects of a room are critical to its suitability for booking.

- **Sensor Data Considerations**:
  - **VOC levels** are critical in industrial settings or newly renovated spaces with strong off-gassing, but in typical classrooms/offices they are **less critical** as long as they stay within the compliance range. The weighting is chosen to prioritize **comfort and usability**, as these are classrooms.

- **Balanced Decision-Making**:
  - This weighting strategy ensures that a room is only **highly ranked** if it meets both the **functional equipment requirements** and maintains a **comfortable, compliant environment**. This balance is key to matching real-world needs.
