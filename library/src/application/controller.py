from application.model import Model
from application.view import View
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from typing import List, IO



class FileOpener:
    encodings = ["utf-8", "windows-1251"]

    def __init__(self, filepath: str, encodings=("utf-8", "windows-1251")):
        self.filepath = filepath
        self.encodings = encodings
        self.file_obj: IO | None = None

    def __enter__(self):
        last_exception = None

        for type_encoding in self.encodings:
            try:
                self.file_obj = open(self.filepath, "r", encoding=type_encoding)
                return self.file_obj
            except UnicodeDecodeError as e:
                last_exception = e
                continue
            except OSError as e:
                raise IOError(f"Не удалось прочитать файл {self.filepath}: {e}") from e

        if last_exception:
            raise IOError(
                f"Не удалось прочитать файл {self.filepath} с кодировками UTF-8 или Windows-1251: {last_exception}") from last_exception
        else:
            raise IOError(
                f"Не удалось прочитать файл {self.filepath} с кодировками UTF-8 или Windows-1251."
            )

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_obj:
            self.file_obj.close()

class Controller:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.loaded_file_paths: List[str] = []  # Список полных путей загруженных файлов
        self._connect_signals()

    def _connect_signals(self) -> None:
        self.view.select_button.clicked.connect(self._on_select_files)
        self.view.convert_button.clicked.connect(self._on_convert_to_excel)
        self.view.clear_button.clicked.connect(
            self._on_clear_selected_file
        )

    def _on_select_files(self) -> None:
        self.view.status.setText("Выбор файлов...")
        files, _ = QFileDialog.getOpenFileNames(
            self.view, "Выберите TXT файлы", "", "Text Files (*.txt)"
        )
        if files:
            # Очищаем все предыдущие данные, если выбраны новые файлы
            self.model.clear_data()
            self.loaded_file_paths.clear()
            self.view.file_list.clear()

            self.view.status.setText("Загрузка и парсинг файлов...")

            for file_path in files:
                try:
                    with FileOpener(file_path) as f:
                        self.model.load_data_from_file(f, file_path.split('/')[-1])

                    self.loaded_file_paths.append(
                        file_path
                    )  # Сохраняем путь только для успешно загруженных
                    self.view.file_list.addItem(f"✓ {file_path.split('/')[-1]}")
                except IOError as e:
                    QMessageBox.critical(
                        self.view,
                        "Ошибка чтения файла",
                        f"Не удалось открыть или прочитать файл {file_path.split('/')[-1]}:\n{e}",
                    )
                    self.view.file_list.addItem(
                        f"✗ {file_path.split('/')[-1]} (Ошибка чтения)"
                    )
                except ValueError as e:
                    QMessageBox.critical(
                        self.view,
                        "Ошибка формата данных",
                        f"Файл {file_path.split('/')[-1]} содержит данные неправильного формата:\n{e}",
                    )
                    self.view.file_list.addItem(
                        f"✗ {file_path.split('/')[-1]} (Неверный формат)"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self.view,
                        "Неизвестная ошибка",
                        f"Произошла непредвиденная ошибка при обработке файла {file_path.split('/')[-1]}:\n{e}",
                    )
                    self.view.file_list.addItem(
                        f"✗ {file_path.split('/')[-1]} (Неизвестная ошибка)"
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
            QMessageBox.warning(self.view, "Ошибка", "Выберите файл для удаления.")
            return

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
                    if row < len(
                        self.model.data
                    ):  # Проверяем, чтобы избежать IndexError
                        self.model.data.pop(row)

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
        if not self.model.data:
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
                self.model.export_data(save_path)
                QMessageBox.information(
                    self.view, "Успех", f"Данные успешно сохранены в {save_path}"
                )
                self.view.status.setText(
                    f"Данные сохранены в {save_path}. Данные очищены."
                )
                self.model.clear_data()
                self.loaded_file_paths.clear()
                self.view.file_list.clear()
                self.view.file_list.addItem("Здесь появятся выбранные TXT отчеты...")
            except Exception as e:
                QMessageBox.critical(
                    self.view, "Ошибка сохранения", f"Не удалось сохранить файл:\n{e}"
                )
                self.view.status.setText(f"Ошибка при сохранении: {e}")
        else:
            self.view.status.setText("Сохранение в Excel отменено.")
