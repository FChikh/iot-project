# Bridge from Serial port to MQTT publisher

## **Overview**

This module acts as a **bridge** between serial port communication (e.g., with Arduino devices) and MQTT publishing. Its purpose is to enable Arduino-based or similar devices to behave like MQTT publishers by receiving data over serial connections, parsing the data, and transmitting it to an MQTT broker.

The module supports **asynchronous** handling of multiple serial ports and devices simultaneously, ensuring scalability and efficient real-time data transfer. It is designed to work within an IoT architecture that requires sensor data to be transmitted over the MQTT protocol.

The script runs continuously in a loop, actively monitoring for newly connected devices. This design enables the system to dynamically handle multiple Arduino devices simultaneously, rather than being limited to a single device. This approach allows the system to scale efficiently, supporting the extension to several Arduino boards or other compatible devices.

### **Data Flow and Processing**

1. **Device Discovery**  
   The module uses `serial.tools.list_ports` to scan for devices connected to serial ports. It looks for devices with descriptors or names containing **"Arduino," "ttyACM," "usbmodem,"** or **"usbserial."**

2. **Serial Data Handling**  
   - For each detected device, the module starts an asynchronous task to read from the serial port.
   - Incoming data is read line-by-line and expected to be valid JSON. An example JSON payload might look like:
     ```json
     {
         "room": "MSA3500",
         "temp": 22.5,
         "light": 300
     }
     ```
   - The data is parsed, and sensor values are extracted.

3. **MQTT Publishing**  
   - Sensor values are published to MQTT topics using `paho.mqtt.publish.single()`.
   - Example MQTT topics for the data above would be:
     - `room_101/sensors/temp` (with payload `{"value": 22.5, "timestamp": "2025-02-02T14:15:00Z"}`)
     - `room_101/sensors/light` (with payload `{"value": 300, "timestamp": "2025-02-02T14:15:00Z"}`)
   - The **broker address** and **port** are configurable through environment variables:
     - `MQTT_BROKER`: Defaults to `mosquitto`.
     - `MQTT_PORT`: Defaults to `1883`.


### Technical Implementation

- **AsyncIO**: Enables asynchronous handling of multiple serial devices.
- **Serial Communication** (`serial_asyncio`, `serial.tools.list_ports`):  
   Used to scan for and read data from serial devices.
- **MQTT** (`paho.mqtt`): Handles communication with the MQTT broker.
- **JSON**: Data format for sensor messages.
