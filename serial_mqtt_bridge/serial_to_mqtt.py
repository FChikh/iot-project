import asyncio
import json
import serial
import serial_asyncio
import serial.tools.list_ports
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import logging
import os
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MQTT broker settings (use environment variables with defaults)
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')  # Docker service name
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))

# Reconnection parameters
SCAN_INTERVAL = 5  # Seconds between scans for new devices
RECONNECT_INTERVAL = 5  # Seconds between reconnection attempts

# Keep track of active tasks and ports
active_tasks = {}
active_ports = {}


async def read_from_serial(port):
    room = None
    try:
        reader, _ = await serial_asyncio.open_serial_connection(url=port, baudrate=9600)
        logger.info(f"Connected to {port}")
        active_ports[port] = True
        while True:
            try:
                line = await reader.readline()
                if not line:
                    # EOF reached
                    raise serial.SerialException("EOF reached")
                data = line.decode('utf-8').strip()
                logger.debug(f"Received from {port}: {data}")

                # Parse the JSON data
                try:
                    data_dict = json.loads(data)
                    room = data_dict.get('room')
                    temp = data_dict.get('temp')
                    light = data_dict.get('light')

                    if not room:
                        logger.error(f"No 'room' key in data from {port}: {data}")
                        continue

                    # Publish to MQTT topics with room identifier
                    temp_topic = f"{room}/sensors/temp"
                    light_topic = f"{room}/sensors/light"
                    

                    # Generate timestamp (ISO 8601)
                    timestamp = time.strftime(
                        "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    
                    # Publish to MQTT topics
                    msg_temp = publish.single(temp_topic, payload=
                        json.dumps({"value": temp, "timestamp": timestamp}), hostname=MQTT_BROKER, port=MQTT_PORT, qos=1)
                    msg_light = publish.single(light_topic, payload=
                        json.dumps({"value": light, "timestamp": timestamp}), hostname=MQTT_BROKER, port=MQTT_PORT, qos=1)

                    print(msg_temp)
                    print(msg_light)
                    logger.info(f"Published to {temp_topic}: {temp}")
                    logger.info(f"Published to {light_topic}: {light}")

                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error on {port}: {e}")
                except KeyError as e:
                    logger.error(f"Missing key in data on {port}: {e}")

            except Exception as e:
                logger.error(f"Error reading from {port}: {e}")
                break  # Exit reading loop to reconnect
    except (serial.SerialException, OSError) as e:
        logger.error(f"Could not open serial port {port}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error on {port}: {e}")

    # Clean up after disconnect
    active_ports.pop(port, None)
    active_tasks.pop(port, None)
    if room:
        # Optionally, log room disconnection
        logger.info(f"Disconnected from {room} on port {port}")
    else:
        logger.info(f"Disconnected from port {port} with unknown room")


async def monitor_devices():
    while True:
        logger.info("New scan")
        # Scan for connected Arduinos
        ports = serial.tools.list_ports.comports()
        logger.info(f'Ports: {[port.device for port in ports]}')
        logger.info(f"Active ports: {active_ports.keys()}")
        logger.info(f"Active tasks: {active_tasks.keys()}")
        connected_ports = set()
        for p in ports:
            if ('Arduino' in p.description or
                'ttyACM' in p.device or
                'usbmodem' in p.device or
                    'usbserial' in p.device):
                
                port = p.device
                connected_ports.add(port)
                
                if port not in active_ports and port not in active_tasks:
                    logger.info(f"Port {port} connected")
                    # Start reading from the new serial port
                    task = asyncio.create_task(read_from_serial(port))
                    active_tasks[port] = task

        # Find ports that are no longer connected
        disconnected_ports = set(active_ports.keys()) - connected_ports
        for port in disconnected_ports:
            logger.info(f"Port {port} disconnected")
            task = active_tasks.pop(port, None)
            if task:
                task.cancel()
            active_ports.pop(port, None)

        await asyncio.sleep(SCAN_INTERVAL)


async def main():
    await monitor_devices()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Exiting...")
