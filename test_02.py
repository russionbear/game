
import sys

from PyQt5 import QtGui
from PyQt5.Qt import *
from PyQt5.QtCore import QCoreApplication

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
    def set_ui(self):
        login_layer = QBoxLayout(QBoxLayout.TopToBottom)
        login_image = QLabel('welcone', self)
        login_contine = QPushButton('继续阅读', self)
        login_get_layer = QBoxLayout(QBoxLayout.LeftToRight)
        login_view = QLabel('vew', self)
        
qApp = QApplication(sys.argv)
import qdarkgraystyle
qApp.setStyleSheet(qdarkgraystyle.load_stylesheet())
window = Window()
window.resize(800, 600)

btn = QPushButton(window)
btn.setText("click")


def moveCenter(obj):
    if isinstance(obj, QWidget):
        qr = obj.frameGeometry()
        qq = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(qq)
        obj.move(qr.topLeft())

window.show()
moveCenter(window)

animatin = QPropertyAnimation(btn, b"size", window)
animatin.setEasingCurve(QEasingCurve.BezierSpline)
animatin.setEndValue(QSize(400, 400))
animatin.setDuration(2000)
animatin.start()

qApp.exec_()
