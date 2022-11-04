from PyQt5.QtWidgets import QWidget

from nothing_request import Ui_Form

class Widget_2(QWidget):
    def __init__(self, parent=None):
        super(Widget_2,self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)