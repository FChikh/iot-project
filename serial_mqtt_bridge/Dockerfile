FROM python:3.9-slim

WORKDIR /app

COPY serial_to_mqtt.py /app/
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    libudev1 \
    && rm -rf /var/lib/apt/lists/*

CMD ["python", "serial_to_mqtt.py"]
