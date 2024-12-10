FROM python:3.9-slim

WORKDIR /app

COPY mqtt_simulator.py /app/

RUN pip install paho-mqtt

ENV MQTT_BROKER=mosquitto
ENV MQTT_PORT=1883

CMD ["python", "mqtt_simulator.py"]
