# 导入必要的包
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import time
import dlib
import cv2

def eye_aspect_ratio(eye):
	# 计算两组垂直方向上的眼睛标记（x，y）坐标之间的欧氏距离
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])
	# 计算水平方向上的眼睛标记（x，y）坐标之间的欧氏距离
	C = dist.euclidean(eye[0], eye[3])
	# 计算眼睛的纵横比
	ear = (A + B) / (2.0 * C)
	# 返回眼睛的纵横比
	return ear

# 定义两个常数，一个用于眼睛纵横比以指示眨眼，第二个作为眨眼连续帧数的阈值
EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 3

# 初始化帧计数器和总闪烁次数
COUNTER = 0
TOTAL = 0

# 初始化dlib的人脸检测器（基于HOG），然后创建面部标志预测器
print("[INFO] loading facial landmark predictor...")
shape_predictor_path = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor_path)

# 分别提取左眼和右眼的面部标志的索引
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# 启动视频流线程
print("[INFO] starting video stream thread...")
vs = VideoStream(src=cv2.CAP_DSHOW).start()
fileStream = False
time.sleep(1.0)

# 在视频流的帧中循环
while True:
	# 如果是一个文件视频流，需要检查缓冲区中是否还有剩余的帧要处理
	if fileStream and not vs.more():
		break

	# 从线程视频文件流中抓取帧，调整其大小，并将其转换为灰度通道
	frame = vs.read()
	frame = imutils.resize(frame, width=450)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# 检测灰度帧中的人脸
	rects = detector(gray, 0)

	# 循环检测人脸
	for rect in rects:
		# 确定面部区域的面部标记，然后将面部标记（x，y）坐标转换为NumPy阵列
		shape = predictor(gray, rect)
		shape = face_utils.shape_to_np(shape)

		# 提取左眼和右眼坐标，然后使用坐标计算双眼的眼睛纵横比
		leftEye = shape[lStart:lEnd]
		rightEye = shape[rStart:rEnd]
		leftEAR = eye_aspect_ratio(leftEye)
		rightEAR = eye_aspect_ratio(rightEye)

		# 两只眼睛的平均眼睛纵横比
		ear = (leftEAR + rightEAR) / 2.0

		# 计算左眼和右眼的凸包，然后可视化每只眼睛
		leftEyeHull = cv2.convexHull(leftEye)
		rightEyeHull = cv2.convexHull(rightEye)
		cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

		# 检查眼睛纵横比是否低于闪烁阈值，如果是，则增加闪烁帧计数器
		if ear < EYE_AR_THRESH:
			COUNTER += 1
		# 否则执行以下
		else:
			# 如果眼睛闭合次数足够则增加眨眼总数
			if COUNTER >= EYE_AR_CONSEC_FRAMES:
				TOTAL += 1

			# 重置眼框计数器
			COUNTER = 0

		# 绘制帧上的闪烁总数以及眼睛的纵横比
		cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
		cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

	# 展示检测框
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	# 设置Q为退出键
	if key == ord("q"):
		break

# 清理线程
cv2.destroyAllWindows()
vs.stop()