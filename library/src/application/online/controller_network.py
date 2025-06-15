from PyQt6.QtCore import Qt

from application.online.error_dialog import ErrorDialog
from application.view import View

from PyQt6.QtWidgets import QFileDialog, QMessageBox
from typing import List, IO
import requests
import sys


class FileOpener:
    encodings = ["utf-8", "windows-1251"]

    def __init__(self, filepath: str, open_mode='r', encodings=("utf-8", "windows-1251")):
        self.filepath = filepath
        self.open_mode = open_mode
        self.encodings = encodings
        self.file_obj: IO | None = None

    def __enter__(self):
        try:
            self.file_obj = open(self.filepath, self.open_mode)
            return self.file_obj
        except OSError as e:
            raise IOError(f"Не удалось прочитать файл {self.filepath}: {e}") from e


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_obj:
            self.file_obj.close()

class Controller:
    def __init__(self, view: View, server_url) -> None:
        self.view = view
        self.view.set_on_close_handler(self._close_app)

        self.server_url = server_url
        self.current_session = None

        self._create_session()
        self._connect_signals()
        self._update_list()

    def _connect_signals(self) -> None:
        self.view.select_button.clicked.connect(self._on_select_files)
        self.view.convert_button.clicked.connect(self._on_convert_to_excel)
        self.view.clear_button.clicked.connect(
            self._on_clear_selected_file
        )

    def _create_session(self) -> bool:
        response = requests.post(self.server_url + "/session/create")
        if response.ok:
            self.current_session = {"authorization": response.json()["session_id"]}
            return True
        return False

    def _show_error_dialog(self) -> None:
        dialog = ErrorDialog()
        dialog.retry_button.clicked.connect(lambda: self._try_reconnect(dialog))
        dialog.exit_button.clicked.connect(self._close_app)
        dialog.exec()

    def _try_reconnect(self, dialog: ErrorDialog):
        success = self._create_session()
        if success:
            dialog.close()

    def _close_app(self) -> None:
        requests.delete(self.server_url + "/session/close", headers=self.current_session)
        sys.exit()

    def _update_list(self) -> None:
        self.view.file_list.clear()

        response = requests.get(self.server_url + "/data", headers=self.current_session)
        if not response.ok:
            self._show_error_dialog()
            return

        if not response.json():
            self.view.file_list.addItem("Здесь появятся выбранные TXT отчеты...")
            return

        for elem in response.json():
            if elem["metadata"]["source"] == "file":
                self.view.file_list.addItem(
                    f"✓ Рабочая станция: {elem['system_data']['PC']['Assigned_IT_Number']} "
                    f"(Загружена из файла: {elem['metadata']['filename']})"
                )
            elif elem["metadata"]["source"] == "cloud":
                raise ValueError("Данный метод еще не реализован")

    def _on_select_files(self) -> None:
        self.view.status.setText("Выбор файлов...")
        files, _ = QFileDialog.getOpenFileNames(
            self.view, "Выберите TXT файлы", "", "Text Files (*.txt)"
        )
        if files:

            self.view.status.setText("Загрузка и парсинг файлов...")

            for file_path in files:
                try:
                    with FileOpener(file_path, open_mode='rb') as f:
                        response = requests.post(self.server_url + "/data/file", files={"file": f}, headers=self.current_session)

                        if response.status_code == 422:
                            raise ValueError(response.text)
                        elif not response.ok:
                            self._show_error_dialog()
                            return

                except IOError as e:
                    QMessageBox.critical(
                        self.view,
                        "Ошибка чтения файла",
                        f"Не удалось открыть или прочитать файл {file_path.split('/')[-1]}:\n{e}",
                    )
                except ValueError as e:
                    QMessageBox.critical(
                        self.view,
                        "Ошибка формата данных",
                        f"Файл {file_path.split('/')[-1]} содержит данные неправильного формата:\n{e}",
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self.view,
                        "Неизвестная ошибка",
                        f"Произошла непредвиденная ошибка при обработке файла {file_path.split('/')[-1]}:\n{e}",
                    )

            self.view.status.setText(
                f"Файлы успешно загружены"
            )
            self._update_list()
        else:
            self.view.status.setText("Выбор файлов отменён.")

    def _on_clear_selected_file(self) -> None:
        response = requests.get(self.server_url + "/data/length", headers=self.current_session)
        if not response.ok:
            self._show_error_dialog()
            return

        if response.json() <= 0:
            QMessageBox.warning(self.view, "Нет данных для удаления", "Сначала загрузите данные.")
            self.view.status.setText("Операция отменена: нет данных для удаления.")
            return

        selected_items = self.view.file_list.selectedItems()
        if not selected_items:
            reply = QMessageBox.question(
                self.view,
                "Подтверждение",
                "Вы действительно хотите удалить все файлы",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                response = requests.delete(self.server_url + "/data", headers=self.current_session)
                if not response.ok:
                    self._show_error_dialog()
                    return
                self.view.status.setText("Все записи удалены")

        else:
            reply = QMessageBox.question(
                self.view,
                "Подтверждение",
                "Вы действительно хотите удалить выделенные файлы из списка?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                for item in selected_items:

                    row = self.view.file_list.row(item)
                    response = requests.delete(self.server_url + f"/data/{row}", headers=self.current_session)

                    if not response.ok:
                        self._show_error_dialog()
                        return
            self.view.status.setText("Выделенные записи удалены")

        self._update_list()

    def _on_convert_to_excel(self) -> None:

        response = requests.get(self.server_url + "/data/length", headers=self.current_session)
        if not response.ok:
            self._show_error_dialog()
            return

        length_data = response.json()

        if length_data == 0:
            QMessageBox.warning(self.view, "Нет данных", "Сначала загрузите TXT файлы.")
            self.view.status.setText("Операция отменена: нет данных для экспорта.")
            return

        self.view.status.setText("Сохранение в Excel...")
        save_path, _ = QFileDialog.getSaveFileName(
            self.view,
            "Сохранить Excel файл",
            "Отчет_инвентаризации.xlsx",
            "Excel Files (*.xlsx)",
        )

        if save_path:
            try:
                response = requests.get(self.server_url + "/data/file", headers=self.current_session)
                if not response.ok:
                    self._show_error_dialog()
                    return

                with open(save_path, "wb") as f:
                    f.write(response.content)

                QMessageBox.information(
                    self.view, "Успех", f"Данные успешно сохранены в {save_path}"
                )
                self.view.status.setText(
                    f"Данные сохранены в {save_path}."
                )

            except Exception as e:
                QMessageBox.critical(
                    self.view, "Ошибка сохранения", f"Не удалось сохранить файл:\n{e}"
                )
                self.view.status.setText(f"Ошибка при сохранении: {e}")
        else:
            self.view.status.setText("Сохранение в Excel отменено.")
