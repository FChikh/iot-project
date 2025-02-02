import os
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Room, Equipment, Sensor 
from db import engine

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
CONFIG_FILE = os.getenv("CONFIG_FILE", "/app/config.json")

with open(CONFIG_FILE, 'r') as file:
    data = json.load(file)

session = Session()
for room_data in data["rooms"]:
    room = session.query(Room).filter_by(name=room_data["name"]).first()
    
    if not room:
        room = Room(name=room_data["name"])
        session.add(room)
        session.commit()  

    for eq_data in room_data["equipment"]:
        existing_equipment = session.query(Equipment).filter(
            Equipment.room_id == room.id,
            Equipment.name == eq_data["name"]
        ).first()
        
        if existing_equipment:
            continue
        equipment = Equipment(
            room_id=room.id,
            name=eq_data["name"],
            value=str(eq_data["value"]),
            type=eq_data["type"]
        )
        session.add(equipment)
        
    for sensor_data in room_data["sensors"]:
        existing_sensor = session.query(Sensor).filter(
            Sensor.room_id == room.id,
            Sensor.name == sensor_data["name"]
        ).first()
        
        if existing_sensor:
            existing_sensor.min_value = sensor_data["range"][0]
            existing_sensor.max_value = sensor_data["range"][1]
            continue
        sensor = Sensor(
            room_id=room.id,
            name=sensor_data["name"],
            min_value=sensor_data["range"][0],
            max_value=sensor_data["range"][1]
        )
        session.add(sensor)

session.commit()
session.close()

print("Database initialized from config.json!")
