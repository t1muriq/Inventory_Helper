import psutil
import platform
import wmi
import screeninfo
import subprocess
import json
import os

wmi_available = False
try:
    c = wmi.WMI()
    wmi_available = True
except Exception:
    pass # WMI не будет использоваться, если недоступен

def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if abs(n) >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

def get_monitor_model_from_wmi_powershell():
    cmd = [
        "powershell",
        "-Command",
        "Get-CimInstance -Namespace root\\wmi -ClassName WmiMonitorID | Select-Object InstanceName,ManufacturerName,UserFriendlyName,SerialNumberID | ConvertTo-Json"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=False)
        if result.returncode != 0:
            return [] # Возвращаем пустой список при ошибке, чтобы избежать падения

        data = json.loads(result.stdout)
        
        monitors_info = []
        if isinstance(data, dict): # Для одного монитора
            data = [data]
        
        for item in data:
            name_arr = item.get('UserFriendlyName', [])
            manuf_arr = item.get('ManufacturerName', [])
            serial_arr = item.get('SerialNumberID', [])

            name = ''.join([chr(x) for x in name_arr if x > 0]).strip()
            manuf = ''.join([chr(x) for x in manuf_arr if x > 0]).strip()
            serial = ''.join([chr(x) for x in serial_arr if x > 0]).strip()

            # Форматируем как в example.txt: MUCAI (SGT)
            display_name = name if name else "Неизвестно"
            display_manuf = f" ({manuf})" if manuf else ""
            
            monitors_info.append(f"{display_name}{display_manuf}")
        return monitors_info
    except json.JSONDecodeError:
        return []
    except Exception:
        return []

def check_server_connection(server_address):
    # Проверяет соединение с сервером с помощью команды ping.
    command = ["ping", "-n", "1", "-w", "1000", server_address]
    try:
        # Запускаем команду без вывода на консоль, проверяем код возврата
        result = subprocess.run(command, capture_output=True, check=False)
        return result.returncode == 0
    except Exception:
        return False

def clear_screen():
    # Очищает экран консоли
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Начало опросника и сбора данных пользователя ---
clear_screen()

# Инициализация переменных для распознанной сети
detected_seti_val = "0" # 0: none, 1: ru, 2: in
detected_seti_name = "none"

# Проверка доступного сервера и определение распознанной сети
if check_server_connection("10.7.75.26"):
    detected_seti_val = "2"
    detected_seti_name = "in"
elif check_server_connection("77.88.8.8"):
    detected_seti_val = "1"
    detected_seti_name = "ru"

# Инициализация переменных для отчета (по умолчанию "нет" для Каспера)
inet_vnutr = "0"
seti = "none"

print(f"Было распознано, что комп {detected_seti_name}. Если верно, то 1, если другая, то 2, если сети нет, то 3")
print(f" (seti y PC {detected_seti_name} verno? 1 - da, 2 - drugaya, 3 - netu)")
podtverd_seti = input()
print("\n")

if podtverd_seti == "1": # Пользователь подтвердил распознанную сеть
    inet_vnutr = detected_seti_val
    seti = detected_seti_name
elif podtverd_seti == "2": # Пользователь выбрал "другая"
    input_seti = input("Введите тип сети (ru/in): ").strip().lower()
    if input_seti == "in":
        inet_vnutr = "2"
        seti = "in"
    else: # По умолчанию ru, если не 'in' или некорректный ввод
        inet_vnutr = "1"
        seti = "ru"
elif podtverd_seti == "3": # Нет сети
    inet_vnutr = "3"
    seti = "none"
else: # Если пользователь ввел что-то некорректное, по умолчанию нет сети
    inet_vnutr = "3"
    seti = "none"

clear_screen()
korpus = input("Введите номер корпуса (korpus): ")
print("\n")

room = input("Введите номер комнаты (komnata): ")
print("\n")

FIO = input("Введите ФИО ответственного (FIO): ")
print("\n")

number = input("Введите внутренний телефонный номер ответственного (telefone vnutr.): ")
print("\n")

otdel = input("Введите номер отдела (otdel): ")
print("\n")

it_number = input("Введите присвоенный номер (новый) (4-ciferniy inventarnik): ")
print("\n")
ibp = input("Есть ли ИБП (1 - ДА, другое - НЕТ) (IBP, 1 - est): ")
print("\n")
tip = input("Тип рабочего места (1 - ПК, 2 - МОНОБЛОК, 3 - НОУТБУК, 4 - ДРУГОЕ) (tip rabochego mesta: 1 - pk, 2- monoblock, 3 - noytbyk, 4 - drygoe): ")
print("\n")
invent = input("Введите инвентарный номер (inventarnik): ")
print("\n")
komment = input("Введите комментарий (kommentariy): ")
print("\n")

name = f"{korpus}-{room}-{it_number}"

# --- Сбор характеристик ПК (оставлено без изменений) ---

# Первичный адрес IP
primary_ip = "Не найдено"
for interface, snic_addrs in psutil.net_if_addrs().items():
    for addr in snic_addrs:
        if addr.family == 2 and not addr.address.startswith('127.'):
            primary_ip = addr.address
            break
    if primary_ip != "Не найдено": break

