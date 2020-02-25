# 导入UI主界面
from main import *
# 导入必要的模块封装
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QLabel, QMainWindow, QMessageBox
from PyQt5.QtGui import QImage, QIcon, QPixmap
from PyQt5.QtCore import QTimer, QDateTime, QCoreApplication, Qt
from imutils.video import VideoStream

import sys
import cv2
import imutils


class MainWindow(QWidget):
    # 类构造函数
    def __init__(self):
        # super()构造器方法返回父级的对象。__init__()方法是构造器的一个方法。
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # 设置窗口名称和图标
        self.setWindowTitle('人脸识别考勤系统')
        self.setWindowIcon(QIcon('fcblogo.jpg'))

        # 设置窗口背景
        pixmap = QPixmap('fcblogo.jpg')
        self.ui.label_logo.setPixmap(pixmap)

        # 设置区分打开摄像头还是人脸识别的标识符
        self.switch_bt = 0

        # 在label_time上显示系统时间
        timer = QTimer(self)
        timer.timeout.connect(self.showTimeText)
        timer.start()

        # 初始化摄像头
        self.url = 0
        self.cap = cv2.VideoCapture()

        # 设置摄像头按键连接函数
        self.ui.bt_openCamera.clicked.connect(self.openCamera)

        # 设置开始考勤按键的回调函数
        self.ui.bt_startCheck.clicked.connect(self.autoControl)

        # 设置“退出系统”按键事件, 按下之后退出主界面
        self.ui.bt_exit.clicked.connect(QCoreApplication.instance().quit)

    # 显示系统时间以及相关文字提示函数
    def showTimeText(self):
        # 设置宽度
        self.ui.label_time.setFixedWidth(200)
        # 设置显示文本格式
        self.ui.label_time.setStyleSheet(
            # "QLabel{background:white;}" 此处设置背景色
            "QLabel{color:rgb(300,300,300,120); font-size:14px; font-weight:bold; font-family:宋体;}")
        datetime = QDateTime.currentDateTime().toString()
        self.ui.label_time.setText("" + datetime)

        # 显示“人脸识别考勤系统”文字
        self.ui.label_title.setFixedWidth(400)
        self.ui.label_title.setStyleSheet(
            "QLabel{font-size:30px; font-weight:bold; font-family:宋体;}")
        self.ui.label_title.setText("人脸识别考勤系统")

    def openCamera(self, url):
        # 判断摄像头是否打开，如果打开则为true，反之为false
        flag = self.cap.isOpened()                 
        if flag == False:
            url = 0
            self.ui.label_logo.clear()
            self.cap.open(self.url)
            self.showCamera()
        else:
            self.cap.release()
            self.ui.label_logo.clear()
            self.ui.label_camera.clear()
            self.ui.bt_openCamera.setText(u'打开相机')

    # 进入考勤模式，通过switch_bt进行控制的函数
    def autoControl(self):
        if self.switch_bt == 0:
            self.switch_bt = 1
            # 用于输出状态信息
            global flagInfo
            flagInfo = 1
            self.ui.bt_startCheck.setText(u'退出考勤')
            self.showCamera()

        elif self.switch_bt == 1:
            self.switch_bt = 0
            flagInfo = 0
            self.ui.bt_startCheck.setText(u'开始考勤')
            self.showCamera()

    def showCamera(self):
        # 如果按键按下
        if self.switch_bt == 0:
            self.ui.label_logo.clear()
            self.ui.bt_openCamera.setText(u'关闭相机')
            while (self.cap.isOpened()):
                # 以BGR格式读取图像
                ret, self.image = self.cap.read()
                QApplication.processEvents()  # 这句代码告诉QT处理来处理任何没有被处理的事件，并且将控制权返回给调用者，让代码变的没有那么卡
                # image = cv2.resize(self, (800, 600))
                # 将图像转换为RGB格式
                show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
                # opencv 读取图片的样式，不能通过Qlabel进行显示，需要转换为Qimage QImage(uchar * data, int width,
                self.showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
                self.ui.label_camera.setPixmap(QPixmap.fromImage(self.showImage))
            # 因为最后会存留一张图像在lable上，需要对lable进行清理
            self.ui.label_camera.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 创建并显示窗口
    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())




