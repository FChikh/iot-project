FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir influxdb-client
CMD ["python", "sensor_simulation.py"]