# Первичный адрес MAC (используем getmac)
primary_mac = "Не найдено"
try:
    command = ["getmac", "/nh", "/fo", "csv"]
    result = subprocess.run(command, capture_output=True, text=True, encoding='cp866', check=True)
    lines = result.stdout.strip().split('\n')
    for line in lines:
        parts = line.split(',')
        if parts and len(parts) > 0:
            mac_address = parts[0].strip().replace('\"', '')
            if mac_address and mac_address.lower() != "n/a":
                primary_mac = mac_address.upper()
                break
except Exception as e:
    primary_mac = f"Ошибка получения MAC: {e}"

# Словарь для сопоставления только DDR2, DDR3, DDR4, DDR5
MEMORY_TYPE_DDR_MAP = {
    21: 'DDR2',
    24: 'DDR3',
    26: 'DDR4',
    27: 'DDR5',
}

def get_ddr_type(mem):
    # Получить тип памяти из MemoryType или SMBIOSMemoryType
    mem_type_code = getattr(mem, 'MemoryType', None)
    smbios_type_code = getattr(mem, 'SMBIOSMemoryType', None)
    code = None
    if mem_type_code in MEMORY_TYPE_DDR_MAP:
        code = mem_type_code
    elif smbios_type_code in MEMORY_TYPE_DDR_MAP:
        code = smbios_type_code
    if code:
        return MEMORY_TYPE_DDR_MAP[code]
    return "Unknown"

# Системная память
vm = psutil.virtual_memory()
# Получаем тип памяти по первому модулю (если есть)
system_memory_type = "Unknown"
if wmi_available:
    try:
        mems = c.Win32_PhysicalMemory()
        if mems:
            system_memory_type = get_ddr_type(mems[0])
    except Exception:
        pass
system_memory_info = f"{vm.total // (1024 ** 2)} МБ  ({system_memory_type})"

# Модули памяти (WMI)
dimm_info = []
if wmi_available:
    try:
        for i, mem in enumerate(c.Win32_PhysicalMemory()):
            mem_type = get_ddr_type(mem)
            speed = getattr(mem, 'Speed', None)
            speed_str = f"-{speed}" if speed else ""
            dimm_info.append(f"DIMM{i+1}: {mem.PartNumber.strip()}                          {int(mem.Capacity) // (1024 ** 2)} МБ {mem_type}{speed_str} {mem_type}")
    except Exception:
        dimm_info.append("Не удалось получить данные DIMM через WMI.")
else:
    dimm_info.append("Не удалось получить данные DIMM (WMI недоступен).")

# Тип ЦП
cpu_display_name = platform.processor()
if wmi_available:
    try:
        for cpu in c.Win32_Processor():
            cpu_display_name = cpu.Name
            break
    except Exception:
        pass

# Системная плата
motherboard_info = "WMI недоступна."
if wmi_available:
    try:
        for board in c.Win32_BaseBoard():
            motherboard_info = f"{board.Manufacturer} {board.Product}"
            break
    except Exception:
        motherboard_info = "Не удалось получить данные системной платы через WMI."

# Дисковые накопители
disk_drives_info = []
if wmi_available:
    try:
        disk_drives = c.Win32_DiskDrive()
        if disk_drives:
            for disk in disk_drives:
                disk_drives_info.append(f"Дисковый накопитель                               {disk.Model}  ({int(disk.Size) // (1024 ** 3)} ГБ)")
        else:
            disk_drives_info.append("Дисковый накопитель                               Не найдено")
    except Exception:
        disk_drives_info.append("Дисковый накопитель                               Не удалось получить данные через WMI.")
else:
    disk_drives_info.append("Дисковый накопитель                               WMI недоступен.")

# Видеоадаптеры
gpu_info = []
if wmi_available:
    try:
        gpus = c.Win32_VideoController()
        if gpus:
            for gpu in gpus:
                vram_mb = int(gpu.AdapterRAM) // (1024 ** 2)
                vram_display = f"({vram_mb} МБ)"
                if vram_mb < 0 or vram_mb > 32768: # Если значение подозрительно (более 32ГБ или отрицательное)
                    vram_display = "(Неизвестно)"
                
                gpu_info.append(f"Видеоадаптер                                      {gpu.Name} {vram_display}")
        else:
            gpu_info.append("Видеоадаптер                                      Не найдено")
    except Exception:
        gpu_info.append("Видеоадаптер                                      Не удалось получить данные через WMI.")
else:
    gpu_info.append("Видеоадаптер                                      WMI недоступен.")

# Мониторы
monitor_display_info = []
monitor_wmi_info = get_monitor_model_from_wmi_powershell()
if monitor_wmi_info:
    for info in monitor_wmi_info:
        monitor_display_info.append(f"Монитор                                           {info}")
else:
    monitor_display_info.append("Монитор                                           Неизвестно (WMI/PowerShell)")

