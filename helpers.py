from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QLineEdit
import sys
from OKPUI import Ui_MainWindow

def pathDragEnterEvent(obj, placeholderText):
    def dragEnter(event):
        if event.mimeData().hasUrls():
            event.accept()
            obj.setPlaceholderText(placeholderText)
        else:
            event.ignore()
    return dragEnter

def pathDropEvent(obj, mainWindow):
    def drop(event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        obj.setText(files[0])
        mainWindow.setTitleText()
    return drop

def pathDragLeaveEvent(obj, placeholderText):
    def helper(event):
        obj.setPlaceholderText(placeholderText)
    return helper