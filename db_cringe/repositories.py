from typing import List, Optional
from .repository import Repository
from .models import (
    Building, Room, Computer, MemoryModule, Processor,
    Motherboard, Disk, VideoAdapter, Monitor, UPS
)


class BuildingRepository(Repository[Building]):
    """
    Репозиторий для работы с моделью Building.
    """
    
    def __init__(self, session):
        super().__init__(session, Building)
    
    def get_by_name(self, name: str) -> Optional[Building]:
        """
        Получает здание по названию.
        
        Args:
            name: Название здания.
            
        Returns:
            Optional[Building]: Здание с указанным названием или None, если здание не найдено.
        """
        return self.session.query(Building).filter(Building.name == name).first()


class RoomRepository(Repository[Room]):
    """
    Репозиторий для работы с моделью Room.
    """
    
    def __init__(self, session):
        super().__init__(session, Room)
    
    def get_by_building_and_number(self, building_id: int, room_number: str) -> Optional[Room]:
        """
        Получает комнату по ID здания и номеру комнаты.
        
        Args:
            building_id: ID здания.
            room_number: Номер комнаты.
            
        Returns:
            Optional[Room]: Комната с указанными параметрами или None, если комната не найдена.
        """
        return self.session.query(Room).filter(
            Room.building_id == building_id,
            Room.room_number == room_number
        ).first()
    
    def get_by_building_id(self, building_id: int) -> List[Room]:
        """
        Получает все комнаты в здании.
        
        Args:
            building_id: ID здания.
            
        Returns:
            List[Room]: Список комнат в здании.
        """
        return self.session.query(Room).filter(Room.building_id == building_id).all()


class ComputerRepository(Repository[Computer]):
    """
    Репозиторий для работы с моделью Computer.
    """
    
    def __init__(self, session):
        super().__init__(session, Computer)
    
    def get_by_assigned_it_number(self, assigned_it_number: str) -> Optional[Computer]:
        """
        Получает компьютер по IT номеру.
        
        Args:
            assigned_it_number: IT номер компьютера.
            
        Returns:
            Optional[Computer]: Компьютер с указанным IT номером или None, если компьютер не найден.
        """
        return self.session.query(Computer).filter(
            Computer.assigned_it_number == assigned_it_number
        ).first()
    
    def get_by_room_id(self, room_id: int) -> List[Computer]:
        """
        Получает все компьютеры в комнате.
        
        Args:
            room_id: ID комнаты.
            
        Returns:
            List[Computer]: Список компьютеров в комнате.
        """
        return self.session.query(Computer).filter(Computer.room_id == room_id).all()
    
    def get_by_department(self, department: str) -> List[Computer]:
        """
        Получает все компьютеры отдела.
        
        Args:
            department: Название отдела.
            
        Returns:
            List[Computer]: Список компьютеров отдела.
        """
        return self.session.query(Computer).filter(Computer.department == department).all()
    
    def get_by_responsible(self, responsible: str) -> List[Computer]:
        """
        Получает все компьютеры, за которые отвечает указанный сотрудник.
        
        Args:
            responsible: ФИО ответственного сотрудника.
            
        Returns:
            List[Computer]: Список компьютеров, за которые отвечает указанный сотрудник.
        """
        return self.session.query(Computer).filter(Computer.responsible == responsible).all()


class MemoryModuleRepository(Repository[MemoryModule]):
    """
    Репозиторий для работы с моделью MemoryModule.
    """
    
    def __init__(self, session):
        super().__init__(session, MemoryModule)
    
    def get_by_computer_id(self, computer_id: int) -> List[MemoryModule]:
        """
        Получает все модули памяти компьютера.
        
        Args:
            computer_id: ID компьютера.
            
        Returns:
            List[MemoryModule]: Список модулей памяти компьютера.
        """
        return self.session.query(MemoryModule).filter(MemoryModule.computer_id == computer_id).all()


