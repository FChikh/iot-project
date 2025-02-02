from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UniqueConstraint, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()


class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    equipment = relationship("Equipment", back_populates="room")
    sensors = relationship("Sensor", back_populates="room")
    
    
class Sensor(Base):
    __tablename__ = 'sensors'
    
    __table_args__ = (UniqueConstraint('room_id', 'name', name='_room_id_name_sensor_uc'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete="CASCADE"))
    name = Column(String, nullable=False)
    min_value = Column(Float, nullable=False)
    max_value = Column(Float, nullable=False)
    room = relationship("Room", back_populates="sensors")
    
    def __repr__(self):
        return (f"<Sensor(id={self.id}, room_id={self.room_id}, "
                f"name='{self.name}', min_value='{self.value}', max_value='{self.type}')>")


class Equipment(Base):
    __tablename__ = 'equipment'
    
    __table_args__ = (UniqueConstraint('room_id', 'name', name='_room_id_name_equip_uc'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete="CASCADE"))
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    type = Column(String, nullable=False)
    room = relationship("Room", back_populates="equipment")
    
    def __repr__(self):
        return (f"<Equipment(id={self.id}, room_id={self.room_id}, "
                f"name='{self.name}', value='{self.value}', type='{self.type}')>")
    
    
