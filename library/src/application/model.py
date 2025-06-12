import re
from abc import ABC, abstractmethod
from typing import Optional, IO

import pandas as pd

from application.base_models import *


class IReader(ABC):

    @abstractmethod
    def read_data(self, file: IO) -> List[str]:
        ...


class IExporter(ABC):

    @abstractmethod
    def export_data(self, data: List[DataModel], output_path: str):
        ...


class ParsingUtils:
    @staticmethod
    def clean_value(value: Optional[str], header: Optional[str] = None) -> str:
        """Удаляет заголовок, ведущие/концевые и множественные пробелы."""
        if value is None:
            return ""
        value_str = str(value)
        if header:
            value_str = re.sub(
                rf"^{re.escape(header)}\s*", "", value_str, flags=re.IGNORECASE
            )
        value_str = re.sub(r"^.*?:\s*", "", value_str)
        value_str = re.sub(r"\s+", " ", value_str).strip()
        return value_str

    @staticmethod
    def get_value(lines: List[str], prefix: str) -> str:
        for l in lines:
            if l.lower().startswith(prefix.lower()):
                return l.split(":", 1)[-1].strip()
        return ""

    @staticmethod
    def split_type_freq(line: str) -> tuple[str, str]:
        m = re.match(r"(.+?),\s*([\d .xMHzМГц()]+)", line)
        if m:
            return m.group(1).strip(), m.group(2).strip()
        return line, ""


class FileReader(IReader):
    encodings = ["utf-8", "windows-1251"]

    def read_data(self, file: str) -> List[str]:

        lines = [
            line.strip()
            for line in file
            if line.strip() and set(line.strip()) != {"-"}
        ]
        return lines




def parser_method(func):
    func.is_parser = True
    return func


