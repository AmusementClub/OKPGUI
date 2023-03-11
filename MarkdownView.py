import sys

from PyQt6.QtCore import QUrl, QByteArray, QSize
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWidgets import QApplication, QTextEdit, QPushButton, QToolBar, QMainWindow, QDialog, QWidget, QVBoxLayout
from PyQt6.QtNetwork import QNetworkCookie, QNetworkCookieJar
from PyQt6.QtGui import QAction
from urllib import parse

class MarkdownViewWindow(QWidget):
    def __init__(self, html, parentWindow, *args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)

        self.resize(1200, 1080)
        self.parentWindow = parentWindow
        self.setWindowTitle("Preview")

        self.browser = QWebEngineView()
        #self.browser.loadFinished.connect(self.onLoadFinished)
        self.browser.setHtml(html)

        vbox = QVBoxLayout(self)


        # toolbar = QToolBar('toolbar')
        # self.saveButton = QAction("保存", parent=self)
        # saveCloseButton = QAction("保存并关闭", parent=self)
        # closeButton = QAction("关闭", parent=self)

        # # saveCloseButton.triggered.connect()
        # # closeButton.triggered.connect()
        # # self.saveButton.triggered.connect()

        # toolbar.addAction(saveCloseButton)
        # toolbar.addAction(closeButton)
        # toolbar.addAction(self.saveButton)


        # #self.cookiesJar = dict() # key: (domain, name) value: cookies(QNetworkCookie)
        # self.cookies = []
        # vbox.addWidget(toolbar)
        vbox.addWidget(self.browser)
        self.setLayout(vbox)
