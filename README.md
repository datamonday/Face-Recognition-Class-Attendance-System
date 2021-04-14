# Class Attendance System based on Face Recognition

基于人脸识别的课堂考勤系统

---

> Contributor : datamonday <br>
>
> Github Repo : https://github.com/datamonday/Face-Recognition-Class-Attendance-System
>
> Initial Blog : [基于人脸识别的考勤系统：Python3 + Qt5 + OpenCV3 + OpenFace + MySQL](https://blog.csdn.net/weixin_39653948/article/details/89291751?spm=1001.2014.3001.5502)
>
> Project Post : 2019.04

---
# 1. 项目简介🐱‍🏍
**🏁本项目使用Python3.6编写，Qt Designer（QT5）设计主界面，PyQt5库编写控件的功能，使用开源 OpenFace人脸识别算法进行人脸识别，使用眨眼检测来实现活体识别，使用OpenCV3实现实时人脸识别。🐱‍👤同时，将班级学生信息，各班级学生人数、考勤信息录入到MySQL数据库中，方便集中统一化管理。🐱‍👓因为本项目仅由我一个人开发，能力精力有限，实现了预期的绝大多数功能，但是活体检测功能还存在bug，主要表现是界面卡死，如果小伙伴对本项目中有不懂的地方或者发现问题提出解决方案，欢迎私聊我或者在此博客评论亦或在github提交。🎠项目大概持续了两三个月的时间，在开发过程中，遇到过许多难题，参考了很多教程，才有了这个项目。🎉相信大家看到这里，一定是在比赛中或者是作业中遇到类似问题了，我也有过类似的经历，很清楚找不到解决方案，自己盲目摸索的苦恼，这也是我选择开源的原因，个人能力有限，但是希望本项目能给需要的小伙伴提供帮助。**

---

# 2. 系统前端设计😎
使用 Qt Designer 设计前端界面。
## 2.1 主界面
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200225112100621.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_1,color_FFFFFF,t_70#pic_center)

---
## 2.2 信息采集界面
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200225112135112.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_1,color_FFFFFF,t_70#pic_center)

---
# 3. 使用教程🍨
## 3.1 系统环境配置
- python >= 3.6
- OpenCV3
- PyQt5
- imutils
- dlib
- freetype-py(optional)
- pymysql

---
## 3.2 需要修改源码
1. 安装 **msqlservice** 然后修改 `mainRUN.py`文件中的数据库连接代码。比如 `db = pymysql.connect("localhost", "root", "mysql105", "facerecognition")`。这首先需要在 navicat中创建数据库。
2. 下载 `shape_predictor_68_face_landmarks.dat`并放到 `/02 Main` 路径下；
3. 下载 `openface_nn4.small2.v1.t7` 放到 `/02 Main/face_detection_model` 路径下；
4. 如果不是通过本系统的信息采集功能采集的人脸照片，请将采集的人脸照片放到 `dataset/XX` 路径下，其中`XX`是学号（唯一索引），如果是通过系统采集的，则会自动存放在该路径下，不需要修改。

## 3.3 使用步骤
1. navicat创建数据库，打开数据库录入学生信息和班级信息；
2. 修改源码，连接到创建的数据库
3. 采集人脸照片，点击界面中的<kbd>信息采集</kbd>，在子窗口操作即可。
4. 训练人脸识别模型，点击界面中的<kbd>更新人脸库</kbd>
5. 开始考勤：<kbd>打开相机</kbd> --> <kbd>开始考勤</kbd>
6. Have fun!😊



---
# 4. 问题交流👏

由于个人精力有限，无法及时回复，还请谅解。近期创建了QQ群，欢迎加入，有问题大家一起交流！<font color=blue> **群号：1062310557**。</font> 二维码：

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200327143228512.png#pic_center)



欢迎关注公众号，获取更多干货内容！
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210310095805745.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_1,color_FFFFFF,t_70#pic_center =200x)

---
---
## 2019.04.14 更新：活体检测功能存在bug
主要表现是：人脸识别开启状态下，再开启活体检测，可能界面卡死。

---
## 2020.03.26 更新：Github压缩包解压失败
压缩包大概32.5MB，解压失败一般是没下载完成导致的，我下载了以便，不科学方式下载确实慢，如果等不及可以留下邮箱或者加交流群自取。

---
## 2020.03.27 更新：关于第一次运行崩溃的问题
请参看上文第五章。

---
## 2020.03.27 更新：Navicat使用
请参看上文第三章第一节。

---
## 2020.05.22 更新：所需包简洁安装流程

```python
opencv+contrib
安装步骤：
1.https://www.lfd.uci.edu/~gohlke/pythonlibs/ 搜索contrib
2.找到对应你系统python版本的opencv+contrib下载
3.我安装的是：opencv_python-4.1.2+contrib-cp37-cp37m-win_amd64.whl
4.打开anaconda命令行 pip install opencv_python-4.1.2+contrib-cp37-cp37m-win_amd64.whl

cmake
官网下载.msi安装包 下载即可，安装注意导入系统环境变量

dilib
直接anaconda命令行中 pip install dlib（时间比较长）

freetype
pip install freetype-py

pymysql
pip install pymysql

pyqt5
pip install pyqt5
```
---
## 2020.05.24 更新：数据库各表字段及需要下载的文件说明
首先需要下载caffemodel和dat文件，并放到图示路径【已经上传群文件】。然后修改人脸照片存放路径。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200525003322326.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)
各表字段说明：
1. studentnums：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200525003753247.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)
2. students
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200525003708987.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)
3.checkin
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200525003628237.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)
---
## 2020.05.25 更新：测试与bug描述
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200525003942549.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70 =700x)

目前的bug是，活体检测开启关闭之后，关闭人脸考勤，再关闭相机的时候会卡死。

---
<font color=red>**看到这了都，白嫖好意思吗（doge）**</font>