from application.view import View
from application.model import Model
from application.controller import Controller

from PyQt6.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)

    window = View()
    model = Model()
    controller = Controller(model, window)

    window.show()
    sys.exit(app.exec())


if __name__  == "__main__":
    main()
