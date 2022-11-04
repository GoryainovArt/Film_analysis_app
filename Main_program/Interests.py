from PyQt5.QtWidgets import QWidget

from playlist_wnd import Ui_Form

class Interest(QWidget):
    def __init__(self, parent=None):
        super(Interest,self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)