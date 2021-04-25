from imutils import paths
import numpy as np
import imutils
import pickle
import cv2
import os
import sys

rootdir = "D://Github//Face-Recognition-Class-Attendance-System//02 Main//"
sys.path.append(rootdir)

def Generator():
    # 人脸数据所在路径
    face_data = "./face_dataset"
    # 输出面部嵌入的序列化数据库的路径
    embeddings = "./saved_weights/embeddings.pickle"
    # OpenCV深度学习人脸检测器的路径
    detector_path = "./face_detection_model"
    # OpenCV深度学习面部嵌入模型的路径
    embedding_model = "./face_detection_model/openface_nn4.small2.v1.t7"
    # 置信度
    default_confidence = 0.5

    # 从磁盘加载序列化面部检测器
    print("[INFO] loading face detector...")
    protoPath = os.path.sep.join([detector_path, "deploy.prototxt"])
    modelPath = os.path.sep.join([detector_path, "res10_300x300_ssd_iter_140000.caffemodel"])
    detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

    # 从磁盘加载序列化面嵌入模型
    print("[INFO] loading face recognizer...")
    embedder = cv2.dnn.readNetFromTorch(embedding_model)

    # 抓住数据集中输入图像的路径
    print("[INFO] quantifying faces...")
    imagePaths = list(paths.list_images(face_data))

    # 初始化提取的面部嵌入列表和相应的人名
    knownEmbeddings = []
    knownNames = []

    # 初始化处理的面部总数
    total = 0

    # 在图像路径上循环
    for (i, imagePath) in enumerate(imagePaths):
        # 从图像路径中提取人名
        print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
        name = imagePath.split(os.path.sep)[-2]

        # 加载图像，将其大小调整为宽度为600像素（同时保持纵横比），然后抓取图像尺寸
        image = cv2.imread(imagePath)
        image = imutils.resize(image, width=600)
        (h, w) = image.shape[:2]

        # 从图像构造一个blob
        imageBlob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)), 1.0, (300, 300),
            (104.0, 177.0, 123.0), swapRB=False, crop=False)

        # 应用OpenCV的基于深度学习的人脸检测器来定位输入图像中的人脸
        detector.setInput(imageBlob)
        detections = detector.forward()

        # 确保至少找到一张脸
        if len(detections) > 0:
            # 我们假设每个图像只有一张脸，所以找到概率最大的边界框
            i = np.argmax(detections[0, 0, :, 2])
            confidence = detections[0, 0, i, 2]

            # 确保最大概率的检测也意味着最小概率测试（从而帮助滤除弱检测）
            if confidence > default_confidence:
                # 计算面部边界框的（x，y）坐标
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # 提取面部ROI并获取ROI维度
                face = image[startY:endY, startX:endX]
                (fH, fW) = face.shape[:2]

                # 确保面部宽度和高度足够大
                if fW < 20 or fH < 20:
                    continue

                # 为面部ROI构造一个blob，然后通过面部嵌入模型传递blob以获得面部的128-d量化
                faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
                                                 (96, 96), (0, 0, 0), swapRB=True, crop=False)
                embedder.setInput(faceBlob)
                vec = embedder.forward()

                # 将人物名和相应的脸部嵌入添加到各自的列表中
                knownNames.append(name)
                knownEmbeddings.append(vec.flatten())
                total += 1

    # 将面部嵌入+名称转储到磁盘
    print("[INFO] serializing {} encodings...".format(total))
    data = {"embeddings": knownEmbeddings, "names": knownNames}
    f = open(embeddings, "wb")
    f.write(pickle.dumps(data))
    f.close()

def TrainModel():
    from sklearn.preprocessing import LabelEncoder
    from sklearn.svm import SVC
    import pickle

    # 面部嵌入的序列化db的路径
    embeddings_path = "./saved_weights/embeddings.pickle"
    # 训练识别面部的输出模型的路径
    recognizer_path = "./saved_weights/recognizer.pickle"
    # 输出标签编码器的路径
    le_path = "./saved_weights/le.pickle"

    # 加载面嵌入
    print("[INFO] loading face embeddings...")
    data = pickle.loads(open(embeddings_path, "rb").read())

    # 编码标签
    print("[INFO] encoding labels...")
    le = LabelEncoder()
    labels = le.fit_transform(data["names"])

    # 训练用于接受面部128-d嵌入的模型，然后产生实际的面部识别
    print("[INFO] training model...")
    recognizer = SVC(C=1.0, kernel="linear", probability=True)
    recognizer.fit(data["embeddings"], labels)

    # 将实际的人脸识别模型写入磁盘
    f = open(recognizer_path, "wb")
    f.write(pickle.dumps(recognizer))
    f.close()

    # 将标签编码器发送到磁盘
    f = open(le_path, "wb")
    f.write(pickle.dumps(le))
    f.close()