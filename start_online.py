import sys

from PyQt6.QtWidgets import QApplication

from application.online.controller_network import Controller
from application.view import View


def main():
    app = QApplication(sys.argv)

    window = View()
    controller = Controller(window, "http://localhost:8000")

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
