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
# 3. 数据库存取信息🥗
## 3.1 数据库可视化工具 Navicat 
使用该软件是为了方便管理维护信息，如果有数据库基础，当然也可以选择其它方式。其主界面如下：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210425230716592.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/202104252307284.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210425230737600.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)

---
## 3.2 创建数据库流程
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200327152533314.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200327152753442.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200327152911944.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200327153021968.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200327153143248.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)


---
## 3.3 PyMySQL
项目中只使用了简单的写入、查询等几个常用命令，即使没有数据库基础的话，上手这个库也比较容易。看一下文档，基本就会了。

---
# 4. 系统功能介绍（正在更新🛵···）
## 4.1 信息采集

## 4.2 人脸识别

## 4.3 活体检测（存在bug😣）
目前的bug是，活体检测开启关闭之后，关闭人脸考勤，再关闭相机的时候会卡死。

## 4.4 查询考勤信息

## 4.5 查询学生信息

## 4.6 请假登记
---
# 5. 使用教程🍨
## 5.1 系统环境配置
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
## 5.2 需要修改源码
文件目录树：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210425230913844.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl8zOTY1Mzk0OA==,size_16,color_FFFFFF,t_70)

1. 安装 **msqlservice** 然后修改 `exacute.py`文件中的数据库连接代码。比如 `db = pymysql.connect("localhost", "root", "mysql105", "facerecognition")`。这首先需要在 navicat中创建数据库。
2. 如果不是通过本系统的信息采集功能采集的人脸照片，请将采集的人脸照片放到 `face_dataset/XX` 路径下，其中`XX`是学号（唯一索引），如果是通过系统采集的，则会自动存放在该路径下，不需要修改。

## 5.3 使用步骤
1. navicat创建数据库，打开数据库录入学生信息和班级信息；
2. 修改源码，连接到创建的数据库
3. 采集人脸照片，点击界面中的<kbd>信息采集</kbd>，在子窗口操作即可。
4. 训练人脸识别模型，点击界面中的<kbd>更新人脸库</kbd>
5. 开始考勤：<kbd>打开相机</kbd> --> <kbd>开始考勤</kbd>
6. Have fun!😊

---
# 6. 待完善功能🚀
## 6.1 系统优化
解决bug，提升系统运行效率与稳定性。
## 6.2 人脸照片存储到数据库中
目前还是存储在本地，不安全。
## 6.3 生成考勤日志
自动统计每个班级的考勤信息，并生成日志。
## 6.4 从教务系统导入学生个人课表，保证判定的稳定性
目前仅仅通过设定的考勤时间统计，不够人性化，应该根据学生的各任课表来统计。
## 6.5 同时多人识别
提升识别效率，比如很多同学同时进教室，如果一人一人识别，则会造成拥堵。
## 6.6 上传图片识别
如果系统出现故障，老师可以用手机拍摄照片存档，然后上传系统进行人脸识别考勤。
## 6.7 开发更稳定的人脸识别
防止用照片或视频骗过系统。
## 6.8 开发更稳定的活体检测
防止视频等骗过系统。

---
# 问题交流👏
由于个人精力有限，无法及时回复还请谅解。有问题欢迎加入QQ群，一起交流！<font color=blue> **群号：1062310557**。</font> 二维码：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200327143228512.png#pic_center)

---
<font color=red>**看到这了都，白嫖好意思吗（doge）**</font>

---
# 问题汇总及更新日志
## 2021.4.25 Update
- 修复Python3.8以后版本PyMySQL连接函数的参数设置问题。
- 更新源码。
- 重构文件目录。
- 添加数据库。

---
## 2021.4.14 Update
<font size=4 color=red> 数据库表格已经上传到 [Github](https://github.com/datamonday/Face-Recognition-Class-Attendance-System)</font>
- 路径：`/02 main/mysql_table`


---
## 2020.03.27 Update
- 关于第一次运行崩溃的问题：参考第五章。
- Navicat使用及数据库：参考第三章第一节。

---
## 2020.03.26 Update
- Github压缩包解压失败
- 解压失败一般是没下载完成导致的，不科学方式下载确实慢。

---
## 2019.04.14 Update
- 活体检测功能存在bug
- 主要表现是：人脸识别开启状态下，再开启活体检测再关闭之后，点击关闭摄像头，界面卡死。


