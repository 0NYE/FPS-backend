# Usage:
# python3 script.py --input original.png --output modified.png
# Based on: https://github.com/mostafaGwely/Structural-Similarity-Index-SSIM-

# Import the necessary packages
from skimage.metrics import structural_similarity as ssim
from flask import request, send_file, jsonify, url_for
from flask_restx import Namespace, Resource
from werkzeug.utils import secure_filename
import module.error_handler

import cv2
import numpy as np
import os

compare = Namespace(name='compare', description="이미지 비교")
     
@compare.route('')
class compare_image(Resource):
    def post(self):
        '''POST : 두 이미지를 받아서 유사도를 비교하고 이미지 url과 점수를 반환합니다..'''
        try:
            # 기본 설정
            cwd = os.getcwd() + "/app/static/image"

            # 두 이미지를 받음
            problem = request.files['problem']
            submit = request.files['submit']
        
            ## 이미지 유사도 비교 후 비교 결과 가져오기
            # 본 코드
            img_path = os.getcwd() + "/app/static"
        
            print(img_path)
        
            problem = cv2.imdecode(np.frombuffer(problem.read(), np.uint8), cv2.IMREAD_COLOR)
            submit = cv2.imdecode(np.frombuffer(submit.read(), np.uint8), cv2.IMREAD_COLOR)
        
            # grayscale로 변경
            grayA = cv2.cvtColor(problem, cv2.COLOR_BGR2GRAY)
            grayB = cv2.cvtColor(submit, cv2.COLOR_BGR2GRAY)

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
    
            # 사각형 그리기
            for c in cnts:
                area = cv2.contourArea(c)                           # contour의 영역 계산
                if area > 50:                                       # count 값이 작으면 무시, 크면 박스 생성
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(problem, (x, y), (x + w, y + h), (255, 0, 255), 2)
                    cv2.rectangle(submit, (x, y), (x + w, y + h), (255, 0, 255), 2)
        
            cv2.imwrite(img_path + '/result.png', problem)
    
            # 이미지 url 생성
            image_url = url_for('static', filename = 'result.png', _external=True)
            
        except:
            module.error_handler.errer_message("Bad Request")
            
        return jsonify({
            "image" : image_url,
            "score" : score
        })