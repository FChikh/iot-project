import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL 
from sqlalchemy.orm import sessionmaker
from models import Base, Room, Equipment, Sensor
import threading
import logging

from simulator import simulator, global_config, active_simulators, simulator_threads

logger = logging.getLogger(__name__)

postgres_user = os.getenv("POSTGRES_USER", "user")
postgres_password = os.getenv("POSTGRES_PASSWORD", "password")
postgres_db = os.getenv("POSTGRES_DB", "rooms_db")
postgres_host = os.getenv("POSTGRES_HOST", "postgres")
postgres_port = os.getenv("POSTGRES_PORT", "5432")

# Construct the connection URL.
db_url = URL.create(
    drivername="postgresql",
    username=postgres_user,
    password=postgres_password,
    host=postgres_host,
    port=postgres_port,
    database=postgres_db
)

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)



# Helper functions for simulator management (with DB updates)
def add_simulator(room, sensor_ranges):
    """
    Add a simulator for the given room by:
      1. Inserting a new Room and corresponding Sensor rows into the DB.
      2. Updating the in-memory global_config and starting a simulator thread.
    """
    if room in active_simulators:
        return False, "Simulator already active."

    # Update in-memory configuration.
    global_config[room] = sensor_ranges.copy()

    # Insert into the DB.
    db_session = SessionLocal()
    try:
        # Check if the room already exists.
        room_instance = db_session.query(
            Room).filter(Room.name == room).first()
        if room_instance:
            # check if sensors already exist
            existing_sensors = db_session.query(Sensor).filter(
                Sensor.room_id == room_instance.id
            ).all()
            if existing_sensors:
                return False, f"Room '{room}' already has sensors."
        else:
            room_instance = Room(name=room)
            db_session.add(room_instance)
            db_session.flush()  # Get new_room.id

        # Add sensor configuration rows.
        for sensor_name, range_vals in sensor_ranges.items():
            new_sensor = Sensor(room_id=room_instance.id, name=sensor_name,
                                min_value=range_vals[0], max_value=range_vals[1])
            db_session.add(new_sensor)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        logger.error(f"DB error adding simulator for {room}: {e}")
        return False, f"DB error adding simulator: {e}"
    finally:
        db_session.close()

    # Start simulator thread.
    stop_event = threading.Event()
    simulator_threads[room] = {
        'ranges': sensor_ranges.copy(),
        'stop_event': stop_event
    }
    thread = threading.Thread(target=simulator, args=(
        room, simulator_threads[room], stop_event), daemon=True)
    thread.start()
    simulator_threads[room]['thread'] = thread
    active_simulators.add(room)
    logger.info(f"Simulator for {room} added.")
    return True, f"Simulator for {room} added."


def update_simulator(room, new_ranges):
    """
    Update the simulator configuration both in memory and in the DB.
    """
    if room not in active_simulators:
        return False, "Simulator not active."

    global_config[room] = new_ranges.copy()
    if room in simulator_threads:
        simulator_threads[room]['ranges'] = new_ranges.copy()

    # Update the DB.
    db_session = SessionLocal()
    try:
        room_record = db_session.query(Room).filter(Room.name == room).first()
        if not room_record:
            return False, f"Room {room} not found in DB."
        # For each sensor in new_ranges, update if exists; otherwise, add it.
        for sensor_name, range_vals in new_ranges.items():
            sensor_record = db_session.query(Sensor).filter(
                Sensor.room_id == room_record.id,
                Sensor.name == sensor_name
            ).first()
            if sensor_record:
                sensor_record.min_value = range_vals[0]
                sensor_record.max_value = range_vals[1]
            else:
                new_sensor = Sensor(room_id=room_record.id, name=sensor_name,
                                    min_value=range_vals[0], max_value=range_vals[1])
                db_session.add(new_sensor)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        logger.error(f"DB error updating simulator for {room}: {e}")
        return False, f"DB error updating simulator: {e}"
    finally:
        db_session.close()

    logger.info(f"Simulator for {room} updated.")
    return True, f"Simulator for {room} updated."


def remove_simulator(room):
    """
    Remove the simulator from memory and delete the corresponding Room (and cascade delete Sensors) from the DB.
    """
    if room not in active_simulators:
        return False, "Simulator not active."

    if room in simulator_threads:
        simulator_threads[room]['stop_event'].set()
        simulator_threads[room]['thread'].join(timeout=2)
        del simulator_threads[room]
    active_simulators.discard(room)
    if room in global_config:
        del global_config[room]

    # Remove from the DB.
    db_session = SessionLocal()
    try:
        room_record = db_session.query(Room).filter(Room.name == room).first()
        if not room_record:
            return False, f"Room '{room}' not found in DB."
        sensor_list = db_session.query(Sensor).filter(
            Sensor.room_id == room_record.id
        ).all()
        for eq in sensor_list:
            db_session.delete(eq)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        logger.error(f"DB error removing simulator for {room}: {e}")
        return False, f"DB error removing simulator: {e}"
    finally:
        db_session.close()

    logger.info(f"Simulator for {room} removed.")
    return True, f"Simulator for {room} removed."

