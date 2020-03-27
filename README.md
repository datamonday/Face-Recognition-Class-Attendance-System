# class-attendance-system-based-on-face-recognition
UI interface is Chinese, English version will be uploaded to this repository in the future.<br>
All functions have been integrated in mainRUN.py<br>
This project was completed in junior year in April 2019. <br>
My level is limited. There may be bugs in the project. Welcome to propose solutions.<br>

## packages you need to install：
python >= 3.6<br>
OpenCV3<br>
PyQt5<br>
imutils<br>
dlib<br>
freetype-py(optional):if you need to put chinese text<br>
pymysql<br>
navicat(optional):if you are not familiar with mysql shell operation<br>

## edit source code:
1.you need to install msqlservice and then edit the code in mainRUN like this "db = pymysql.connect("localhost", "root", "mysql105", "facerecognition")".<br>
2.you need to import the identified objects in the database through the visual database software navicat if you are not familiar with mysql operation. <br>
3.you need to download `shape_predictor_68_face_landmarks.dat`-- put into `/02 Main` path <br>
4. you need to download `openface_nn4.small2.v1.t7` into `/02 Main/face_detection_model` path<br>
3.you need to move photos of user into `dataset/XX` if the photos taked not in these file.<br>
4.you need to generator train_model.<br>
5.have fun!<br>

Please indicate the source if reprinted.<br>

# About more details
Please view this blog：<https://blog.csdn.net/weixin_39653948/article/details/89291751>.
