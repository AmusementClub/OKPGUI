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


if __name__ == "__main__":
    request= """
![](https://p.sda1.dev/9/bfe103bd0e51cce16697e7e6ebf0537d/Onimai%20Poster%20v2.jpg)  


**字幕: SweetSub**

**脚本: sinsanction@LoliHouse**

**压制: Jalapeño@LoliHouse**

**本片与 SweetSub 合作，感谢字幕组的辛勤劳动。**

&nbsp;


---

&nbsp;

是采用 Abema 源的无修版。

&nbsp;

---

&nbsp;

欢迎大家关注 SweetSub 的 [telegram 频道](https://t.me/SweetSub) 。

SweetSub 新开设了 [提问箱](https://marshmallow-qa.com/sweetsub)，大家对字幕组有什么好奇的，或是有报错，都可以来此提问。问题的回答会发布在 telegram 频道中。

[点此下载字幕文件](https://github.com/tastysugar/SweetSub)

&nbsp;

---
&nbsp;

SweetSub 的字幕在二次使用时默认遵从 [知识共享 署名-非商业性使用-禁止演绎 4.0 许可协议](https://creativecommons.org/licenses/by-nc-nd/4.0/) （Creative Common BY-NC-ND 4.0） ，在遵循规则的情况下可以在不需要与我联系的情况下自由转载、使用。  
但是，对于调整时间轴用于匹配自己的不同片源的小伙伴，可以例外在署名、非商业使用的情况下，调整时间轴，不需要与我联系，自由转载、使用。   
如果对字幕做了除了调整时间轴以外的修改，请不要公开发布，留着自己看就好，谢谢。   
详细说明请 [点击这里查看](https://github.com/SweetSub/SweetSub#%E8%BD%AC%E8%BD%BD%E5%8F%8A%E5%86%8D%E5%88%A9%E7%94%A8%E8%AF%B4%E6%98%8E)

&nbsp;
---
&nbsp;

**为了顺利地观看我们的作品，推荐大家使用以下播放器：**

**Windows：[mpv](https://mpv.io/)（[教程](https://vcb-s.com/archives/7594)）**

**macOS：[IINA](https://iina.io/)**

**iOS/Android：[VLC media player](https://www.videolan.org/vlc/)**


---
&nbsp;

**[点击查看LoliHouse五周年纪念公告（附往年全部礼包）](https://share.dmhy.org/topics/view/599634_LoliHouse_LoliHouse_5th_Anniversary_Announcement.html)**
    """

    w = MarkdownViewWindow(html=request,parentWindow=None)
    w.show()