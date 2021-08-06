
import sys
from PyQt5.Qt import *

qApp = QApplication(sys.argv)
'''移动参数，攻击参数，图片参数'''

class Btn(QPushButton):
    def __init__(self, string):
        super(Btn, self).__init__(string)
        self.string = string
    def mousePressEvent(self, evt):
        window.deal(self.string)

class myWin(QWidget):
    def __init__(self):
        super(myWin, self).__init__()
        self.setWindowTitle('senData_edit[*]')
        self.resize(800, 600)
        self.show()
        self.mylayor = QVBoxLayout()
        # self.setLayout(self.mylayor)
        # self.setWindowModified(False)
    def deal(self,*args):
        print(args)
    def core(self):
        pass




sen_data_move = {'keyRow':['plain', 'mountain', 'tree', 'road', 'river', 'sea', 'sand'], \
                 'keyCol':['foot', 'wheel', 'caterprillar', 'propeller', 'turbine']}
sen_data_arms = {'keyRow':['vest', 'armor_l_01', 'armor_l_10', 'aromor_p', 'aromor_s_10'], \
                 'keyCol':['bullet', 'cannon', 'bigCannon']}
sen_data_dw = {'footmen':{'attack':'', 'defense':'', 'view':2, 'Adistance':0, 'Mdistance':3, 'dsc':''}}
sen_data_image = {'footmen':{'stand':''}}
sen_data = {'move':sen_data_move, 'image':sen_data_image, 'dw':sen_data_dw, 'arms':sen_data_arms}
def complete_check(sen_data):
    sen_data['dsc'] = {}
    for i in sen_data['keyCol']:
        if i not in sen_data:
            sen_data[i] = {}
            sen_data['dsc'][i] = 'none'
        for j in sen_data['keyRow']:
            try:
                sen_data[i][j]
            except KeyError:
                sen_data[i][j] = -2
    for i in sen_data['keyRow']:
        sen_data['dsc'][i] = 'none'

complete_check(sen_data_move)
complete_check(sen_data_arms)
# print(sen_data_arms)
# print(sen_data_move)

window = myWin()

topW = QWidget()
topW.show()
topW_l = QHBoxLayout()
for i in list(sen_data.keys()):
    tem_btn = Btn(i)
    tem_btn.clicked.connect(window.deal)
    topW_l.addWidget(tem_btn)


topW.setLayout(topW_l)
window.mylayor.addWidget(topW)
window.setLayout(window.mylayor)

sys.exit(qApp.exec_())