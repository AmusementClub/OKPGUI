import sys

from PyQt6.QtWidgets import QApplication
from OKPLogic import OKPMainWIndow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Windows')

    window = OKPMainWIndow()
    window.show()
    sys.exit(app.exec())
