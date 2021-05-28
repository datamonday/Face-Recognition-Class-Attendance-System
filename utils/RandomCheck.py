import random
from copy import deepcopy


def random_check(choices):
    # 停止标志
    exit_flag = False
    # 防止原地修改
    choices = deepcopy(choices)
    while len(choices) != 0:
        random_choice = random.choice(choices)
        print(random_choice)
        choices.remove(random_choice)

        if exit_flag:
            break


if __name__ == '__main__':
    choice_list = ['1', '2', '3', '4', '5', '7', '9', '11', '12', '13', '16', '18', '21', '22', '23']
    random_check(choice_list)

import os
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QIcon, QPixmap
from PyQt5.QtCore import QCoreApplication, QThread
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QInputDialog


# 导入信息采集框界面
from ui import RandomCheckUI

# 将根目录（execute所在目录）添加到环境变量
from utils.GlobalVar import add_path_to_sys, connect_to_sql
rootdir = add_path_to_sys()


class RCDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.Dialog = RandomCheckUI.Ui_Form()
        self.Dialog.setupUi(self)

        # 实现路径错误提示，方便定位错误
        self.current_filename = os.path.basename(__file__)

        try:
            # 设置窗口名称和图标
            self.setWindowTitle("随机点名答题系统")
            self.setWindowIcon(QIcon(f'{rootdir}/logo_imgs/fcb_logo.jpg'))
        except FileNotFoundError as e:
            print("[ERROR] UI背景图片路径不正确！(source file: {})".format(self.current_filename), e)
        else:
            print("[INFO] 设置icon成功！")

        self.Dialog.pb_connect_db.clicked.connect(self.get_id_name_from_db)

        self.Dialog.pb_start.clicked.connect(self.start_random_check)

        self.Dialog.pb_success.clicked.connect(self.answer_success)

        self.Dialog.pb_fail.clicked.connect(self.answer_fail)

        self.Dialog.pb_absence.clicked.connect(self.answer_absence)

        self.Dialog.pb_other.clicked.connect(self.answer_other)

        self.get_id_name_from_db()

    # 核验本地人脸与数据库信息是否一致
    def get_id_name_from_db(self):
        try:
            db, cursor = connect_to_sql()
        except ConnectionAbortedError as e:
            self.ui.textBrowser_log.append('[INFO] 连接数据库失败，请检查配置信息！')
        else:
            sql = "select id, name from students"
            # 执行查询
            cursor.execute(sql)
            results = cursor.fetchall()
            self.student_ids = []
            self.student_names = []
            for item in results:
                self.student_ids.append(item[0])
                self.student_names.append(item[1])
            # 初始化点名列表
            self.random_check_names = deepcopy(self.student_names)
            self.random_check_ids = deepcopy(self.student_ids)
            print("[INFO] 查询成功！")

    # 随机点名
    def start_random_check(self):
        try:
            if len(self.random_check_ids) == 0 or len(self.random_check_names) == 0:
                box_choose = QMessageBox.information(self, "Notice", "已经遍历完毕，是否重新开始点名？", QMessageBox.Yes | QMessageBox.No)
                if box_choose == QMessageBox.Yes:
                    self.random_check_names = deepcopy(self.student_names)
                    self.random_check_ids = deepcopy(self.student_ids)
                else:
                    pass
            else:
                self.rc_id = random.choice(self.random_check_ids)
                self.rc_name = self.random_check_names[self.random_check_ids.index(self.rc_id)]
                self.random_check_ids.remove(self.rc_id)
                self.random_check_names.remove(self.rc_name)

                self.Dialog.lcdNumber_id.display(self.rc_id)
                self.Dialog.textBrowser_name.append(self.rc_name)

                # 获取系统时间，保存到秒
                self.current_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        except Exception as e:
            QMessageBox.critical(self, "Error", "[Error] 随机点名列表未定义！请先连接数据库！", QMessageBox.Ok)
            print("[Exception]: ", e)

    # 成功回答
    def answer_success(self):
        print(self.rc_id, self.rc_name, self.current_time, "成功回答")

    # 回答失败
    def answer_fail(self):
        print(self.rc_id, self.rc_name, self.current_time, "回答失败")

    # 未到
    def answer_absence(self):
        print(self.rc_id, self.rc_name, self.current_time, "未到")

    # 其它情况
    def answer_other(self):
        print(self.rc_id, self.rc_name, self.current_time, "其他情况")

    def handle_click(self):
        if not self.isVisible():
            self.show()
