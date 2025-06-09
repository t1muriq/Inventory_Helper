from pydantic import BaseModel
from typing import List


class PCModel(BaseModel):
    Assigned_IT_Number: str
    Department: str
    Responsible: str
    Phone: str
    Building_and_Room: str
    Kaspersky_Installation_Attempted: str
    Kaspersky_Network: str
    Inventory_Number_NII_TP: str
    DMI_System_Serial_Number: str
    Primary_IP_Address: str
    Primary_MAC_Address: str

class MemoryModule(BaseModel):
    Name: str
    Description: str

class SystemMemoryModel(BaseModel):
    Capacity: str
    Type: str
    Modules: List[MemoryModule]

class ProcessorModel(BaseModel):
    Type: str
    Frequency: str

class MotherboardModel(BaseModel):
    Model: str

class DiskDriveModel(BaseModel):
    Name: str
    Capacity: str

class VideoAdapterModel(BaseModel):
    Name: str
    Memory: str

class MonitorModel(BaseModel):
    Assigned_IT_Number: str
    Model: str
    Serial_Number: str
    Year: str
    Resolution: str

class UPSModel(BaseModel):
    Assigned_IT_Number: str

class DataModel(BaseModel):
    PC: PCModel
    System_Memory: SystemMemoryModel
    Processor: ProcessorModel
    Motherboard: MotherboardModel
    Disk_Drives: List[DiskDriveModel]
    Video_Adapter: VideoAdapterModel
    Monitors: List[MonitorModel]
    UPS: UPSModel
    Workstation_Composition: str
    Comment: str