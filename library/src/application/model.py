import re
import pandas as pd
from typing import List, Dict, Optional

from application.base_models import (
    PCModel,
    MemoryModule,
    SystemMemoryModel,
    ProcessorModel,
    MotherboardModel,
    DiskDriveModel,
    VideoAdapterModel,
    MonitorModel,
    UPSModel,
    DataModel,
)


class Model:
    def __init__(self) -> None:
        self.data: list[DataModel] = []

    @staticmethod
    def _clean_value(value: Optional[str], header: Optional[str] = None) -> str:
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
    def _get_value(lines: List[str], prefix: str) -> str:
        for l in lines:
            if l.lower().startswith(prefix.lower()):
                return l.split(":", 1)[-1].strip()
        return ""

    @staticmethod
    def _split_type_freq(line: str) -> tuple[str, str]:
        m = re.match(r"(.+?),\s*([\d .xMHzМГц()]+)", line)
        if m:
            return m.group(1).strip(), m.group(2).strip()
        return line, ""

    @staticmethod
    def read_lines_from_file(filepath: str) -> List[str]:
        lines = None
        last_exception = None

        for type_encoding in ["utf-8", "windows-1251"]:
            try:
                with open(filepath, "r", encoding=type_encoding) as f:
                    lines = [
                        line.strip()
                        for line in f
                        if line.strip() and set(line.strip()) != {"-"}
                    ]
                break
            except UnicodeDecodeError as e:
                last_exception = e
                continue
            except OSError as e:

                raise IOError(f"Не удалось прочитать файл {filepath}: {e}") from e

        if lines is None:
            if last_exception:
                raise IOError(
                    f"Не удалось прочитать файл {filepath} с кодировками UTF-8 или Windows-1251: {last_exception}") from last_exception
            else:
                raise IOError(
                    f"Не удалось прочитать файл {filepath} с кодировками UTF-8 или Windows-1251."
                )
        return lines

    def parse_pc_info(self, lines: List[str]) -> Dict[str, str]:
        # --- PC --- (Остальные части из parser_txt_to_json.py) ---
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
            value = self._get_value(lines, label)
            pc[key] = self._clean_value(value, label)
        return pc

    def parse_system_memory(self, lines: List[str]) -> SystemMemoryModel:
        # --- System Memory ---
        mem_capacity_line = self._get_value(lines, "Системная память")
        mem_capacity_match = re.search(r"(\d+)\s*(\S+)", mem_capacity_line)
        if mem_capacity_match:
            mem_capacity = (
                f"{mem_capacity_match.group(1)} {mem_capacity_match.group(2)}"
            )
        else:
            mem_capacity = self._clean_value(mem_capacity_line, "Системная память")
        mem_type = "DDR4 SDRAM"
        modules = []
        for l in lines:
            if l.startswith("DIMM"):
                name_desc = l.split(":", 1)
                if len(name_desc) == 2:
                    name = self._clean_value(name_desc[0])
                    desc = re.sub(r"\s+", " ", name_desc[1]).strip()
                else:
                    name, desc = l.split(" ", 1)
                    name = self._clean_value(name)
                    desc = re.sub(r"\s+", " ", desc).strip()
                desc = re.sub(r"\s*\([^)]*\)", "", desc).strip()
                desc = self._clean_value(desc)
                modules.append(MemoryModule(Name=name, Description=desc))
        return SystemMemoryModel(
            Capacity=mem_capacity, Type=mem_type, Modules=modules
        )

    def parse_processor(self, lines: List[str]) -> ProcessorModel:
        # --- Processor ---
        proc_line = self._get_value(lines, "Тип ЦП")
        proc_type_full, proc_freq = self._split_type_freq(proc_line)
        proc_type = self._clean_value(proc_type_full, "Тип ЦП")
        return ProcessorModel(
            Type=proc_type, Frequency=self._clean_value(proc_freq)
        )

    def parse_motherboard(self, lines: List[str]) -> MotherboardModel:
        # --- Motherboard ---
        mb_model_line = self._get_value(lines, "Системная плата")
        mb_model = self._clean_value(mb_model_line, "Системная плата")
        return MotherboardModel(Model=mb_model)

    def parse_disk_drives(self, lines: List[str]) -> List[DiskDriveModel]:
        # --- Disk Drives ---
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
                name = self._clean_value(name, "Дисковый накопитель")
                disk_drives.append(
                    DiskDriveModel(Name=name, Capacity=self._clean_value(cap))
                )
        return disk_drives

    def parse_video_adapter(self, lines: List[str]) -> VideoAdapterModel:
        # --- Video Adapter ---
        video_line = self._get_value(lines, "Видеоадаптер")
        m = re.match(r"(.+?)\s+\((.+)\)", video_line)
        if m:
            video_name = m.group(1).strip()
            video_mem = m.group(2).strip()
        else:
            video_name = video_line
            video_mem = ""
        video_name = self._clean_value(video_name, "Видеоадаптер")
        return VideoAdapterModel(
            Name=video_name, Memory=self._clean_value(video_mem)
        )

    def parse_monitors(self, lines: List[str]) -> List[MonitorModel]:
        # --- Monitors ---
        monitors = []
        mon_idx = lines.index("Мониторы") if "Мониторы" in lines else -1
        if mon_idx != -1:
            i = mon_idx + 1
            while i < len(lines):
                if lines[i].startswith("Присваиваемый номер ИТ 171:"):
                    assigned = self._clean_value(
                        lines[i].split(":", 1)[-1].strip(),
                        "Присваиваемый номер ИТ 171:",
                    )
                    model, serial, year, res = "", "", "", ""
                    if i + 1 < len(lines) and lines[i + 1].startswith("Монитор"):
                        m = re.match(
                            r"Монитор\s+(.+?)\s+\((.+)\)\s+\{(\d{4})\}", lines[i + 1]
                        )
                        if m:
                            model = self._clean_value(m.group(1), "Монитор")
                            serial = self._clean_value(m.group(2))
                            year = self._clean_value(m.group(3))
                        else:
                            model = self._clean_value(lines[i + 1][8:], "Монитор")
                            serial = ""
                            year = ""
                    if i + 2 < len(lines) and lines[i + 2].startswith("Разрешение:"):
                        res = self._clean_value(
                            lines[i + 2].split(":", 1)[-1].strip(), "Разрешение:"
                        )
                    monitors.append(
                        MonitorModel(
                            Assigned_IT_Number=assigned,
                            Model=model,
                            Serial_Number=serial,
                            Year=year,
                            Resolution=res,
                        )
                    )
                    i += 3
                else:
                    break
        return monitors

    def parse_ups(self, lines: List[str]) -> UPSModel:
        # --- UPS ---
        ups_idx = lines.index("ИБП") if "ИБП" in lines else -1
        ups_assigned_it_number = ""
        if ups_idx != -1 and ups_idx + 1 < len(lines):
            ups_line = lines[ups_idx + 1]
            if ups_line.startswith("Присваиваемый номер ИТ 171:"):
                ups_assigned_it_number = self._clean_value(
                    ups_line.split(":", 1)[-1].strip(), "Присваиваемый номер ИТ 171:"
                )
        return UPSModel(Assigned_IT_Number=ups_assigned_it_number)

    def parse_misc_info(self, lines: List[str]) -> Dict[str, str]:
        # --- Workstation Composition and Comment ---
        ws_comp = self._clean_value(
            self._get_value(lines, "Состав рабочей станции:"), "Состав рабочей станции:"
        )
        comment = self._clean_value(
            self._get_value(lines, "Комментарий:"), "Комментарий:"
        )
        return {
            "Workstation_Composition": ws_comp,
            "Comment": comment
        }

    def load_from_txt(self, filepath: str) -> None:
        lines = self.read_lines_from_file(filepath)

        pc = self.parse_pc_info(lines)
        system_memory = self.parse_system_memory(lines)
        processor = self.parse_processor(lines)
        motherboard = self.parse_motherboard(lines)
        disk_drives = self.parse_disk_drives(lines)
        video_adapter = self.parse_video_adapter(lines)
        monitors = self.parse_monitors(lines)
        ups = self.parse_ups(lines)
        misc_info = self.parse_misc_info(lines)

        parsed_data = DataModel(
            PC=PCModel(**pc),
            System_Memory=system_memory,
            Processor=processor,
            Motherboard=motherboard,
            Disk_Drives=disk_drives,
            Video_Adapter=video_adapter,
            Monitors=monitors,
            UPS=ups,
            Workstation_Composition=misc_info["Workstation_Composition"],
            Comment=misc_info["Comment"],
        )
        self.data.append(parsed_data)

    def export_to_excel(self, output_filepath: str) -> None:
        if not self.data:
            raise ValueError("Нет данных для экспорта в Excel.")

        excel_rows = []

        for item in self.data:
            # --- Извлечение Корпуса и Комнаты ---
            building_room_str = self._clean_value(item.PC.Building_and_Room)
            building = ""
            room = ""
            building_match = re.search(
                r"(\d+)\s*корпус", building_room_str, re.IGNORECASE
            )
            if building_match:
                building = building_match.group(1)
            room_match = re.search(r"(\d+)\s*комната", building_room_str, re.IGNORECASE)
            if room_match:
                room = room_match.group(1)
            # Fallback if no specific pattern found, use the whole string for building, if room is empty
            if (
                    not building and building_room_str
            ):  # If building not found, but string exists
                building = (
                    building_room_str.strip().split(" ")[0]
                    if " " in building_room_str
                    else building_room_str.strip()
                )
                if " " in building_room_str:
                    room = (
                        building_room_str.strip().split(" ")[1]
                        if len(building_room_str.strip().split(" ")) > 1
                        else ""
                    )

            # --- Формирование "Состав рабочей станции" ---
            # Собираем все номера ИТ, которые должны быть в составе рабочей станции
            composition_items = []

            # Добавляем номера ИТ мониторов, если они есть
            monitor_it_numbers = [
                self._clean_value(m.Assigned_IT_Number)
                for m in item.Monitors
                if self._clean_value(m.Assigned_IT_Number)
            ]
            if monitor_it_numbers:
                composition_items.extend(monitor_it_numbers)

            # Добавляем номер ИТ ИБП, если он есть
            ups_it_number = self._clean_value(item.UPS.Assigned_IT_Number)
            if ups_it_number:
                composition_items.append(ups_it_number)

            # Объединяем все элементы через перенос строки
            workstation_composition_display = (
                "\n".join(composition_items) if composition_items else ""
            )

            # --- Формирование "Характеристики" ---
            characteristics = []
            if item.System_Memory:
                if item.System_Memory.Capacity or item.System_Memory.Type:
                    characteristics.append(
                        f"Память: {self._clean_value(item.System_Memory.Capacity)} {self._clean_value(item.System_Memory.Type)}"
                    )
                for m in item.System_Memory.Modules:
                    if m.Name or m.Description:
                        characteristics.append(
                            f"{self._clean_value(m.Name)} ({self._clean_value(m.Description)})"
                        )

            if item.Processor and (item.Processor.Type or item.Processor.Frequency):
                characteristics.append(
                    f"Процессор: {self._clean_value(item.Processor.Type)} {self._clean_value(item.Processor.Frequency)}"
                )
            if item.Motherboard and item.Motherboard.Model:
                characteristics.append(
                    f"Мат. плата: {self._clean_value(item.Motherboard.Model)}"
                )
            if item.Disk_Drives:
                for d in item.Disk_Drives:
                    if d.Name or d.Capacity:
                        characteristics.append(
                            f"Диск: {self._clean_value(d.Name)} ({self._clean_value(d.Capacity)})"
                        )
            if item.Video_Adapter and (
                    item.Video_Adapter.Name or item.Video_Adapter.Memory
            ):
                characteristics.append(
                    f"Видео: {self._clean_value(item.Video_Adapter.Name)} ({self._clean_value(item.Video_Adapter.Memory)})"
                )

            characteristics_str = "\n".join(characteristics)

            # --- "Тип устройства" ---
            # Проверяем наличие Product_Name в PCModel, если нет, используем дефолтное значение
            # getattr безопасен, если поле не существует
            device_type = self._clean_value(getattr(item.PC, "Product_Name", None))
            if not device_type:
                device_type = "Стационарный ПК"

            # --- "Серийный номер Каспер" ---
            # Проверяем наличие Kaspersky_Serial_Number в PCModel, если нет, используем пустую строку
            kaspersky_serial = self._clean_value(
                getattr(item.PC, "Kaspersky_Serial_Number", None)
            )
            if (
                    not kaspersky_serial
            ):  # Если нет номера, но есть инфа о каспере, можно добавить Да/Нет
                if (
                        self._clean_value(item.PC.Kaspersky_Installation_Attempted).lower()
                        == "да"
                ):
                    kaspersky_serial = "Да"
                else:
                    kaspersky_serial = "Нет"

            excel_rows.append(
                {
                    "Номер УП ИТ № 171": self._clean_value(item.PC.Assigned_IT_Number),
                    "Состав рабочей станции": workstation_composition_display,
                    "Работник": self._clean_value(item.PC.Responsible),
                    "Подразделение": self._clean_value(item.PC.Department),
                    "Корпус": self._clean_value(building),
                    "Комната": self._clean_value(room),
                    "Телефон": self._clean_value(item.PC.Phone),
                    "Тип устройства": device_type,
                    "Характеристики": characteristics_str,
                    "IP адрес": self._clean_value(item.PC.Primary_IP_Address),
                    "MAC адрес": self._clean_value(item.PC.Primary_MAC_Address),
                    "Вид сети": self._clean_value(item.PC.Kaspersky_Network),
                    "ИНВ. номер НИИТП": self._clean_value(
                        item.PC.Inventory_Number_NII_TP
                    ),
                    "Серийный номер": self._clean_value(
                        item.PC.DMI_System_Serial_Number
                    ),
                    "Каспер": (
                        "Да"
                        if self._clean_value(
                            item.PC.Kaspersky_Installation_Attempted
                        ).lower()
                           == "да"
                        else "Нет"
                    ),
                }
            )

        df = pd.DataFrame(excel_rows)

        with pd.ExcelWriter(output_filepath, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Отчет по ПК", index=False)

    def clear_data(self) -> None:
        self.data = []
