import asyncio
import json
import serial
import serial_asyncio
import serial.tools.list_ports
import paho.mqtt.client as mqtt
import logging
import os

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

# Initialize MQTT client
client = mqtt.Client()

def connect_mqtt():
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}: {e}")
        # Schedule reconnection
        asyncio.get_event_loop().call_later(RECONNECT_INTERVAL, connect_mqtt)

connect_mqtt()

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
                    temp_topic = f"{room}/temp"
                    light_topic = f"{room}/light"

                    client.publish(temp_topic, temp)
                    client.publish(light_topic, light)
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
    if room:
        # Optionally, log room disconnection
        logger.info(f"Disconnected from {room} on port {port}")
    else:
        logger.info(f"Disconnected from port {port} with unknown room")

    logger.info(f"Reconnecting to {port} in {RECONNECT_INTERVAL} seconds...")
    await asyncio.sleep(RECONNECT_INTERVAL)
    # Attempt to reconnect by restarting the read_from_serial coroutine
    asyncio.create_task(read_from_serial(port))

async def monitor_devices():
    while True:
        logger.info("New scan")
        # Scan for connected Arduinos
        ports = serial.tools.list_ports.comports()
        logger.info(f'Ports: {[port.device for port in ports]}')
        connected_ports = set()
        for p in ports:
            if ('Arduino' in p.description or 
                'ttyACM' in p.device or 
                'usbmodem' in p.device or 
                'usbserial' in p.device):
                port = p.device
                connected_ports.add(port)
                if port not in active_ports and port not in active_tasks:
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
        client.disconnect()
