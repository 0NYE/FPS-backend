# Usage:
# python3 script.py --input original.png --output modified.png
# Based on: https://github.com/mostafaGwely/Structural-Similarity-Index-SSIM-

# Import the necessary packages
from skimage.metrics import structural_similarity as ssim
from skimage import io
from flask import request, send_file, jsonify, render_template
from flask_restx import Namespace, Resource
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import os
compare = Namespace('compare', description="이미지 비교")

@compare.route('')
class compare_image(Resource):
    def post(self):
        '''POST : 두 이미지를 전달하면 유사도와 비교 사진을 전해주는 HTML를 보내줍니다.'''
        # TEST
        file1 = request.files['image1']
        file2 = request.files['image2']
        
        # 현재 절대경로로 밖에 안되서 나중에 수정 필요
        image_path = 'static/image/modifyResult.png'
        image_path = 'C:/Project/ONYE_FPS/FPS-backend/server/app/static/image/modifyResult.png'
        
        origin = cv2.imdecode(np.frombuffer(file1.read(), np.uint8), cv2.IMREAD_COLOR)
        modify = cv2.imdecode(np.frombuffer(file2.read(), np.uint8), cv2.IMREAD_COLOR)

        # grayscale로 변경
        grayA = cv2.cvtColor(origin, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(modify, cv2.COLOR_BGR2GRAY)

        # Compute the Structural Similarity Index (SSIM) between the two images, ensuring that the difference image is returned
        (score, diff) = ssim(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")

        # print only the score if you want
        # print("SSIM: {}".format(score))

        # 이진화
        thresh = cv2.threshold(diff, 100, 255, cv2.THRESH_BINARY_INV)[1]

        # get contours : 윤곽 잡기 -> 검은색 바탕에서 하얀색 물체 찾기
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]       # 한 개만 가져와서 사용
    
        # 사각형 그리기
        for c in cnts:
            area = cv2.contourArea(c)                           # contour의 영역 계산
            if area > 50:                                       # count 값이 작으면 무시, 크면 박스 생성
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(origin, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.rectangle(modify, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        cv2.imwrite(image_path, modify)

        
        # 1. 이미지 직접 전달을 위한 바이너리 이진화
        compare_result_image = send_file(image_path, mimetype='image/png')
        return compare_result_image
        
        # 2. 경로 전달
        # response_data = {
        #     'image' : image_path,
        #     'ssim' : score
        # }
        
        # return jsonify(response_data)
        
        # 3. html로 전달하기
        # return render_template('result.html', image_file="image/modifyResult.png", ssim = score)
