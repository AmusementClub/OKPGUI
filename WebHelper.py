import sys

from PyQt6.QtCore import QUrl, QByteArray, QSize, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWidgets import QApplication, QTextEdit, QPushButton, QToolBar, QMainWindow, QDialog, QWidget, QVBoxLayout
from PyQt6.QtNetwork import QNetworkCookie, QNetworkProxy
from PyQt6.QtGui import QAction
from urllib import parse
import traceback
import datetime


def bytestostr(data):
    if isinstance(data, str):
        return data
    if isinstance(data, QByteArray):
        data = data.data()
    if isinstance(data, bytes):
        data = data.decode(errors='ignore')
    else:
        data = str(data)
    return data

def cookiesToStr(cookie: QNetworkCookie):
    domain = cookie.domain()
    path = cookie.path()
    name = bytestostr(cookie.name().data())
    value = bytestostr(cookie.value().data())

    flags = []
    flags.append(f"{name}={value}")
    flags.append(f"domain={domain}")
    flags.append(f"path={path}")

    if cookie.isSecure(): flags.append("Secure")
    if cookie.isHttpOnly(): flags.append("HttpOnly")
    match cookie.sameSitePolicy():
        case QNetworkCookie.SameSite.Default:
            pass
        case QNetworkCookie.SameSite.Lax:
            flags.append("SameSite=Lax")
        case QNetworkCookie.SameSite.Strict:
            flags.append("SameSite=Strict")
        case QNetworkCookie.SameSite.None_:
            flags.append("SameSite=None")

    #now2 = datetime.datetime.fromisoformat(now.toString(Qt.DateFormat.ISODate))
    #strftime("%a, %d %b %Y %H:%M:%S %Z")
    if not cookie.isSessionCookie():
        time = cookie.expirationDate().toString(Qt.DateFormat.ISODate)
        time = datetime.datetime.fromisoformat(time).strftime("%a, %d %b %Y %H:%M:%S GMT") 
        flags.append(f"expires={time}")

    flags = "; ".join(flags)
    
    return f"https://{domain}\t{flags}"

def filterCookies(cookie: QNetworkCookie) -> bool:
    if cookie.domain() == "share.dmhy.org":
        if bytestostr(cookie.name().data()) in {"pass", "rsspass", "tid", "uname", "uid"}:
            return True
    if cookie.domain() == "nyaa.si":
        if bytestostr(cookie.name().data()) == "session":
            return True
    if cookie.domain() == "acg.rip":
        if bytestostr(cookie.name().data()) == "remember_user_token":
            return True
    if cookie.domain() == "bangumi.moe":
        if bytestostr(cookie.name().data()) in {"locale", "koa:sess", "koa:sess.sig"}:
            return True
    return False


class WebEngineView(QWidget):

    def __init__(self, url, parentWindow, *args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)
        QWebEngineProfile.defaultProfile().cookieStore().cookieAdded.connect(self.onCookieAdd)
        self.resize(1920, 600)
        self.parentWindow = parentWindow
        self.browser = QWebEngineView()
        self.browser.loadFinished.connect(self.onLoadFinished)
        

        vbox = QVBoxLayout(self)


        toolbar = QToolBar('toolbar')
        self.saveButton = QAction("保存 cookies", parent=self)
        backButton = QAction("后退", parent=self)
        refreshButton = QAction("刷新", parent=self)

        backButton.triggered.connect(self.browser.back)
        refreshButton.triggered.connect(self.browser.reload)
        self.saveButton.triggered.connect(self.saveCookies)

        toolbar.addAction(backButton)
        toolbar.addAction(refreshButton)
        toolbar.addAction(self.saveButton)

        self.cookies = []
        vbox.addWidget(toolbar)
        vbox.addWidget(self.browser)
        self.setLayout(vbox)

        if parentWindow.menuProxyType.currentText == "HTTP":
            parsed = parse.urlparse(self.parentWindow.profile['proxy'])
            self.proxy = QNetworkProxy(QNetworkProxy.ProxyType.HttpProxy, hostName=parsed.hostname, port=parsed.port)
            QNetworkProxy.setApplicationProxy(self.proxy)

        
        self.browser.load(url)


    def closeEvent(self, event):
        self.parentWindow.addCookies("\n".join(self.cookies))
        self.parentWindow.setUserAgent(self.browser.page().profile().httpUserAgent())
        self.parentWindow.saveProfile()
        super(WebEngineView, self).closeEvent(event)

    def onLoadFinished(self):
        pass

    def onCookieAdd(self, cookie:QNetworkCookie):
        if filterCookies(cookie):
            self.cookies.append(cookiesToStr(cookie))
        

    def saveCookies(self):
        self.close()


    
