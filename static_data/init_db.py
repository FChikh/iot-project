import sqlite3
import os

# Get the current working directory (where the script is running)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the full path for the database file
db_path = os.path.join(script_dir, "rooms.db")

# Print the database path for debugging
print(f"Database will be created at: {db_path}")

# Create a connection to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the rooms table
cursor.execute('''
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    projector BOOLEAN NOT NULL,
    pc_count INTEGER,
    computer_class BOOLEAN,
    microphone BOOLEAN,
    smart_board_webex BOOLEAN,
    blackboard BOOLEAN,
    whiteboard BOOLEAN
)
''')

# Insert room data
rooms = [
    ("Room_1", 62, True, None, False, False, False, True, True),
    ("Room_2", 23, True, 20, True, False, False, False, True),
    ("Room_3", 30, True, 10, True, True, False, True, False),
    ("Room_4", 12, False, None, False, False, False, False, True),
    ("Room_5", 40, True, 25, True, True, True, True, False)
]

cursor.executemany('''
INSERT INTO rooms (name, capacity, projector, pc_count, computer_class, microphone, smart_board_webex, blackboard, whiteboard)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', rooms)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database initialized and populated!")