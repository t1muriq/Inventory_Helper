from sqlalchemy.orm import Session
from application.database import SessionLocal, engine
from application.db_models import (
    Base, Building, Room, Computer, MemoryModule, Processor, Motherboard,
    Disk, VideoAdapter, Monitor, UPS
)

def populate_db():
    db: Session = SessionLocal()
    try:
        # Clear existing data (optional, for development)
        # Base.metadata.drop_all(bind=engine)
        # Base.metadata.create_all(bind=engine)

        # Test Data
        building1 = Building(name="Корпус А")
        building2 = Building(name="Корпус Б")
        db.add_all([building1, building2])
        db.commit()
        db.refresh(building1)
        db.refresh(building2)

        room1_a = Room(building_id=building1.id, room_number="101")
        room2_a = Room(building_id=building1.id, room_number="102")
        room1_b = Room(building_id=building2.id, room_number="201")
        db.add_all([room1_a, room2_a, room1_b])
        db.commit()
        db.refresh(room1_a)

        computer1 = Computer(
            room_id=room1_a.id,
            assigned_it_number="ИТ-001",
            department="Отдел 1",
            responsible="Иванов И.И.",
            phone="+7 (123) 456-78-90",
            inventory_number="INV-001",
            serial_number="SN-001",
            ip_address="192.168.1.100",
            mac_address="00:11:22:33:44:55",
            kaspersky_attempted="Да",
            kaspersky_network="Корпоративная",
            comment="Тестовый ПК №1"
        )
        db.add(computer1)
        db.commit()
        db.refresh(computer1)

        mem_module1 = MemoryModule(
            computer_id=computer1.id,
            name="DIMM1",
            description="8GB DDR4"
        )
        proc1 = Processor(
            computer_id=computer1.id,
            type="Intel Core i7",
            frequency="3.4GHz"
        )
        mb1 = Motherboard(
            computer_id=computer1.id,
            model="ASUS ROG STRIX"
        )
        disk1 = Disk(
            computer_id=computer1.id,
            name="SSD Samsung",
            capacity="500GB"
        )
        video1 = VideoAdapter(
            computer_id=computer1.id,
            name="NVIDIA GeForce RTX 3060",
            memory="12GB"
        )
        monitor1 = Monitor(
            computer_id=computer1.id,
            assigned_it_number="МОН-001",
            model="Dell UltraSharp",
            serial_number="DL-SN-001",
            resolution="1920x1080"
        )
        ups1 = UPS(
            computer_id=computer1.id,
            assigned_it_number="ИБП-001"
        )

        db.add_all([mem_module1, proc1, mb1, disk1, video1, monitor1, ups1])
        db.commit()

        print("Database populated with test data successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error populating database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_db() 