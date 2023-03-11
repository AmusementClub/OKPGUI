from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow
import sys
from OKPLogic import OKPMainWIndow




 
if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = OKPMainWIndow()
    window.show()
    sys.exit(app.exec())