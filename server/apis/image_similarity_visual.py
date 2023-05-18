# Usage:
# python3 script.py --input original.png --output modified.png
# Based on: https://github.com/mostafaGwely/Structural-Similarity-Index-SSIM-

# Import the necessary packages
from skimage.metrics import structural_similarity as ssim
from skimage import io
from flask import request, send_file, jsonify, render_template
from flask_restx import Namespace, Resource
from werkzeug.utils import secure_filename
from module.database import Database;
from html2image import Html2Image

import cv2
import numpy as np
import os

compare = Namespace(name='compare', description="이미지 비교")

def image_compare(file1, file2):
        cwd = os.getcwd() + "/app/static/image"
        # problem = cv2.imdecode(np.frombuffer(file1.read(), np.uint8), cv2.IMREAD_COLOR)
        # submit = cv2.imdecode(np.frombuffer(file2.read(), np.uint8), cv2.IMREAD_COLOR)
        problem = cv2.imread(file1)
        submit = cv2.imread(file2)
        
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
        
        cv2.imwrite(cwd + '/result.png', submit)
    
     
@compare.route('')
class compare_image(Resource):
    def post(self):
        '''POST : query String으로 problem과 user값을 보내면 비교 사진을 전달합니다.'''
        # 기본 설정
        db = Database()
        problem = request.args.get('problem')
        user = request.args.get('user')
        
        # 작업 경로(server) + 위치로 설정
        cwd = os.getcwd() + "/app/static/image"
        
        # 1. 문제 정보를 가져온다.
        sql_problem = '''
            SELECT HTML_code, CSS_code FROM PROBLEM WHERE id = %s
        '''
        val_problem = (int(problem))
        
        result_problem = db.execute_all(sql_problem, val_problem)
        db.commit()
        
        # 2. 답안 정보를 가져온다.
        sql_submit = '''
            SELECT HTML_code, CSS_code FROM SUBMIT WHERE problem_id = %s AND user_id = %s;
        '''
        val_submit = (int(problem), user)
                
        result_submit = db.execute_all(sql_submit, val_submit)
        db.commit()
        
        print(result_problem)
        print(result_submit)
        
        # 3. html2image를 이용해서 이미지를 생성한다.
        hti = Html2Image(output_path=cwd)
        
        html_problem = result_problem[0]['HTML_code']
        css_problem = result_problem[0]['CSS_code']
        html_submit = result_submit[0]['HTML_code']
        css_submit = result_submit[0]['CSS_code']
        
        hti.screenshot(html_str=[html_problem, html_submit], 
                       css_str=[css_problem, css_submit], 
                       save_as=['problem.png', 'submit.png'])
        
        path_problem = cwd + '/problem.png'
        path_submit = cwd + '/submit.png'
        
        image_compare(path_problem, path_submit)
        
        # compare_result_image = send_file(cwd + '/Aris.jpg', mimetype='image/png')
        
        compare_result_image = send_file(cwd + '/result.png', mimetype='image/png')
        return compare_result_image
    
        # cv2.imwrite(image_path, modify)

        
        # # 1. 이미지 직접 전달을 위한 바이너리 이진화
        # compare_result_image = send_file(image_path, mimetype='image/png')
        # return compare_result_image
        
        # 2. 경로 전달
        # response_data = {
        #     'image' : image_path,
        #     'ssim' : score
        # }
        
        # return jsonify(response_data)
        
        # 3. html로 전달하기
        # return render_template('result.html', image_file="image/modifyResult.png", ssim = score)
