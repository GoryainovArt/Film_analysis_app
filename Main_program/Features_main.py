import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from Features import Ui_Form

class  Features_window(QWidget):
    signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super(Features_window,self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.check_list = []
        self.checkBox_list = [self.ui.checkBox_11, self.ui.checkBox_13, self.ui.checkBox_14, self.ui.checkBox_15,
                              self.ui.checkBox_16,
                              self.ui.checkBox_17, self.ui.checkBox_18, self.ui.checkBox_19, self.ui.checkBox_20,
                              self.ui.checkBox_21, self.ui.checkBox_5, self.ui.checkBox_6, self.ui.checkBox_7,
                              self.ui.checkBox_8, self.ui.checkBox_9,
                              self.ui.checkBox_11,
                              self.ui.checkBox_22]
        self.ui.checkBox_12.clicked.connect(lambda: self.set_all())

        # Set Main background to transparent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # ХЗ, что это

        self.ui.pushButton.clicked.connect(lambda: self.clk())
        self.ui.pushButton_2.clicked.connect(lambda: self.close())

        def MoveWindow(e):
            if self.isMaximized() == False:
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()

        self.ui.frame_2.mouseMoveEvent = MoveWindow

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()


    def set_all(self):

        if self.ui.checkBox_12.isChecked():
            for i in self.checkBox_list:
                i.setChecked(True)
        else:
            for i in self.checkBox_list:
                i.setChecked(False)


    @pyqtSlot()
    def clk(self):
        for i in self.checkBox_list:
            if i.isChecked():
                self.check_list.append(i.text())
        print(self.check_list)
        self.signal.emit(self.check_list)
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Features_window(0)
    window.show()
    sys.exit(app.exec_())
