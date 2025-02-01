import os
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Room, Equipment  

DB_NAME = os.getenv("POSTGRES_DB", "rooms_db")
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
CONFIG_FILE = os.getenv("CONFIG_FILE", "/app/config.json")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

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
        equipment = Equipment(
            room_id=room.id,
            name=eq_data["name"],
            value=str(eq_data["value"]),
            type=eq_data["type"]
        )
        session.add(equipment)

session.commit()
session.close()

print("Database initialized from config.json!")