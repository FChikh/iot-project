import psycopg2
import json
import os

# Load database credentials from environment variables
DB_NAME = os.getenv("POSTGRES_DB", "rooms_db")
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# Load configuration data
CONFIG_FILE = os.getenv("CONFIG_FILE", "/app/config.json")

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

# Create the rooms table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment (
        id SERIAL PRIMARY KEY,
        room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        value TEXT NOT NULL,
        type TEXT NOT NULL
    )
''')

# Load data from config.json
with open(CONFIG_FILE, 'r') as file:
    data = json.load(file)

# Insert rooms and equipment
for room in data["rooms"]:
    cursor.execute('INSERT INTO rooms (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id', (room["name"],))
    room_id = cursor.fetchone()

    if room_id:
        room_id = room_id[0]
    else:
        cursor.execute('SELECT id FROM rooms WHERE name = %s', (room["name"],))
        room_id = cursor.fetchone()[0]

    for item in room["equipment"]:
        cursor.execute('''
            INSERT INTO equipment (room_id, name, value, type) 
            VALUES (%s, %s, %s, %s) 
            ON CONFLICT DO NOTHING
        ''', (room_id, item["name"], str(item["value"]), item["type"]))

# Commit changes and close
conn.commit()
conn.close()

print("✅ Database initialized from config.json!")