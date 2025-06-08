import os
import re
import json
from typing import List, Optional
from pydantic import BaseModel

# Модели данных по примеру example.json
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

class OutputModel(BaseModel):
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

input_filename = 'test.txt'
input_path = os.path.join(os.path.dirname(__file__), input_filename)
output_filename = 'test.json'
output_path = os.path.join(os.path.dirname(__file__), output_filename)

def clean_value(value, header=None):
    """Удаляет заголовок, ведущие/концевые и множественные пробелы."""
    if header:
        value = re.sub(rf'^{re.escape(header)}\s+', '', value, flags=re.IGNORECASE)
    # Удалить всё до первого не-пробела после двоеточия, если есть
    value = re.sub(r'^.*?:\s*', '', value)
    value = re.sub(r'\s+', ' ', value).strip()
    return value

def parse_file(filepath):
    with open(filepath, encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and set(line.strip()) != {'-'}]

    # --- PC ---
    pc = {}
    pc['Assigned_IT_Number'] = clean_value(get_value(lines, 'Присваиваемый номер ИТ 171:'), 'Присваиваемый номер ИТ 171:')
    pc['Department'] = clean_value(get_value(lines, 'Подразделение:'), 'Подразделение:')
    pc['Responsible'] = clean_value(get_value(lines, 'Ответственный:'), 'Ответственный:')
    pc['Phone'] = clean_value(get_value(lines, 'Телефон:'), 'Телефон:')
    pc['Building_and_Room'] = clean_value(get_value(lines, 'Корпус и комната:'), 'Корпус и комната:')
    pc['Kaspersky_Installation_Attempted'] = clean_value(get_value(lines, 'Была ли попытка установки каспера:'), 'Была ли попытка установки каспера:')
    pc['Kaspersky_Network'] = clean_value(get_value(lines, 'На какую сеть стоит каспер:'), 'На какую сеть стоит каспер:')
    pc['Inventory_Number_NII_TP'] = clean_value(get_value(lines, 'Инвентарный номер НИИ ТП:'), 'Инвентарный номер НИИ ТП:')
    pc['DMI_System_Serial_Number'] = clean_value(get_value(lines, 'DMI системный серийный номер'), 'DMI системный серийный номер')
    pc['Primary_IP_Address'] = clean_value(get_value(lines, 'Первичный адрес IP'), 'Первичный адрес IP')
    pc['Primary_MAC_Address'] = clean_value(get_value(lines, 'Первичный адрес MAC'), 'Первичный адрес MAC')

    # --- System Memory ---
    mem_capacity_line = get_value(lines, 'Системная память')
    mem_capacity_match = re.search(r'(\d+)\s*(\S+)', mem_capacity_line)
    if mem_capacity_match:
        mem_capacity = f"{mem_capacity_match.group(1)} {mem_capacity_match.group(2)}"
    else:
        mem_capacity = clean_value(mem_capacity_line, 'Системная память')
    mem_type = 'DDR4 SDRAM'  # по примеру
    modules = []
    for l in lines:
        if l.startswith('DIMM'):
            name_desc = l.split(':', 1)
            if len(name_desc) == 2:
                name = clean_value(name_desc[0])
                desc = re.sub(r'\s+', ' ', name_desc[1]).strip()
            else:
                name, desc = l.split(' ', 1)
                name = clean_value(name)
                desc = re.sub(r'\s+', ' ', desc).strip()
            # Удаляем все скобки и содержимое в них (тайминги)
            desc = re.sub(r'\s*\([^)]*\)', '', desc).strip()
            desc = clean_value(desc)
            modules.append(MemoryModule(Name=name, Description=desc))
    system_memory = SystemMemoryModel(Capacity=mem_capacity, Type=mem_type, Modules=modules)

    # --- Processor ---
    proc_line = get_value(lines, 'Тип ЦП')
    proc_type_full, proc_freq = split_type_freq(proc_line)
    proc_type = clean_value(proc_type_full, 'Тип ЦП')
    processor = ProcessorModel(Type=proc_type, Frequency=clean_value(proc_freq))

    # --- Motherboard ---
    mb_model_line = get_value(lines, 'Системная плата')
    mb_model = clean_value(mb_model_line, 'Системная плата')
    motherboard = MotherboardModel(Model=mb_model)

    # --- Disk Drives ---
    disk_drives = []
    for l in lines:
        if l.startswith('Дисковый накопитель'):
            m = re.match(r'Дисковый накопитель\s+(.+?)\s+\((.+)\)', l)
            if m:
                name = m.group(1).strip()
                cap = m.group(2).strip()
            else:
                name = l.split(':',1)[-1].strip()
                cap = 'Не указано'
            name = clean_value(name, 'Дисковый накопитель')
            disk_drives.append(DiskDriveModel(Name=name, Capacity=clean_value(cap)))

    # --- Video Adapter ---
    video_line = get_value(lines, 'Видеоадаптер')
    m = re.match(r'(.+?)\s+\((.+)\)', video_line)
    if m:
        video_name = m.group(1).strip()
        video_mem = m.group(2).strip()
    else:
        video_name = video_line
        video_mem = ''
    video_name = clean_value(video_name, 'Видеоадаптер')
    video_adapter = VideoAdapterModel(Name=video_name, Memory=clean_value(video_mem))

    # --- Monitors ---
    monitors = []
    mon_idx = lines.index('Мониторы') if 'Мониторы' in lines else -1
    if mon_idx != -1:
        i = mon_idx + 1
        while i < len(lines):
            if lines[i].startswith('Присваиваемый номер ИТ 171:'):
                assigned = clean_value(lines[i].split(':',1)[-1].strip(), 'Присваиваемый номер ИТ 171:')
                model, serial, year, res = '', '', '', ''
                if i+1 < len(lines) and lines[i+1].startswith('Монитор'):
                    m = re.match(r'Монитор\s+(.+?)\s+\((.+)\)\s+\{(\d{4})\}', lines[i+1])
                    if m:
                        model = clean_value(m.group(1), 'Монитор')
                        serial = clean_value(m.group(2))
                        year = clean_value(m.group(3))
                    else:
                        model = clean_value(lines[i+1][8:], 'Монитор')
                        serial = ''
                        year = ''
                if i+2 < len(lines) and lines[i+2].startswith('Разрешение:'):
                    res = clean_value(lines[i+2].split(':',1)[-1].strip(), 'Разрешение:')
                monitors.append(MonitorModel(
                    Assigned_IT_Number=assigned,
                    Model=model,
                    Serial_Number=serial,
                    Year=year,
                    Resolution=res
                ))
                i += 3
            else:
                break
    # --- UPS ---
    ups_line = next((l for l in lines if l.startswith('Присваиваемый номер ИТ 171:') and '-' in l), None)
    ups = UPSModel(Assigned_IT_Number=clean_value(ups_line.split(':',1)[-1].strip(), 'Присваиваемый номер ИТ 171:') if ups_line else '')

    # --- Workstation Composition ---
    ws_comp = clean_value(get_value(lines, 'Состав рабочей станции:'), 'Состав рабочей станции:')
    comment = clean_value(get_value(lines, 'Комментарий:'), 'Комментарий:')

    return OutputModel(
        PC=PCModel(**pc),
        System_Memory=system_memory,
        Processor=processor,
        Motherboard=motherboard,
        Disk_Drives=disk_drives,
        Video_Adapter=video_adapter,
        Monitors=monitors,
        UPS=ups,
        Workstation_Composition=ws_comp,
        Comment=comment
    )

def get_value(lines, prefix):
    for l in lines:
        if l.lower().startswith(prefix.lower()):
            return l.split(':',1)[-1].strip()
    return ''

def split_type_freq(line):
    m = re.match(r'(.+?),\s*([\d .xMHzМГц\(\)]+)', line)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return line, ''

def main():
    parsed = parse_file(input_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(parsed.model_dump(), f, ensure_ascii=False, indent=2)
    print(f'Данные сохранены в {output_path}')

if __name__ == '__main__':
    main() 