class DataParser:
    parse_methods = []

    def __init__(self):
        self.parsed_data = {}

    @parser_method
    def parse_pc(self, lines: List[str]):
        pc_fields = [
            ("Assigned_IT_Number", "Присваиваемый номер ИТ 171:"),
            ("Department", "Подразделение:"),
            ("Responsible", "Ответственный:"),
            ("Phone", "Телефон:"),
            ("Building_and_Room", "Корпус и комната:"),
            ("Kaspersky_Installation_Attempted", "Была ли попытка установки каспера:"),
            ("Kaspersky_Network", "На какую сеть стоит каспер:"),
            ("Inventory_Number_NII_TP", "Инвентарный номер НИИ ТП:"),
            ("DMI_System_Serial_Number", "DMI системный серийный номер"),
            ("Primary_IP_Address", "Первичный адрес IP"),
            ("Primary_MAC_Address", "Первичный адрес MAC"),
        ]

        pc = {}
        for key, label in pc_fields:
            value = ParsingUtils.get_value(lines, label)
            pc[key] = ParsingUtils.clean_value(value, label)

        # Разделение Building_and_Room на два разделных Building и Room
        building_room_str = pc["Building_and_Room"]
        building_match = re.search(
            r"(\d+)\s*корпус", building_room_str, re.IGNORECASE
        )
        if building_match:
            pc["Building"] = building_match.group(1)

        room_match = re.search(r"(\d+)\s*комната", building_room_str, re.IGNORECASE)
        if room_match:
            pc["Room"] = room_match.group(1)

        self.parsed_data["PC"] = PCModel(**pc)

    @parser_method
    def parse_system_memory(self, lines: List[str]):
        mem_capacity_line = ParsingUtils.get_value(lines, "Системная память")
        mem_capacity_match = re.search(r"(\d+)\s*(\S+)", mem_capacity_line)
        if mem_capacity_match:
            mem_capacity = (
                f"{mem_capacity_match.group(1)} {mem_capacity_match.group(2)}"
            )
        else:
            mem_capacity = ParsingUtils.clean_value(mem_capacity_line, "Системная память")
        mem_type = "DDR4 SDRAM"
        modules = []
        for l in lines:
            if l.startswith("DIMM"):
                name_desc = l.split(":", 1)
                if len(name_desc) == 2:
                    name = ParsingUtils.clean_value(name_desc[0])
                    desc = re.sub(r"\s+", " ", name_desc[1]).strip()
                else:
                    name, desc = l.split(" ", 1)
                    name = ParsingUtils.clean_value(name)
                    desc = re.sub(r"\s+", " ", desc).strip()
                desc = re.sub(r"\s*\([^)]*\)", "", desc).strip()
                desc = ParsingUtils.clean_value(desc)
                modules.append(MemoryModule(Name=name, Description=desc))
        self.parsed_data["System_Memory"] = SystemMemoryModel(
            Capacity=mem_capacity, Type=mem_type, Modules=modules
        )

    @parser_method
    def parse_processor(self, lines: List[str]):
        proc_line = ParsingUtils.get_value(lines, "Тип ЦП")
        proc_type_full, proc_freq = ParsingUtils.split_type_freq(proc_line)
        proc_type = ParsingUtils.clean_value(proc_type_full, "Тип ЦП")
        self.parsed_data["Processor"] = ProcessorModel(
            Type=proc_type, Frequency=ParsingUtils.clean_value(proc_freq)
        )

    @parser_method
    def parse_motherboard(self, lines: List[str]):
        mb_model_line = ParsingUtils.get_value(lines, "Системная плата")
        mb_model = ParsingUtils.clean_value(mb_model_line, "Системная плата")
        self.parsed_data["Motherboard"] = MotherboardModel(Model=mb_model)

    @parser_method
    def parse_disk_drive(self, lines: List[str]):
        disk_drives = []
        for l in lines:
            if l.startswith("Дисковый накопитель"):
                m = re.match(r"Дисковый накопитель\s+(.+?)\s+\((.+)\)", l)
                if m:
                    name = m.group(1).strip()
                    cap = m.group(2).strip()
                else:
                    name = l.split(":", 1)[-1].strip()
                    cap = "Не указано"
                name = ParsingUtils.clean_value(name, "Дисковый накопитель")
                disk_drives.append(
                    DiskDriveModel(Name=name, Capacity=ParsingUtils.clean_value(cap))
                )
        self.parsed_data["Disk_Drives"] = disk_drives

    @parser_method
    def parse_video_adapter(self, lines: List[str]):
        video_adapters = []
        for l in lines:
            if l.startswith("Видеоадаптер"):
                m = re.match(r"(.+?)\s+\((.+)\)", l)
                if m:
                    video_name = m.group(1).strip()
                    video_mem = m.group(2).strip()
                else:
                    video_name = l
                    video_mem = ""
                video_name = ParsingUtils.clean_value(video_name, "Видеоадаптер")
                video_adapters.append(
                    VideoAdapterModel(Name=video_name, Memory=ParsingUtils.clean_value(video_mem))
                )
        self.parsed_data["Video_Adapters"] = video_adapters

    @parser_method
    def parse_monitor(self, lines: List[str]):
        monitors = []
        mon_idx = lines.index("Мониторы") if "Мониторы" in lines else -1
        if mon_idx != -1:
            i = mon_idx + 1
            while i < len(lines):
                if lines[i].startswith("Присваиваемый номер ИТ 171:"):
                    assigned = ParsingUtils.clean_value(
                        lines[i].split(":", 1)[-1].strip(),
                        "Присваиваемый номер ИТ 171:",
                    )
                    model, serial, year, res = "", "", "", ""
                    if i + 1 < len(lines) and lines[i + 1].startswith("Монитор"):
                        m = re.match(
                            r"Монитор\s+(.+?)\s+\((.+)\)\s+\{(\d{4})}", lines[i + 1]
                        )
                        if m:
                            model = ParsingUtils.clean_value(m.group(1), "Монитор")
                            serial = ParsingUtils.clean_value(m.group(2))
                        else:
                            model = ParsingUtils.clean_value(lines[i + 1][8:], "Монитор")
                            serial = ""
                    if i + 2 < len(lines) and lines[i + 2].startswith("Разрешение:"):
                        res = ParsingUtils.clean_value(
                            lines[i + 2].split(":", 1)[-1].strip(), "Разрешение:"
                        )
                    monitors.append(
                        MonitorModel(
                            Assigned_IT_Number=assigned,
                            Model=model,
                            Serial_Number=serial,
                            Resolution=res,
                        )
                    )
                    i += 3
                else:
                    break
        self.parsed_data["Monitors"] = monitors

    @parser_method
    def parse_ups(self, lines: List[str]):
        ups_idx = lines.index("ИБП") if "ИБП" in lines else -1
        ups_assigned_it_number = ""
        if ups_idx != -1 and ups_idx + 1 < len(lines):
            ups_line = lines[ups_idx + 1]
            if ups_line.startswith("Присваиваемый номер ИТ 171:"):
                ups_assigned_it_number = ParsingUtils.clean_value(
                    ups_line.split(":", 1)[-1].strip(), "Присваиваемый номер ИТ 171:"
                )
        self.parsed_data["UPS"] = UPSModel(Assigned_IT_Number=ups_assigned_it_number)

    @parser_method
    def parse_misc_info(self, lines: List[str]):
        ws_comp = ParsingUtils.clean_value(
            ParsingUtils.get_value(lines, "Состав рабочей станции:"), "Состав рабочей станции:"
        )
        comment = ParsingUtils.clean_value(
            ParsingUtils.get_value(lines, "Комментарий:"), "Комментарий:"
        )
        self.parsed_data["Workstation_Composition"] = ws_comp
        self.parsed_data["Comment"] = comment

    @parser_method
    def parse_type_pc(self, lines: List[str]):
        self.parsed_data["Type"] = lines[0]

    def parse_all_data(self, lines: List[str]) -> DataModel:
        for name in dir(self):
            method = getattr(self, name)
            if callable(method) and getattr(method, "is_parser", False):
                method(lines)
        return DataModel(**self.parsed_data)


