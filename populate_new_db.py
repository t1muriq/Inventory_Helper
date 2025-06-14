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

        building12 = Building(name="12")
        building28 = Building(name="28")
        db.add_all([building12, building28])
        db.commit()
        db.refresh(building12)
        db.refresh(building28)

        room312 = Room(building_id=building12.id, room_number="312")
        room102 = Room(building_id=building28.id, room_number="102")
        db.add_all([room312, room102])
        db.commit()
        db.refresh(room312)
        db.refresh(room102)

        # ПК 1
        computer1 = Computer(
            room_id=room312.id,
            assigned_it_number="0021",
            department="117",
            responsible="Пронин Сергей Дмитриевич",
            phone="43-01",
            inventory_number="10-1000-2025",
            serial_number="Default string",
            ip_address="26.213.59.133",
            mac_address="D8-5E-D3-A6-03-54",
            kaspersky_attempted="нет",
            kaspersky_network="ru",
            comment=""
        )
        db.add(computer1)
        db.commit()
        db.refresh(computer1)

        db.add_all([
            MemoryModule(computer_id=computer1.id, name="DIMM1", description="KF3200C16D4/16GX 16384 МБ DDR4-3200 DDR4 SDRAM"),
            MemoryModule(computer_id=computer1.id, name="DIMM2", description="KF3200C16D4/16GX 16384 МБ DDR4-3200 DDR4 SDRAM"),
            Processor(computer_id=computer1.id, type="12th Gen Intel(R) Core(TM) i5-12400", frequency=""),
            Motherboard(computer_id=computer1.id, model="Gigabyte Technology Co., Ltd. B660M GAMING DDR4"),
            Disk(computer_id=computer1.id, name="SPCC M.2 PCIe SSD", capacity="119 ГБ"),
            Disk(computer_id=computer1.id, name="XPG GAMMIX S5", capacity="953 ГБ"),
            Disk(computer_id=computer1.id, name="WDC WD10EARS-00Y5B1", capacity="931 ГБ"),
            VideoAdapter(computer_id=computer1.id, name="Intel(R) UHD Graphics 730", memory="2047 МБ"),
            VideoAdapter(computer_id=computer1.id, name="NVIDIA GeForce RTX 4060 Ti", memory="Неизвестно"),
            Monitor(computer_id=computer1.id, assigned_it_number="0021-01", model="N2788HZ (HKM)", serial_number="", resolution="2560x1440"),
            UPS(computer_id=computer1.id, assigned_it_number="0021-02")
        ])
        db.commit()


        print("Database populated with updated data successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error populating database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_db()
