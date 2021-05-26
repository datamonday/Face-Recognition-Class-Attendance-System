from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QIcon, QPixmap
from PyQt5.QtCore import QCoreApplication, QThread
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QInputDialog
# 导入信息采集框界面
from ui import InfoUI

import threading
import cv2
import imutils
import os
import sys
from datetime import datetime
# 导入全局变量，主要包含摄像头ID，默认采集人脸数量等
from utils.GlobalVar import CAMERA_ID, COLLENCT_FACE_NUM_DEFAULT, LOOP_FRAME
# 将根目录（execute所在目录）添加到环境变量
from utils.GlobalVar import add_path_to_sys
rootdir = add_path_to_sys()

# 添加数据库连接操作
from utils.GlobalVar import connect_to_sql


class InfoDialog(QWidget):
    def __init__(self):
        # super()构造器方法返回父级的对象。__init__()方法是构造器的一个方法。
        super().__init__()

        self.lists = []
        self.Dialog = InfoUI.Ui_Form()
        self.Dialog.setupUi(self)

        # 实现路径错误提示，方便定位错误
        self.current_filename = os.path.basename(__file__)

        try:
            # 设置窗口名称和图标
            self.setWindowTitle('个人信息采集')
            self.setWindowIcon(QIcon(f'{rootdir}/logo_imgs/fcb_logo.jpg'))
            # 设置单张图片背景
            pixmap = QPixmap(f'{rootdir}/logo_imgs/bkg2.png')
            self.Dialog.label_capture.setPixmap(pixmap)
        except FileNotFoundError as e:
            print("[ERROR] 路径不正确！(source file: {})".format(self.current_filename), e)

        # 设置信息采集按键连接函数
        self.Dialog.bt_start_collect.clicked.connect(self.open_camera)
        # 设置拍照按键连接函数
        self.Dialog.bt_take_photo.clicked.connect(self.take_photo)
        # 设置查询信息按键连接函数
        self.Dialog.bt_check_info.clicked.connect(self.check_info)
        # 设置写入信息按键连接函数
        self.Dialog.bt_change_info.clicked.connect(self.change_info)

        # 初始化信息导入列表
        self.users = []

        # 初始化摄像头
        # self.cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
        self.cap = cv2.VideoCapture()

        # 设置默认采集的照片数量
        self.Dialog.spinBox_set_num.setValue(COLLENCT_FACE_NUM_DEFAULT)
        # 初始化已经采集的人脸数目
        self.have_token_photos = 0

        # 初始化一个变量用来存储上一次采集人脸的ID
        self.dialog_text_id_past = None

        self.collect_photos = int(self.Dialog.spinBox_set_num.text())

    def handle_click(self):
        if not self.isVisible():
            self.show()

    def handle_close(self):
        self.close()

    def open_camera(self):
        # 判断摄像头是否打开，如果打开则为true，反之为false
        if not self.cap.isOpened():
            # 通过对话框设置被采集人学号
            self.dialog_text_id, ok = QInputDialog.getText(self, '创建个人图像数据库', '请输入学号:')
            if ok and self.dialog_text_id != '':

                # 如果两次输入的学号不同，则将上一次的采集图像数量图片等删除
                if self.dialog_text_id != self.dialog_text_id_past:
                    self.have_token_photos = 0
                    self.Dialog.lcdNumber_collection_nums.display(0)

                self.Dialog.label_capture.clear()
                self.cap.open(CAMERA_ID)
                self.show_capture()
        else:
            self.cap.release()
            self.Dialog.label_capture.clear()
            self.Dialog.bt_start_collect.setText(u'开始采集')

    def show_capture(self):
        self.Dialog.bt_start_collect.setText(u'停止采集')
        self.Dialog.label_capture.clear()
        print("[INFO] starting video stream...")
        loop_num = 0

        # 循环来自视频文件流的帧
        while self.cap.isOpened():
            # 获取设定的最大采集张数
            self.collect_photos = int(self.Dialog.spinBox_set_num.text())
            # 循环自增
            loop_num += 1

            ret, frame = self.cap.read()
            QApplication.processEvents()
            frame = imutils.resize(frame, width=500)
            # frame = cv2.putText(frame, "Have token {}/{} faces".format(self.have_token_photos,
            # self.Dialog.spinBox_set_num.text()), (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 100, 50), 2) 显示输出框架
            show_video = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
            # opencv读取图片的样式，不能通过Qlabel进行显示，需要转换为Qimage。
            # QImage(uchar * data, int width, int height, int bytesPerLine, Format format)
            self.showImage = QImage(show_video.data,
                                    show_video.shape[1],
                                    show_video.shape[0],
                                    QImage.Format_RGB888)
            self.Dialog.label_capture.setPixmap(QPixmap.fromImage(self.showImage))
            # 是否为自动采集
            is_auto_collect = self.Dialog.checkBox_auto_collect.isChecked()

            if is_auto_collect:
                # 如果达到设定的最大采集数量则退出
                if self.have_token_photos != self.collect_photos:
                    # 大量I/O，为保证每次都写入磁盘，20次循环写入一次
                    if loop_num == LOOP_FRAME:
                        self.have_token_photos += 1
                        self.save_image()

                        loop_num = 0
                if self.have_token_photos == self.collect_photos:
                    QMessageBox.warning(self, "Warning", "已达到最大采集张数:{}！请增加采集数量或停止采集！".format(self.have_token_photos), QMessageBox.Ok)
                    self.cap.release()
                    self.Dialog.bt_start_collect.setText('开始采集')
                    break
            else:
                QMessageBox.information(self, "Tips", "已退出自动采集模式，请手动采集！")
                # self.cap.release()
                # self.Dialog.bt_start_collect.setText('开始采集')
                break

        # 记录上次需要采集的照片数量
        self.dialog_text_id_past = self.dialog_text_id

        # 因为最后一张画面会显示在GUI中，此处实现清除。
        self.Dialog.label_capture.clear()

    def save_image(self, method='qt5'):
        self.filename = '{}/face_dataset/{}/'.format(rootdir, self.dialog_text_id)
        self.mk_folder(self.filename)
        if method == 'qt5':
            photo_save_path = os.path.join(os.path.dirname(os.path.abspath('__file__')), '{}'.format(self.filename))
            save_filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".png"
            self.showImage.save(photo_save_path + save_filename)
        else:
            p = os.path.sep.join([output, "{}.png".format(str(total).zfill(5))])
            cv2.imwrite(p, self.showImage)

        self.Dialog.lcdNumber_collection_nums.display(self.have_token_photos)

    # 创建文件夹
    def mk_folder(self, path):
        # 去除首位空格
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")
        # 判断路径是否存在, 存在=True; 不存在=False
        is_dir_exists = os.path.exists(path)
        # 判断结果
        if not is_dir_exists:
            # 如果不存在则创建目录
            os.makedirs(path)
            return True

    def take_photo(self):
        if self.cap.isOpened():
            self.collect_photos = int(self.Dialog.spinBox_set_num.text())
            # print('self.collect_photos: ', self.collect_photos, type(self.collect_photos))
            # print(self.have_token_photos, type(self.have_token_photos))
            if self.have_token_photos != self.collect_photos:
                self.have_token_photos += 1
                try:
                    self.save_image()
                except FileNotFoundError as e:
                    print("[ERROR] 路径不正确！(source file: {})".format(self.current_filename), e)

            else:
                QMessageBox.information(self, "Information", self.tr("已达到设置的最大采集张数!"), QMessageBox.Ok)

        else:
            QMessageBox.information(self, "Information", self.tr("请先打开摄像头！"), QMessageBox.Ok)

    # 数据库查询
    def check_info(self):
        global cursor, db
        # 打开数据库连接
        try:
            db, cursor = connect_to_sql()
        except ValueError:
            print("[ERROR] 数据库连接失败！")

        self.input_id = self.Dialog.lineEdit_id.text()
        # 查询语句，实现通过ID关键字检索个人信息的功能
        sql = "SELECT * FROM STUDENTS WHERE ID = {}".format(self.input_id)
        # 执行查询
        if self.input_id != '':
            try:
                cursor.execute(sql)
                # 获取所有记录列表
                results = cursor.fetchall()
                for i in results:
                    self.lists.append(i[0])
                    self.lists.append(i[1])
                    self.lists.append(i[2])
                    self.lists.append(i[3])
                    self.lists.append(i[4])
            except ValueError:
                print("[ERROR] 无法查询！")

        # 设置显示数据层次结构，5行2列(包含行表头)
        self.module = QtGui.QStandardItemModel(5, 0)
        # 设置数据行、列标题
        self.module.setHorizontalHeaderLabels(['值'])
        self.module.setVerticalHeaderLabels(['学号', '姓名', '班级', '性别', '生日'])

        # 设置填入数据内容
        nums = len(self.lists)
        if nums == 0:
            QMessageBox.warning(self, "warning", "人脸数据库中无此人信息，请马上录入！", QMessageBox.Ok)

        for row in range(nums):
            item = QtGui.QStandardItem(self.lists[row])
            # 设置每个位置的文本值
            self.module.setItem(row, 0, item)
        # 指定显示的tableView控件，实例化表格视图
        self.table_view = self.Dialog.tableView
        self.table_view.setModel(self.module)
        # 关闭数据库连接
        db.close()

    # 将采集信息写入数据库
    def write_info(self):
        student_id = self.Dialog.lineEdit_id.text()
        name = self.Dialog.lineEdit_name.text()
        which_class = self.Dialog.lineEdit_class.text()
        sex = self.Dialog.lineEdit_sex.text()
        birth = self.Dialog.lineEdit_birth.text()
        self.users.append((student_id, name, which_class, sex, birth))

        return self.users

    def change_info(self):
        # 写入数据库
        try:
            db, cursor = connect_to_sql()
            # 如果存在数据，先删除再写入。前提是设置唯一索引字段或者主键。
            insert_sql = "replace into students(ID, Name, Class, Sex, Birthday) values(%s, %s, %s, %s, %s)"
            users = self.write_info()
            cursor.executemany(insert_sql, users)
        except Exception as e:
            print()
            print("[ERROR] sql execute failed", e)
        else:
            print("[INFO] sql execute success")
            QMessageBox.warning(self, "warning", "录入成功，请勿重复操作！", QMessageBox.Ok)

        # 提交到数据库执行
        db.commit()
        # 关闭数据库
        cursor.close()
        # 关闭数据库连接
        db.close()
