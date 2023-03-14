import sys

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QProcess
from PyQt6.QtGui import QTextCursor, QFont
from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QWidget, QVBoxLayout, QPushButton
import locale


class ProcessOutputReader(QProcess):
    produce_output = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # merge stderr channel into stdout channel
        self.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)


        # only necessary when stderr channel isn't merged into stdout:
        # self._decoder_stderr = codec.makeDecoder()

        self.readyReadStandardOutput.connect(self._ready_read_standard_output)
        # only necessary when stderr channel isn't merged into stdout:
        # self.readyReadStandardError.connect(self._ready_read_standard_error)

    @pyqtSlot()
    def _ready_read_standard_output(self):
        raw_bytes = self.readAllStandardOutput()
        text = raw_bytes.data().decode(locale.getencoding())
        self.produce_output.emit(text)



class MyConsoleWidget(QPlainTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setReadOnly(True)
        self.setMaximumBlockCount(10000)  # limit console to 10000 lines
        

        self._cursor_output = self.textCursor()

    @pyqtSlot(str)
    def append_output(self, text):
        self._cursor_output.insertText(text)
        self.scroll_to_last_line()

    def scroll_to_last_line(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.movePosition(QTextCursor.MoveOperation.Up if cursor.atBlockStart() else
                            QTextCursor.MoveOperation.StartOfLine)
        self.setTextCursor(cursor)

class MyConsole(QWidget):
    def __init__(self, parentWindow, *args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)
        self.resize(800, 600)
        self.vbox = QVBoxLayout(self)

        self.publishButton = QPushButton(self)
        self.publishButton.setText("确定")
        font = QFont()
        font.setPointSize(20)
        self.publishButton.setFont(font)

        self.publishButton.clicked.connect(self.onPublishButton)
        self.reader = ProcessOutputReader()
        self.consoleWidget = MyConsoleWidget()

        self.reader.produce_output.connect(self.consoleWidget.append_output)

        self.vbox.addWidget(self.consoleWidget)
        self.vbox.addWidget(self.publishButton)

        self.setWindowTitle("OKP 运行中…")

        #self.reader.start('python', ['test.py'])  # start the process

    def onPublishButton(self):
        self.consoleWidget.append_output("\n")
        self.reader.write(b"\n")

    def start(self, *args, **kargs):
        self.reader.start(*args, **kargs)

    def onFinished(self, func):
        self.reader.finished.connect(func)

    def closeEvent(self, event):
        self.reader.terminate()
    

        

if __name__ == "__main__":
    # create the application instance
    app = QApplication(sys.argv)
    # create a console and connect the process output reader to it
    console = MyConsole(None)
    console.start('python', ['test.py'])
    
    console.show()
    app.exec()