def get_rooms():
    """
    Retrieve all room names from the database.
    Returns a list of room names.
    """
    db_session = SessionLocal()
    try:
        rooms = db_session.query(Room).all()
        return {'rooms': [room.name for room in rooms]}
    except Exception as e:
        logger.error(f"Error retrieving room names: {e}")
        return []
    finally:
        db_session.close()

# Helper functions for equipment management (with DB updates)
def get_equipment_for_room(room):
    """
    Retrieve the equipment list for the specified room from the database.
    Returns a dict of the form {"room": room, "equipment": [...]} if found,
    or None if the room does not exist.
    Raises an exception on other errors.
    """
    db_session = SessionLocal()
    try:
        room_record = db_session.query(Room).filter(Room.name == room).first()
        if not room_record:
            return None
        equipment_list = db_session.query(Equipment).filter(
            Equipment.room_id == room_record.id
        ).all()
        result = []
        for eq in equipment_list:
            result.append({
                "id": eq.id,
                "name": eq.name,
                "value": eq.value,
                "type": eq.type
            })
        return {"room": room, "equipment": result}
    except Exception as e:
        logger.error(f"Error retrieving equipment for room {room}: {e}")
        raise  # Let the caller handle the exception.
    finally:
        db_session.close()


def add_equipment_for_room(room, equipment_list):
    """
    Add equipment records for the given room.
    - Looks up the room by name.
    - For each equipment item in equipment_list (a list of dicts with keys "name", "value", "type"):
        - If an equipment record with the same name for that room already exists, it is skipped.
        - Otherwise, a new Equipment record is inserted.
    Returns (True, message) on success, or (False, error message) on failure.
    """
    db_session = SessionLocal()
    try:
        room_record = db_session.query(Room).filter(Room.name == room).first()
        if not room_record:
            # create a new room
            new_room = Room(name=room)
            db_session.add(new_room)
            db_session.flush()  # Get new_room.id
            room_record = new_room
        created = []
        for eq_data in equipment_list:
            eq_name = eq_data.get("name")
            eq_value = eq_data.get("value")
            eq_type = eq_data.get("type")
            if eq_name is None or eq_value is None or eq_type is None:
                continue  # Skip incomplete records
            # Check for uniqueness: same room and equipment name
            existing = db_session.query(Equipment).filter(
                Equipment.room_id == room_record.id,
                Equipment.name == eq_name
            ).first()
            if existing:
                continue  # Skip if already exists.
            new_eq = Equipment(
                room_id=room_record.id,
                name=eq_name,
                value=str(eq_value),
                type=eq_type
            )
            db_session.add(new_eq)
            created.append(eq_name)
        db_session.commit()
        return True, f"Equipment created for room '{room}'. Created: {created}"
    except Exception as e:
        db_session.rollback()
        logger.error(f"DB error adding equipment for room {room}: {e}")
        return False, f"DB error adding equipment: {e}"
    finally:
        db_session.close()


def update_equipment_for_room(room, equipment_list):
    """
    Update the equipment records for the given room.
    For each equipment item (dict with keys "name", "value", "type") in equipment_list:
      - If a record with that name exists, update its value and type.
      - Otherwise, insert a new record.
    Returns (True, message) on success, or (False, error message) on failure.
    """
    db_session = SessionLocal()
    try:
        room_record = db_session.query(Room).filter(Room.name == room).first()
        if not room_record:
            return False, f"Room '{room}' not found in DB."
        for eq_data in equipment_list:
            eq_name = eq_data.get("name")
            eq_value = eq_data.get("value")
            eq_type = eq_data.get("type")
            if eq_name is None or eq_value is None or eq_type is None:
                continue  # Skip incomplete records.
            existing_eq = db_session.query(Equipment).filter(
                Equipment.room_id == room_record.id,
                Equipment.name == eq_name
            ).first()
            if existing_eq:
                existing_eq.value = str(eq_value)
                existing_eq.type = eq_type
            else:
                new_eq = Equipment(
                    room_id=room_record.id,
                    name=eq_name,
                    value=str(eq_value),
                    type=eq_type
                )
                db_session.add(new_eq)
        db_session.commit()
        
        return True, f"Equipment for room '{room}' updated."
    except Exception as e:
        db_session.rollback()
        logger.error(f"DB error updating equipment for room {room}: {e}")
        return False, f"DB error updating equipment: {e}"
    finally:
        db_session.close()
    


def remove_equipment_for_room(room):
    """
    Remove all equipment records for the given room.
    Returns (True, message) on success, or (False, error message) on failure.
    """
    db_session = SessionLocal()
    try:
        room_record = db_session.query(Room).filter(Room.name == room).first()
        if not room_record:
            return False, f"Room '{room}' not found in DB."
        equipment_list = db_session.query(Equipment).filter(
            Equipment.room_id == room_record.id
        ).all()
        for eq in equipment_list:
            db_session.delete(eq)
        db_session.commit()
        return True, f"All equipment for room '{room}' has been deleted."
    except Exception as e:
        db_session.rollback()
        logger.error(f"DB error deleting equipment for room {room}: {e}")
        return False, f"DB error deleting equipment: {e}"
    finally:
        db_session.close()
