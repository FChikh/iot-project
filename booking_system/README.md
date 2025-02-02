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
- Added tolerances to compliances, because of possible outliers due to faulty sensor measurements

##### Compliance Standards:
1. **CO₂**: [German Committee on Indoor Air Guide Values](https://www.umweltbundesamt.de/en/topics/health/commissions-working-groups/german-committee-on-indoor-air-guide-values#german-committee-on-indoor-air-guide-values-air)
  - Good air quality: CO2 levels < 1000 ppm.
  - Acceptable threshold: CO2 levels should not exceed 1500 ppm.
2. **PM2.5 & PM10**: [EU Air Quality Standards](https://environment.ec.europa.eu/topics/air/air-quality/eu-air-quality-standards_en)
  - PM2.5: 24-hour average should not exceed 25 µg/m^3.
  - PM10: 24-hour average should not exceed 50 µg/m^3.
3. **Acoustic**: EN ISO 3382-2:2008
  - Noise Limit: 85dB.
4. **Light**: EN 12464-1
  - Minimum Light Intensity: 500 lux.
5. **Humidity**: EN ISO 773
  - Minimum Humidity: 30%
  - Maximum Humidity: 70%
6. **VOC**: [German Umweltbundesamt](https://www.umweltbundesamt.de/sites/default/files/medien/4031/dokumente/agbb_evaluation_scheme_2024.pdf)
  - VOC Limit: 400 ppb
7. **Temperature**: According to German ASR (Arbeitsstätten Regeln), an office workspace should have a minimum temperature of 19°C and a maximum temperature of 26°C (without ventilation/AC).
  - Minimum Temperature 19°C
  - Maximum Temperature 26°C

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
- **Detailed TOPSIS Theory (as Implemented in `topsis_decision_logic`): The TOPSIS method used in the system works as follows:

1. **Preference Adjustment (Z-Score Transformation):**
   - **Objective:** Transform raw sensor data by comparing each attribute value against the user’s preferred value.
   - **Method:**  
     For each attribute with a user preference:
     ```math
     \text{adjusted value} = -\left|\frac{x - \text{user\_pref}}{\sigma}\right|
     ```
     - Here, \(x\) is the room's actual sensor reading, \(\text{user\_pref}\) is the target value, and \(\sigma\) is the standard deviation of the attribute across all rooms.
     - This transformation ensures that values closer to the user’s preference yield a higher (less negative) score.

2. **Normalization:**
   - **Objective:** Ensure that all attributes are on the same scale regardless of their original units or ranges.
   - **Method:**  
     Normalize each column (attribute) using the Euclidean norm:
     ```math
     V_{ij} = \frac{X_{ij}}{\sqrt{\sum X_{ij}^2}}
     ```
     This scales the data so that each attribute has values between 0 and 1, making them directly comparable.

3. **Weighting:**
   - **Objective:** Reflect the relative importance of each attribute.
   - **Method:**  
     Multiply each normalized attribute by its corresponding weight. If no weights are provided, equal weight is assumed for all attributes.

4. **Determination of Ideal and Negative-Ideal Solutions:**
   - **Objective:** Establish reference points against which each room is evaluated.
   - **Method:**  
     - **Positive Ideal Solution (PIS)**: The best possible attribute values. For attributes where higher is better, this is the maximum value; for attributes where lower is better (like CO₂ or noise), it is the minimum value.
     - **Negative Ideal Solution (NIS)**: The worst possible attribute values. For higher-is-better attributes, this is the minimum value; for lower-is-better attributes, it is the maximum value.
    

5. **Calculation of Euclidean Distances:**
   - **Objective:** Measure the distance of each room’s performance from the ideal and negative-ideal solutions.
   - **Method:**  
     Calculate the Euclidean distance to both the PIS and NIS:
     ```math
     D_i^+ = \sqrt{\sum (V_{ij} - A^+_j)^2} \quad \text{and} \quad D_i^- = \sqrt{\sum (V_{ij} - A^-_j)^2}
     ```

6. **Closeness Coefficient and Ranking:**
   - **Objective:** Quantify how close each room is to the ideal solution.
   - **Method:**  
     Compute the closeness coefficient:
     ```math
     C_i = \frac{D_i^-}{D_i^+ + D_i^-}
     ```
     Rooms are then ranked based on \(C_i\) in descending order, where a higher value indicates a better match to the user’s requirements.


### C. Booking Interface

#### 5. Booking Interface (`booking_interface.py`):
- The **Streamlit interface** collects user details, desired booking times, and room preferences. It uses natural language for the selection of the sensor data preferences as the user can interpret them better than the actual values. 
- **`fetch_room_ranking`**: This function builds the API URL with the appropriate query parameters and sends a GET request to the decision logic REST API endpoint. The endpoint is documented with Swagger for clarity and ease of testing.
- The **ranked list of rooms**, along with their environmental and equipment attributes, is then displayed. Users can select a room from the ranked list that they prefer and trigger the booking process via a button that calls `send_booking`, which posts booking requests to the room service.
- The **Google Calendar** is displayed on the webpage to provide an overview of the booking schedule.

## 3. Why TOPSIS Was Chosen
Several Multi-Criteria Decision Making (MCDM) methods are available (such as AHP, ELECTRE, and PROMETHEE), but **TOPSIS was selected** for this system because:

- **Simplicity and Intuitiveness**: TOPSIS is straightforward to implement and understand. By measuring the Euclidean distance to an ideal solution, it allows for an intuitive ranking of alternatives.
- **Computational Efficiency**: The method scales well and is efficient, which is crucial given the multiple sensor and equipment parameters involved.
- **Effective Normalization and Weighting**: TOPSIS easily accommodates varying scales by normalizing data and applying weights. This is essential when combining continuous sensor data with binary equipment data.
- **Clear Outcome**: The algorithm produces a **closeness coefficient** for each room, allowing for a transparent and interpretable rank order based on both environmental and equipment criteria.

## 4. Motivation Behind the Weight Selection
The weights in the TOPSIS algorithm were carefully chosen based on the following priorities:

- **Higher Importance of Equipment Data if selected**:
  - Equipment features such as projector availability, PC, smartboard, and other amenities were given **higher weights**. This is because the physical and functional aspects of a room are critical to its suitability for booking. Seating capacity got a high weight, so that rooms with higher capacities than needed are ranked lower.

- **Sensor Data Considerations**:
  - **VOC levels** are critical in industrial settings or newly renovated spaces with strong off-gassing, but in typical classrooms/offices they are **less critical** as long as they stay within the compliance range. The weighting is chosen to prioritize **comfort and usability**, as these are classrooms.

- **Balanced Decision-Making**:
  - This weighting strategy ensures that a room is only **highly ranked** if it meets both the **functional equipment requirements** and maintains a **comfortable, compliant environment**. This balance is key to matching real-world needs.