class ProcessorRepository(Repository[Processor]):
    """
    Репозиторий для работы с моделью Processor.
    """
    
    def __init__(self, session):
        super().__init__(session, Processor)
    
    def get_by_computer_id(self, computer_id: int) -> List[Processor]:
        """
        Получает все процессоры компьютера.
        
        Args:
            computer_id: ID компьютера.
            
        Returns:
            List[Processor]: Список процессоров компьютера.
        """
        return self.session.query(Processor).filter(Processor.computer_id == computer_id).all()


class MotherboardRepository(Repository[Motherboard]):
    """
    Репозиторий для работы с моделью Motherboard.
    """
    
    def __init__(self, session):
        super().__init__(session, Motherboard)
    
    def get_by_computer_id(self, computer_id: int) -> List[Motherboard]:
        """
        Получает все материнские платы компьютера.
        
        Args:
            computer_id: ID компьютера.
            
        Returns:
            List[Motherboard]: Список материнских плат компьютера.
        """
        return self.session.query(Motherboard).filter(Motherboard.computer_id == computer_id).all()


class DiskRepository(Repository[Disk]):
    """
    Репозиторий для работы с моделью Disk.
    """
    
    def __init__(self, session):
        super().__init__(session, Disk)
    
    def get_by_computer_id(self, computer_id: int) -> List[Disk]:
        """
        Получает все диски компьютера.
        
        Args:
            computer_id: ID компьютера.
            
        Returns:
            List[Disk]: Список дисков компьютера.
        """
        return self.session.query(Disk).filter(Disk.computer_id == computer_id).all()


class VideoAdapterRepository(Repository[VideoAdapter]):
    """
    Репозиторий для работы с моделью VideoAdapter.
    """
    
    def __init__(self, session):
        super().__init__(session, VideoAdapter)
    
    def get_by_computer_id(self, computer_id: int) -> List[VideoAdapter]:
        """
        Получает все видеоадаптеры компьютера.
        
        Args:
            computer_id: ID компьютера.
            
        Returns:
            List[VideoAdapter]: Список видеоадаптеров компьютера.
        """
        return self.session.query(VideoAdapter).filter(VideoAdapter.computer_id == computer_id).all()


class MonitorRepository(Repository[Monitor]):
    """
    Репозиторий для работы с моделью Monitor.
    """
    
    def __init__(self, session):
        super().__init__(session, Monitor)
    
    def get_by_computer_id(self, computer_id: int) -> List[Monitor]:
        """
        Получает все мониторы компьютера.
        
        Args:
            computer_id: ID компьютера.
            
        Returns:
            List[Monitor]: Список мониторов компьютера.
        """
        return self.session.query(Monitor).filter(Monitor.computer_id == computer_id).all()
    
    def get_by_assigned_it_number(self, assigned_it_number: str) -> Optional[Monitor]:
        """
        Получает монитор по IT номеру.
        
        Args:
            assigned_it_number: IT номер монитора.
            
        Returns:
            Optional[Monitor]: Монитор с указанным IT номером или None, если монитор не найден.
        """
        return self.session.query(Monitor).filter(
            Monitor.assigned_it_number == assigned_it_number
        ).first()


class UPSRepository(Repository[UPS]):
    """
    Репозиторий для работы с моделью UPS.
    """
    
    def __init__(self, session):
        super().__init__(session, UPS)
    
    def get_by_computer_id(self, computer_id: int) -> List[UPS]:
        """
        Получает все ИБП компьютера.
        
        Args:
            computer_id: ID компьютера.
            
        Returns:
            List[UPS]: Список ИБП компьютера.
        """
        return self.session.query(UPS).filter(UPS.computer_id == computer_id).all()
    
    def get_by_assigned_it_number(self, assigned_it_number: str) -> Optional[UPS]:
        """
        Получает ИБП по IT номеру.
        
        Args:
            assigned_it_number: IT номер ИБП.
            
        Returns:
            Optional[UPS]: ИБП с указанным IT номером или None, если ИБП не найден.
        """
        return self.session.query(UPS).filter(
            UPS.assigned_it_number == assigned_it_number
        ).first()