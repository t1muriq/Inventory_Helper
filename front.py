import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QGroupBox, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class JsonToExcelDesign(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON to Excel Converter")
        self.setGeometry(100, 100, 540, 420)
        self.setStyleSheet("""
            QWidget {
                background: #f6f8fa;
            }
            QPushButton {
                background: #1976d2;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 15px;
            }
            QPushButton:hover {
                background: #1565c0;
            }
            QListWidget {
                background: #fff;
                border: 1px solid #cfd8dc;
                border-radius: 6px;
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #90caf9;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                font-weight: bold;
                color: #1976d2;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 18, 24, 18)
        main_layout.setSpacing(16)

        # Заголовок
        title = QLabel("JSON → Excel Converter")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Группа выбора файлов
        file_group = QGroupBox("Выбор файлов")
        file_layout = QVBoxLayout()
        self.select_button = QPushButton("Выбрать JSON файлы")
        self.select_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        file_layout.addWidget(self.select_button)
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(120)
        self.file_list.addItem("Файлы не выбраны")
        file_layout.addWidget(self.file_list)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # Кнопки управления
        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.convert_button = QPushButton("Преобразовать в Excel")
        self.convert_button.setMinimumWidth(180)
        button_layout.addWidget(self.convert_button)
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        main_layout.addLayout(button_layout)

        # Статус-бар
        self.status = QLabel("")
        self.status.setStyleSheet("color: #888; font-size: 13px; padding: 4px;")
        main_layout.addWidget(self.status)

        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JsonToExcelDesign()
    window.show()
    sys.exit(app.exec())