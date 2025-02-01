import sqlite3
import json
from flask import jsonify

# The path inside the shared volume
db_path = "/app/rooms.db"


def get_equipment_by_room(room_id):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT name, capacity, projector, pc_count, computer_class, 
               microphone, smart_board_webex, blackboard, whiteboard
        FROM rooms WHERE name = ?
    ''', (room_id,))

    row = cursor.fetchone()
    
    conn.close()

    if row is None:
        return json.dumps({"error": "Room not found"})

    room_name, capacity, projector, pc_count, computer_class, microphone, smart_board, blackboard, whiteboard = row

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

    return jsonify(response)


def get_equipment_all_rooms():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT name, capacity, projector, pc_count, computer_class, 
               microphone, smart_board_webex, blackboard, whiteboard
        FROM rooms
    ''')

    rows = cursor.fetchall()

    conn.close()

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

    return jsonify(rooms_list)






