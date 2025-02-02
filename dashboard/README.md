# **Dashboard for Equipment and Sensor Simulation**

## Overview

This module is designed to manage and monitor room equipment while simulating sensor device behavior in an IoT environment. The main objective is to simulate real-world conditions, enabling testing and validation of other project components for feasibility and applicability. It offers both API and Streamlit-based user interfaces to handle room data and equipment information, structured into several submodules:

### Sensor Simulator

The Sensor Simulator is responsible for emulating sensor devices. Originally, the project required integration with Arduino-based devices to measure room conditions. However, due to hardware constraints, we developed a simulation framework that generates sensor data based on predefined decision logic. The simulated data mimics real-world conditions for the following parameters:
- Temperature  
- Humidity  
- Light intensity  
- CO₂ levels  
- PM2.5 and PM10 particle concentrations  
- VOC (Volatile Organic Compounds) levels  

#### How It Works
- **Multithreading**: Each simulated device runs asynchronously on its own thread to enable concurrent sensor operations.
- **Configuration**: Initial parameters for the simulations are retrieved from a PostgreSQL database through an auxiliary REST API (described below).
- **Data Transmission**: Simulated data is published to a `mosquitto` MQTT broker, mimicking how physical microcontrollers or embedded systems would transmit real sensor data. 

#### Why MQTT?
MQTT was chosen for its efficient **publish-subscribe (Pub-Sub)** architecture, which excels in real-time, frequent data updates across multiple devices. This makes it ideal for IoT environments.

**Topic convention:**  
`{room_id}/sensors/{sensor_name}`

For testing and demonstration purposes, the sensor data refresh rate is set to **10 seconds**.

#### Simulation logic

Each sensor's data is generated as follows:

- **Gaussian Distribution**:
    - The sensor value is generated using a Gaussian (normal) distribution.
    - The **mean** is the midpoint of the sensor's configured range, calculated by `mean(ranges['sensor_type'])`.
    - The **standard deviation (sigma)** is one-sixth of the range (`sigma_3()`), ensuring most values stay within the range.

- **Cosine Adjustment**:
    - For certain sensors, an additional time-based cosine adjustment is applied to mimic natural daily variations:
    - Temperature decreases at night and peaks during the day.
    - Light intensity peaks during the day and drops at night.
    - Other sensors have similar behavior to reflect environmental changes. This is just our assumptions about the natural behaviour, to provide a demonstration.
    ```python
    temp += -1.5 * cos((hour - 1) / 12 * pi)
    ```

##### **Example Sensor Logic**
```python
if 'temp' in ranges:
    temp = round(random.gauss(mean(ranges['temp']), sigma_3(ranges['temp'])), 2)
    temp += -1.5 * cos((hour - 1) / 12 * pi)
```


#### User Interface
The simulator's interface is built using the **Streamlit** framework, which offers a lightweight, intuitive solution for data visualization and control. The backend REST API provides access to the data stored in the hosted database, ensuring real-time updates and easy configurability.

### Equipment Editor

In addition to dynamic sensor data, each room is associated with static equipment and parameters. Examples include:
- Number of available seats  
- Blackboard and whiteboard availability  
- Microphones  
- Smart systems for Webex meetings  
- Projectors  
- PCs for students  

This equipment information is stored in a PostgreSQL database. Since changes (e.g., repairs, replacements, or technical issues) may require updates to the data, a management dashboard has been implemented to facilitate these modifications.

#### User Interface
- The equipment editor is also built using the **Streamlit** framework, offering an easy-to-use interface for administrators and technicians to update room equipment records.
- Data is retrieved and updated through the same REST API used by other components, ensuring consistency across the system.

---

### REST API for Database Management

The REST API serves as a critical interface between the PostgreSQL database and the visual components of the simulation module. It supports standard **CRUD (Create, Read, Update, Delete)** operations and can be extended to handle additional IoT components in the future. 

The API was designed to allow multiple interface options, enabling administrators to choose between different frontend solutions depending on their needs. 

#### Technical Implementation
- The API is built with **Flask**, selected for its simplicity and lightweight nature, which suits small-to-medium-scale web services.
- **SQLAlchemy**, a popular Python ORM (Object-Relational Mapper), is used to interact with the PostgreSQL database, providing efficient and maintainable database management.
