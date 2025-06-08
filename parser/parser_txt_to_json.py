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

def parse_file(filepath):
    with open(filepath, encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and set(line.strip()) != {'-'}]

    # --- PC ---
    pc = {}
    pc['Assigned_IT_Number'] = get_value(lines, 'Присваиваемый номер ИТ 171:')
    pc['Department'] = get_value(lines, 'Подразделение:')
    pc['Responsible'] = get_value(lines, 'Ответственный:')
    pc['Phone'] = get_value(lines, 'Телефон:')
    pc['Building_and_Room'] = get_value(lines, 'Корпус и комната:')
    pc['Kaspersky_Installation_Attempted'] = get_value(lines, 'Была ли попытка установки каспера:')
    pc['Kaspersky_Network'] = get_value(lines, 'На какую сеть стоит каспер:')
    pc['Inventory_Number_NII_TP'] = get_value(lines, 'Инвентарный номер НИИ ТП:')
    pc['DMI_System_Serial_Number'] = get_value(lines, 'DMI системный серийный номер')
    pc['Primary_IP_Address'] = get_value(lines, 'Первичный адрес IP')
    pc['Primary_MAC_Address'] = get_value(lines, 'Первичный адрес MAC')

    # --- System Memory ---
    mem_capacity_line = get_value(lines, 'Системная память')
    # Извлекаем только число и единицу измерения (например, '15989 МБ')
    mem_capacity_match = re.search(r'(\d+)\s*(\S+)', mem_capacity_line)
    if mem_capacity_match:
        mem_capacity = f"{mem_capacity_match.group(1)} {mem_capacity_match.group(2)}"
    else:
        mem_capacity = mem_capacity_line.strip()
    mem_type = 'DDR4 SDRAM'  # по примеру
    modules = []
    for l in lines:
        if l.startswith('DIMM'):
            # Убираем лишние пробелы между названием и описанием
            name_desc = l.split(':', 1)
            if len(name_desc) == 2:
                name = name_desc[0].strip()
                desc = re.sub(r'\s+', ' ', name_desc[1]).strip()
            else:
                name, desc = l.split(' ', 1)
                name = name.strip()
                desc = re.sub(r'\s+', ' ', desc).strip()
            # Удаляем все скобки и содержимое в них (тайминги)
            desc = re.sub(r'\s*\([^)]*\)', '', desc).strip()
            modules.append(MemoryModule(Name=name, Description=desc))
    system_memory = SystemMemoryModel(Capacity=mem_capacity, Type=mem_type, Modules=modules)

    # --- Processor ---
    proc_line = get_value(lines, 'Тип ЦП')
    # Убираем заголовок и лишние пробелы
    proc_type_full, proc_freq = split_type_freq(proc_line)
    proc_type = re.sub(r'^Тип ЦП\s+', '', proc_type_full).strip()
    processor = ProcessorModel(Type=proc_type, Frequency=proc_freq)

    # --- Motherboard ---
    mb_model_line = get_value(lines, 'Системная плата')
    mb_model = re.sub(r'^Системная плата\s+', '', mb_model_line).strip()
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
            # Убираем заголовок и лишние пробелы
            name = re.sub(r'^Дисковый накопитель\s+', '', name).strip()
            disk_drives.append(DiskDriveModel(Name=name, Capacity=cap))

    # --- Video Adapter ---
    video_line = get_value(lines, 'Видеоадаптер')
    m = re.match(r'(.+?)\s+\((.+)\)', video_line)
    if m:
        video_name = m.group(1).strip()
        video_mem = m.group(2).strip()
    else:
        video_name = video_line
        video_mem = ''
    # Убираем заголовок и лишние пробелы
    video_name = re.sub(r'^Видеоадаптер\s+', '', video_name).strip()
    video_adapter = VideoAdapterModel(Name=video_name, Memory=video_mem)

    # --- Monitors ---
    monitors = []
    mon_idx = lines.index('Мониторы') if 'Мониторы' in lines else -1
    if mon_idx != -1:
        i = mon_idx + 1
        while i < len(lines):
            if lines[i].startswith('Присваиваемый номер ИТ 171:'):
                assigned = lines[i].split(':',1)[-1].strip()
                model, serial, year, res = '', '', '', ''
                if i+1 < len(lines) and lines[i+1].startswith('Монитор'):
                    m = re.match(r'Монитор\s+(.+?)\s+\((.+)\)\s+\{(\d{4})\}', lines[i+1])
                    if m:
                        model = m.group(1).strip()
                        serial = m.group(2).strip()
                        year = m.group(3).strip()
                    else:
                        model = lines[i+1][8:].strip()
                        serial = ''
                        year = ''
                if i+2 < len(lines) and lines[i+2].startswith('Разрешение:'):
                    res = lines[i+2].split(':',1)[-1].strip()
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
    ups = UPSModel(Assigned_IT_Number=ups_line.split(':',1)[-1].strip() if ups_line else '')

    # --- Workstation Composition ---
    ws_comp = get_value(lines, 'Состав рабочей станции:')
    comment = get_value(lines, 'Комментарий:')

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