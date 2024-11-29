FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY serial_to_mqtt.py ./

CMD ["python", "serial_to_mqtt.py"]
