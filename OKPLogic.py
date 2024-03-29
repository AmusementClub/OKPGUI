from PyQt6.QtCore import (
    QUrl, 
    QProcess, 
    Qt, 
    QFileInfo,
)
from PyQt6.QtWidgets import (
    QApplication, 
    QWidget, 
    QMainWindow, 
    QFileDialog, 
    QDialog,
    QTreeWidgetItem, 
    QFileIconProvider, 
    QStyle,
)
import sys
from OKPUI import Ui_MainWindow
from WarningDialog import Ui_Dialog
import yaml
from pathlib import Path
from WebHelper import WebEngineView
import re
import markdown
from MarkdownView import MarkdownViewWindow
import toml
from html2phpbbcode.parser import HTML2PHPBBCode
from collections import defaultdict
import torrent_parser as tp
from ProcessWindow import MyConsole
import platform

VERSION = "v0.1.7 Beta"

CATEGORY = {
    'Anime': ['Default', 'MV', 'TV', 'Movie', 'Collection', 'Raw', 'English'],
    'Music': ['Default', 'Lossless', 'Lossy', 'ACG', 'Doujin', 'Pop'],
    'Comic': ['Default', 'HongKong', 'Taiwan', 'Japanese', 'English'],
    'Novel': ['Default', 'HongKong', 'Taiwan', 'Japanese', 'English'],
    'Action': ['Default', 'Idol', 'TV', 'Movie', 'Tokusatsu', 'Show', 'Raw', 'English'],
    'Picture': ['Default', 'Graphics', 'Photo'],
    'Software': ['Default', 'App', 'Game']
}

TEMPLATE_CONFIG = Path("okpgui_config.yml")
PROFILE_CONFIG = Path("okpgui_profile.yml")

class OKPerror(Exception):
    pass

