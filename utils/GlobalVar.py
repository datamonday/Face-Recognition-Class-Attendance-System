import os
import sys
import pymysql


# 全局变量
# 摄像头ID
CAMERA_ID = 1
# 默认采集人脸数量
COLLENCT_FACE_NUM_DEFAULT = 100

# 多少次循环保存一帧图像
LOOP_FRAME = 20

# 设定一节课(大课，两小节)时长
COURSE_TIME = 35  # minutes
# 设定上课多长时间认为是迟到
LATE_SPAN = 30


# 将execute文件所在目录添加到根目录
def add_path_to_sys():
    rootdir = "D:/Github/Face-Recognition-Class-Attendance-System/"
    # rootdir = os.getcwd()
    sys.path.append(rootdir)

    return rootdir


# 连接数据库操作
def connect_to_sql():
    db = pymysql.connect(host="localhost", user="root", password="mysql105", database="facerecognition")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    return db, cursor


print(os.path.basename(__file__))
