import paho.mqtt.client as mqtt
import asyncio
import json
import random
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MQTT settings
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
CONTROL_TOPIC = 'control/simulator'

class Simulator:
    def __init__(self, broker, port):
        self.broker = broker
        self.port = port
        self.devices = {}  # key: room, value: Device
        self.client = mqtt.Client()
        self.loop = asyncio.get_event_loop()

    def start(self):
        # Setup MQTT callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Connect to MQTT broker
        try:
            self.client.connect(self.broker, self.port, 60)
        except Exception as e:
            logger.error(f"Could not connect to MQTT Broker: {e}")
            return

        self.client.loop_start()

        # Start asyncio loop
        try:
            self.loop.run_until_complete(self.main())
        except KeyboardInterrupt:
            logger.info("Simulator shutting down.")
            self.loop.run_until_complete(self.shutdown())

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Simulator connected to MQTT broker.")
            # Subscribe to control topic
            client.subscribe(CONTROL_TOPIC + '/#')
        else:
            logger.error(f"Simulator failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        # Parse control messages
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        logger.info(f"Received control message on {topic}: {payload}")
        try:
            message = json.loads(payload)
            action = message.get('action')
            room = message.get('room')
            if not room:
                logger.error("No 'room' key in control message.")
                return

            if action == 'add':
                if room not in self.devices:
                    asyncio.run_coroutine_threadsafe(self.add_device(room), self.loop)
            elif action == 'remove':
                if room in self.devices:
                    asyncio.run_coroutine_threadsafe(self.remove_device(room), self.loop)
            elif action == 'update':
                temp_range = message.get('temp_range')
                light_range = message.get('light_range')
                if room in self.devices:
                    asyncio.run_coroutine_threadsafe(self.update_device(room, temp_range, light_range), self.loop)
            else:
                logger.warning(f"Unknown action: {action}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in control message: {e}")

    async def add_device(self, room):
        logger.info(f"Adding device for {room}")
        device = Device(room, self.client)
        self.devices[room] = device
        await device.start()

    async def remove_device(self, room):
        logger.info(f"Removing device for {room}")
        device = self.devices.pop(room, None)
        if device:
            await device.stop()

    async def update_device(self, room, temp_range, light_range):
        logger.info(f"Updating device {room} with temp_range {temp_range} and light_range {light_range}")
        device = self.devices.get(room)
        if device:
            if temp_range:
                device.set_temp_range(temp_range)
            if light_range:
                device.set_light_range(light_range)

    async def main(self):
        # Keep the program running
        while True:
            await asyncio.sleep(1)

    async def shutdown(self):
        # Stop all devices
        for room in list(self.devices.keys()):
            await self.remove_device(room)
        self.client.loop_stop()
        self.client.disconnect()

class Device:
    def __init__(self, room, mqtt_client):
        self.room = room
        self.client = mqtt_client
        self.task = None
        # Default sensor ranges
        self.temp_min = 20.0
        self.temp_max = 30.0
        self.light_min = 300
        self.light_max = 800
        self.active = True

    def set_temp_range(self, temp_range):
        if isinstance(temp_range, list) and len(temp_range) == 2:
            self.temp_min, self.temp_max = temp_range
            logger.info(f"{self.room}: Temperature range set to {self.temp_min} - {self.temp_max} °C")

    def set_light_range(self, light_range):
        if isinstance(light_range, list) and len(light_range) == 2:
            self.light_min, self.light_max = light_range
            logger.info(f"{self.room}: Light range set to {self.light_min} - {self.light_max}")

    async def start(self):
        self.task = asyncio.create_task(self.run())

    async def stop(self):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                logger.info(f"Device {self.room} simulation cancelled.")

    async def run(self):
        """Simulate sensor data for the device."""
        try:
            while True:
                # Generate random sensor data within the specified ranges
                temperature = round(random.uniform(self.temp_min, self.temp_max), 2)  # Celsius
                light = random.randint(self.light_min, self.light_max)  # Arbitrary light sensor value

                # Publish to MQTT topics
                temp_topic = f"{self.room}/temp"
                light_topic = f"{self.room}/light"

                self.client.publish(temp_topic, temperature)
                self.client.publish(light_topic, light)

                logger.info(f"Published to {temp_topic}: {temperature}")
                logger.info(f"Published to {light_topic}: {light}")

                await asyncio.sleep(0.5)  # 500ms interval
        except asyncio.CancelledError:
            logger.info(f"Device {self.room} simulation stopped.")
        except Exception as e:
            logger.error(f"Error in device {self.room} simulation: {e}")

if __name__ == "__main__":
    simulator = Simulator(MQTT_BROKER, MQTT_PORT)
    simulator.start()