class ExcelExporter(IExporter):

    def export_data(self, data: List[DataModel], output_path: str):
        if not data:
            raise ValueError("Нет данных для экспорта в Excel.")

        excel_rows = []

        for item in data:
            excel_rows.append(
                {
                    "Номер УП ИТ № 171": item.PC.Assigned_IT_Number,
                    "Состав рабочей станции": '\n'.join([m.Assigned_IT_Number for m in item.Monitors] + [item.UPS.Assigned_IT_Number]),
                    "Работник": item.PC.Responsible,
                    "Подразделение": item.PC.Department,
                    "Корпус": item.PC.Building,
                    "Комната": item.PC.Room,
                    "Телефон": item.PC.Phone,
                    "Тип устройства": item.Type,
                    "Характеристики":
                        '\n'.join([f"Память: {item.System_Memory.Capacity} {item.System_Memory.Type}"] +
                                  [f"{m.Name} {m.Description}" for m in item.System_Memory.Modules] +
                                  [f"Процессор: {item.Processor.Type} {item.Processor.Frequency}"] +
                                  [f"Мат. плата: {item.Motherboard.Model}"] +
                                  [f"{d.Name} {d.Capacity}" for d in item.Disk_Drives] +
                                  [f"{v.Name} {v.Memory}" for v in item.Video_Adapters]
                                  ),
                    "IP адрес": item.PC.Primary_IP_Address,
                    "MAC адрес": item.PC.Primary_MAC_Address,
                    "Вид сети": item.PC.Kaspersky_Network,
                    "ИНВ. номер НИИТП": item.PC.Inventory_Number_NII_TP,
                    "Серийный номер": item.PC.DMI_System_Serial_Number,
                    "Каспер": item.PC.Kaspersky_Installation_Attempted,
                }
            )

        df = pd.DataFrame(excel_rows)

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Отчет по ПК", index=False)


class Model:
    def __init__(self, reader: IReader, exporter: IExporter):
        self.data = []
        self.reader = reader
        self.exporter = exporter
        self.parser = DataParser()

    def load_data(self, file: IO):
        lines = self.reader.read_data(file)
        parsed_data = self.parser.parse_all_data(lines)
        self.data.append(parsed_data)

    def export_data(self, output_path: str):
        self.exporter.export_data(self.data, output_path)

    def clear_data(self):
        self.data = []
