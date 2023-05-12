# Usage:
# python3 script.py --input original.png --output modified.png
# Based on: https://github.com/mostafaGwely/Structural-Similarity-Index-SSIM-

# Import the necessary packages
from skimage.metrics import structural_similarity as ssim
from skimage import io
from flask import Blueprint, request, jsonify
import requests
import cv2
import numpy as np

bp = Blueprint('image', __name__, url_prefix='/image')

@bp.route('/compare', methods = ['POST'])
def compare_image():
    # TEST
    file1 = request.files['image1']
    file2 = request.files['image2']
    
    origin = cv2.imdecode(np.frombuffer(file1.read(), np.uint8), cv2.IMREAD_COLOR)
    modify = cv2.imdecode(np.frombuffer(file2.read(), np.uint8), cv2.IMREAD_COLOR)

    # 만약 url에서 불러올 거면 다음을 활용
    # imageA = cv2.imread(origin)
    # imageB = cv2.imread(modify)

    # grayscale로 변경
    grayA = cv2.cvtColor(origin, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(modify, cv2.COLOR_BGR2GRAY)

    # Compute the Structural Similarity Index (SSIM) between the two images, ensuring that the difference image is returned
    (score, diff) = ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")

    # print only the score if you want
    print("SSIM: {}".format(score))

    # 이진화
    thresh = cv2.threshold(diff, 100, 255, cv2.THRESH_BINARY_INV)[1]

    # get contours : 윤곽 잡기 -> 검은색 바탕에서 하얀색 물체 찾기
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]       # 한 개만 가져와서 사용

    for c in cnts:
        area = cv2.contourArea(c)                           # contour의 영역 계산
        if area > 50:                                       # count 값이 작으면 무시, 크면 박스 생성
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(origin, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(modify, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
    # cv2.imshow("Original", modify)
    # cv2.imshow("Modified", origin)
    # cv2.waitKey(0)
            
    return jsonify({
        "SSIM" : str(score)
    })