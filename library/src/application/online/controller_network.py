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

        self.loaded_file_paths: List[str] = []  # Список полных путей загруженных файлов

        self.server_url = server_url
        self.current_session = None

        self._create_session()
        self._connect_signals()

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

    def _on_select_files(self) -> None:
        self.view.status.setText("Выбор файлов...")
        files, _ = QFileDialog.getOpenFileNames(
            self.view, "Выберите TXT файлы", "", "Text Files (*.txt)"
        )
        if files:

            items = self.view.file_list.findItems(
                "Здесь появятся выбранные TXT отчеты...", Qt.MatchFlag.MatchExactly
            )
            for item in items:
                row = self.view.file_list.row(item)
                self.view.file_list.takeItem(row)

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

                    self.loaded_file_paths.append(
                        file_path
                    )  # Сохраняем путь только для успешно загруженных
                    self.view.file_list.addItem(f"✓ Рабочая станция: {response.json()["it_num"]} (Загружена из файла: {file_path.split('/')[-1]})")
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

            if not self.loaded_file_paths:  # Если ни один файл не загрузился успешно
                self.view.file_list.addItem(
                    "Здесь появятся выбранные TXT отчеты..."
                )  # Снова placeholder
                self.view.status.setText("Нет файлов для загрузки или все с ошибками.")
            else:
                self.view.status.setText(
                    f"Успешно загружено {len(self.loaded_file_paths)} файлов."
                )
        else:
            self.view.status.setText("Выбор файлов отменён.")

    def _on_clear_selected_file(self) -> None:
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

                self.loaded_file_paths.clear()
                self.view.file_list.clear()
        else:
            reply = QMessageBox.question(
                self.view,
                "Подтверждение",
                "Вы действительно хотите удалить выделенный файл из списка?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                for item in selected_items:

                    row = self.view.file_list.row(item)
                    if 0 <= row < len(self.loaded_file_paths):
                        # Удаляем из внутренних списков
                        removed_path = self.loaded_file_paths.pop(row)
                        # Удаляем соответствующий объект из модели по индексу

                        response = requests.get(self.server_url + "/data/length", headers=self.current_session)

                        if response.ok:
                            if row < response.json():  # Проверяем, чтобы избежать IndexError
                                response = requests.delete(self.server_url + f"/data/{row}", headers=self.current_session)

                                if not response.ok:
                                    self._show_error_dialog()
                                    return

                        else:
                            self._show_error_dialog()
                            return

                        # Удаляем из GUI списка
                        self.view.file_list.takeItem(row)
                        self.view.status.setText(
                            f"Файл {removed_path.split('/')[-1]} удален. Обновлено: {len(self.loaded_file_paths)} файлов."
                        )
                    else:
                        self.view.status.setText(
                            "Ошибка: выбранный файл не найден во внутренних данных."
                        )

        if not self.loaded_file_paths:  # Если список стал пустым после удаления
            self.view.file_list.addItem("Здесь появятся выбранные TXT отчеты...")
            self.view.status.setText("Список файлов пуст.")

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
