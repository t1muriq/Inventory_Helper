from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False, unique=True)

    rooms = relationship("Room", back_populates="building")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="CASCADE"))
    room_number = Column(Text, nullable=False)

    building = relationship("Building", back_populates="rooms")
    computers = relationship("Computer", back_populates="room")

class Computer(Base):
    __tablename__ = "computers"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"))
    assigned_it_number = Column(Text, unique=True)
    department = Column(Text)
    responsible = Column(Text)
    phone = Column(Text)
    inventory_number = Column(Text)
    serial_number = Column(Text)
    ip_address = Column(Text)
    mac_address = Column(Text)
    kaspersky_attempted = Column(Text)
    kaspersky_network = Column(Text)
    comment = Column(Text)

    room = relationship("Room", back_populates="computers")
    memory_modules = relationship("MemoryModule", back_populates="computer")
    processors = relationship("Processor", back_populates="computer")
    motherboards = relationship("Motherboard", back_populates="computer")
    disks = relationship("Disk", back_populates="computer")
    video_adapters = relationship("VideoAdapter", back_populates="computer")
    monitors = relationship("Monitor", back_populates="computer")
    upss = relationship("UPS", back_populates="computer")

class MemoryModule(Base):
    __tablename__ = "memory_modules"

    id = Column(Integer, primary_key=True, index=True)
    computer_id = Column(Integer, ForeignKey("computers.id", ondelete="CASCADE"))
    name = Column(Text)
    description = Column(Text)

    computer = relationship("Computer", back_populates="memory_modules")

class Processor(Base):
    __tablename__ = "processors"

    id = Column(Integer, primary_key=True, index=True)
    computer_id = Column(Integer, ForeignKey("computers.id", ondelete="CASCADE"))
    type = Column(Text)
    frequency = Column(Text)

    computer = relationship("Computer", back_populates="processors")

class Motherboard(Base):
    __tablename__ = "motherboards"

    id = Column(Integer, primary_key=True, index=True)
    computer_id = Column(Integer, ForeignKey("computers.id", ondelete="CASCADE"))
    model = Column(Text)

    computer = relationship("Computer", back_populates="motherboards")

class Disk(Base):
    __tablename__ = "disks"

    id = Column(Integer, primary_key=True, index=True)
    computer_id = Column(Integer, ForeignKey("computers.id", ondelete="CASCADE"))
    name = Column(Text)
    capacity = Column(Text)

    computer = relationship("Computer", back_populates="disks")

class VideoAdapter(Base):
    __tablename__ = "video_adapters"

    id = Column(Integer, primary_key=True, index=True)
    computer_id = Column(Integer, ForeignKey("computers.id", ondelete="CASCADE"))
    name = Column(Text)
    memory = Column(Text)

    computer = relationship("Computer", back_populates="video_adapters")

class Monitor(Base):
    __tablename__ = "monitors"

    id = Column(Integer, primary_key=True, index=True)
    computer_id = Column(Integer, ForeignKey("computers.id", ondelete="CASCADE"))
    assigned_it_number = Column(Text)
    model = Column(Text)
    serial_number = Column(Text)
    year = Column(Text)
    resolution = Column(Text)

    computer = relationship("Computer", back_populates="monitors")

class UPS(Base):
    __tablename__ = "upss"

    id = Column(Integer, primary_key=True, index=True)
    computer_id = Column(Integer, ForeignKey("computers.id", ondelete="CASCADE"))
    assigned_it_number = Column(Text)

    computer = relationship("Computer", back_populates="upss") 