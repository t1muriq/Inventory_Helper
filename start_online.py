from application.view import View
from application.model import Model, FileReader, ExcelExporter
from application.online.controller_network import Controller

from PyQt6.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)

    window = View()
    controller = Controller(window)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
