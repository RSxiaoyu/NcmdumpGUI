import sys
import ncmdump
import os
from glob import glob
from PySide6.QtCore import QThread,Signal,Qt
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog
from Crypto.Cipher import AES
from ui_form import Ui_Widget


class DumpThread(QThread):
    progressUpdated = Signal(int)
    enable = Signal()
    disable = Signal(int)
    def __init__(self,dirpath):
        super().__init__()
        self.files = glob(dirpath+"\\*.ncm")
        self.exists =[os.path.splitext(music)[0] for music in glob(dirpath+"\\*.m4a")+glob(dirpath+"\\*.mp3")+glob(dirpath+"\\*.flac")+glob(dirpath+"\\*.wav")]

    def run(self):
        self.disable.emit(len(self.files))
        for index, file in enumerate(self.files):
            print(os.path.splitext(file)[0],self.exists)
            if os.path.splitext(file)[0] not in self.exists:
                ncmdump.dump(file)
            self.progressUpdated.emit(index + 1)
        self.enable.emit()


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.setFixedSize(self.width(), self.height()); 
        self.ui.fileButton.clicked.connect(self.fileChoose)
        self.ui.pushButton.clicked.connect(self.startDump)
        self.dump_thread = None

    def fileChoose(self):#选择目录
        dir_path = QFileDialog.getExistingDirectory(self).replace("/","\\")
        self.ui.lineEdit.setText(dir_path)

    def startDump(self):#开始转换
        if os.path.exists(self.ui.lineEdit.text()):
            if self.dump_thread is None or not self.dump_thread.isRunning():
                dirpath = self.ui.lineEdit.text()
                self.dump_thread = DumpThread(dirpath)
                if self.dump_thread.files != []:
                    self.dump_thread.enable.connect(self.enableButton)
                    self.dump_thread.disable.connect(self.disableButton)
                    self.dump_thread.progressUpdated.connect(self.updateProgress)
                    self.dump_thread.start()
        else:
            self.ui.lineEdit.setText("路径不合法！")

    def updateProgress(self, value):
        self.ui.progressBar.setValue(value)

    def disableButton(self,value):
        self.ui.progressBar.setRange(0,value)
        self.ui.progressBar.setValue(0)
        self.ui.pushButton.setEnabled(False)
        self.ui.fileButton.setEnabled(False)
        self.ui.lineEdit.setEnabled(False)

    def enableButton(self):
        self.ui.pushButton.setEnabled(True)
        self.ui.fileButton.setEnabled(True)
        self.ui.lineEdit.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
