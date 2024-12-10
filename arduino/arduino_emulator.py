import serial
import time
import json
import random
import argparse


def emulate_arduino(port, room):
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        print(f"Emulator connected to {port} as {room}")
    except serial.SerialException as e:
        print(f"Failed to open port {port}: {e}")
        return

    try:
        while True:
            # Generate random sensor values
            temperature = round(random.uniform(20.0, 30.0), 2)  # Celsius
            light = random.randint(300, 800)  # Arbitrary light sensor value

            # Create JSON data
            data = {
                "room": room,
                "temp": temperature,
                "light": light
            }

            # Send JSON data over serial
            ser.write((json.dumps(data) + "\n").encode('utf-8'))
            print(f"Emulator {room} sent: {data}")

            time.sleep(0.5)  # 500ms delay
    except KeyboardInterrupt:
        print(f"Emulator {room} disconnected.")
    finally:
        ser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Arduino Emulator')
    parser.add_argument('--port', type=str, required=True,
                        help='Serial port to emulate')
    parser.add_argument('--room', type=str, required=True,
                        help='Room identifier')
    args = parser.parse_args()

    emulate_arduino(args.port, args.room)
