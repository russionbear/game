#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :mainWindow.py
# @Time      :2021/8/7 14:11
# @Author    :russionbear

from PyQt5.Qt import *
from PyQt5 import QtCore
import sys
from resource_load import resource

Qapp = QApplication(sys.argv)
class TopDirector(QWidget):
    def __init__(self):
        super(TopDirector, self).__init__()
        self.initUI()
    def initUI(self):
        bgUrl = ''
        self.bgFrame = QFrame(self)
        self.fgFrame = QFrame(self)
        bgImage = QLabel(self.bgFrame)
        bgImage_ = QLabel(self.bgFrame)
        pixmap = resource.find({'usage':'hero', ' name':'hero', 'action':'post'})['pixmap']
        bgImage.setPixmap(pixmap)
        bgImage_.setPixmap(pixmap)
        bgImage_.resize(pixmap.size())
        bgImage_.resize(pixmap.size())
        self.fgFrame.resize(pixmap.size())
        bgImage_.move(0, pixmap.height())
        # self.setFixedSize(pixmap.size())
        self.resize(pixmap.size())
        self.startTimer(20)

        self.toBegin()
        # self.toOptions()

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        speed = 1
        for i in self.bgFrame.findChildren(QLabel):
            i.move(0, i.y()+speed)
            i.show()
        if i.y() >= self.height():
            for i1, i in enumerate(self.bgFrame.findChildren(QLabel)):
                i.move(0, (i1-1)*self.height())
        a0.accept()

    def toBegin(self):
        tipText = '这fsdfsdfsdfsdfsdfsdfsd是一个提示'
        self.fgFrame.deleteLater()
        self.fgFrame = QFrame(self)
        self.fgFrame.resize(self.size())
        tip = QLabel(tipText, self.fgFrame)
        tip.setAlignment(QtCore.Qt.AlignCenter)
        tip.setFont(QFont('宋体', 25))
        tip.setWordWrap(True)
        tip.setFixedWidth(self.width()//2)
        tip.setStyleSheet('color:white;')
        beginBtn = QPushButton('开始', self.fgFrame)
        beginBtn.clicked.connect(self.toOptions)
        layoutBegin = QBoxLayout(QBoxLayout.TopToBottom)
        layoutBegin.setAlignment(QtCore.Qt.AlignCenter)
        layoutBegin.addWidget(tip)
        layoutBegin.addSpacing(30)
        layoutBegin.addWidget(beginBtn)
        self.fgFrame.setLayout(layoutBegin)
        self.fgFrame.show()


    def toOptions(self):
        self.fgFrame.deleteLater()
        self.fgFrame = QFrame(self)
        self.fgFrame.resize(self.size())
        btns_text = ['战役', '局域网', '自定义', '编辑', '设置', '返回']
        btns_backMethod = [self.toBegin, self.toIntranet, self.toCustom, self.toEdit, self.toSetting, self.toBegin]
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.setAlignment(QtCore.Qt.AlignHCenter)
        for i1, i in enumerate(btns_text):
            tem_btn = QPushButton(i, self.fgFrame)
            tem_btn.clicked.connect(btns_backMethod[i1])
            tem_btn.show()
            layout.addWidget(tem_btn)
            layout.addSpacing(tem_btn.height()*2)
        self.fgFrame.setLayout(layout)
        self.fgFrame.show()

    def toBattle(self):
        pass
    def toIntranet(self):
        self.fgFrame.deleteLater()
        self.fgFrame = QFrame(self)
        self.fgFrame.resize(self.size())
        beginBtn = QPushButton('开始', self.fgFrame)
        beginBtn.clicked.connect(self.toOptions)
        layoutBegin = QBoxLayout(QBoxLayout.TopToBottom)
        layoutBegin.setAlignment(QtCore.Qt.AlignCenter)
        layoutBegin.addSpacing(30)
        layoutBegin.addWidget(beginBtn)
        self.fgFrame.setLayout(layoutBegin)
        self.fgFrame.show()

    def toCustom(self):
        pass
    def toEdit(self):
        pass
    def toSetting(self):
        pass

if __name__ == "__main__":
    window = TopDirector()
    window.show()
    sys.exit(Qapp.exec_())
