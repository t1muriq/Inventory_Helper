# Импортируем напрямую из файлов в той же директории
import sys
import os

# Добавляем путь к директории проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Теперь импортируем модули
from library.src.application.db.database import Database
from library.src.application.db.models import Building, Room, Computer, MemoryModule, Processor, Motherboard, Disk, VideoAdapter, Monitor, UPS


def init_database(db_url=None):
    """
    Инициализирует базу данных: создает все таблицы.
    
    Args:
        db_url (str, optional): URL подключения к базе данных.
            Если не указан, будет использоваться значение по умолчанию из класса Database.
    
    Returns:
        Database: Экземпляр класса Database для дальнейшего использования.
    """
    # Создаем экземпляр класса Database
    db = Database(db_url)
    
    # Создаем все таблицы
    db.create_tables()
    
    return db


def reset_database(db_url=None):
    """
    Сбрасывает базу данных: удаляет все таблицы и создает их заново.
    
    Args:
        db_url (str, optional): URL подключения к базе данных.
            Если не указан, будет использоваться значение по умолчанию из класса Database.
    
    Returns:
        Database: Экземпляр класса Database для дальнейшего использования.
    """
    # Создаем экземпляр класса Database
    db = Database(db_url)
    
    # Удаляем все таблицы
    db.drop_tables()
    
    # Создаем все таблицы заново
    db.create_tables()
    
    return db


def seed_test_data(db):
    """
    Заполняет базу данных тестовыми данными.
    
    Args:
        db (Database): Экземпляр класса Database.
    """
    session = db.get_session()
    
    try:
        # Создаем здания
        building1 = Building(name="Главный корпус")
        building2 = Building(name="Лабораторный корпус")
        
        session.add_all([building1, building2])
        session.flush()  # Чтобы получить ID зданий
        
        # Создаем комнаты
        room1 = Room(building_id=building1.id, room_number="101")
        room2 = Room(building_id=building1.id, room_number="102")
        room3 = Room(building_id=building2.id, room_number="201")
        
        session.add_all([room1, room2, room3])
        session.flush()  # Чтобы получить ID комнат
        
        # Создаем компьютеры
        computer1 = Computer(
            room_id=room1.id,
            assigned_it_number="IT-001",
            department="Отдел разработки",
            responsible="Иванов И.И.",
            phone="123-456",
            inventory_number="INV-001",
            serial_number="SN-001",
            ip_address="192.168.1.101",
            mac_address="00:11:22:33:44:55",
            kaspersky_attempted="Да",
            kaspersky_network="Сеть 1",
            comment="Рабочая станция разработчика"
        )
        
        computer2 = Computer(
            room_id=room2.id,
            assigned_it_number="IT-002",
            department="Бухгалтерия",
            responsible="Петрова П.П.",
            phone="789-012",
            inventory_number="INV-002",
            serial_number="SN-002",
            ip_address="192.168.1.102",
            mac_address="AA:BB:CC:DD:EE:FF",
            kaspersky_attempted="Да",
            kaspersky_network="Сеть 1",
            comment="Рабочая станция бухгалтера"
        )
        
        session.add_all([computer1, computer2])
        session.flush()  # Чтобы получить ID компьютеров
        
        # Добавляем компоненты для компьютера 1
        memory1 = MemoryModule(computer_id=computer1.id, name="Kingston", description="8GB DDR4")
        memory2 = MemoryModule(computer_id=computer1.id, name="Kingston", description="8GB DDR4")
        processor1 = Processor(computer_id=computer1.id, type="Intel Core i5", frequency="3.2 GHz")
        motherboard1 = Motherboard(computer_id=computer1.id, model="ASUS Prime B450")
        disk1 = Disk(computer_id=computer1.id, name="Samsung SSD", capacity="500GB")
        video1 = VideoAdapter(computer_id=computer1.id, name="NVIDIA GeForce GTX 1660", memory="6GB")
        monitor1 = Monitor(
            computer_id=computer1.id,
            assigned_it_number="MON-001",
            model="Dell P2419H",
            serial_number="DELL-001",
            year="2020",
            resolution="1920x1080"
        )
        ups1 = UPS(computer_id=computer1.id, assigned_it_number="UPS-001")
        
        # Добавляем компоненты для компьютера 2
        memory3 = MemoryModule(computer_id=computer2.id, name="Crucial", description="16GB DDR4")
        processor2 = Processor(computer_id=computer2.id, type="Intel Core i7", frequency="3.6 GHz")
        motherboard2 = Motherboard(computer_id=computer2.id, model="MSI B550")
        disk2 = Disk(computer_id=computer2.id, name="Western Digital", capacity="1TB")
        video2 = VideoAdapter(computer_id=computer2.id, name="Intel UHD Graphics 630", memory="Shared")
        monitor2 = Monitor(
            computer_id=computer2.id,
            assigned_it_number="MON-002",
            model="LG 24MP88",
            serial_number="LG-001",
            year="2021",
            resolution="1920x1080"
        )
        
        session.add_all([
            memory1, memory2, memory3,
            processor1, processor2,
            motherboard1, motherboard2,
            disk1, disk2,
            video1, video2,
            monitor1, monitor2,
            ups1
        ])
        
        # Фиксируем изменения
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        db.close_session(session)


if __name__ == "__main__":
    # Этот код выполняется только при непосредственном запуске файла
    db = reset_database()
    seed_test_data(db)
    print("База данных успешно инициализирована и заполнена тестовыми данными.")