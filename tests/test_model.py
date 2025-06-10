import unittest
from application.model import Model
from unittest.mock import patch, mock_open, MagicMock


class TestModel(unittest.TestCase):

    def setUp(self):
        self.model = Model()

    @patch("builtins.open", new_callable=mock_open, read_data="Строка 1\nСтрока 2\n---\nСтрока 3")
    def test_load_from_txt_utf8_success(self, mock_file_open: MagicMock):
        """Тест успешного чтения файла в UTF-8"""
        self.model.load_from_txt("mock_path")
        mock_file_open.assert_called_once_with("mock_path", "r", encoding="utf-8")
        self.assertEqual(
            self.model.data
        )


if __name__ == "__main__":
    unittest.main()
