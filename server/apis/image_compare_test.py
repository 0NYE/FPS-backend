import math
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

from skimage.metrics import structural_similarity as ssim           
from datetime import datetime

print(datetime.datetime.now())

# # 점수 보정하기
# def score_remix(_score):
#     return math.pow(_score, 4)

# # 이미지를 시각적으로 보도록 설정
# def show_img_compar(img_1, img_2 ):
#     f, ax = plt.subplots(1, 2, figsize=(10,10))
#     ax[0].imshow(img_1)
#     ax[1].imshow(img_2)
#     ax[0].axis('off') # hide the axis
#     ax[1].axis('off')
#     f.tight_layout()
#     plt.show()

# # 받은 이미지 값을 시각적으로 보도록 설정
# def palette(clusters):
#     width=300
#     palette = np.zeros((50, width, 3), np.uint8)
#     steps = width/clusters.cluster_centers_.shape[0]
#     for idx, centers in enumerate(clusters.cluster_centers_): 
#         palette[:, int(idx*steps):(int((idx+1)*steps)), :] = centers
#     return palette

# # 특정 색상을 검은색으로 변경하기
# def replace_color(image, lower_color, upper_color):
#     replacement_color = (0, 0, 0)  # 검정색
#     change_image = image.copy()
#     lower_color = np.array(lower_color, dtype=np.uint8)
#     upper_color = np.array(upper_color, dtype=np.uint8)
    
#     mask = cv2.inRange(change_image, lower_color, upper_color)

#     change_image[mask > 0] = replacement_color
#     cv2.imshow('mask', mask)
#     cv2.imshow('change_image', change_image)
#     cv2.waitKey()
#     return change_image

# # 기본 설정
# img_path = os.getcwd() + "/server/app/static"
# print(img_path)

# # 두 이미지 대입
# problem_path = img_path + "/10.png"
# submit_path = img_path + "/11.png"

# problem_image = cv2.imread(problem_path)
# problem_image = cv2.cvtColor(problem_image, cv2.COLOR_BGR2RGB)
# submit_image = cv2.imread(submit_path)
# submit_image = cv2.cvtColor(submit_image, cv2.COLOR_BGR2RGB)

# clt = KMeans(n_clusters=1)
# clt.fit(submit_image.reshape(-1, 3))
# print(clt.labels_)
# print(clt.cluster_centers_)
# # show_img_compar(submit_image, palette(clt))
# target_color = (255, 255, 255)

# lower_color = (clt.cluster_centers_[0][0] - 20, clt.cluster_centers_[0][1] - 20, clt.cluster_centers_[0][2] - 20)
# upper_color = (clt.cluster_centers_[0][0] + 20, clt.cluster_centers_[0][1] + 20, clt.cluster_centers_[0][2] + 20)
# change_image = replace_color(submit_image, target_color, target_color)
# show_img_compar(submit_image, change_image)

# # grayscale로 변경
# grayA = cv2.cvtColor(problem_image, cv2.COLOR_RGB2GRAY)
# grayB = cv2.cvtColor(submit_image, cv2.COLOR_RGB2GRAY)
# grayC = cv2.cvtColor(change_image, cv2.COLOR_RGB2GRAY)          # 배경 검은색으로 전환한 것

# # Compute the Structural Similarity Index (SSIM) between the two images, ensuring that the difference image is returned
# (score_origin, diff_origin) = ssim(grayA, grayB, full=True)
# diff_origin = (diff_origin * 255).astype("uint8")

# (score_change, diff_change) = ssim(grayA, grayC, full=True)
# diff_change = (diff_change * 255).astype("uint8")

# # print only the score if you want
# print("SSIM: {}".format(score_origin))
# print("SSIM: {}".format(score_change))

# # 점수를 다시 정규화, result를 최종적으로 전송한다.
# result = score_remix(score)

# # 이진화
# thresh = cv2.threshold(diff, 0, 200, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)[1]

# # get contours : 윤곽 잡기 -> 검은색 바탕에서 하얀색 물체 찾기
# cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cnts = cnts[0] if len(cnts) == 2 else cnts[1]       # 한 개만 가져와서 사용
    
# # 사각형 그리기
# for c in cnts:
#     area = cv2.contourArea(c)                           # contour의 영역 계산
#     if area > 40:                                       # count 값이 작으면 무시, 크면 박스 생성
#         x, y, w, h = cv2.boundingRect(c)
#         cv2.rectangle(problem_image, (x, y), (x + w, y + h), (255, 0, 255), 2)
#         cv2.rectangle(submit_image, (x, y), (x + w, y + h), (255, 0, 255), 2)
        
        
# cv2.imwrite(img_path + '/result.png', problem_image)