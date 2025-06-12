import unittest
from unittest.mock import patch, mock_open

from application.model import Model as TrueModel
from application.base_models import PCModel
from application.model import Model as WrongModel
from application.model import DataParser, FileReader, ParsingUtils, ExcelExporter


class TestFunctions(unittest.TestCase):

    test_file="""
ПК
Присваиваемый номер ИТ 171: 4567
Подразделение: 111
Ответственный: fio
Телефон: +91111
Корпус и комната: 12 корпус 133 комната 
Была ли попытка установки каспера: да
На какую сеть стоит каспер: ru
Инвентарный номер НИИ ТП: 1000000000001
DMI системный серийный номер                      To Be Filled By O.E.M.
Первичный адрес IP                                172.18.240.1
Первичный адрес MAC                               00-15-5D-78-23-E0
-------------------------------------------------------------------------------------
Системная память                                  15989 МБ  (DDR4 SDRAM)
DIMM1: CD4-US08G32M22-01                          8 ГБ DDR4-3200 DDR4 SDRAM  (24-22-22-52 @ 1600 МГц)  (22-22-22-52 @ 1600 МГц)  (21-21-21-49 @ 1527 МГц)  (20-20-20-47 @ 1454 МГц)  (19-19-19-45 @ 1381 МГц)  (18-18-18-42 @ 1309 МГц)  (17-17-17-40 @ 1236 МГц)  (16-16-16-38 @ 1163 МГц)  (15-15-15-35 @ 1090 МГц)  (14-14-14-33 @ 1018 МГц)  (13-13-13-31 @ 945 МГц)  (12-12-12-28 @ 872 МГц)  (11-11-11-26 @ 800 МГц)  (10-10-10-24 @ 727 МГц)
DIMM3: CD4-US08G32M22-01                          8 ГБ DDR4-3200 DDR4 SDRAM  (24-22-22-52 @ 1600 МГц)  (22-22-22-52 @ 1600 МГц)  (21-21-21-49 @ 1527 МГц)  (20-20-20-47 @ 1454 МГц)  (19-19-19-45 @ 1381 МГц)  (18-18-18-42 @ 1309 МГц)  (17-17-17-40 @ 1236 МГц)  (16-16-16-38 @ 1163 МГц)  (15-15-15-35 @ 1090 МГц)  (14-14-14-33 @ 1018 МГц)  (13-13-13-31 @ 945 МГц)  (12-12-12-28 @ 872 МГц)  (11-11-11-26 @ 800 МГц)  (10-10-10-24 @ 727 МГц)
-------------------------------------------------------------------------------------
Тип ЦП                                            HexaCore Intel Core i5-11500, 4400 MHz (44 x 100)
-------------------------------------------------------------------------------------
Системная плата                                   ASRock H510M-H2/M.2 SE
-------------------------------------------------------------------------------------
Дисковый накопитель                               HFS512GEJ9X110N  (476 ГБ)
Дисковый накопитель                               Mass Storage Device USB Device
-------------------------------------------------------------------------------------
Видеоадаптер                                      Intel(R) UHD Graphics 750  (2 ГБ)
-------------------------------------------------------------------------------------
Мониторы
Присваиваемый номер ИТ 171: 4567-01
Монитор                                           Универсальный монитор PnP [NoDB]  (PB6H284100236)  {2024}
Разрешение: ??????
Присваиваемый номер ИТ 171: 4567-02
Монитор                                           Универсальный монитор PnP [NoDB]  (34361)  {2024}
Разрешение: ??????
-------------------------------------------------------------------------------------
ИБП
Присваиваемый номер ИТ 171: 4567-03
-------------------------------------------------------------------------------------
Состав рабочей станции: ПК и 2 монитор(а) и  ИБП
Комментарий: 

    """

    def setUp(self):
        self.right_model = TrueModel()
        self.parser = DataParser()
        self.file_reader = FileReader()
        self.excel_exp = ExcelExporter()
        self.wrong_model = WrongModel(self.file_reader, self.excel_exp)


    @patch("builtins.open", new_callable=mock_open, read_data=test_file)
    def test_func_to_txt(self, mock_file_open):
        self.right_model.load_from_txt("blank")
        self.wrong_model.load_data("blank")
        self.assertEqual(self.right_model.data, self.wrong_model.data)

    @patch("builtins.open", new_callable=mock_open, read_data=test_file)
    def test_pc_parser(self, mock_file_open):
        lines = self.file_reader.read_data_from_file("blank")
        print(lines, "dsa")
        res_true = PCModel(**self.right_model.parse_pc_info(lines))
        res_false = self.parser.parse_pc(lines)
        self.assertEqual(res_true, res_false)

    @patch("builtins.open", new_callable=mock_open, read_data=test_file)
    def test_clean_util(self, mock_file_open):
        label = "DMI системный серийный номер"
        lines = self.file_reader.read_data_from_file("blank", )
        value = self.right_model._get_value(lines, label)

        res_a = self.right_model._clean_value(value, label)
        res_b = ParsingUtils.clean_value(value, label)
        self.assertEqual(res_a, res_b)

    @patch("builtins.open", new_callable=mock_open, read_data=test_file)
    def test_get_value(self, mock_file_open):
        label = "Системная память"
        lines = self.file_reader.read_data_from_file("blank", )

        res_true = self.right_model._get_value(lines, label)
        res_false = ParsingUtils.get_value(lines, label)
        self.assertEqual(res_true, res_false)

    @patch("builtins.open", new_callable=mock_open, read_data=test_file)
    def test_memory_parser(self, mock_file_open):
        lines = self.file_reader.read_data_from_file("blank", )
        res_true = self.right_model.parse_system_memory(lines)
        res_false = self.parser.parse_system_memory(lines)
        self.assertEqual(res_true, res_false)

if __name__ == '__main__':
    unittest.main()
