from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QDialog
import sys
from OKPUI import Ui_MainWindow
from WarningDialog import Ui_Dialog
import helpers
import yaml
from pathlib import Path
from WebHelper import WebEngineView
import webbrowser
import re
import markdown
from MarkdownView import MarkdownViewWindow
import toml
import subprocess
from html2phpbbcode.parser import HTML2PHPBBCode
from helpers import exc

VERSION = "v0.0.3 Alpha 内部测试版"

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
    
    @exc
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
       # self.textTorrentPath.setAcceptDrops(True)
        self.HomeTab.dragEnterEvent = helpers.pathDragEnterEvent(self.textTorrentPath, "请在此释放鼠标")
        self.HomeTab.dropEvent = helpers.pathDropEvent(self.textTorrentPath, self)
        self.HomeTab.dragLeaveEvent = helpers.pathDragLeaveEvent(self.textTorrentPath, "可直接 .torrent 文件拖放到此处")

        # Select template
        self.reloadProfile()

        self.reloadTemplate()
        self.updateTemplate()

        # Save / Delete template
        self.buttonSaveTemplate.clicked.connect(self.saveTemplate)
        self.buttonDeleteTemplate.clicked.connect(self.deleteTemplate)

        # Select tags
        self.buttonHowToUseTags.clicked.connect(lambda _: webbrowser.open("https://github.com/AmusementClub/OKP/wiki/TagsConvert"))

        # preview markdown
        self.buttonPreviewMarkdown.clicked.connect(self.previewMarkdown)
        #self.textDescription.setMarkdown(self.textDescription.toPlainText())

        

        # tab 2 login
        self.buttonDmhyLogin.clicked.connect(self.loginWebsite("https://share.dmhy.org/user/login"))
        self.buttonNyaaLogin.clicked.connect(self.loginWebsite("https://nyaa.si/login"))
        self.buttonAcgripLogin.clicked.connect(self.loginWebsite("https://acg.rip/users/sign_in"))
        self.buttonBangumiLogin.clicked.connect(self.loginWebsite("https://bangumi.moe/"))
        self.buttonAcgnxasiaLogin.clicked.connect(self.loginWebsite("https://share.acgnx.se/user.php?o=login"))
        self.buttonAcgnxglobalLogin.clicked.connect(self.loginWebsite("https://www.acgnx.se/user.php?o=login"))

        self.buttonSaveProfile.clicked.connect(self.saveProfile)
        self.buttonDeleteProfile.clicked.connect(self.deleteProfile)

        # publish button
        self.buttonOKP.clicked.connect(self.publishRun)

    
    def selectTorrentFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\',"Torrent file v1 (*.torrent)")[0]
        self.textTorrentPath.setText(fname)

    def initializeConfig(self):
        with open(TEMPLATE_CONFIG, "w", encoding='utf-8') as f:
            f.write('''
lastUsed: 新模板
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


    def loadConfig(self):
        path = Path(TEMPLATE_CONFIG)
        if not path.exists():
            self.initializeConfig()

        with open(path, "r", encoding="utf-8") as f:
            self.conf = yaml.safe_load(f)
            

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
        cookies = re.sub(r"https://.", "https://", cookies)
        if c == "":
            self.textCookies.setText(cookies)
        else:
            c += "\n" + cookies
            c = re.sub(r"\n\n", "", c)
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
            # warning = WarningDialog()
            # warning.show()
            # warning.exec()
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
            conf = self.conf['template'][selected]
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

            self.checkboxDmhyPublish.setChecked(conf['checkDmhy'])
            self.checkboxNyaaPublish.setChecked(conf['checkNyaa'])
            self.checkboxAcgripPublish.setChecked(conf['checkAcgrip'])
            self.checkboxAcgnxasiaPublish.setChecked(conf['checkAcgnxasia'])
            self.checkboxAcgnxglobalPublish.setChecked(conf['checkAcgnxglobal'])


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
            'profile': self.menuProfileSelection.currentText(),
            'checkDmhy': self.checkboxDmhyPublish.isChecked(),
            'checkNyaa': self.checkboxNyaaPublish.isChecked(),
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
    dmhyName: 新身份
    nyaaName: 新身份
    acgripName: 新身份
    bangumiName: 新身份
    acgnxasiaName: 新身份
    acgnxglobalName: 新身份
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
        self.menuProfileSelection.activated.connect(self.updateProfile)
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
            self.textAcgnxglobalName.clear()
            self.textCookies.clear()
        elif selected not in self.profile["profiles"]:
            return
        else:
            prof = self.profile["profiles"][selected]
            self.textProfileName.setText(selected)
            self.textDmhyName.setText(prof['dmhyName'])
            self.textNyaaName.setText(prof['nyaaName'])
            self.textAcgripName.setText(prof['acgripName'])
            self.textBangumiName.setText(prof['bangumiName'])
            self.textAcgnxasiaName.setText(prof['acgnxasiaName'])
            self.textAcgnxglobalName.setText(prof['acgnxglobalName'])
            self.textCookies.setText(prof['cookies'])

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

    def publishRun(self):
        # Sanity check
        if self.textTorrentPath.text() == "":
            self.warning("种子文件不能为空。")
            return
        
        if not Path(self.textTorrentPath.text()):
            self.warning("无法找到种子文件。")
            return
        
        if self.textTitle.text() == "":
            self.warning("标题不能为空。")
            return

        # Generate template.toml
        tags = map(lambda x: x.strip() , self.textTags.text().split(","))
        intro_templates = []

        md = self.textDescription.toPlainText()
        html = markdown.markdown(md)
        parser = HTML2PHPBBCode()
        bbcode = parser.feed(html)
        

        if self.checkboxDmhyPublish.isChecked():
            intro_templates.append(
                {
                'site': 'dmhy',
                'name': self.textDmhyName.text(),
                'content': html
                }
            )
        
        if self.checkboxNyaaPublish.isChecked():
            intro_templates.append(
                {
                'site': 'nyaa',
                'name': self.textNyaaName.text(),
                'content': md
                }
            )

        if self.checkboxAcgripPublish.isChecked():
            intro_templates.append(
                {
                'site': 'acgrip',
                'name': self.textAcgripName.text(),
                'content': bbcode
                }
            )

        if self.checkboxBangumiPublish.isChecked():
            intro_templates.append(
                {
                'site': 'bangumi',
                'name': self.textBangumiName.text(),
                'content': html
                }
            )

        if self.checkboxAcgnxasiaPublish.isChecked():
            intro_templates.append(
                {
                'site': 'acgnx_asia',
                'name': self.textAcgnxasiaName.text(),
                'content': html
                }
            )

        if self.checkboxAcgnxglobalPublish.isChecked():
            intro_templates.append(
                {
                'site': 'acgnx_global',
                'name': self.textAcgnxglobalName.text(),
                'content': html
                }
            )

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
        
        p = subprocess.Popen([
            "OKP.Core.exe", 
            self.textTorrentPath.text(),
            "-s", str(Path.cwd().joinpath("template.toml")),
            '--cookies', str(Path.cwd().joinpath("cookies.txt"))
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)



class WarningDialog(QDialog, Ui_Dialog):
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = OKPMainWIndow()
    window.show()
    sys.exit(app.exec())