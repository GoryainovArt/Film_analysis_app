from PyQt5.QtWidgets import QWidget

from Similar_requests import Ui_Form

class Widget_1(QWidget):
    def __init__(self, parent=None):
        super(Widget_1,self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)