import sys
from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt

from mainwindow import MainWindow

class MyMainWindow(QMainWindow, MainWindow):
    def __init(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)

    if __name__ == "__main__":
        #initialize screen
        app = QApplication(sys.argv)
        myWin = MyMainWindow()
        myWin.show()
        sys.exit(app.exec_())
