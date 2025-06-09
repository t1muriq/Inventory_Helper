# from openpyxl import Workbook

# import json

# # # Создаем новую книгу и выбираем активный лист
# # wb = Workbook()
# # ws = wb.active

# # # Записываем данные
# # ws['A1'] = "Имя"
# # ws['B5'] = "Возраст"
# # ws['C1'] = "Город"

# # ws.append(["Алексей", 25])
# # ws.append(["Мария", 30])

# # # Сохраняем файл
# # wb.save("example.xlsx")


# with open('example.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)

# print(data['PC']['Assigned_IT_Number'])

# from PyQt5.QtWidgets import QFileDialog, QMessageBox

import pandas as pd
import json

from pydantic import BaseModel
from typing import List, Optional

class Person(BaseModel):
    name: str
    age: int
    email: Optional[str]
    skills: List[str]


files = ['test.json']
people = []
for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                people.extend([Person(**item) for item in data])
            else:
                people.append(Person(**data))
    except Exception as e:
        print(f"Ошибка в файле {file}:\n{e}")

df = pd.DataFrame([{
    'name': p.name,
    'age': p.age,
    'email': p.email,
    'skills': '\n'.join(p.skills)
} for p in people])

df.to_excel("output.xlsx", index=False)