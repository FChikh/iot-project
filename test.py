import sqlite3
import json

# Define the database path (update as needed)
db_path = "./static_data/rooms.db"

def get_equipment_by_room(room_id):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to get room details by ID
    cursor.execute('''
        SELECT name, capacity, projector, pc_count, computer_class, 
               microphone, smart_board_webex, blackboard, whiteboard
        FROM rooms WHERE name = ?
    ''', (room_id,))

    # Fetch the room data
    row = cursor.fetchone()
    
    # Close the connection
    conn.close()

    # If the room does not exist, return an error message
    if row is None:
        return json.dumps({"error": "Room not found"})

    # Map database fields to JSON keys
    room_name, capacity, projector, pc_count, computer_class, microphone, smart_board, blackboard, whiteboard = row

    # Construct the JSON response
    response = {
        "equipment": {
            "blackboard": bool(blackboard),
            "capacity": capacity,
            "computer-class": bool(computer_class),
            "microphone": bool(microphone),
            "pc": pc_count is not None and pc_count > 0,
            "projector": bool(projector),
            "smartboard": bool(smart_board),
            "whiteboard": bool(whiteboard)
        },
        "room": room_name
    }

    return json.dumps(response, indent=2)



def get_equipment_all_rooms():
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to get all room details
    cursor.execute('''
        SELECT name, capacity, projector, pc_count, computer_class, 
               microphone, smart_board_webex, blackboard, whiteboard
        FROM rooms
    ''')

    # Fetch all rows
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    # Process each row and construct the JSON list
    rooms_list = []
    for row in rows:
        room_name, capacity, projector, pc_count, computer_class, microphone, smart_board, blackboard, whiteboard = row
        
        room_data = {
            "equipment": {
                "blackboard": bool(blackboard),
                "capacity": capacity,
                "computer-class": bool(computer_class),
                "microphone": bool(microphone),
                "pc": pc_count is not None and pc_count > 0,
                "projector": bool(projector),
                "smartboard": bool(smart_board),
                "whiteboard": bool(whiteboard)
            },
            "room": room_name
        }

        rooms_list.append(room_data)

    return json.dumps(rooms_list, indent=2)


# print(get_equipment_all_rooms())
print(get_equipment_by_room("Room_1"))

