from PyQt5.QtWidgets import QWidget

from Interests_not_defined import Ui_Form

class Interests_not_defined_wdgt(QWidget):
    def __init__(self, parent=None):
        super(Interests_not_defined_wdgt,self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)