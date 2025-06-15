import sys

from PyQt6.QtWidgets import QApplication

from application.online.controller_network import Controller
from application.view import View


def main():
    app = QApplication(sys.argv)

    window = View()
    controller = Controller(window, "http://127.0.0.1:8000", update_time=10000)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
