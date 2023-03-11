import datetime
import traceback

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

def exc(func):
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            with open(f"Traceback_{datetime.datetime.now().strftime(r'%Y%m%d%H%M%S')}.txt", "w", encoding="utf-8") as f:
                traceback.print_exception(e, file=f)
            raise e
    return inner