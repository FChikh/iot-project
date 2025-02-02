from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()


class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    equipment = relationship("Equipment", back_populates="room")


class Equipment(Base):
    __tablename__ = 'equipment'
    
    __table_args__ = (UniqueConstraint('room_id', 'name', name='_room_id_name_uc'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete="CASCADE"))
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    type = Column(String, nullable=False)
    room = relationship("Room", back_populates="equipment")
    
    def __repr__(self):
        return (f"<Equipment(id={self.id}, room_id={self.room_id}, "
                f"name='{self.name}', value='{self.value}', type='{self.type}')>")
    
    
