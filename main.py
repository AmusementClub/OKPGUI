import sys

from PyQt6.QtWidgets import QApplication
from OKPLogic import OKPMainWIndow
import platform


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if platform.system() != "Windows":
        app.setStyle('Fusion')

    window = OKPMainWIndow()
    window.show()
    sys.exit(app.exec())
