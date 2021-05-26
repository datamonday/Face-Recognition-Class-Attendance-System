from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QDateTime, QCoreApplication, QThread
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QInputDialog

# 导入人脸关键点检测库
import cv2
import dlib
import imutils
from imutils import face_utils
from imutils.video import VideoStream
# 导入眨眼检测必要的包
from scipy.spatial import distance as dist

# 将根目录（execute所在目录）添加到环境变量
from utils.GlobalVar import add_path_to_sys
rootdir = add_path_to_sys()

# 导入全局变量：摄像头ID
from utils.GlobalVar import CAMERA_ID


# 定义活体检测-眨眼检测类
class BlinksDetectThread(QThread):
    trigger = QtCore.pyqtSignal()

    def __init__(self):
        """
        :rtype: object
        """
        super(BlinksDetectThread, self).__init__()

        # 人眼关键点检测模型路径，用于活体鉴别
        self.shape_predictor_path = f"{rootdir}/model_blink_detection/shape_predictor_68_face_landmarks.dat"
        # 定义两个常数，一个用于眼睛纵横比以指示眨眼，第二个作为眨眼连续帧数的阈值
        self.EYE_AR_THRESH = 0.20
        self.EYE_AR_CONSEC_FRAMES = 2

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
            detector = dlib.get_frontal_face_detector()
            predictor = dlib.shape_predictor(self.shape_predictor_path)
            # 分别提取左眼和右眼的面部标志的索引
            (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
            (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
            while self.BlinksFlag == 1:
                # 从线程视频文件流中抓取帧，调整其大小，并将其转换为灰度通道
                # vs = VideoStream(src=cv2.CAP_DSHOW).start()
                vs = VideoStream(src=CAMERA_ID).start()
                frame = vs.read()
                QApplication.processEvents()
                frame = imutils.resize(frame, width=900)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
                    print("[INFO] 活体！眨眼次数为: {}".format(self.TOTAL))
                    print("[INFO] 人眼纵横比：", self.ear)

    # 定义停止线程操作
    def terminate(self):
        self.BlinksFlag = 0
        if flag2 == 0:
            VideoStream(src=CAMERA_ID).stop()