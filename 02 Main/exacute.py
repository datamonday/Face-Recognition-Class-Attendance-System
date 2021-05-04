# 导入必要的模块
import os
import pickle
import sys
from datetime import datetime

import cv2
import dlib
import imutils
import numpy as np
# 导入数据库操作包
import pymysql
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer, QDateTime, QCoreApplication, QThread
from PyQt5.QtGui import QImage, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QInputDialog

from imutils import face_utils
from imutils.video import VideoStream
# 导入眨眼检测必要的包
from scipy.spatial import distance as dist

# 导入UI主界面
from utils import MainUI
# 导入信息采集框界面
from utils import InfoUI
# 导入打印中文脚本
from utils import PutChineseText
# 导入人脸识别检测包
from utils import GeneratorModel


# 定义活体检测-眨眼检测类
class BlinksDetectThread(QThread):
    trigger = QtCore.pyqtSignal()

    def __init__(self):
        super(BlinksDetectThread, self).__init__()
        # 定义两个常数，一个用于眼睛纵横比以指示眨眼，第二个作为眨眼连续帧数的阈值
        self.EYE_AR_THRESH = 0.25
        self.EYE_AR_CONSEC_FRAMES = 3

        # 初始化帧计数器和总闪烁次数
        self.COUNTER = 0
        self.TOTAL = 0

        # 初始化变量
        self.A = 0
        self.B = 0
        self.C = 0
        self.leftEye = 0
        self.rightEye = 0
        self.leftEAR = 0
        self.rightEAR = 0
        self.ear = 0

        # 线程启动停止标识符
        self.BlinksFlag = 1

        try:
            # 初始化摄像头
            self.cap3 = cv2.VideoCapture()
            # self.cap3.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
            # self.cap3.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)
            # self.cap3.set(cv2.CAP_PROP_FPS, 30)

        except IOError as e:
            print("初始化摄像头失败！", e)

    # 定义眨眼检测距离函数
    def eye_aspect_ratio(self, eye):
        # 计算两组垂直方向上的眼睛标记（x，y）坐标之间的欧氏距离
        self.A = dist.euclidean(eye[1], eye[5])
        self.B = dist.euclidean(eye[2], eye[4])
        # 计算水平方向上的眼睛标记（x，y）坐标之间的欧氏距离
        self.C = dist.euclidean(eye[0], eye[3])
        # 计算眼睛的纵横比
        ear = (self.A + self.B) / (2.0 * self.C)
        # 返回眼睛的纵横比
        return ear

    def run(self):
        if self.BlinksFlag == 1:
            # 初始化dlib的人脸检测器（基于HOG），然后创建面部标志预测器
            print("[INFO] loading facial landmark predictor...")
            shape_predictor_path = "./facenet_model/shape_predictor_68_face_landmarks.dat"
            detector = dlib.get_frontal_face_detector()
            predictor = dlib.shape_predictor(shape_predictor_path)
            # 分别提取左眼和右眼的面部标志的索引
            (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
            (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
            # 在视频流的帧中循环
            self.cap3.open(0 + cv2.CAP_DSHOW)
            while self.BlinksFlag == 1:
                # 从线程视频文件流中抓取帧，调整其大小，并将其转换为灰度通道
                vs = VideoStream(src=cv2.CAP_DSHOW).start()
                frame3 = vs.read()
                # ret, frame3 = self.cap3.read()
                QApplication.processEvents()
                frame3 = imutils.resize(frame3, width=900)
                gray = cv2.cvtColor(frame3, cv2.COLOR_BGR2GRAY)
                # 检测灰度帧中的人脸
                rects = detector(gray, 0)
                # 循环检测人脸
                for rect in rects:
                    # 确定面部区域的面部标记，然后将面部标记（x，y）坐标转换为NumPy阵列
                    shape = predictor(gray, rect)
                    shape = face_utils.shape_to_np(shape)
                    # 提取左眼和右眼坐标，然后使用坐标计算双眼的眼睛纵横比
                    self.leftEye = shape[lStart:lEnd]
                    self.rightEye = shape[rStart:rEnd]
                    self.leftEAR = self.eye_aspect_ratio(self.leftEye)
                    self.rightEAR = self.eye_aspect_ratio(self.rightEye)
                    # 两只眼睛的平均眼睛纵横比
                    self.ear = (self.leftEAR + self.rightEAR) / 2.0
                    # 检查眼睛纵横比是否低于闪烁阈值,如果是,则增加闪烁帧计数器;否则执行else
                    if self.ear < self.EYE_AR_THRESH:
                        self.COUNTER += 1
                    else:
                        # 如果眼睛闭合次数足够则增加眨眼总数
                        if self.COUNTER >= self.EYE_AR_CONSEC_FRAMES:
                            self.TOTAL += 1
                        # 重置眼框计数器
                        self.COUNTER = 0
                self.trigger.emit()
                if self.TOTAL == 1:
                    print("活体！眨眼次数为: {}".format(self.TOTAL))

    # 定义停止线程操作
    def terminate(self):
        self.BlinksFlag = 0
        if flag2 == 0:
            VideoStream(src=cv2.CAP_DSHOW).stop()


#########################################################################################
class MainWindow(QWidget):
    # 类构造函数
    def __init__(self):
        # super()构造器方法返回父级的对象。__init__()方法是构造器的一个方法。
        super().__init__()
        self.ui = MainUI.Ui_Form()
        self.ui.setupUi(self)
        # 设置窗口名称和图标
        self.setWindowTitle('人脸识别考勤系统')
        self.setWindowIcon(QIcon('./logo_imgs/fcblogo.jpg'))

        # # # 造成卡顿
        # # label_time显示系统时间
        # timer = QTimer(self)
        # timer.timeout.connect(self.showTimeText)
        # timer.start()

        # 初始化摄像头
        # self.url = 0 # 这样调用摄像头会报错，并且会卡死。
        self.url = cv2.CAP_DSHOW  # 默认调用0，如果要调用摄像头1，可以这样写:cv2.CAP_DSHOW + 1
        self.cap = cv2.VideoCapture()
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)
        # self.cap.set(cv2.CAP_PROP_FPS, 20)

        # 设置单张图片背景
        self.pixmap = QPixmap('./logo_imgs/bkg1.png')
        self.ui.label_camera.setPixmap(self.pixmap)
        # 设置摄像头按键连接函数
        self.ui.bt_openCamera.clicked.connect(self.openCamera)
        # 设置开始考勤按键的回调函数
        self.ui.bt_startCheck.clicked.connect(self.autoControl)
        # 设置活体检测按键的回调函数
        self.ui.bt_blinks.clicked.connect(self.BlinksThread)
        # 设置“退出系统”按键事件, 按下之后退出主界面
        self.ui.bt_exit.clicked.connect(QCoreApplication.instance().quit)
        # 设置信息采集按键连接
        self.bt_gathering = self.ui.bt_gathering
        # 设置区分打开摄像头还是人脸识别的标识符
        self.switch_bt = 0
        global flag2
        flag2 = 0

        # 初始化需要记录的人名
        self.record_name1 = ([])

        # 设置更新人脸数据库的按键连接函数
        self.ui.bt_generator.clicked.connect(self.trainModel)
        # 设置查询班级人数按键的连接函数
        self.ui.bt_check.clicked.connect(self.checkNums)
        # 设置请假按键的连接函数
        self.ui.bt_leave.clicked.connect(self.leaveButton)
        # 设置漏签补签按键的连接函数
        self.ui.bt_Supplement.clicked.connect(self.supplymentButton)
        # 设置对输入内容的删除提示
        self.ui.lineEdit.setClearButtonEnabled(True)
        self.ui.lineEdit_2.setClearButtonEnabled(True)
        # 设置查看结果（显示未到和迟到）按键的连接函数
        self.ui.bt_view.clicked.connect(self.showLateAbsentee)

        self.checkTime, ok = QInputDialog.getText(self, '考勤时间设定', '请输入考勤时间(格式为00:00:00):')

    # 显示系统时间以及相关文字提示函数
    def showTimeText(self):
        # 设置宽度
        self.ui.label_time.setFixedWidth(200)
        # 设置显示文本格式
        self.ui.label_time.setStyleSheet(
            # "QLabel{background:white;}" 此处设置背景色
            # "QLabel{color:rgb(300,300,300,120); font-size:14px; font-weight:bold; font-family:宋体;}"
            "QLabel{font-size:14px; font-weight:bold; font-family:宋体;}"
        )
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
            self.ui.label_logo.clear()
            # 默认打开Windows系统笔记本自带的摄像头，如果是外接USB，可以将0改成1
            self.cap.open(0 + self.url)
            self.showCamera()
        elif flag == True:
            self.cap.release()
            self.ui.label_logo.clear()
            self.ui.label_camera.clear()
            self.ui.bt_openCamera.setText(u'打开相机')

    # 进入考勤模式，通过switch_bt进行控制的函数
    def autoControl(self):
        if self.switch_bt == 0:
            self.switch_bt = 1
            flag2 = 1
            self.ui.bt_startCheck.setText(u'退出考勤')
            self.showCamera()
        elif self.switch_bt == 1:
            self.switch_bt = 0
            flag2 = 0
            self.ui.bt_startCheck.setText(u'开始考勤')
            self.showCamera()

    def BlinksThread(self):
        bt_text = self.ui.bt_blinks.text()
        if bt_text == '活体检测':
            # 初始化眨眼检测线程
            self.startThread = BlinksDetectThread()
            self.startThread.start()  # 启动线程
            self.ui.bt_blinks.setText('停止检测')
        else:
            self.ui.bt_blinks.setText('活体检测')
            # self.startThread.terminate()  # 停止线程

    def showCamera(self):
        # 如果按键按下
        global embedded, le, recognizer
        if self.switch_bt == 0:
            self.ui.label_logo.clear()
            self.ui.bt_openCamera.setText(u'关闭相机')
            while (self.cap.isOpened()):
                # 以BGR格式读取图像

                # ret, self.image = self.cap.read(0 + cv2.CAP_DSHOW)
                ret, self.image = self.cap.read()

                QApplication.processEvents()  # 这句代码告诉QT处理来处理任何没有被处理的事件，并且将控制权返回给调用者，让代码变的没有那么卡
                # 将图像转换为RGB格式
                show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
                # opencv 读取图片的样式，不能通过Qlabel进行显示，需要转换为Qimage QImage(uchar * data, int width,
                self.showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
                self.ui.label_camera.setPixmap(QPixmap.fromImage(self.showImage))
            # 因为最后会存留一张图像在lable上，需要对lable进行清理
            self.ui.label_camera.clear()
            self.ui.bt_openCamera.setText(u'打开相机')
            # 设置单张图片背景
            self.ui.label_camera.setPixmap(self.pixmap)

        elif self.switch_bt == 1:
            self.ui.label_logo.clear()
            self.ui.bt_startCheck.setText(u'退出考勤')
            # OpenCV深度学习人脸检测器的路径
            detector_path = "./face_detection_model"
            # OpenCV深度学习面部嵌入模型的路径
            embedding_model = "./face_detection_model/openface_nn4.small2.v1.t7"
            # 训练模型以识别面部的路径
            recognizer_path = "./saved_weights/recognizer.pickle"
            # 标签编码器的路径
            le_path = "./saved_weights/le.pickle"
            # 置信度
            confidence_default = 0.5
            # 从磁盘加载序列化面部检测器
            proto_path = os.path.sep.join([detector_path, "deploy.prototxt"])
            model_path = os.path.sep.join([detector_path, "res10_300x300_ssd_iter_140000.caffemodel"])
            detector = cv2.dnn.readNetFromCaffe(proto_path, model_path)
            # 从磁盘加载序列化面嵌入模型
            try:
                print("[INFO] loading face recognizer...")
                embedded = cv2.dnn.readNetFromTorch(embedding_model)
            except IOError:
                print("面部嵌入模型的路径不正确！")

            # 加载实际的人脸识别模型和标签
            try:
                recognizer = pickle.loads(open(recognizer_path, "rb").read())
                le = pickle.loads(open(le_path, "rb").read())
            except IOError:
                print("人脸识别模型保存路径不正确！")
            # 循环来自视频文件流的帧
            while (self.cap.isOpened()):
                # 从线程视频流中抓取帧
                ret, frame = self.cap.read()
                QApplication.processEvents()
                if ret:
                    # 调整框架的大小以使其宽度为900像素（同时保持纵横比），然后抓取图像尺寸
                    frame = imutils.resize(frame, width=900)
                    (h, w) = frame.shape[:2]
                    # 从图像构造一个blob
                    imageBlob = cv2.dnn.blobFromImage(
                        cv2.resize(frame, (300, 300)), 1.0, (300, 300),
                        (104.0, 177.0, 123.0), swapRB=False, crop=False)
                    # 应用OpenCV的基于深度学习的人脸检测器来定位输入图像中的人脸
                    detector.setInput(imageBlob)
                    detections = detector.forward()
                    # 保存识别到的人脸
                    face_names = []
                    # 循环检测
                    for i in np.arange(0, detections.shape[2]):
                        # 提取与预测相关的置信度（即概率）
                        confidence = detections[0, 0, i, 2]

                        # 用于更新相机开关按键信息
                        flag = self.cap.isOpened()
                        if flag == False:
                            self.ui.bt_openCamera.setText(u'打开相机')
                        elif flag == True:
                            self.ui.bt_openCamera.setText(u'关闭相机')

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
                            faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
                            embedded.setInput(faceBlob)
                            vec = embedded.forward()
                            # 执行分类识别面部
                            preds = recognizer.predict_proba(vec)[0]
                            j = np.argmax(preds)
                            proba = preds[j]
                            name = le.classes_[j]
                            # 绘制面部的边界框以及相关的概率
                            text = "{}: {:.2f}%".format(name, proba * 100)
                            y = startY - 10 if startY - 10 > 10 else startY + 10
                            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                            frame = cv2.putText(frame, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                            face_names.append(name)

                    bt_liveness = self.ui.bt_blinks.text()
                    if bt_liveness == '停止检测':
                        ChineseText = PutChineseText.put_chinese_text('./utils/microsoft.ttf')
                        frame = ChineseText.draw_text(frame, (330, 80), ' 请眨眨眼睛 ', 25, (55, 255, 55))
                    # 显示输出框架
                    show_video = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
                    # opencv读取图片的样式，不能通过Qlabel进行显示，需要转换为Qimage。
                    # QImage(uchar * data, int width, int height, int bytesPerLine, Format format)
                    self.showImage = QImage(show_video.data, show_video.shape[1], show_video.shape[0], QImage.Format_RGB888)
                    self.ui.label_camera.setPixmap(QPixmap.fromImage(self.showImage))
                    self.set_name = set(face_names)
                    self.set_names = tuple(self.set_name)
                    self.recordNames()
                else:
                    self.cap.release()

            # 因为最后一张画面会显示在GUI中，此处实现清除。
            self.ui.label_camera.clear()

    def recordNames(self):
        if self.set_name.issubset(self.record_name1):  # 如果self.set_names是self.record_names 的子集返回ture
            pass  # record_name1是要写进数据库中的名字信息 set_name是从摄像头中读出人脸的tuple形式
        else:
            self.different_name1 = self.set_name.difference(self.record_name1)  # 获取到self.set_name有而self.record_name无的名字
            self.record_name1 = self.set_name.union(self.record_name1)  # 把self.record_name变成两个集合的并集
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
                db2 = pymysql.connect(host="localhost", user="root", password="mysql105", database="facerecognition")
                # 使用cursor()方法获取操作游标
                cursor2 = db2.cursor()
                # 获取系统时间，保存到秒
                import datetime
                currentTime2 = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                results2 = self.useIDGetInfo(self.write_data[0])
                # 判断是否迟到
                import datetime
                self.ymd = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.ymd2 = datetime.datetime.now().strftime("%H:%M:%S")
                compareResult2 = self.compare_time('{}'.format(self.ymd2), '{}'.format(self.checkTime))

                # 82800表示23个小时,在compare_time()函数中,如果第一个时间小于第二个时间,则为第一个时间加24h后再减去第二时间;
                # 而正常的结果应该为'正常'.
                if compareResult2 <= 82800:
                    self.description2 = '迟到'
                else:
                    self.description2 = '正常'
                self.lineTextInfo2.append((results2[0], results2[1], results2[2], currentTime2, self.description2))
                print(self.lineTextInfo2)

                # 写入数据库
                try:
                    # 如果存在数据，先删除再写入。前提是设置唯一索引字段或者主键。
                    insert_sql2 = "replace into checkin(Name, ID, Class, Time, Description) values(%s, %s, %s, %s, %s)"
                    users2 = self.lineTextInfo2
                    cursor2.executemany(insert_sql2, users2)
                except ValueError as e:
                    print(e)
                    print("SQL execute failed!")
                else:
                    print("SQL execute success!")
                    QMessageBox.information(self, "Tips", "签到成功，请勿重复操作！", QMessageBox.Yes | QMessageBox.No)
                # 提交到数据库执行
                db2.commit()
                cursor2.close()
                db2.close()

    # 比较时间大小，判断是否迟到
    def compare_time(self, time1, time2):
        import datetime
        s_time = datetime.datetime.strptime(time1, '%H:%M:%S')
        e_time = datetime.datetime.strptime(time2, '%H:%M:%S')
        delta = s_time - e_time

        return delta.seconds

    # 查询班级人数
    def checkNums(self):
        # 选择的班级
        global cursor, sql, db
        input_class = self.ui.comboBox.currentText()
        print("你当前选择的班级为:", input_class)

        try:
            # 打开数据库连接
            db = pymysql.connect(host="localhost", user="root", password="mysql105", database="facerecognition")
            # 使用cursor()方法获取操作游标
            cursor = db.cursor()
            # 查询语句，实现通过ID关键字检索个人信息的功能
            sql = "select * from studentnums where class = {}".format(input_class)

        except ValueError:
            print("连接数据库失败！")
        else:
            print("连接数据库成功，正在执行查询···")

        # 执行查询
        if input_class != '':
            try:
                cursor.execute(sql)
                # 获取所有记录列表
                results = cursor.fetchall()
                self.nums = []
                for i in results:
                    self.nums.append(i[1])

            except ValueError:
                print("查询失败，请检查命令！")
            else:
                print("查询成功！")

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
            except ValueError:
                print("查询实到人数失败！")
            else:
                print("查询成功！")

        # lcd控件显示人数
        self.ui.lcd_1.display(self.nums[0])
        self.ui.lcd_2.display(len(self.nums2))
        # 关闭数据库连接
        db.close()

    # 请假/补签登记
    def leaveButton(self):
        self.leaveStudents(1)

    def supplymentButton(self):
        self.leaveStudents(2)

    def leaveStudents(self, button):
        global results
        self.lineTextInfo = []
        # 为防止输入为空卡死，先进行是否输入数据的判断
        if self.ui.lineEdit.isModified() or self.ui.lineEdit_2.isModified():
            # 打开数据库连接
            db = pymysql.connect(host="localhost", user="root", password="mysql105", database="facerecognition")
            # 使用cursor()方法获取操作游标
            cursor = db.cursor()
            # 获取系统时间，保存到秒
            currentTime = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            if button == 1:
                print("正在执行请假登记···")
                self.description = "请假"
                self.lineTextID = self.ui.lineEdit.text()
                results = self.useIDGetInfo(self.lineTextID)
            elif button == 2:
                print("正在执行漏签补签···")
                self.description = "漏签补签"
                self.lineTextID = self.ui.lineEdit_2.text()
                results = self.useIDGetInfo(self.lineTextID)
            try:
                print("正在从数据库获取当前用户信息···")
                self.lineTextInfo.append((results[0], results[1], results[2], currentTime, self.description))
            except ValueError:
                print("从数据库获取信息失败，请保证当前用户的信息和考勤记录已录入数据库！")

            # 写入数据库
            try:
                # 如果存在数据，先删除再写入。前提是设置唯一索引字段或者主键。
                insert_sql = "replace into checkin(Name, ID, Class, Time, Description) values(%s, %s, %s, %s, %s)"
                users = self.lineTextInfo
                cursor.executemany(insert_sql, users)
            except ValueError as e:
                print(e)
                print("写入数据库失败！")
            else:
                print("写入数据库成功！")
                QMessageBox.warning(self, "warning", "{} 登记成功，请勿重复操作！".format(self.description),
                                    QMessageBox.Yes | QMessageBox.No)
            # 提交到数据库执行
            db.commit()
            cursor.close()
            db.close()
        else:
            QMessageBox.warning(self, "warning", "学号不能为空，请输入后重试！", QMessageBox.Yes | QMessageBox.No)
        # 输入框清零
        self.ui.lineEdit.clear()
        self.ui.lineEdit_2.clear()

    # 使用ID当索引找到其它信息
    def useIDGetInfo(self, ID):
        # 打开数据库连接
        db = pymysql.connect(host="localhost", user="root", password="mysql105", database="facerecognition")
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()
        # 查询语句，实现通过ID关键字检索个人信息的功能
        sql = "select * from students where ID = {}".format(ID)
        # 执行查询
        if ID != '':
            try:
                cursor.execute(sql)
                # 获取所有记录列表
                results = cursor.fetchall()
                self.checkInfo = []
                for i in results:
                    self.checkInfo.append(i[1])
                    self.checkInfo.append(i[0])
                    self.checkInfo.append(i[2])
                return self.checkInfo
            except:
                print("Error: unable to fetch data")

    # 显示迟到和未到
    def showLateAbsentee(self):
        db = pymysql.connect(host="localhost", user="root", password="mysql105", database="facerecognition")
        cursor = db.cursor()
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
            # print(self.lateNums)
        except:
            print("Error: unable to fetch latedata")
        try:
            cursor.execute(sql2)
            results2 = cursor.fetchall()
            self.allNums = []
            for i in results2:
                self.allNums.append(i[0])
            self.allNums.sort()
            print(self.allNums)
        except:
            print("Error: unable to fetch absenteedata")

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

    # 训练人脸识别模型
    def trainModel(self):
        GeneratorModel.Generator()
        GeneratorModel.TrainModel()
        print('Model have been trained!')


##########################################################################################
class infoDialog(QWidget):
    def __init__(self):
        # super()构造器方法返回父级的对象。__init__()方法是构造器的一个方法。
        super().__init__()
        self.Dialog = InfoUI.Ui_Form()
        self.Dialog.setupUi(self)

        # 设置窗口名称和图标
        self.setWindowTitle('个人信息采集')
        self.setWindowIcon(QIcon('./logo_imgs/fcblogo.jpg'))

        # 设置单张图片背景
        pixmap = QPixmap('background2.png')
        self.Dialog.label_capture.setPixmap(pixmap)

        # 设置信息采集按键连接函数
        self.Dialog.bt_collectInfo.clicked.connect(self.openCam)
        # 设置拍照按键连接函数
        self.Dialog.bt_takephoto.clicked.connect(self.takePhoto)
        # 设置查询信息按键连接函数
        self.Dialog.bt_checkInfo.clicked.connect(self.checkInfo)
        # 设置写入信息按键连接函数
        self.Dialog.bt_changeInfo.clicked.connect(self.changeInfo)
        # 初始化信息导入列表
        self.users = []
        # 初始化摄像头
        self.url2 = cv2.CAP_DSHOW
        self.cap2 = cv2.VideoCapture()

        # 初始化保存人脸数目
        self.photos = 0

    def handle_click(self):
        if not self.isVisible():
            self.show()

    def handle_close(self):
        self.close()

    def openCam(self):
        # 判断摄像头是否打开，如果打开则为true，反之为false
        flagCam = self.cap2.isOpened()
        if flagCam == False:
            # 通过对话框设置被采集人学号
            self.text, self.ok = QInputDialog.getText(self, '创建个人图像数据库', '请输入学号:')
            if self.ok and self.text != '':
                self.Dialog.label_capture.clear()
                self.cap2.open(0 + self.url2)
                self.showCapture()
        elif flagCam == True:
            self.cap2.release()
            self.Dialog.label_capture.clear()
            self.Dialog.bt_collectInfo.setText(u'采集人像')

    def showCapture(self):
        self.Dialog.bt_collectInfo.setText(u'停止采集')
        self.Dialog.label_capture.clear()
        # 导入opencv人脸检测xml文件
        cascade = './haar_cascades/haarcascade_frontalface_default.xml'
        # 加载 Haar级联人脸检测库
        detector = cv2.CascadeClassifier(cascade)
        print("[INFO] starting video stream...")
        # 循环来自视频文件流的帧
        while self.cap2.isOpened():
            ret, frame2 = self.cap2.read()
            QApplication.processEvents()
            self.orig = frame2.copy()
            frame2 = imutils.resize(frame2, width=500)
            rects = detector.detectMultiScale(cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY), scaleFactor=1.1,
                                              minNeighbors=5, minSize=(30, 30))
            for (x, y, w, h) in rects:
                cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 255, 0), 2)
                frame2 = cv2.putText(frame2, "Have token {}/20 faces".format(self.photos), (50, 60),
                                     cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                     (200, 100, 50), 2)
            # 显示输出框架
            show_video2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
            # opencv读取图片的样式，不能通过Qlabel进行显示，需要转换为Qimage。
            # QImage(uchar * data, int width, int height, int bytesPerLine, Format format)
            self.showImage2 = QImage(show_video2.data, show_video2.shape[1], show_video2.shape[0], QImage.Format_RGB888)
            self.Dialog.label_capture.setPixmap(QPixmap.fromImage(self.showImage2))
            # 因为最后一张画面会显示在GUI中，此处实现清除。
        self.Dialog.label_capture.clear()

    # 创建文件夹
    def mkdir(self, path):
        # 去除首位空格
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")
        # 判断路径是否存在, 存在=True; 不存在=False
        isExists = os.path.exists(path)
        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            os.makedirs(path)
            return True

    def takePhoto(self):
        self.photos += 1
        self.filename = "./face_dataset/{}/".format(self.text)
        self.mkdir(self.filename)
        photo_save_path = os.path.join(os.path.dirname(os.path.abspath('__file__')), '{}'.format(self.filename))
        self.showImage2.save(photo_save_path + datetime.now().strftime("%Y%m%d%H%M%S") + ".png")
        # p = os.path.sep.join([output, "{}.png".format(str(total).zfill(5))])
        # cv2.imwrite(p, self.showImage2)
        if self.photos == 20:
            QMessageBox.information(self, "Information", self.tr("采集成功!"), QMessageBox.Yes | QMessageBox.No)

    # 数据库查询
    def checkInfo(self):
        # 键入ID
        global cursor, db
        self.input_ID = self.Dialog.lineEdit_ID.text()
        # 打开数据库连接
        try:
            db = pymysql.connect(host="localhost", user="root", password="mysql105", database="facerecognition")
            # 使用cursor()方法获取操作游标
            cursor = db.cursor()
        except ValueError:
            print("数据库连接失败！")

        # 查询语句，实现通过ID关键字检索个人信息的功能
        sql = "SELECT * FROM STUDENTS WHERE ID = {}".format(self.input_ID)
        # 执行查询
        if self.input_ID != '':
            try:
                cursor.execute(sql)
                # 获取所有记录列表
                results = cursor.fetchall()
                self.lists = []
                for i in results:
                    self.lists.append(i[0])
                    self.lists.append(i[1])
                    self.lists.append(i[2])
                    self.lists.append(i[3])
                    self.lists.append(i[4])
            except ValueError:
                print("Error: unable to fetch data")

        # 设置显示数据层次结构，5行2列(包含行表头)
        self.model = QtGui.QStandardItemModel(5, 0)
        # 设置数据行、列标题
        self.model.setHorizontalHeaderLabels(['值'])
        self.model.setVerticalHeaderLabels(['学号', '姓名', '班级', '性别', '生日'])
        # 设置填入数据内容
        nums = len(self.lists)
        if nums == 0:
            QMessageBox.warning(self, "warning", "人脸数据库中无此人信息，请马上录入！", QMessageBox.Yes | QMessageBox.No)

        for row in range(nums):
            item = QtGui.QStandardItem(self.lists[row])
            # 设置每个位置的文本值
            self.model.setItem(row, 0, item)
        # 指定显示的tableView控件，实例化表格视图
        self.View = self.Dialog.tableView
        self.View.setModel(self.model)
        # 关闭数据库连接
        db.close()

    # 将采集信息写入数据库
    def userInfo(self):
        ID = self.Dialog.lineEdit_ID.text()
        Name = self.Dialog.lineEdit_Name.text()
        Class = self.Dialog.lineEdit_Class.text()
        Sex = self.Dialog.lineEdit_Sex.text()
        Birth = self.Dialog.lineEdit_Birth.text()
        self.users.append((ID, Name, Class, Sex, Birth))

        return self.users

    def changeInfo(self):
        # 打开数据库连接
        db = pymysql.connect(host="localhost", user="root", password="mysql105", database="facerecognition")
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()
        # 写入数据库
        try:
            # 如果存在数据，先删除再写入。前提是设置唯一索引字段或者主键。
            insert_sql = "replace into students(ID, Name, Class, Sex, Birthday) values(%s, %s, %s, %s, %s)"
            users = self.userInfo()
            cursor.executemany(insert_sql, users)
        except Exception as e:
            print(e)
            print("sql execute failed")
        else:
            print("sql execute success")
            QMessageBox.warning(self, "warning", "录入成功，请勿重复操作！", QMessageBox.Yes | QMessageBox.No)

        # 提交到数据库执行
        db.commit()
        # 关闭数据库
        cursor.close()
        # 关闭数据库连接
        db.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建并显示窗口
    mainWindow = MainWindow()
    infoWindow = infoDialog()
    mainWindow.ui.bt_gathering.clicked.connect(infoWindow.handle_click)
    mainWindow.show()
    sys.exit(app.exec_())
