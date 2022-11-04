import sys
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal


from Enter_films import Ui_Form


class CoordWidget(QWidget):
    execute = pyqtSignal(int)

    def __init__(self,id_widget,parent=None):
        super(CoordWidget,self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.id_widget = id_widget
        self.ui.pushButton.clicked.connect(lambda: self.clk())
        self.ui.label_3.setText('')
        self.ui.label_4.setText('')
        self.ui.label_5.setText('')

    @pyqtSlot()
    def clk(self):
        self.execute.emit(self.id_widget)
