from flask import jsonify
from sqlalchemy.orm import sessionmaker
from ..models import Room, Equipment  # Import the new models
from ..db import engine  # Assuming you have a db.py file for engine setup

# Create a session factory
Session = sessionmaker(bind=engine)

def get_equipment_by_room(room_name):
    session = Session()
    
    # Query the room by name
    room = session.query(Room).filter_by(name=room_name).first()
    
    if not room:
        session.close()
        return jsonify({"error": "Room not found"}), 404

    equipment = {
        "capacity": next((int(eq.value) for eq in room.equipment if eq.name == "capacity"), None),
        "projector": any(eq.name == "projector" and eq.value.lower() == "true" for eq in room.equipment),
        "pc": any(eq.name == "computer_class" and eq.value.lower() == "true" for eq in room.equipment),
        "microphone": any(eq.name == "microphone" and eq.value.lower() == "true" for eq in room.equipment),
        "smartboard": any(eq.name == "smart_board_webex" and eq.value.lower() == "true" for eq in room.equipment),
        "blackboard": any(eq.name == "blackboard" and eq.value.lower() == "true" for eq in room.equipment),
        "whiteboard": any(eq.name == "whiteboard" and eq.value.lower() == "true" for eq in room.equipment),
    }

    session.close()

    return jsonify({
        "room": room.name,
        "equipment": equipment
    })

def get_equipment_all_rooms():
    session = Session()  # Create a session

    rooms = session.query(Room).all()

    rooms_list = []
    for room in rooms:
        room_data = {
            "room": room.name,
            "equipment": {
                "capacity": next((int(eq.value) for eq in room.equipment if eq.name == "capacity"), None),
                "projector": any(eq.name == "projector" and eq.value.lower() == "true" for eq in room.equipment),
                "pc": any(eq.name == "computer_class" and eq.value.lower() == "true" for eq in room.equipment),
                "microphone": any(eq.name == "microphone" and eq.value.lower() == "true" for eq in room.equipment),
                "smartboard": any(eq.name == "smart_board_webex" and eq.value.lower() == "true" for eq in room.equipment),
                "blackboard": any(eq.name == "blackboard" and eq.value.lower() == "true" for eq in room.equipment),
                "whiteboard": any(eq.name == "whiteboard" and eq.value.lower() == "true" for eq in room.equipment),
            }
        }
        rooms_list.append(room_data)

    session.close()  # Close session
    return jsonify(rooms_list)
