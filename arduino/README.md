# Arduino Device as an IoT Data Collector

As part of the project, an **Arduino Uno R3** was provided to demonstrate the integration of IoT devices in a sensor network. This microcontroller serves as a **data collector**, capable of connecting to sensors from the **GroVe starter kit**. While the device was useful as a proof-of-concept, certain limitations and challenges influenced its role in the project.


### Device Overview

The **Arduino Uno R3** is a basic microcontroller that supports analog and digital sensor inputs. However, it lacks built-in Wi-Fi or other direct networking capabilities, making it difficult to connect to **MQTT** or other IoT protocols without additional hardware.

### Challenges Encountered

1. **Sensor Applicability and Calibration**  
   Many sensors in the GroVe kit did not fully align with the requirements of the project. Moreover, some sensors returned **relative** rather than **absolute** values, making them unsuitable for real-world measurements without calibration. We would like to thank Henrik Klasen from Group 6 who conducted extensive research on sensor calibration and shared his findings, which was greatly appreciated. However, due to time and scope constraints, we opted to focus on building a **proof-of-concept** rather than implementing precise calibrations.

2. **Communication with MQTT**  
   Due to the absence of Wi-Fi or Ethernet capabilities, direct communication between the Arduino and the MQTT broker was not possible. Instead, we implemented a **serial communication bridge**:
   - The Arduino sends sensor data via **USB serial connection**.
   - A **serial-to-MQTT bridge script** on the host machine reads this data and publishes it to the MQTT broker.


### Demonstration Setup

For the proof-of-concept, we connected:
- **Temperature sensor** (analog input)
- **Light sensor** (analog input)
- **LCD Display** (for real-time feedback)

The Arduino reads data from the sensors, performs basic calibration, and outputs both sensor values to the serial port as a **JSON object**. Additionally, the data is displayed on the attached screen.

### Data Flow Overview

1. **Arduino** collects sensor data and sends it to the **serial port**.
2. The **Serial-to-MQTT Bridge Script** (running on the host machine) reads the data, parses it, and publishes it to the MQTT broker (see: *Bridge from Serial Port to MQTT Publisher*).
3. Other IoT components can then subscribe to the relevant MQTT topics to receive real-time sensor data.

