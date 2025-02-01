from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Device(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    equipment = relationship("Equipment", back_populates="device", cascade="all, delete-orphan")

class Equipment(Base):
    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False)
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    type = Column(String, nullable=False)
    device = relationship("Device", back_populates="equipment")

