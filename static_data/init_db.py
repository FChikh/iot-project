import os
import json
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Load environment variables
DB_NAME = os.getenv("POSTGRES_DB", "rooms_db")
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
CONFIG_FILE = os.getenv("CONFIG_FILE", "/app/config.json")

# Create the database connection URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize SQLAlchemy
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Define Models
class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    equipment = relationship("Equipment", back_populates="room")

class Equipment(Base):
    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete="CASCADE"))
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)  # Storing all values as strings for flexibility
    type = Column(String, nullable=False)
    room = relationship("Room", back_populates="equipment")

# Create tables in the database
Base.metadata.create_all(engine)

# Load data from config.json
with open(CONFIG_FILE, 'r') as file:
    data = json.load(file)

# Insert data into the database
session = Session()
for room_data in data["rooms"]:
    room = session.query(Room).filter_by(name=room_data["name"]).first()
    
    if not room:
        room = Room(name=room_data["name"])
        session.add(room)
        session.commit()  # Commit to get the room ID

    # Insert equipment for the room
    for eq_data in room_data["equipment"]:
        equipment = Equipment(
            room_id=room.id,
            name=eq_data["name"],
            value=str(eq_data["value"]),
            type=eq_data["type"]
        )
        session.add(equipment)

# Commit all changes
session.commit()
session.close()

print("Database initialized from config.json!")