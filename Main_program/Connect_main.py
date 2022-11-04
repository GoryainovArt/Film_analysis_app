from PyQt5.QtWidgets import QApplication, QWidget
import sys

from Connection_error import Ui_Form
from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Connection_error_wnd(QWidget):
    def __init__(self, parent=None):
        super(Connection_error_wnd,self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Убрать Windows рамку кнопок
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # ХЗ, что это


        self.ui.pushButton.clicked.connect(lambda: self.close())

        def MoveWindow(e):
            if e.buttons() == Qt.LeftButton:
                self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

        self.ui.frame_2.mouseMoveEvent = MoveWindow

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Connection_error_wnd()
    window.show()
    sys.exit(App.exec())