# tensorflow와 tf.keras를 임포트
import tensorflow as tf
from tensorflow import keras
import numpy as np
import os
import cv2

# MNIST 데이터를 학습용, 테스트 데이터로 구분하여 읽어옴(재료준비)
mnist = keras.datasets.mnist
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

# 내가 모은 오답 데이터
folder_name = "training_number_data"
extra_images = [] #사진
extra_labels = [] #정답

#파일 불러오기
if os.path.exists(folder_name):
    for file in os.listdir(folder_name):
        label = int(file.split("_")[0])
        img = cv2.imread(f"{folder_name}/{file}", cv2.IMREAD_GRAYSCALE)

        extra_images.append(img)
        extra_labels.append(label)

#오답파일이 존재하면 합치기, 오답파일 뻥튀기(1,000개 이상이면 그만둘것)
if extra_images:
    extra_images = np.concatenate([train_images, np.array(extra_images * 10)])
    extra_labels = np.concatenate([train_labels, np.array(extra_labels * 10)])

#정규화 작업
(train_images, test_images) = (train_images / 255, test_images / 255)

#모델 소환
model = keras.models.load_model("my_second_DNN_model.keras")

# 훈련
model.fit(train_images, train_labels, epochs=5)
