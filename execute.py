import os
import pickle
import sys
from datetime import datetime

import cv2
import imutils
import numpy as np
# 导入数据库操作包
import pymysql
# 导入界面处理包
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QDateTime, QCoreApplication, QThread
from PyQt5.QtGui import QImage, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QInputDialog
# 导入频帧画面大小调整包
from imutils import face_utils
from imutils.video import VideoStream
# 导入眨眼检测必要的包
from scipy.spatial import distance as dist

# 导入UI主界面
from ui import MainUI

# 导入打印中文脚本
from utils import PutChineseText
# 导入人脸识别检测包
from utils import GeneratorModel
# 导入眨眼检测类
from utils.BlinksDetectionThread import BlinksDetectThread
# 导入信息采集槽函数类
from utils.InfoDialog import InfoDialog
# 添加数据库连接操作
from utils.GlobalVar import connect_to_sql

# # 为方便调试，修改后导入模块，重新导入全局变量模块
# import importlib
# importlib.reload(GeneratorModel)

import sys
import os
# 添加当前路径到环境变量
sys.path.append(os.getcwd())

# 导入全局变量，主要包含摄像头ID等
from utils.GlobalVar import CAMERA_ID


class MainWindow(QtWidgets.QMainWindow):
    # 类构造函数
    def __init__(self):
        # super()构造器方法返回父级的对象。__init__()方法是构造器的一个方法。
        super().__init__()
        self.ui = MainUI.Ui_Form()
        self.ui.setupUi(self)

        # ####################### 相对路径 ######################
        # 初始化label显示的(黑色)背景
        self.bkg_pixmap = QPixmap('./logo_imgs/bkg1.png')
        # 设置主窗口的logo
        self.logo = QIcon('./logo_imgs/fcb_logo.jpg')
        # 设置提示框icon
        self.info_icon = QIcon('./logo_imgs/info_icon.jpg')
        # OpenCV深度学习人脸检测器的路径
        self.detector_path = "./model_face_detection"
        # OpenCV深度学习面部嵌入模型的路径
        self.embedding_model = "./model_facenet/openface_nn4.small2.v1.t7"
        # 训练模型以识别面部的路径
        self.recognizer_path = "./saved_weights/recognizer.pickle"
        # 标签编码器的路径
        self.le_path = "./saved_weights/le.pickle"

        # ###################### 窗口初始化 ######################
        # 设置窗口名称和图标
        self.setWindowTitle('人脸识别考勤系统 v2.0')
        self.setWindowIcon(self.logo)
        # 设置单张图片背景
        self.ui.label_camera.setPixmap(self.bkg_pixmap)
        # label_time显示系统时间
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_time_text)
        # 启动时间任务
        self.timer.start()

        # ###################### 摄像头初始化 ######################
        # 初始化摄像头，默认调用第一个摄像头
        # self.url = 0
        # 如果要调用摄像头1，则设置为1，适用于：笔记本外接USB摄像头
        self.url = 1
        self.cap = cv2.VideoCapture()
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)
        # self.cap.set(cv2.CAP_PROP_FPS, 20)

        # ###################### 按键的槽函数 ######################
        # 设置摄像头按键连接函数
        self.ui.bt_open_camera.clicked.connect(self.open_camera)
        # 设置开始考勤按键的回调函数
        self.ui.bt_start_check.clicked.connect(self.auto_control)
        # 设置活体检测按键的回调函数
        self.ui.bt_blinks.clicked.connect(self.blinks_thread)
        # 设置“退出系统”按键事件, 按下之后退出主界面
        self.ui.bt_exit.clicked.connect(QCoreApplication.instance().quit)
        # 设置信息采集按键连接
        self.ui.bt_gathering.clicked.connect(self.open_info_dialog)
        # 设置区分打开摄像头还是人脸识别的标识符
        self.switch_bt = 0

        # ###################### 数据库相关操作 ######################
        # 初始化需要记录的人名
        self.record_name1 = []
        # 设置更新人脸数据库的按键连接函数
        self.ui.bt_generator.clicked.connect(self.train_model)
        # 设置查询班级人数按键的连接函数
        self.ui.bt_check.clicked.connect(self.check_nums)
        # 设置请假按键的连接函数
        self.ui.bt_leave.clicked.connect(self.leave_button)
        # 设置漏签补签按键的连接函数
        self.ui.bt_supplement.clicked.connect(self.supplyment_button)
        # 设置对输入内容的删除提示
        self.ui.lineEdit_leave.setClearButtonEnabled(True)
        self.ui.lineEdit_supplement.setClearButtonEnabled(True)
        # 设置查看结果（显示未到和迟到）按键的连接函数
        self.ui.bt_view.clicked.connect(self.show_late_absence)

        # self.check_time_set, ok = QInputDialog.getText(self, '考勤时间设定', '请输入考勤时间(格式为00:00:00):')
        self.check_time_set = '08:00:00'

        # 设置输入考勤时间的限制
        self.ui.spinBox_time_hour.setRange(0, 23)
        self.ui.spinBox_time_minute.setRange(0, 59)

    # 显示系统时间以及相关文字提示函数
    def show_time_text(self):
        # 设置宽度
        self.ui.label_time.setFixedWidth(200)
        # 设置显示文本格式
        self.ui.label_time.setStyleSheet(
            # "QLabel{background:white;}" 此处设置背景色
            "QLabel{color:rgb(0, 0, 0); font-size:14px; font-weight:bold; font-family:宋体;}"
            "QLabel{font-size:14px; font-weight:bold; font-family:宋体;}")

        current_datetime = QDateTime.currentDateTime().toString()
        self.ui.label_time.setText("" + current_datetime)

        # 显示“人脸识别考勤系统”文字
        self.ui.label_title.setFixedWidth(400)
        self.ui.label_title.setStyleSheet("QLabel{font-size:26px; font-weight:bold; font-family:宋体;}")
        self.ui.label_title.setText("人脸识别考勤系统")

    def open_camera(self):
        # 判断摄像头是否打开，如果打开则为true，反之为false
        flag = self.cap.isOpened()
        if not flag:
            self.ui.label_logo.clear()
            # 默认打开Windows系统笔记本自带的摄像头，如果是外接USB，可将0改成1
            self.cap.open(self.url)
            self.show_camera()
        elif flag:
            self.cap.release()
            self.ui.label_logo.clear()
            self.ui.label_camera.clear()
            self.ui.bt_open_camera.setText(u'打开相机')

    # 进入考勤模式，通过switch_bt进行控制的函数
    def auto_control(self):
        self.check_time_set = str(self.ui.spinBox_time_hour.text()) + ":" + \
                              str(self.ui.spinBox_time_minute.text()) + ":" + "00"
        if self.check_time_set == '':
            QMessageBox.warning(self, "Warning", "请先设定考勤时间(例 08:00)！", QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Tips", f"您设定的考勤时间为：{self.check_time_set}", QMessageBox.Ok)

            if self.cap.isOpened():
                if self.switch_bt == 0:
                    self.switch_bt = 1
                    self.ui.bt_start_check.setText(u'退出考勤')
                    self.show_camera()
                elif self.switch_bt == 1:
                    self.switch_bt = 0
                    self.ui.bt_start_check.setText(u'开始考勤')
                    self.show_camera()
            else:
                QMessageBox.information(self, "Tips", "请先打开摄像头！", QMessageBox.Ok)

    def blinks_thread(self):
        bt_text = self.ui.bt_blinks.text()
        if self.cap.isOpened():
            if bt_text == '活体检测':
                # 初始化眨眼检测线程
                self.startThread = BlinksDetectThread()
                self.startThread.start()  # 启动线程
                self.ui.bt_blinks.setText('停止检测')
            else:
                self.ui.bt_blinks.setText('活体检测')
                # self.startThread.terminate()  # 停止线程
        else:
            QMessageBox.information(self, "Tips", "请先打开摄像头！", QMessageBox.Ok)

    def show_camera(self):
        # 如果按键按下
        global embedded, le, recognizer
        if self.switch_bt == 0:
            self.ui.label_logo.clear()
            self.ui.bt_open_camera.setText(u'关闭相机')
            while self.cap.isOpened():
                # 以BGR格式读取图像
                ret, self.image = self.cap.read()
                # 告诉QT处理来处理任何没有被处理的事件，并且将控制权返回给调用者，让代码变的没有那么卡
                QApplication.processEvents()
                # 将图像转换为RGB格式
                show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
                # opencv 读取图片的样式，不能通过Qlabel进行显示，需要转换为Qimage QImage(uchar * data, int width,
                self.showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
                self.ui.label_camera.setPixmap(QPixmap.fromImage(self.showImage))
            # 因为最后会存留一张图像在lable上，需要对lable进行清理
            self.ui.label_camera.clear()
            self.ui.bt_open_camera.setText(u'打开相机')
            # 设置单张图片背景
            self.ui.label_camera.setPixmap(self.bkg_pixmap)

        elif self.switch_bt == 1:
            self.ui.label_logo.clear()
            self.ui.bt_start_check.setText(u'退出考勤')

            # 人脸检测的置信度
            confidence_default = 0.5
            # 从磁盘加载序列化面部检测器
            proto_path = os.path.sep.join([self.detector_path, "deploy.prototxt"])
            model_path = os.path.sep.join([self.detector_path, "res10_300x300_ssd_iter_140000.caffemodel"])
            detector = cv2.dnn.readNetFromCaffe(proto_path, model_path)
            # 从磁盘加载序列化面嵌入模型
            try:
                self.ui.textBrowser_log.append("[INFO] loading face recognizer...")
                embedded = cv2.dnn.readNetFromTorch(self.embedding_model)
            except FileNotFoundError as e:
                self.ui.textBrowser_log.append("面部嵌入模型的路径不正确！", e)

            # 加载实际的人脸识别模型和标签
            try:
                recognizer = pickle.loads(open(self.recognizer_path, "rb").read())
                le = pickle.loads(open(self.le_path, "rb").read())
            except FileNotFoundError as e:
                self.ui.textBrowser_log.append("人脸识别模型保存路径不正确！", e)

            # 循环来自视频文件流的帧
            while self.cap.isOpened():
                # 从线程视频流中抓取帧
                ret, frame = self.cap.read()
                QApplication.processEvents()
                if ret:
                    # 调整框架的大小以使其宽度为900像素（同时保持纵横比），然后抓取图像尺寸
                    frame = imutils.resize(frame, width=900)
                    (h, w) = frame.shape[:2]
                    # 从图像构造一个blob
                    image_blob = cv2.dnn.blobFromImage(
                        cv2.resize(frame, (300, 300)), 1.0, (300, 300),
                        (104.0, 177.0, 123.0), swapRB=False, crop=False)
                    # 应用OpenCV的基于深度学习的人脸检测器来定位输入图像中的人脸
                    detector.setInput(image_blob)
                    detections = detector.forward()
                    # 保存识别到的人脸
                    face_names = []
                    # 识别到的人脸字典
                    face_name_dict = {}
                    # 循环检测
                    for i in np.arange(0, detections.shape[2]):
                        # 提取与预测相关的置信度（即概率）
                        confidence = detections[0, 0, i, 2]

                        # 用于更新相机开关按键信息
                        flag = self.cap.isOpened()
                        if not flag:
                            self.ui.bt_open_camera.setText(u'打开相机')
                        elif flag:
                            self.ui.bt_open_camera.setText(u'关闭相机')

                        # 过滤弱检测
                        if confidence > confidence_default:
                            # 计算面部边界框的（x，y）坐标
                            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                            (startX, startY, endX, endY) = box.astype("int")

                            # 提取面部ROI
                            face = frame[startY:endY, startX:endX]
                            (fH, fW) = face.shape[:2]

                            # 确保面部宽度和高度足够大
                            if fW < 20 or fH < 20:
                                continue

                            # 为面部ROI构造一个blob，然后通过我们的面部嵌入模型传递blob以获得面部的128-d量化
                            face_blob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
                            embedded.setInput(face_blob)
                            vec = embedded.forward()
                            # 执行分类识别面部
                            prediction = recognizer.predict_proba(vec)[0]
                            j = np.argmax(prediction)
                            probability = prediction[j]
                            name = le.classes_[j]
                            # 绘制面部的边界框以及相关的概率
                            text = "{}: {:.2f}%".format(name, probability * 100)
                            y = startY - 10 if startY - 10 > 10 else startY + 10
                            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                            frame = cv2.putText(frame, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                            face_names.append(name)

                            # face_name_dict[j] += 1

                    bt_liveness = self.ui.bt_blinks.text()
                    if bt_liveness == '停止检测':
                        ChineseText = PutChineseText.put_chinese_text('./utils/microsoft.ttf')
                        frame = ChineseText.draw_text(frame, (330, 80), ' 请眨眨眼睛 ', 25, (55, 255, 55))
                    # 显示输出框架
                    show_video = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
                    # opencv读取图片的样式，不能通过Qlabel进行显示，需要转换为Qimage。
                    # QImage(uchar * data, int width, int height, int bytesPerLine, Format format)
                    self.showImage = QImage(show_video.data, show_video.shape[1], show_video.shape[0],
                                            QImage.Format_RGB888)
                    self.ui.label_camera.setPixmap(QPixmap.fromImage(self.showImage))
                    self.set_name = set(face_names)
                    self.set_names = tuple(self.set_name)
                    self.record_names()
                else:
                    self.cap.release()

            # 因为最后一张画面会显示在GUI中，此处实现清除。
            self.ui.label_camera.clear()

    def record_names(self):
        if self.set_name.issubset(self.record_name1):  # 如果self.set_names是self.record_names 的子集返回ture
            pass  # record_name1是要写进数据库中的名字信息 set_name是从摄像头中读出人脸的tuple形式
        else:
            # 获取到self.set_name有而self.record_name无的名字
            self.different_name1 = self.set_name.difference(self.record_name1)
            # 把self.record_name变成两个集合的并集
            self.record_name1 = self.set_name.union(self.record_name1)
            # different_name是为了获取到之前没有捕捉到的人脸，并再次将record_name1进行更新
            # 将集合变成tuple，并统计人数
            self.write_data = tuple(self.different_name1)
            names_num = len(self.write_data)
            # 显示签到人数
            self.ui.lcd_2.display(len(self.record_name1))

            if names_num > 0:
                # 将签到信息写入数据库
                self.lineTextInfo2 = []
                # 打开数据库连接
                db, cursor = connect_to_sql()
                # 获取系统时间，保存到秒
                current_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                results2 = self.use_id_get_info(self.write_data[0])

                # 判断是否迟到
                self.ymd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.ymd2 = datetime.now().strftime("%H:%M:%S")
                compareResult2 = self.compare_time('{}'.format(self.ymd2), '{}'.format(self.check_time_set))

                # 82800表示23个小时,在compare_time()函数中,如果第一个时间小于第二个时间,则为第一个时间加24h后再减去第二时间;
                # 而正常的结果应该为'正常'.
                if compareResult2 <= 82800:
                    self.description2 = '迟到'
                else:
                    self.description2 = '正常'
                self.lineTextInfo2.append((results2[0], results2[1], results2[2], current_time, self.description2))
                print(self.lineTextInfo2)

                # 写入数据库
                try:
                    # 如果存在数据，先删除再写入。前提是设置唯一索引字段或者主键。
                    insert_sql2 = "replace into checkin(Name, ID, Class, Time, Description) values(%s, %s, %s, %s, %s)"
                    users2 = self.lineTextInfo2
                    cursor.executemany(insert_sql2, users2)
                except ValueError as e:
                    self.ui.textBrowser_log.append("[INFO] SQL execute failed!", e)
                else:
                    self.ui.textBrowser_log.append("[INFO] SQL execute success!")
                    QMessageBox.information(self, "Tips", "签到成功，请勿重复操作！", QMessageBox.Ok)
                # 提交到数据库执行
                db.commit()
                cursor.close()
                db.close()

    # 比较时间大小，判断是否迟到
    def compare_time(self, time1, time2):
        s_time = datetime.strptime(time1, '%H:%M:%S')
        e_time = datetime.strptime(time2, '%H:%M:%S')
        delta = s_time - e_time

        return delta.seconds

    # 查询班级人数
    def check_nums(self):
        # 选择的班级
        input_class = self.ui.comboBox_class.currentText()
        print("你当前选择的班级为:", input_class)
        try:
            # 打开数据库连接
            # 添加数据库连接操作, 使用cursor()方法获取操作游标
            db, cursor = connect_to_sql()
            # 查询语句，实现通过ID关键字检索个人信息的功能
            sql = "select * from studentnums where class = {}".format(input_class)

        except ValueError:
            self.ui.textBrowser_log.append("连接数据库失败！")
        else:
            self.ui.textBrowser_log.append("连接数据库成功，正在执行查询···")

        # 执行查询
        if input_class != '':
            try:
                cursor.execute(sql)
                # 获取所有记录列表
                results = cursor.fetchall()
                self.nums = []
                for i in results:
                    self.nums.append(i[1])

            except ValueError as e:
                self.ui.textBrowser_log.append("[ERROR] 查询失败，请检查命令！", e)
            else:
                self.ui.textBrowser_log.append("[INFO] 查询成功！")

        # 用于查询每班的实到人数
        sql2 = "select * from checkin where class = {}".format(input_class)
        # 执行查询
        if input_class != '':
            try:
                cursor.execute(sql2)
                # 获取所有记录列表
                results2 = cursor.fetchall()
                self.nums2 = []
                for i in results2:
                    self.nums2.append(i[2])
            except ValueError as e:
                self.ui.textBrowser_log.append("[ERROR] 查询实到人数失败！", e)
            else:
                self.ui.textBrowser_log.append("[INFO] 查询成功！")

        # lcd控件显示人数
        self.ui.lcd_1.display(self.nums[0])
        self.ui.lcd_2.display(len(self.nums2))
        # 关闭数据库连接
        db.close()

    # 请假/补签登记
    def leave_button(self):
        self.leave_students(1)

    def supplyment_button(self):
        self.leave_students(2)

    def leave_students(self, button):
        global results
        self.lineTextInfo = []
        # 为防止输入为空卡死，先进行是否输入数据的判断
        if self.ui.lineEdit_leave.isModified() or self.ui.lineEdit_supplement.isModified():
            # 打开数据库连接
            db, cursor = connect_to_sql()
            # 获取系统时间，保存到秒
            currentTime = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            if button == 1:
                self.ui.textBrowser_log.append("[INFO] 正在执行请假登记···")
                self.description = "请假"
                self.lineText_leave_id = self.ui.lineEdit_leave.text()
                results = self.use_id_get_info(self.lineText_leave_id)
            elif button == 2:
                self.ui.textBrowser_log.append("[INFO] 正在执行漏签补签···")
                self.description = "漏签补签"
                self.lineText_leave_id = self.ui.lineEdit_supplement.text()
                results = self.use_id_get_info(self.lineText_leave_id)
            
            if len(results) != 0:
                try:
                    self.ui.textBrowser_log.append("[INFO] 正在从数据库获取当前用户信息···")
                    print(results[0], results[1], results[2], currentTime, self.description)
                except ConnectionAbortedError as e:
                    self.ui.textBrowser_log.append("[INFO] 从数据库获取信息失败，请保证当前用户的信息和考勤记录已录入数据库！", e)
                # 写入数据库
                try:
                    # 如果存在数据，先删除再写入。前提是设置唯一索引字段或者主键。
                    insert_sql = "replace into checkin(Name, ID, Class, Time, Description) values(%s, %s, %s, %s, %s)"
                    users = self.lineTextInfo
                    cursor.executemany(insert_sql, users)
                except ValueError as e:
                    self.ui.textBrowser_log.append("[INFO] 写入数据库失败！", e)
                else:
                    self.ui.textBrowser_log.append("[INFO] 写入数据库成功！")
                    QMessageBox.warning(self, "Warning", "{} {}登记成功，请勿重复操作！".format(self.lineText_leave_id,
                                                                                    self.description), QMessageBox.Ok)
                # 提交到数据库执行
                db.commit()
                cursor.close()
                db.close()
            else:
                QMessageBox.warning(self, "Error", f"您输入的ID {self.lineText_leave_id} 不存在！请先录入数据库！")
        else:
            QMessageBox.warning(self, "Error", "学号不能为空，请输入后重试！", QMessageBox.Ok)  # (QMessageBox.Yes | QMessageBox.No)
        # 输入框清零
        self.ui.lineEdit_leave.clear()
        self.ui.lineEdit_supplement.clear()

    # 使用ID当索引找到其它信息
    def use_id_get_info(self, ID):
        # 打开数据库连接
        db, cursor = connect_to_sql()
        # 查询语句，实现通过ID关键字检索个人信息的功能
        sql = "select * from students where ID = {}".format(ID)
        # 执行查询
        if ID != '':
            try:
                cursor.execute(sql)
                # 获取所有记录列表
                results = cursor.fetchall()
                self.check_info = []
                for i in results:
                    self.check_info.append(i[1])
                    self.check_info.append(i[0])
                    self.check_info.append(i[2])
                return self.check_info
            except ConnectionAbortedError as e:
                self.ui.textBrowser_log.append("[ERROR] 数据库连接失败！")

        cursor.close()
        db.close()

    # 显示迟到和未到
    def show_late_absence(self):
        db, cursor = connect_to_sql()
        # 一定要注意字符串在检索时要加''！
        sql1 = "select name from checkin where Description = '{}'".format('迟到')
        sql2 = "select name from students"
        try:
            cursor.execute(sql1)
            results = cursor.fetchall()
            self.lateNums = []
            for x in results:
                self.lateNums.append(x[0])
            self.lateNums.sort()
            # self.ui.textBrowser_log.append(self.lateNums)
        except ConnectionAbortedError as e:
            self.ui.textBrowser_log.append('[INFO] 查询迟到数据失败', e)
        try:
            cursor.execute(sql2)
            results2 = cursor.fetchall()
            self.allNums = []
            for i in results2:
                self.allNums.append(i[0])
            self.allNums.sort()
            print(self.allNums)
        except ConnectionAbortedError as e:
            self.ui.textBrowser_log.append('[INFO] 查询未到数据失败', e)

        db.commit()
        cursor.close()
        db.close()

        # 集合运算，算出未到的和迟到的
        self.AbsenteeNums = set(set(self.allNums) - set(self.lateNums))
        self.AbsenteeNums = list(self.AbsenteeNums)
        self.AbsenteeNums.sort()

        # 在控件中显示未到的同学
        rowLate = len(self.lateNums)
        rowAbsentee = len(self.AbsenteeNums)
        model1 = QtGui.QStandardItemModel(rowLate, 0)
        # 设置数据行、列标题
        model1.setHorizontalHeaderLabels(['姓名'])
        # 设置填入数据内容
        for row in range(rowLate):
            item = QtGui.QStandardItem(self.lateNums[row])
            # 设置每个位置的文本值
            model1.setItem(row, 0, item)
        # 指定显示的tableView控件，实例化表格视图
        View1 = self.ui.tableView_escape
        View1.setModel(model1)

        # 迟到显示
        model2 = QtGui.QStandardItemModel(rowAbsentee, 0)
        # 设置数据行、列标题
        model2.setHorizontalHeaderLabels(['姓名'])
        # 设置填入数据内容
        for row in range(rowAbsentee):
            item = QtGui.QStandardItem(self.AbsenteeNums[row])
            # 设置每个位置的文本值
            model2.setItem(row, 0, item)
        # 指定显示的tableView控件，实例化表格视图
        View2 = self.ui.tableView_late
        View2.setModel(model2)

    # 训练人脸识别模型，静态方法
    # @staticmethod
    def train_model(self):
        q_message = QMessageBox.information(self, "Tips", "你确定要重新训练模型吗？", QMessageBox.Yes | QMessageBox.No)
        if QMessageBox.Yes == q_message:
            GeneratorModel.Generator()
            GeneratorModel.TrainModel()
            self.ui.textBrowser_log.append('[INFO] Model has been trained!')
        else:
            self.ui.textBrowser_log.append('[INFO] Cancel train process!')

    def open_info_dialog(self):
        if self.cap.isOpened():
            QMessageBox.warning(self, "Warning", "为防止摄像头冲突，已自动关闭摄像头！", QMessageBox.Ok)
            self.cap.release()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建并显示窗口
    mainWindow = MainWindow()
    infoWindow = InfoDialog()
    mainWindow.ui.bt_gathering.clicked.connect(infoWindow.handle_click)
    mainWindow.show()
    sys.exit(app.exec_())