monitor_resolution_info = []
monitors = screeninfo.get_monitors()
if monitors:
    for monitor in monitors:
        monitor_resolution_info.append(f"Разрешение: {monitor.width}x{monitor.height}")
else:
    monitor_resolution_info.append("Разрешение: ??????")

# DMI системный серийный номер
dmi_serial = "Не найдено"
if wmi_available:
    try:
        for bios in c.Win32_BIOS():
            serial_num = bios.SerialNumber.strip()
            if not serial_num or serial_num == "To Be Filled By O.E.M.":
                dmi_serial = "DMI системный серийный номер                      НУЖНО ЗАПОЛНИТЬ"
            else:
                dmi_serial = f"DMI системный серийный номер                      {serial_num}"
            break
    except Exception:
        dmi_serial = "DMI системный серийный номер                      Не удалось получить через WMI."
else:
    dmi_serial = "DMI системный серийный номер                      WMI недоступен."


# --- Формирование итогового отчёта ---

final_report_content = []

tip1 = ""
if tip == "1":
    tip1 = "ПК"
elif tip == "2":
    tip1 = "Моноблок"
elif tip == "3":
    tip1 = "Ноутбук"
elif tip == "4":
    tip1 = "Другое"
final_report_content.append(tip1)

final_report_content.append(f"Присваиваемый номер ИТ 171: {it_number}")
final_report_content.append(f"Подразделение: {otdel}")
final_report_content.append(f"Ответственный: {FIO}")
final_report_content.append(f"Телефон: {number}")
final_report_content.append(f"Корпус и комната: {korpus} корпус {room} комната ")
final_report_content.append(f"Была ли попытка установки каспера: нет")
final_report_content.append(f"На какую сеть стоит каспер: {seti}")
final_report_content.append(f"Инвентарный номер НИИ ТП: {invent}")
final_report_content.append(dmi_serial)
final_report_content.append(f"Первичный адрес IP                                {primary_ip}")
final_report_content.append(f"Первичный адрес MAC                               {primary_mac}")

final_report_content.append("-------------------------------------------------------------------------------------")

final_report_content.append(f"Системная память                                  {system_memory_info}")
final_report_content.extend(dimm_info)

final_report_content.append("-------------------------------------------------------------------------------------")
final_report_content.append(f"Тип ЦП                                            {cpu_display_name}")

final_report_content.append("-------------------------------------------------------------------------------------")
final_report_content.append(f"Системная плата                                   {motherboard_info}")

final_report_content.append("-------------------------------------------------------------------------------------")
final_report_content.extend(disk_drives_info)

final_report_content.append("-------------------------------------------------------------------------------------")
final_report_content.extend(gpu_info)

final_report_content.append("-------------------------------------------------------------------------------------")

# Мониторы
monitor_counter = 1
if tip == "1" or tip == "2" or tip == "4": 
    final_report_content.append("Мониторы")
    for i, info in enumerate(monitor_display_info):
        final_report_content.append(f"Присваиваемый номер ИТ 171: {it_number}-0{monitor_counter}")
        final_report_content.append(info)
        if i < len(monitor_resolution_info):
            final_report_content.append(monitor_resolution_info[i])
        else:
            final_report_content.append("Разрешение: ??????")
        monitor_counter += 1

if tip == "1" or tip == "2" or tip == "4": 
    final_report_content.append("-------------------------------------------------------------------------------------")

if ibp == "1":
    final_report_content.append("ИБП")
    final_report_content.append(f"Присваиваемый номер ИТ 171: {it_number}-0{monitor_counter}")
    monitor_counter += 1 
    final_report_content.append("-------------------------------------------------------------------------------------")


# Состав рабочей станции
j = len(monitor_display_info) if (tip == "1" or tip == "4") else (len(monitor_display_info) if (tip == "2") else 0)
g = 1 if ibp == "1" else 0

composition_string = f"Состав рабочей станции: {tip1}"
if tip == "1" or tip == "4":
    if j > 0:
        composition_string += f" и {j} монитор(а)"
elif tip == "2" and j > 0:
    composition_string += f" и {j} монитор(а)"

if ibp == "1":
    composition_string += " и  ИБП"
final_report_content.append(composition_string)

final_report_content.append(f"Комментарий: {komment}")

# --- Сохранение отчёта ---

report_dir = os.path.join(os.getcwd(), "reports")
os.makedirs(report_dir, exist_ok=True)

output_file_path = os.path.join(report_dir, f"{name}.txt")

# Проверка существования файла и запрос перезаписи
vibor1 = "1" 
if os.path.exists(output_file_path):
    print(f"Такой файл ({output_file_path}) уже существует! Хотите перезаписать? (perezapisat\' 1 - da, 2 - net)")
    print("1 - ДА, другое - НЕТ")
    vibor1 = input()
    if vibor1 != "1":
        print("Операция отменена.")
        exit()

with open(output_file_path, "w", encoding='utf-8') as f:
    for line in final_report_content:
        f.write(line + '\n')

print(f"Данные успешно обработаны и записаны в файл: {output_file_path}")

print("\n--- Отчет успешно создан ---\n")
input("Нажмите Enter для выхода...") 