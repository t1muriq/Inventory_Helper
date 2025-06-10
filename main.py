from application.view import View
from application.new_model.refactor_model import Model, FileReader, ExcelExporter
from application.controller import Controller

from PyQt6.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)

    window = View()
    model = Model(FileReader(), ExcelExporter())
    controller = Controller(model, window)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
