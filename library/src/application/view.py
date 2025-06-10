import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QLabel,
    QGroupBox,
    QSizePolicy,
    QSpacerItem,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class View(QWidget):
    select_button: QPushButton
    file_list: QListWidget
    convert_button: QPushButton
    clear_button: QPushButton
    status: QLabel

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система инвентаризации НИИ ТП")
        self.setGeometry(100, 100, 600, 480)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2C3E50; /* Темно-синий фон */
                color: #ECF0F1; /* Светлый текст */
                font-family: Arial, sans-serif;
            }
            QLabel#mainTitle {
                color: #3498DB; /* Голубой для заголовков */
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 15px;
            }
            QGroupBox {
                border: 1px solid #34495E; /* Темная граница */
                border-radius: 8px;
                margin-top: 10px;
                background-color: #34495E; /* Темный фон для групп */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #BDC3C7; /* Светло-серый для заголовков групп */
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton {
                background-color: #3498DB; /* Голубой для кнопок */
                color: white;
                border-radius: 6px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2980B9; /* Темнее при наведении */
            }
            QPushButton#clearButton {
                background-color: #E74C3C; /* Красный для кнопки очистки */
            }
            QPushButton#clearButton:hover {
                background-color: #C0392B;
            }
            QListWidget {
                background-color: #2D3E50; /* Темный фон списка */
                border: 1px solid #34495E; /* Темная рамка */
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                color: #ECF0F1;
            }
            QLabel#statusLabel {
                background-color: #34495E; /* Темный фон для статуса */
                border: 1px solid #2C3E50;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
                color: #BDC3C7;
            }
        """
        )

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        # Заголовок приложения
        title_label = QLabel("Система инвентаризации НИИ ТП")
        title_label.setObjectName("mainTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Группа для выбора файлов
        file_selection_group = QGroupBox("Загрузка отчетов инвентаризации (.txt)")
        file_selection_layout = QVBoxLayout()
        self.select_button = QPushButton("Выбрать файлы отчетов инвентаризации")
        self.select_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        file_selection_layout.addWidget(self.select_button)
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(150)
        self.file_list.addItem("Здесь появятся выбранные TXT отчеты...")
        file_selection_layout.addWidget(self.file_list)
        file_selection_group.setLayout(file_selection_layout)
        main_layout.addWidget(file_selection_group)

        # Группа для действий (кнопки)
        actions_group = QGroupBox("Действия с данными")
        actions_layout = QHBoxLayout()
        actions_layout.addSpacerItem(
            QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        self.convert_button = QPushButton("Сформировать итоговый Excel отчет")
        actions_layout.addWidget(self.convert_button)

        self.clear_button = QPushButton("Очистить выбранные файлы")
        self.clear_button.setObjectName("clearButton")
        actions_layout.addWidget(self.clear_button)

        actions_layout.addSpacerItem(
            QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        actions_group.setLayout(actions_layout)
        main_layout.addWidget(actions_group)

        # Статус-бар
        self.status = QLabel("Приложение готово к работе.")
        self.status.setObjectName("statusLabel")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status)

        main_layout.addStretch(1)

        self.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = View()
    window.show()
    sys.exit(app.exec())
