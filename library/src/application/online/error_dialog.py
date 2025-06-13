from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QDialog,
)


class ErrorDialog(QDialog):
    retry_button: QPushButton
    exit_button: QPushButton

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ошибка соединения")
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #2C3E50;
                color: #ECF0F1;
            }
            QLabel {
                color: #E74C3C;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton#exitButton {
                background-color: #E74C3C;
            }
            QPushButton#exitButton:hover {
                background-color: #C0392B;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Иконка и текст ошибки
        error_label = QLabel("Ошибка соединения с сервером")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(error_label)

        # Дополнительное описание
        description = QLabel("Проверьте подключение к интернету\nи попробуйте снова")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: #BDC3C7; font-size: 14px;")
        layout.addWidget(description)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.retry_button = QPushButton("Повторить попытку")
        button_layout.addWidget(self.retry_button)

        self.exit_button = QPushButton("Закрыть приложение")
        self.exit_button.setObjectName("exitButton")
        button_layout.addWidget(self.exit_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
