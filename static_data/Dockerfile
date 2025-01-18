FROM python:3.9-slim

WORKDIR /app

COPY . .

# Install necessary Python dependencies (if any other than sqlite3)
RUN pip install --no-cache-dir -r requirements.txt || true

CMD ["python", "init_db.py"]