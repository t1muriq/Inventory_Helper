from typing import List, Optional, Dict, Any
from .repositories import (
    BuildingRepository, RoomRepository, ComputerRepository,
    MemoryModuleRepository, ProcessorRepository, MotherboardRepository,
    DiskRepository, VideoAdapterRepository, MonitorRepository, UPSRepository
)
from .models import (
    Building, Room, Computer, MemoryModule, Processor,
    Motherboard, Disk, VideoAdapter, Monitor, UPS
)
from .database import Database


class InventoryService:
    """
    Сервис для работы с инвентаризацией компьютерного оборудования.
    Предоставляет высокоуровневые методы для работы с данными.
    """
    
    def __init__(self, db: Database):
        """
        Инициализация сервиса.
        
        Args:
            db: Экземпляр класса Database для работы с базой данных.
        """
        self.db = db
        self.session = db.get_session()
        
        # Инициализация репозиториев
        self.building_repo = BuildingRepository(self.session)
        self.room_repo = RoomRepository(self.session)
        self.computer_repo = ComputerRepository(self.session)
        self.memory_repo = MemoryModuleRepository(self.session)
        self.processor_repo = ProcessorRepository(self.session)
        self.motherboard_repo = MotherboardRepository(self.session)
        self.disk_repo = DiskRepository(self.session)
        self.video_adapter_repo = VideoAdapterRepository(self.session)
        self.monitor_repo = MonitorRepository(self.session)
        self.ups_repo = UPSRepository(self.session)
    
    def close(self):
        """
        Закрывает сессию базы данных.
        """
        self.db.close_session(self.session)
    
    # Методы для работы со зданиями
    
    def get_all_buildings(self) -> List[Building]:
        """
        Получает список всех зданий.
        
        Returns:
            List[Building]: Список всех зданий.
        """
        return self.building_repo.get_all()
    
    def get_building_by_id(self, building_id: int) -> Optional[Building]:
        """
        Получает здание по ID.
        
        Args:
            building_id: ID здания.
            
        Returns:
            Optional[Building]: Здание с указанным ID или None, если здание не найдено.
        """
        return self.building_repo.get_by_id(building_id)
    
    def get_building_by_name(self, name: str) -> Optional[Building]:
        """
        Получает здание по названию.
        
        Args:
            name: Название здания.
            
        Returns:
            Optional[Building]: Здание с указанным названием или None, если здание не найдено.
        """
        return self.building_repo.get_by_name(name)
    
    def create_building(self, name: str) -> Building:
        """
        Создает новое здание.
        
        Args:
            name: Название здания.
            
        Returns:
            Building: Созданное здание.
        """
        building = Building(name=name)
        return self.building_repo.create(building)
    
    def update_building(self, building_id: int, name: str) -> Optional[Building]:
        """
        Обновляет информацию о здании.
        
        Args:
            building_id: ID здания.
            name: Новое название здания.
            
        Returns:
            Optional[Building]: Обновленное здание или None, если здание не найдено.
        """
        building = self.building_repo.get_by_id(building_id)
        if building:
            building.name = name
            return self.building_repo.update(building)
        return None
    
    def delete_building(self, building_id: int) -> bool:
        """
        Удаляет здание по ID.
        
        Args:
            building_id: ID здания.
            
        Returns:
            bool: True, если здание успешно удалено, иначе False.
        """
        return self.building_repo.delete(building_id)
    
    # Методы для работы с комнатами
    
    def get_all_rooms(self) -> List[Room]:
        """
        Получает список всех комнат.
        
        Returns:
            List[Room]: Список всех комнат.
        """
        return self.room_repo.get_all()
    
    def get_rooms_by_building_id(self, building_id: int) -> List[Room]:
        """
        Получает список всех комнат в здании.
        
        Args:
            building_id: ID здания.
            
        Returns:
            List[Room]: Список комнат в здании.
        """
        return self.room_repo.get_by_building_id(building_id)
    
    def get_room_by_id(self, room_id: int) -> Optional[Room]:
        """
        Получает комнату по ID.
        
        Args:
            room_id: ID комнаты.
            
        Returns:
            Optional[Room]: Комната с указанным ID или None, если комната не найдена.
        """
        return self.room_repo.get_by_id(room_id)
    
    def create_room(self, building_id: int, room_number: str) -> Room:
        """
        Создает новую комнату.
        
        Args:
            building_id: ID здания.
            room_number: Номер комнаты.
            
        Returns:
            Room: Созданная комната.
        """
        room = Room(building_id=building_id, room_number=room_number)
        return self.room_repo.create(room)
    
    def update_room(self, room_id: int, room_number: str) -> Optional[Room]:
        """
        Обновляет информацию о комнате.
        
        Args:
            room_id: ID комнаты.
            room_number: Новый номер комнаты.
            
        Returns:
            Optional[Room]: Обновленная комната или None, если комната не найдена.
        """
        room = self.room_repo.get_by_id(room_id)
        if room:
            room.room_number = room_number
            return self.room_repo.update(room)
        return None
    
    def delete_room(self, room_id: int) -> bool:
        """
        Удаляет комнату по ID.
        
        Args:
            room_id: ID комнаты.
            
        Returns:
            bool: True, если комната успешно удалена, иначе False.
        """
        return self.room_repo.delete(room_id)
    
    # Методы для работы с компьютерами
    
    def get_all_computers(self) -> List[Computer]:
        """
        Получает список всех компьютеров.
        
        Returns:
            List[Computer]: Список всех компьютеров.
        """
        return self.computer_repo.get_all()
    
    def get_computers_by_room_id(self, room_id: int) -> List[Computer]:
        """
        Получает список всех компьютеров в комнате.
        
        Args:
            room_id: ID комнаты.
            
        Returns:
            List[Computer]: Список компьютеров в комнате.
        """
        return self.computer_repo.get_by_room_id(room_id)
    
    def get_computer_by_id(self, computer_id: int) -> Optional[Computer]:
        """
        Получает компьютер по ID.
        
        Args:
            computer_id: ID компьютера.
            
        Returns:
            Optional[Computer]: Компьютер с указанным ID или None, если компьютер не найден.
        """
        return self.computer_repo.get_by_id(computer_id)
    
    def get_computer_by_assigned_it_number(self, assigned_it_number: str) -> Optional[Computer]:
        """
        Получает компьютер по IT номеру.
        
        Args:
            assigned_it_number: IT номер компьютера.
            
        Returns:
            Optional[Computer]: Компьютер с указанным IT номером или None, если компьютер не найден.
        """
        return self.computer_repo.get_by_assigned_it_number(assigned_it_number)
    
    def create_computer(self, computer_data: Dict[str, Any]) -> Computer:
        """
        Создает новый компьютер.
        
        Args:
            computer_data: Словарь с данными компьютера.
                Должен содержать следующие ключи:
                - room_id: ID комнаты.
                - assigned_it_number: IT номер компьютера.
                Может содержать следующие ключи:
                - department: Отдел.
                - responsible: ФИО ответственного.
                - phone: Телефон.
                - inventory_number: Инвентарный номер.
                - serial_number: Серийный номер.
                - ip_address: IP-адрес.
                - mac_address: MAC-адрес.
                - kaspersky_attempted: Попытка установки Касперского.
                - kaspersky_network: Сеть Касперского.
                - comment: Комментарий.
            
        Returns:
            Computer: Созданный компьютер.
        """
        computer = Computer(**computer_data)
        return self.computer_repo.create(computer)
    
    def update_computer(self, computer_id: int, computer_data: Dict[str, Any]) -> Optional[Computer]:
        """
        Обновляет информацию о компьютере.
        
        Args:
            computer_id: ID компьютера.
            computer_data: Словарь с данными компьютера для обновления.
            
        Returns:
            Optional[Computer]: Обновленный компьютер или None, если компьютер не найден.
        """
        computer = self.computer_repo.get_by_id(computer_id)
        if computer:
            for key, value in computer_data.items():
                if hasattr(computer, key):
                    setattr(computer, key, value)
            return self.computer_repo.update(computer)
        return None
    
    def delete_computer(self, computer_id: int) -> bool:
        """
        Удаляет компьютер по ID.
        
        Args:
            computer_id: ID компьютера.
            
        Returns:
            bool: True, если компьютер успешно удален, иначе False.
        """
        return self.computer_repo.delete(computer_id)
    
    # Методы для работы с компонентами компьютера
    
    def add_memory_module(self, computer_id: int, name: str, description: str) -> MemoryModule:
        """
        Добавляет модуль памяти к компьютеру.
        
        Args:
            computer_id: ID компьютера.
            name: Название модуля памяти.
            description: Описание модуля памяти.
            
        Returns:
            MemoryModule: Созданный модуль памяти.
        """
        memory = MemoryModule(computer_id=computer_id, name=name, description=description)
        return self.memory_repo.create(memory)
    
    def add_processor(self, computer_id: int, type: str, frequency: str) -> Processor:
        """
        Добавляет процессор к компьютеру.
        
        Args:
            computer_id: ID компьютера.
            type: Тип процессора.
            frequency: Частота процессора.
            
        Returns:
            Processor: Созданный процессор.
        """
        processor = Processor(computer_id=computer_id, type=type, frequency=frequency)
        return self.processor_repo.create(processor)
    
    def add_motherboard(self, computer_id: int, model: str) -> Motherboard:
        """
        Добавляет материнскую плату к компьютеру.
        
        Args:
            computer_id: ID компьютера.
            model: Модель материнской платы.
            
        Returns:
            Motherboard: Созданная материнская плата.
        """
        motherboard = Motherboard(computer_id=computer_id, model=model)
        return self.motherboard_repo.create(motherboard)
    
    def add_disk(self, computer_id: int, name: str, capacity: str) -> Disk:
        """
        Добавляет диск к компьютеру.
        
        Args:
            computer_id: ID компьютера.
            name: Название диска.
            capacity: Емкость диска.
            
        Returns:
            Disk: Созданный диск.
        """
        disk = Disk(computer_id=computer_id, name=name, capacity=capacity)
        return self.disk_repo.create(disk)
    
    def add_video_adapter(self, computer_id: int, name: str, memory: str) -> VideoAdapter:
        """
        Добавляет видеоадаптер к компьютеру.
        
        Args:
            computer_id: ID компьютера.
            name: Название видеоадаптера.
            memory: Объем памяти видеоадаптера.
            
        Returns:
            VideoAdapter: Созданный видеоадаптер.
        """
        video_adapter = VideoAdapter(computer_id=computer_id, name=name, memory=memory)
        return self.video_adapter_repo.create(video_adapter)
    
    def add_monitor(self, computer_id: int, monitor_data: Dict[str, Any]) -> Monitor:
        """
        Добавляет монитор к компьютеру.
        
        Args:
            computer_id: ID компьютера.
            monitor_data: Словарь с данными монитора.
                Должен содержать следующие ключи:
                - assigned_it_number: IT номер монитора.
                Может содержать следующие ключи:
                - model: Модель монитора.
                - serial_number: Серийный номер.
                - year: Год выпуска.
                - resolution: Разрешение.
            
        Returns:
            Monitor: Созданный монитор.
        """
        monitor_data['computer_id'] = computer_id
        monitor = Monitor(**monitor_data)
        return self.monitor_repo.create(monitor)
    
    def add_ups(self, computer_id: int, assigned_it_number: str) -> UPS:
        """
        Добавляет ИБП к компьютеру.
        
        Args:
            computer_id: ID компьютера.
            assigned_it_number: IT номер ИБП.
            
        Returns:
            UPS: Созданный ИБП.
        """
        ups = UPS(computer_id=computer_id, assigned_it_number=assigned_it_number)
        return self.ups_repo.create(ups)
    
    # Методы для получения компонентов компьютера
    
    def get_computer_components(self, computer_id: int) -> Dict[str, List]:
        """
        Получает все компоненты компьютера.
        
        Args:
            computer_id: ID компьютера.
            
        Returns:
            Dict[str, List]: Словарь с компонентами компьютера.
                Ключи:
                - memory_modules: Список модулей памяти.
                - processors: Список процессоров.
                - motherboards: Список материнских плат.
                - disks: Список дисков.
                - video_adapters: Список видеоадаптеров.
                - monitors: Список мониторов.
                - upss: Список ИБП.
        """
        return {
            'memory_modules': self.memory_repo.get_by_computer_id(computer_id),
            'processors': self.processor_repo.get_by_computer_id(computer_id),
            'motherboards': self.motherboard_repo.get_by_computer_id(computer_id),
            'disks': self.disk_repo.get_by_computer_id(computer_id),
            'video_adapters': self.video_adapter_repo.get_by_computer_id(computer_id),
            'monitors': self.monitor_repo.get_by_computer_id(computer_id),
            'upss': self.ups_repo.get_by_computer_id(computer_id)
        }