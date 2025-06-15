from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from data_base.db_models import *
from application.base_models import *
from application.model import Model, FileReader, ExcelExporter

def create_sql_row_from_pydantic(db: Session, data: DataModel):

    existing_pc = db.query(Computer).filter_by(assigned_it_number=data.PC.Assigned_IT_Number).first()

    if existing_pc:
        db.delete(existing_pc)
        db.commit()

    pc = Computer(
        assigned_it_number=data.PC.Assigned_IT_Number,
        type=data.Type,
        room=data.PC.Room,
        building = data.PC.Building,
        department=data.PC.Department,
        responsible = data.PC.Responsible,
        phone = data.PC.Phone,
        inventory_number = data.PC.Inventory_Number_NII_TP,
        serial_number = data.PC.DMI_System_Serial_Number,
        capacity_ram=data.System_Memory.Capacity,
        ip_address = data.PC.Primary_IP_Address,
        mac_address = data.PC.Primary_MAC_Address,
        kaspersky_attempted = data.PC.Kaspersky_Installation_Attempted,
        kaspersky_network = data.PC.Kaspersky_Network,
        workstation_composition=data.Workstation_Composition,
        comment = data.Comment
    )
    db.add(pc)
    db.flush()

    # Добавление модулей памяти
    for module in data.System_Memory.Modules:
        mem_module = MemoryModule(
            computer_id=pc.assigned_it_number,
            name=module.Name,
            type=data.System_Memory.Type,
            description=module.Description
        )
        db.add(mem_module)

    # Добавление процессора
    processor = Processor(
        computer_id=pc.assigned_it_number,
        type=data.Processor.Type,
        frequency=data.Processor.Frequency
    )
    db.add(processor)

    # Добавление материнской платы
    motherboard = Motherboard(
        computer_id=pc.assigned_it_number,
        model=data.Motherboard.Model
    )
    db.add(motherboard)

    # Добавление дисков
    for disk in data.Disk_Drives:
        disk_drive = Disk(
            computer_id=pc.assigned_it_number,
            name=disk.Name,
            capacity=disk.Capacity
        )
        db.add(disk_drive)

    # Добавление видеоадаптеров
    for video_adapter in data.Video_Adapters:
        v_adapter = VideoAdapter(
            computer_id=pc.assigned_it_number,
            name=video_adapter.Name,
            memory=video_adapter.Memory
        )
        db.add(v_adapter)

    # Добавление мониторов
    for monitor in data.Monitors:
        mon = Monitor(
            computer_id=pc.assigned_it_number,
            assigned_it_number=monitor.Assigned_IT_Number,
            model=monitor.Model,
            serial_number=monitor.Serial_Number,
            resolution=monitor.Resolution
        )
        db.add(mon)

    # Добавление ИБП
    ups = UPS(
        computer_id=pc.assigned_it_number,
        assigned_it_number=data.UPS.Assigned_IT_Number
    )
    db.add(ups)

    db.commit()
    db.refresh(pc)

def create_pydantic_model_from_sql_row(db: Session, assigned_it_number: str) -> DataModel:
    pc = db.query(Computer).filter(Computer.assigned_it_number == assigned_it_number).first()

    if not pc:
        raise IndexError(f"Не найден пк в базе с данным assigned_it_number: {assigned_it_number}")

    pc_model = PCModel(
        Assigned_IT_Number=pc.assigned_it_number,
        Department=pc.department,
        Responsible=pc.responsible,
        Phone=pc.phone,
        Building=pc.building,
        Room=pc.room,
        Kaspersky_Installation_Attempted=pc.kaspersky_attempted,
        Kaspersky_Network=pc.kaspersky_network,
        Inventory_Number_NII_TP=pc.inventory_number,
        DMI_System_Serial_Number=pc.serial_number,
        Primary_IP_Address=pc.ip_address,
        Primary_MAC_Address=pc.mac_address
    )

    pydantic_memory_modules = [
        MemoryModel(Name=mm.name, Description=mm.description)
        for mm in pc.memory_modules
    ]
    system_memory_model = SystemMemoryModel(
        Capacity=pc.capacity_ram, 
        Type=pc.memory_modules[0].type if pc.memory_modules else "", 
        Modules=pydantic_memory_modules
    )

    processor = pc.processors[0] if pc.processors else None
    processor_model = ProcessorModel(
        Type=processor.type if processor else "",
        Frequency=processor.frequency if processor else ""
    )

    motherboard = pc.motherboards[0] if pc.motherboards else None
    motherboard_model = MotherboardModel(
        Model=motherboard.model if motherboard else ""
    )

    disk_drive_models = [
        DiskDriveModel(Name=d.name, Capacity=d.capacity)
        for d in pc.disks
    ]

    video_adapter_models = [
        VideoAdapterModel(Name=va.name, Memory=va.memory)
        for va in pc.video_adapters
    ]

    monitor_models = [
        MonitorModel(
            Assigned_IT_Number=m.assigned_it_number,
            Model=m.model,
            Serial_Number=m.serial_number,
            Resolution=m.resolution
        )
        for m in pc.monitors
    ]

    ups = pc.upss[0] if pc.upss else None
    ups_model = UPSModel(
        Assigned_IT_Number=ups.assigned_it_number if ups else ""
    )

    data_model = DataModel(
        Type=pc.type,
        PC=pc_model,
        System_Memory=system_memory_model,
        Processor=processor_model,
        Motherboard=motherboard_model,
        Disk_Drives=disk_drive_models,
        Video_Adapters=video_adapter_models,
        Monitors=monitor_models,
        UPS=ups_model,
        Workstation_Composition=pc.workstation_composition,
        Comment=pc.comment
    )

    return data_model

if __name__ == '__main__':
    #  Определение тестовой pydantic модели
    a = Model(FileReader(), ExcelExporter())
    with open("my_sys.txt", 'r') as f:
        a.load_data_from_file(f, "my_sys.txt")
        test_model = a.data[0].system_data

    print(test_model)
    print()

    #  Определение тестовой бд

    # engine = create_engine("sqlite:///:memory:", echo=False)

    DATABASE_URL = "postgresql://postgres:123@localhost:5435/inventory_db"
    engine = create_engine(DATABASE_URL, echo=True)

    # Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Data_Base = SessionLocal()

    create_sql_row_from_pydantic(Data_Base, test_model)

    models = [Computer, MemoryModule, Processor, Motherboard, Disk, VideoAdapter, Monitor, UPS]

    for model in models:
        print(f"--- {model.__tablename__} ---")
        for row in Data_Base.query(model).all():
            print(row.__dict__)
        print()

    # selected_model = create_pydantic_model_from_sql_row(Data_Base, "0021")
    # print(selected_model)
    # print(test_model)
    # print(selected_model == test_model)

