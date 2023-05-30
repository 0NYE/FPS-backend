# Usage:
# python3 script.py --input original.png --output modified.png
# Based on: https://github.com/mostafaGwely/Structural-Similarity-Index-SSIM-

# Import the necessary packages
from skimage.metrics import structural_similarity as ssim
from sklearn.cluster import KMeans
from flask import request, send_file, jsonify, url_for
from flask_restx import Namespace, Resource
from werkzeug.utils import secure_filename

import module.error_handler
import math
import cv2
import numpy as np
import os

def score_remix(_score):
    return math.pow(_score, 10)

def replace_color(image, lower_color, upper_color):
    replacement_color = (0, 0, 0)  # 검정색
    change_image = image.copy()
    lower_color = np.array(lower_color, dtype=np.uint8)
    upper_color = np.array(upper_color, dtype=np.uint8)
    
    mask = cv2.inRange(change_image, lower_color, upper_color)

    change_image[mask > 0] = replacement_color
    
    return change_image

compare = Namespace(name='compare', description="이미지 비교")

@compare.route('')
class compare_image(Resource):
    def post(self):
        '''POST : 두 이미지를 받아서 유사도를 비교하고 이미지 url과 점수를 반환합니다..'''
        try:
            # 두 이미지를 받음
            problem = request.files['problem']
            submit = request.files['submit']
            img_path = os.getcwd() + "/app/static"

            problem = cv2.imdecode(np.frombuffer(problem.read(), np.uint8), cv2.IMREAD_COLOR)
            submit = cv2.imdecode(np.frombuffer(submit.read(), np.uint8), cv2.IMREAD_COLOR)
            
            # problem = cv2.imdecode(np.frombuffer(problem.read(), np.uint8), cv2.COLOR_BGR2RGB)
            # submit = cv2.imdecode(np.frombuffer(submit.read(), np.uint8), cv2.COLOR_BGR2RGB)
            
            # 크기에 대한 예외처리
            pw, ph, pc = problem.shape
            sw, sh, sc = submit.shape
            
            if(ph != sh or pw != sw): return module.error_handler.errer_message_opencv("크기 오류", ph, pw, sh, sw)
            
            # 예외 처리를 위해 대표 색깔을 KMeans로 추출
            clt = KMeans(n_clusters=1)
            clt.fit(problem.reshape(-1, 3))
            
            white_test = True      # 예외처리를 하기 위한 변수
            
            for i in clt.cluster_centers_[0]:
                if i < 245:
                    white_test = False
            
            # 예외 처리를 한다면, 흰 배경을 검은색으로 바꾼다.
            if white_test:
                # 흰 배경을 검은색으로 변경
                target_color = (255, 255, 255)
                change_image = replace_color(problem, target_color, target_color)
                
                # grayscale로 변경
                grayA = cv2.cvtColor(problem, cv2.COLOR_BGR2GRAY)
                grayB = cv2.cvtColor(submit, cv2.COLOR_BGR2GRAY)
                grayC = cv2.cvtColor(change_image, cv2.COLOR_BGR2GRAY)
                
                (score_origin, diff) = ssim(grayA, grayB, full=True)
                diff = (diff * 255).astype("uint8")

                (score_change, diff_change) = ssim(grayA, grayC, full=True)
                diff_change = (diff_change * 255).astype("uint8")
                
                if(score_origin == 1): score = 1.0                            # 완전 같은 모양일 경우 1를 반환
                else: score = score_origin * 0.9 + score_change * 0.1           # 두 값의 평균값을 구한다.
            
            # 평범한 경우에는 여기를 쓴다.
            else:       
                # grayscale로 변경
                grayA = cv2.cvtColor(problem, cv2.COLOR_BGR2GRAY)
                grayB = cv2.cvtColor(submit, cv2.COLOR_BGR2GRAY)

                # Compute the Structural Similarity Index (SSIM) between the two images, ensuring that the difference image is returned
                (score, diff) = ssim(grayA, grayB, full=True)
                diff = (diff * 255).astype("uint8")  

            # print only the score if you want
            # print("SSIM: {}".format(score))
            
            # 점수를 다시 정규화, result를 최종적으로 전송한다.
            result = score_remix(score)
            
            # 이진화
            thresh = cv2.threshold(diff, 0, 200, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)[1]

            # get contours : 윤곽 잡기 -> 검은색 바탕에서 하얀색 물체 찾기
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]       # 한 개만 가져와서 사용
    
            # 사각형 그리기
            for c in cnts:
                area = cv2.contourArea(c)                           # contour의 영역 계산
                if area > 40:                                       # count 값이 작으면 무시, 크면 박스 생성
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
            "score" : result
        })