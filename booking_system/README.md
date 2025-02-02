# Room Booking System – Feature Implementation Report

## 1. Overview

The room booking system is designed to rank available classrooms based on two sets of criteria:

1. **Environmental Sensor Data**: Measurements include CO₂, PM2.5, PM10, noise, lighting, humidity, VOC, and temperature. Each sensor’s data is checked against EU and international standards for compliance.
2. **Equipment Data**: This includes room features such as seating capacity, projector, smartboard, PC, whiteboard, and other relevant equipment.

User preferences for environmental conditions and room amenities are provided through a web interface built with Streamlit. The system processes sensor and equipment data using a decision-making logic based on the **TOPSIS** (Technique for Order Preference by Similarity to Ideal Solution) method to rank rooms. **REST API** endpoints, documented with Swagger, facilitate the integration and testing of these services.

---

## 2. Execution Flow and Function Order

### A. Data Retrieval and Preprocessing

#### 1. Data Fetching (`data_fetcher.py`):
- **`fetch_api_data`**: Manages GET requests with retries and exponential backoff to ensure reliable communication with the `room_db` REST API.
- **`download_sensor_data`**: Retrieves sensor-specific JSON data (e.g., for CO₂, temperature).
- **Other functions**:
  - `fetch_room_bookings`: Collects booking information.
  - `fetch_rooms_and_equipments`: Retrieves room and equipment details.
  - `fetch_rooms`: Fetches room data.
  - `fetch_equipment`: Fetches equipment details.

#### 2. Compliance Checking (`check_compliance.py`):
Each sensor type has a dedicated function to:

- **Compute key statistics**: Such as average, maximum, and the percentage of compliant or non-compliant readings.
- **Evaluate compliance**: Based on EU/German regulations. The **German compliance rules** were chosen as they are stricter than Luxembourgish regulations, and Luxembourgish compliance information was limited.

##### Compliance Standards:
- **CO₂**: [German Committee on Indoor Air Guide Values](https://www.umweltbundesamt.de/en/topics/health/commissions-working-groups/german-committee-on-indoor-air-guide-values#german-committee-on-indoor-air-guide-values-air)
- **PM2.5 & PM10**: [EU Air Quality Standards](https://environment.ec.europa.eu/topics/air/air-quality/eu-air-quality-standards_en)
- **Acoustics**: EN ISO 3382-2:2008
- **Lighting**: EN 12464-1
- **Humidity**: EN ISO 773
- **Temperature**: According to German **ASR (Arbeitsstätten Regeln)**, office workspaces should have:
  - Minimum temperature: **19°C**
  - Maximum temperature: **26°C** (without ventilation/AC)

---

### B. Decision Logic and Room Ranking

#### 3. Primary Room Validations:
- **`check_seats`** and **`check_availability`**: Ensure that rooms have adequate seating and are available for the requested time slots.
- **`create_user_prefs`**: Consolidates user input regarding environmental and equipment preferences into a dictionary used to adjust the decision matrix.

#### 4. Decision Logic (`decision_logic.py`):
- **`perform_compliance_check`**: Iterates over the sensor data for each room and calls the corresponding compliance function.
- **`extract_sensor_attributes`**: Extracts average sensor attributes (e.g., CO₂, temperature) from the compliance results for the decision matrix.
- **`build_topsis_matrix`**:
  1. Compiles both sensor attributes and equipment data for each room (after validating seating capacity and environmental compliance) into a unified decision matrix.
  2. **REST API Integration**: A **GET request** is sent to the REST API endpoint (documented via Swagger) to trigger the ranking process. The endpoint calls functions like `get_ranking` to build the decision matrix and apply the TOPSIS algorithm.
- **`topsis_decision_logic`**:
  1. **Normalization and Weighting**:
     - The decision matrix is normalized, and each attribute is weighted.
     - Equipment data (e.g., seating capacity, projector, PC) have **higher importance** relative to sensor data since equipment directly impacts room functionality.
  2. **Ideal Solutions Calculation**:
     - Determines the **positive ideal solution (PIS)** and **negative ideal solution (NIS)** based on user preferences.
     - For criteria where **lower values are preferable** (e.g., CO₂ or noise levels), the ideal best is defined as the minimum value.
  3. **Closeness Coefficient Calculation**:
     - Computes each room’s distance from the ideal solution to derive a **closeness coefficient**, which is used for ranking.

---

### C. Booking Interface

#### 5. Booking Interface (`booking_interface.py`):
- The **Streamlit interface** collects user details, desired booking times, and room preferences.
- **`fetch_room_ranking`**:
  - Builds the API URL with the appropriate query parameters.
  - Sends a GET request to the decision logic REST API endpoint (**documented with Swagger** for clarity and testing).
- The **ranked list of rooms**, along with their environmental and equipment attributes, is displayed.
- Users can trigger the booking process via a **button** that calls `send_booking`, which **posts booking requests** to the room service.
- **Google Calendar** is displayed on the webpage for an **overview of the booking schedule**.

---

## 3. Why TOPSIS Was Chosen

Several **Multi-Criteria Decision Making (MCDM)** methods were considered (e.g., AHP, ELECTRE, PROMETHEE), but **TOPSIS** was chosen because:

- **Simplicity and Intuitiveness**: Measures **Euclidean distance** to an ideal solution, making ranking intuitive.
- **Computational Efficiency**: Scales well, crucial given the multiple sensor and equipment parameters.
- **Effective Normalization and Weighting**: Handles varying scales by normalizing data and applying weights.
- **Clear Outcome**: Produces a **closeness coefficient**, offering a transparent and interpretable ranking.

---

## 4. Rationale Behind the Weight Selection

Weights in the **TOPSIS** algorithm were chosen based on:

- **Higher Importance of Equipment Data**:
  - Seating capacity, projector, PC, smartboard, and other **physical amenities** were given **higher weights**.
  - These directly impact room **functionality**.
  
- **Sensor Data Considerations**:
  - **VOC levels** are **critical in industrial settings** but less significant in classrooms/offices **as long as they remain compliant**.
  - The **weighting prioritizes comfort and usability**, as these are classrooms.

- **Balanced Decision-Making**:
  - A room is **highly ranked only if**:
    - It meets **functional equipment requirements**.
    - It maintains a **comfortable and compliant environment**.
  - This balance ensures real-world applicability.