class OKPMainWIndow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.setupUi2()
        if not Path("OKP.Core.exe").exists():
            self.warning("找不到 OKP.Core.exe，请将本程序复制到 OKP.Core.exe 同目录下。")
            sys.exit(1)
    
    def setupUi2(self):
        # set title
        self.setWindowTitle("OKPGUI by AmusementClub " + VERSION)

        self.textAboutProgram.setText(f"""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li {{ white-space: pre-wrap; }}
</style></head><body style=" font-family:'Microsoft YaHei UI'; font-size:12pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">此软件为 <a href="https://github.com/AmusementClub/OKP"><span style=" text-decoration: underline; color:#0000ff;">OKP</span></a> 的 GUI，由<a href="https://github.com/AmusementClub"><span style=" text-decoration: underline; color:#0000ff;">娱乐部</span></a>制作，用于快速在多个 BT 资源站发布种子。</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">使用方法参见 GitHub 上的 <a href="https://github.com/AmusementClub/OKPGUI"><span style=" text-decoration: underline; color:#0000ff;">README</span></a>。</p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Version: {VERSION}</p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">作者：<a href="https://github.com/tastysugar"><span style=" text-decoration: underline; color:#0000ff;">tastySugar</span></a></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html>
                                      """)

        # Select torrent
        self.buttonBrowse.clicked.connect(self.selectTorrentFile)
        
        self.HomeTab.setAcceptDrops(True)
        self.tab.currentChanged.connect(self.changeTabHandler)
        # self.textTorrentPath.setAcceptDrops(True)
        self.HomeTab.dragEnterEvent = self.onDragEnterEvent
        self.HomeTab.dropEvent = self.onDropEvent
        self.HomeTab.dragLeaveEvent = self.onDragLeaveEvent
        self.textTorrentPath.textChanged.connect(self.loadTorrent)


        # Select template
        self.reloadProfile()

        self.reloadTemplate()
        self.updateTemplate()
        self.selectCookiesChangeHandler(self.menuSelectCookies.currentText())

        self.loadProxy()

        # Save / Delete template
        self.buttonSaveTemplate.clicked.connect(self.saveTemplate)
        self.buttonDeleteTemplate.clicked.connect(self.deleteTemplate)


        # preview markdown
        self.buttonPreviewMarkdown.clicked.connect(self.previewMarkdown)
        #self.textDescription.setMarkdown(self.textDescription.toPlainText())

        self.textEpPattern.textEdited.connect(self.setTitleText)
        self.textTitlePattern.textEdited.connect(self.setTitleText)

        self.menuSelectCookies.currentTextChanged.connect(self.selectCookiesChangeHandler)

        self.fileTree.setColumnWidth(0,450)

        # tab 2 login
        self.buttonDmhyLogin.clicked.connect(self.loginWebsite("https://share.dmhy.org/user/login"))
        self.buttonNyaaLogin.clicked.connect(self.loginWebsite("https://nyaa.si/login"))
        self.buttonAcgripLogin.clicked.connect(self.loginWebsite("https://acg.rip/users/sign_in"))
        self.buttonBangumiLogin.clicked.connect(self.loginWebsite("https://bangumi.moe/"))

        self.textNyaaName.setDisabled(True)


        self.buttonSaveProfile.clicked.connect(self.saveProfile)
        self.buttonDeleteProfile.clicked.connect(self.deleteProfile)

        self.menuProxyType.currentTextChanged.connect(self.onProxySelection)
        self.onProxySelection()

        self.buttonSaveProxy.clicked.connect(self.saveProxy)

        self.textAcgnxasiaToken.textEdited.connect(self.applyAcgnxasiaAPIToken)
        self.textAcgnxglobalToken.textEdited.connect(self.applyAcgnxglobalAPIToken)
        self.textCookies.textChanged.connect(self.onCookiesChange)

        # publish button
        self.buttonOKP.clicked.connect(self.publishRun)

    def changeTabHandler(self, event):
        if event == 1:
            self.reloadProfile()
        if event == 2:
            self.loadProxy()

    def onDragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.textTorrentPath.setPlaceholderText("请在此释放鼠标")
        else:
            event.ignore()

    def onDropEvent(self, event):
        self.textTorrentPath.setPlaceholderText("可直接 .torrent 文件拖放到此处")
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.textTorrentPath.setText(files[0])

    def onDragLeaveEvent(self, evet):
        self.textTorrentPath.setPlaceholderText("可直接 .torrent 文件拖放到此处")

    def loadTorrent(self):

        def sizeof_fmt(num, suffix="B"):
            if num == -1:
                return ""
            
            for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
                if abs(num) < 1024.0:
                    return f"{num:3.1f} {unit}{suffix}"
                num /= 1024.0
            return f"{num:.1f} Yi{suffix}"
        
        self.fileTree.clear()
        self.setTitleText()

        torrentPath = Path(self.textTorrentPath.text())
        try:
            data = tp.parse_torrent_file(torrentPath)
        except:
            return
        

        if 'files' not in data['info']:
            # One file torrent
            root = QTreeWidgetItem(self.fileTree)
            root.setText(0, Path(data['info']['name']).stem)
            root.setText(1, sizeof_fmt(data['info']['length']))
            file_info = QFileInfo(str(data['info']['name']))
            file_icon_provider = QFileIconProvider()
            root.setIcon(0, file_icon_provider.icon(file_info))

        else:
            # Multi file torrent
            data = data['info']['files']
            folder_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)

            root = QTreeWidgetItem(self.fileTree)
            root.setText(0, torrentPath.stem)
            root.setIcon(0, folder_icon)
            root.setExpanded(True)
            self.fileTree.insertTopLevelItem(0, root)

            d = {str(x['path']):x['length'] for x in data}
            d["[]"] = root

            longetstPath = 0
            for file in data:
                if len(file['path']) > longetstPath:
                    longetstPath = len(file['path'])

            nodes = dict() # path: length, if length = -1 then it is a dir

            for x in range(longetstPath + 1):
                for path, length in d.items():
                    path = eval(path)
                    if len(path) > x:
                        nodes[str(path[:x])] = -1
                    else:
                        nodes[str(path)] = length


            sorted_nodes = sorted(nodes, key=lambda x: len(eval(x)))

            for n in sorted_nodes:
                if n == "[]":
                    continue
                item = QTreeWidgetItem(nodes[f'{eval(n)[:-1]}'])
                item.setText(0, eval(n)[-1])
                item.setText(1, sizeof_fmt(nodes[n]))
                if nodes[n] == -1:
                    item.setIcon(0, folder_icon)
                else:
                    file_info = QFileInfo(eval(n)[-1])
                    file_icon_provider = QFileIconProvider()
                    item.setIcon(0, file_icon_provider.icon(file_info))
                nodes[n] = item

            self.fileTree.sortByColumn(1, Qt.SortOrder.AscendingOrder)
            self.fileTree.setAlternatingRowColors(True)





    def selectTorrentFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\',"Torrent file v1 (*.torrent)")[0]
        self.textTorrentPath.setText(fname)





    def loadConfig(self):
        path = Path(TEMPLATE_CONFIG)
        if not path.exists():
            with open(TEMPLATE_CONFIG, "w", encoding='utf-8') as f:
                f.write('''
lastUsed: 新模板
proxy: http://127.0.0.1:7890
proxyType: 不使用代理
template:
  新模板:
    about: 
    checkAcgnxasia: false
    checkAcgnxglobal: false
    checkAcgrip: false
    checkDmhy: false
    checkNyaa: false
    description: ""
    epPattern: ""
    poster: ""
    profile: ""
    tags: "Anime"
    titlePattern: ""
    title: ""
                ''')

        with open(path, "r", encoding="utf-8") as f:
            self.conf = yaml.safe_load(f)
    
    def loadProxy(self):
        conf = defaultdict(str, self.conf)
        self.menuProxyType.setCurrentText(conf['proxyType'])
        self.textProxyHost.setText(conf['proxy'])

    def saveProxy(self):
        self.conf['proxyType'] = self.menuProxyType.currentText()
        self.conf['proxy'] = self.textProxyHost.text()
        with open(TEMPLATE_CONFIG, "w", encoding='utf-8') as file:
            yaml.safe_dump(self.conf, file, encoding='utf-8',allow_unicode=True)


    def loginWebsite(self, url):
        def login():
            self.webview = WebEngineView(url=QUrl(url),parentWindow=self)
            self.webview.show()

        return login
    
    def getCookies(self):
        return self.textCookies.toPlainText()

    def setCookies(self, cookies:str):
        self.textCookies.setText(cookies)

    def addCookies(self, cookies:str):
        c = self.textCookies.toPlainText()
        cookies = re.sub(r"https://\.", "https://", cookies)
        if c == "":
            if len(cookies) > 0 and cookies[-1] != "\n":
                cookies += "\n"
            self.textCookies.setText(cookies)
        else:
            c += cookies
            c = re.sub(r"\n\n", "", c)
            if c[-1] != "\n":
                c += "\n"
            self.textCookies.setText(c)

    def setUserAgent(self, ua:str):
        if not re.search(r"^user-agent:", self.textCookies.toPlainText()):
            self.textCookies.setText(f"user-agent:\t{ua}\n" + self.textCookies.toPlainText())
        else:
            self.textCookies.setText(
                re.sub(r"^user-agent:.*\n", f"user-agent:\t{ua}\n", self.textCookies.toPlainText())
            )
            
    def updateTemplate(self):
        selected = self.menuTemplateSelection.currentText()
        if selected == "创建新模板":
            self.textTemplateName.setText("新模板")
            self.textEpPattern.clear()
            self.textTitlePattern.clear()
            self.textTitle.clear()
            self.textPoster.clear()
            self.textAbout.clear()
            self.textTags.setText("Anime")
            self.textDescription.clear()
            self.menuSelectCookies.setCurrentIndex(0)


        elif selected not in self.conf['template']:
            return
        else:

            conf = defaultdict(str, self.conf['template'][selected])
            self.textTemplateName.setText(selected)
            self.textEpPattern.setText(conf['epPattern'])
            self.textTitlePattern.setText(conf['titlePattern'])
            self.setTitleText()
            self.textPoster.setText(conf['poster'])
            self.textAbout.setText(conf['about'])
            self.textDescription.setText(conf['description'])
            self.reloadMenuSelectCookies()
            self.textTags.setText(conf['tags'])
            self.textTitle.setText(conf['title'])
            self.setTitleText()
            self.conf['template'][selected] = dict(conf)

            conf = defaultdict(bool, self.conf['template'][selected])
            self.checkboxDmhyPublish.setChecked(conf['checkDmhy'])
            self.checkboxNyaaPublish.setChecked(conf['checkNyaa'])
            self.checkboxBangumiPublish.setChecked(conf['checkBangumi'])
            self.checkboxAcgripPublish.setChecked(conf['checkAcgrip'])
            self.checkboxAcgnxasiaPublish.setChecked(conf['checkAcgnxasia'])
            self.checkboxAcgnxglobalPublish.setChecked(conf['checkAcgnxglobal'])
            self.conf['template'][selected] = dict(conf)

    def setTitleText(self):
        # set title based on patterns, set to "" when no pattern set
        filename = Path(self.textTorrentPath.text()).name
        epPattern = self.textEpPattern.text()
        titlePattern = self.textTitlePattern.text()

        if epPattern == "" or titlePattern == "":
            return
        
        replaces = re.findall(r"<\w+>", epPattern)
        epPattern = re.escape(epPattern)
        epPattern = re.sub(r"<", r"(?P<", epPattern)
        epPattern = re.sub(r">", r">.+)", epPattern)

        try:
            m = re.search(epPattern, filename)
        except re.error:
            return 

        if not m:
            return

        title = titlePattern
        for i in replaces:
            title = re.sub(i, m[f'{re.sub("<|>", "", i)}'], title)
        
        self.textTitle.setText(title)

    def selectCookiesChangeHandler(self, event):
        if event == "":
            return

        cookies = self.profile['profiles'][event]['cookies']


        if cookies is None or not re.search(r"https:\/\/share\.dmhy\.org", cookies):
            self.checkboxDmhyPublish.setChecked(False)
            self.checkboxDmhyPublish.setCheckable(False)
        else:
            self.checkboxDmhyPublish.setCheckable(True)

        if cookies is None or not re.search(r"https:\/\/nyaa\.si", cookies):
            self.checkboxNyaaPublish.setChecked(False)
            self.checkboxNyaaPublish.setCheckable(False)
        else:
            self.checkboxNyaaPublish.setCheckable(True)

        if cookies is None or not re.search(r"https:\/\/acg\.rip", cookies):
            self.checkboxAcgripPublish.setChecked(False)
            self.checkboxAcgripPublish.setCheckable(False)
        else:
            self.checkboxAcgripPublish.setCheckable(True)

        if cookies is None or not re.search(r"https:\/\/bangumi\.moe", cookies):
            self.checkboxBangumiPublish.setChecked(False)
            self.checkboxBangumiPublish.setCheckable(False)
        else:
            self.checkboxBangumiPublish.setCheckable(True)

        if cookies is None or not re.search(r"https:\/\/share\.acgnx\.se", cookies):
            self.checkboxAcgnxasiaPublish.setChecked(False)
            self.checkboxAcgnxasiaPublish.setCheckable(False)
        else:
            self.checkboxAcgnxasiaPublish.setCheckable(True)

        if cookies is None or not re.search(r"https:\/\/www\.acgnx\.se", cookies):
            self.checkboxAcgnxglobalPublish.setChecked(False)
            self.checkboxAcgnxglobalPublish.setCheckable(False)
        else:
            self.checkboxAcgnxglobalPublish.setCheckable(True)


    def reloadTemplate(self):
        self.loadConfig()
        templateList = list(self.conf['template'].keys())
        self.menuTemplateSelection.clear()
        self.menuTemplateSelection.addItems(templateList)
        self.menuTemplateSelection.addItem("创建新模板")
        self.menuTemplateSelection.currentTextChanged.connect(self.updateTemplate)
        try:
            self.menuTemplateSelection.setCurrentText(self.conf['lastUsed'])
            self.updateTemplate()
        except: 
            pass

        
    def saveTemplate(self):
        templateName = self.textTemplateName.text()

        if templateName in ["", "创建新模板"]:
            self.warning(f"非法模板名\"{templateName}\"，请换个名字。")
            return
        
        if templateName in self.conf['template']:
            if not self.warning(f"即将覆盖模板\"{templateName}\"，是否确认？"):
                return
        
        self.conf['lastUsed'] = templateName
        self.conf['template'][templateName] = {
            'epPattern': self.textEpPattern.text(),
            'titlePattern': self.textTitlePattern.text(),
            'poster': self.textPoster.text(),
            'about': self.textAbout.text(),
            'tags': self.textTags.text(),
            'description': self.textDescription.toPlainText(),
            'profile': self.menuSelectCookies.currentText(),
            'checkDmhy': self.checkboxDmhyPublish.isChecked(),
            'checkNyaa': self.checkboxNyaaPublish.isChecked(),
            'checkBangumi': self.checkboxBangumiPublish.isChecked(),
            'checkAcgrip': self.checkboxAcgripPublish.isChecked(),
            'checkAcgnxasia': self.checkboxAcgnxasiaPublish.isChecked(),
            'checkAcgnxglobal': self.checkboxAcgnxglobalPublish.isChecked(),
            'title': self.textTitle.text()
        }

        with open(TEMPLATE_CONFIG, "w", encoding='utf-8') as file:
            yaml.safe_dump(self.conf, file, encoding='utf-8',allow_unicode=True)
        
        self.reloadTemplate()
            

    def deleteTemplate(self):
        # todo: ask for confirmation
        if self.warning(f'正在删除"{self.menuTemplateSelection.currentText()}"模板，删除后将无法恢复，是否继续？'):
            self.conf['template'].pop(self.menuTemplateSelection.currentText())
            with open(TEMPLATE_CONFIG, "w", encoding='utf-8') as file:
                yaml.safe_dump(self.conf, file, encoding='utf-8',allow_unicode=True)
        
            self.reloadTemplate()

    def loadProfile(self):
        path = Path(PROFILE_CONFIG)
        if not path.exists():
            with open(path, "w", encoding="utf-8") as f:
                f.write(
'''
lastUsed: 新身份
profiles:
  新身份:
    cookies: 
    dmhyName: 
    nyaaName: 
    acgripName: 
    bangumiName: 
    acgnxasiaName: 
    acgnxglobalName: 
'''
                )
        with open(path, "r", encoding="utf-8") as f:
            self.profile = yaml.safe_load(f)

    def reloadProfile(self):
        self.loadProfile()
        profileList = list(self.profile["profiles"].keys())
        self.menuProfileSelection.clear()
        self.menuProfileSelection.addItems(profileList)
        self.menuProfileSelection.addItem("创建新身份")
        self.updateProfile()
        self.menuProfileSelection.currentTextChanged.connect(self.updateProfile)
        try:
            self.menuProfileSelection.setCurrentText(self.profile["lastUsed"])
            self.updateProfile()
        except:
            pass
        
    def updateProfile(self):
        
        selected = self.menuProfileSelection.currentText()
        
        if selected == "创建新身份":
            # todo: warning
            self.textProfileName.setText("新身份")
            self.textDmhyName.clear()
            self.textNyaaName.clear()
            self.textAcgripName.clear()
            self.textBangumiName.clear()
            self.textAcgnxasiaName.clear()
            self.textAcgnxasiaToken.clear()
            self.textAcgnxglobalName.clear()
            self.textAcgnxglobalToken.clear()
            self.textCookies.clear()
            # self.menuProxyType.setCurrentIndex(0)
            # self.textProxyHost.setText("http://127.0.0.1:7890")

        elif selected not in self.profile["profiles"]:
            return
        else:
            # if 'proxyType' in self.profile: self.menuProxyType.setCurrentText(self.profile['proxyType'])
            # if 'proxy' in self.profile: self.textProxyHost.setText(self.profile['proxy'])

            prof = defaultdict(str, self.profile["profiles"][selected])
            
            self.textProfileName.setText(selected)
            self.textDmhyName.setText(prof['dmhyName'])
            self.textNyaaName.setText(prof['nyaaName'])
            self.textAcgripName.setText(prof['acgripName'])
            self.textBangumiName.setText(prof['bangumiName'])
            self.textAcgnxasiaName.setText(prof['acgnxasiaName'])
            self.textAcgnxglobalName.setText(prof['acgnxglobalName'])
            self.textCookies.setText(prof['cookies'])
            

            res = re.search(r'https:\/\/share.acgnx.se\ttoken=(?P<token>.*)(\n|$)', str(prof['cookies']))
            if res:
                self.textAcgnxasiaToken.setText(res['token'])
            else:
                self.textAcgnxasiaToken.clear()
            res = re.search(r'https:\/\/www.acgnx.se\ttoken=(?P<token>.*)(\n|$)', str(prof['cookies']))
            if res:
                self.textAcgnxglobalToken.setText(res['token'])
            else:
                self.textAcgnxglobalToken.clear()

            self.profile["profiles"][selected] = dict(prof)


    def saveProfile(self):
        profileName = self.textProfileName.text()
        
        if profileName in ["", "创建新身份"]:
            self.warning(f"非法身份名\"{profileName}\"，请换个名字。")
            return
        
        if profileName in self.profile["profiles"]:
            if not self.warning(f"即将覆盖身份\"{profileName}\", 是否确认？"):
                return
            
        self.profile["lastUsed"] = self.textProfileName.text()
        self.profile["profiles"][self.textProfileName.text()] = {
            'cookies': self.textCookies.toPlainText(),
            'dmhyName': self.textDmhyName.text(),
            'nyaaName': self.textNyaaName.text(),
            'acgripName': self.textAcgripName.text(),
            'bangumiName': self.textBangumiName.text(),
            'acgnxasiaName': self.textAcgnxasiaName.text(),
            'acgnxglobalName': self.textAcgnxglobalName.text(),
        }

        with open(PROFILE_CONFIG, "w", encoding='utf-8') as file:
            yaml.safe_dump(self.profile, file, encoding='utf-8',allow_unicode=True)
        
        self.reloadProfile()
        self.reloadMenuSelectCookies()


    def deleteProfile(self):
        if self.warning(f'正在删除"{self.menuProfileSelection.currentText()}"身份，删除后将无法恢复，是否继续？'):
            self.profile['profiles'].pop(self.menuProfileSelection.currentText())
            with open(PROFILE_CONFIG, "w", encoding='utf-8') as file:
                yaml.safe_dump(self.profile, file, encoding='utf-8',allow_unicode=True)
            
            self.reloadMenuSelectCookies()
            self.reloadProfile()


    def previewMarkdown(self):
        md = markdown.markdown(self.textDescription.toPlainText())
        #self.textDescription.setPlainText(md)
        self.markdownWindow = MarkdownViewWindow(html=md,parentWindow=self)
        self.markdownWindow.show()

    def warning(self, message):
        warning = WarningDialog()
        warning.label.setText(message)
        warning.show()
        return warning.exec()

    def reloadMenuSelectCookies(self):
        self.menuSelectCookies.clear()
        self.menuSelectCookies.addItems(self.profile['profiles'].keys())
        try: self.menuSelectCookies.setCurrentText(self.conf['template'][self.menuTemplateSelection.currentText()]['profile'])
        except: pass

    def onProxySelection(self):
        selected = self.menuProxyType.currentText()
        if selected == "不使用代理":
            self.textProxyHost.setDisabled(True)
            return
        if selected == "HTTP":
            self.textProxyHost.setEnabled(True)
            return
        
    def applyAcgnxasiaAPIToken(self):
        cookies = self.textCookies.toPlainText()
        new_string, n = re.subn(
            r"https:\/\/share.acgnx.se\ttoken=.*(\n|$)", 
            f"https://share.acgnx.se\ttoken={self.textAcgnxasiaToken.text()}\n", 
            cookies)
        if n != 0:
            self.textCookies.setText(new_string)
        else:
            if cookies and cookies[-1] != "\n": cookies += "\n"
            self.textCookies.setText(
                cookies + f"https://share.acgnx.se\ttoken={self.textAcgnxasiaToken.text()}\n"
            )

    def applyAcgnxglobalAPIToken(self):
        cookies = self.textCookies.toPlainText()
        new_string, n = re.subn(
            r"https:\/\/www.acgnx.se\ttoken=.*(\n|$)", 
            f"https://www.acgnx.se\ttoken={self.textAcgnxglobalToken.text()}\n", 
            cookies)
        if n != 0:
            self.textCookies.setText(new_string)
        else:
            if cookies and cookies[-1] != "\n": cookies += "\n"
            self.textCookies.setText(
                cookies + f"https://www.acgnx.se\ttoken={self.textAcgnxglobalToken.text()}\n"
            )

    def onCookiesChange(self):
        cookies = self.textCookies.toPlainText()
        m = re.search(r"https:\/\/share.acgnx.se\ttoken=(?P<token>.*)(\n|$)", cookies)
        if m:
            self.textAcgnxasiaToken.setText(m['token'])

        m = re.search(r"https:\/\/www.acgnx.se\ttoken=(?P<token>.*)(\n|$)", cookies)
        if m:
            self.textAcgnxglobalToken.setText(m['token'])



    def publishRun(self):
        # Sanity check
        path = self.textTorrentPath.text()
        if path == "":
            self.warning("种子文件不能为空。")
            return
        
        if not Path(path).exists():
            self.warning(f"无法找到种子文件'{path}'。")
            return
        
        if Path(path).suffix != ".torrent":
            self.warning(f"'{path}' 不是一个 .torrent 文件")
            return
        
        if self.textTitle.text() == "":
            self.warning("标题不能为空。")
            return
        
        if self.textDescription.toPlainText() == "":
            self.warning("内容不能为空。")

        # Generate template.toml
        tags = map(lambda x: x.strip() , self.textTags.text().split(","))
        intro_templates = []

        md = self.textDescription.toPlainText()
        html = markdown.markdown(md)
        parser = HTML2PHPBBCode()
        bbcode = parser.feed(html)
        proxy = self.conf["proxy"]

        cookies = self.profile['profiles'][self.menuSelectCookies.currentText()]['cookies']
        profile = self.profile['profiles'][self.menuSelectCookies.currentText()]

        if self.checkboxDmhyPublish.isChecked() and self.checkboxDmhyPublish.isCheckable():
            intro_templates.append(
                {
                'site': 'dmhy',
                'name': profile['dmhyName'],
                'content': html,
                }
            )
        
        if self.checkboxNyaaPublish.isChecked() and self.checkboxNyaaPublish.isCheckable():
            intro_templates.append(
                {
                'site': 'nyaa',
                'name': profile['nyaaName'],
                'content': md,
                }
            )

        if self.checkboxAcgripPublish.isChecked() and self.checkboxAcgripPublish.isCheckable():
            intro_templates.append(
                {
                'site': 'acgrip',
                'name': profile['acgripName'],
                'content': bbcode,
                }
            )

        if self.checkboxBangumiPublish.isChecked() and self.checkboxBangumiPublish.isCheckable():
            intro_templates.append(
                {
                'site': 'bangumi',
                'name': profile['bangumiName'],
                'content': html,
                }
            )

        if self.checkboxAcgnxasiaPublish.isChecked() and self.checkboxAcgnxasiaPublish.isCheckable():
            intro_templates.append(
                {
                'site': 'acgnx_asia',
                'name': profile['acgnxasiaName'],
                'content': html,
                }
            )

        if self.checkboxAcgnxglobalPublish.isChecked() and self.checkboxAcgnxglobalPublish.isCheckable():
            intro_templates.append(
                {
                'site': 'acgnx_global',
                'name': profile['acgnxglobalName'],
                'content': html,
                }
            )

        if self.conf['proxyType'] == "HTTP":
            for d in intro_templates:
                d['proxy'] = proxy

        template_conf = {
            'display_name': self.textTitle.text(),
            'poster': self.textPoster.text(),
            'about': self.textAbout.text(),
            'filename_regex': '',
            'resolution_regex': '',
            'tags': list(tags),
            'intro_template': intro_templates
        }

        with open("template.toml", "w", encoding='utf-8') as f:
            toml.dump(template_conf, f)
        
        # Generate cookies.txt
        with open("cookies.txt", "w", encoding='utf-8') as f:
            f.write(self.profile['profiles'][self.menuSelectCookies.currentText()]['cookies'])
        
        self.console = MyConsole(self)
        self.console.onFinished(self.updateCookies)
        self.console.start("OKP.Core.exe", [
            self.textTorrentPath.text(),
            "-s", str(Path.cwd().joinpath("template.toml")),
            '--cookies', str(Path.cwd().joinpath("cookies.txt"))
        ])
        self.console.show()


        
        
    def updateCookies(self, int, exitStatus):
        if exitStatus == QProcess.ExitStatus.NormalExit:
            try:
                with open("cookies.txt", "r", encoding="utf-8") as f:
                    newCookies = f.read()

                self.profile["profiles"][self.menuSelectCookies.currentText()]["cookies"] = newCookies

                with open(PROFILE_CONFIG, "w", encoding="utf-8") as file:
                    yaml.safe_dump(self.profile, file, encoding='utf-8',allow_unicode=True)

                self.reloadProfile()

            except:
                return
            


class WarningDialog(QDialog, Ui_Dialog):
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if platform.system() != "Windows":
        app.setStyle('Fusion')

    window = OKPMainWIndow()
    window.show()
    sys.exit(app.exec())