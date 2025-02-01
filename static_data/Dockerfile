FROM python:3.9-slim

WORKDIR /app

# Install dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev musl-dev

# Copy only requirements first to leverage Docker cache
COPY static_data/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire static_data folder
COPY static_data/init_db.py /app/init_db.py

# Copy models.py and config.json from the root of the project
COPY --from=configs models.py /app/models.py
COPY --from=configs config.json /app/config.json

CMD ["python", "/app/init_db.py"]
