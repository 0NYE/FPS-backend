# 문제 테이블 컨트롤 view입니다.
# flask_restx Namespace를 이용해 Rest API를 구성했습니다.

from flask import request, jsonify, session, url_for, render_template
from flask_restx import Resource, Namespace

from module.database import Database;
from datetime import datetime

import pymysql
import datetime
import module.error_handler
import json
import ast
import requests
import os
import time

problem = Namespace(name='problems', description="문제 DB 관리")

## 테이블을 가져올 때 데이터 정리
# 태그의 문자열을 파싱한다.
def tag_parser(tags):
    print(tags)
    result = ast.literal_eval(tags)
    print(result)
    return result

# 각 코드가 존재하는지에 대한 여부를 확인한다.
def is_code(row, key, new_name):
    if row[key] == "":
        del row[key]
        row[new_name] = False
    else:
        del row[key]
        row[new_name] = True
    return row

## 본체
@problem.route('')
class problem_list(Resource):
    def get(self):
        """GET : 모든 테이블 내의 컬럼을 JSON으로 가져옵니다 테이블이 없으면 새로 생성합니다."""
        db = Database()
        try:
            # 0. 만약 테이블이 없으면 새로 생성
            sql = '''
            CREATE TABLE IF NOT EXISTS `PROBLEM` (
            `id` int NOT NULL AUTO_INCREMENT,
            `title` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
            `description` varchar(1000) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
            `HTML_code` mediumtext CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
            `CSS_code` mediumtext CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
            `JS_code` mediumtext CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
            `registration_date` date NOT NULL,
            `modification_date` date NOT NULL,
            `uploader` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
            `tags` varchar(200) DEFAULT NULL,
            `likeCount` int DEFAULT '0',
            `dislikeCount` int DEFAULT '0',
            `bookmarkCount` int DEFAULT '0',
            `successRate` int DEFAULT '0',
            PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

            '''
            db.execute_all(sql)
            db.commit()
        
            # 1. 테이블 내의 필요한 정보 가져오기
            sql = '''
            SELECT `PROBLEM`.`id`,
                `PROBLEM`.`title`,
                `PROBLEM`.`HTML_code`,
                `PROBLEM`.`CSS_code`,
                `PROBLEM`.`JS_code`,
                `PROBLEM`.`uploader`,
                `PROBLEM`.`tags`,
                `PROBLEM`.`likeCount`,
                `PROBLEM`.`dislikeCount`,
                `PROBLEM`.`bookmarkCount`,
                `PROBLEM`.`successRate`
            FROM `fps`.`PROBLEM`;
            '''
            rows = db.execute_all(sql)
            db.commit()
        
            # 2. 정보 가공하기 : 각 코드의 존재 여부, tag 문자열 나누기
            for row in rows:
                print(row)
                row['tags'] = tag_parser(row['tags'])
                row = is_code(row, 'HTML_code', 'isHTML')
                row = is_code(row, 'CSS_code', 'isCSS')
                row = is_code(row, 'JS_code', 'isJS')
                
        except:
            return module.error_handler.errer_message("Bad Request")
        
        return jsonify(rows)
    
    def post(self):
        """POST : 테이블 내의 칼럼을 하나 추가합니다 인덱스는 자동으로 증가 json 형식으로 받습니다."""
        db = Database()
        # 1. JSON으로 정보 가져오기
        problem = request.get_json()
        tags_string = json.dumps(problem['tags'])
        
        # 1-1. 로그인 로그아웃이 구현이 완료된다면 여기에 업로더 이름 넣기
        uploarder = "WinterHana"
        
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 2. 값 받아서 데이터베이스에 넣기
        try:
            sql = '''
            INSERT INTO `fps`.`PROBLEM`
            (`title`, `description`, `HTML_code`, `CSS_code`,`JS_code`, `registration_date`,`modification_date`, `uploader`,`tags`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            '''
    
            val = (problem['title'], problem['description'], problem['html_code'], problem['css_code'], problem['js_code'], 
                   current_time, current_time, uploarder, tags_string)
    
            db.execute_all(sql, val)
            db.commit()
            
        except:
            return module.error_handler.errer_message("Bad Request")
            
        return module.error_handler.success_message("OK")

@problem.route('/<int:problem_id>')
class problem_id(Resource):
    def get(self, problem_id):
        """GET 문제 가져오기 : 문제 번호가 주어지면 그 문제 번호의 정보를 가져옵니다."""
        db = Database()
        
        # 0. 세션에 문제 번호 임시로 저장하기
        session['problem_id'] = problem_id
        
        # 1. 필요한 정보 Select 후 전송하기
        try:
            sql = '''
                SELECT `PROBLEM`.`id`,
                `PROBLEM`.`description`,
                `PROBLEM`.`title`,
                `PROBLEM`.`HTML_code`,
                `PROBLEM`.`CSS_code`,
                `PROBLEM`.`JS_code`
                FROM `fps`.`PROBLEM` where id = %s;
            '''
            val = (problem_id)
        
            result = db.execute_all(sql, val)
            db.commit()
            
            # print(result[0])
            
        except pymysql.err.InterfaceError as e:
            return module.error_handler.errer_message("Bad Request")
        
        if not result:
            return module.error_handler.errer_message("Bad Request")
        else:
            return jsonify(result[0])
    
    def delete(self, problem_id):
        """DELETE 문제 내용 삭제하기 : 문제 번호가 주어지면 그 번호의 문제를 삭제합니다."""
        db = Database()
        try:
            sql = "DELETE FROM PROBLEM WHERE id = %s"
            val = (problem_id)
        
            db.execute_all(sql, val)
            db.commit()
        except pymysql.err.IntegrityError as e:
            return module.error_handler.errer_message("Bad Request")
        
        return module.error_handler.success_message("OK")
    

@problem.route('/submit')
class problem_submit(Resource):
    def post(self):
        """POST : 문제를 제출합니다."""
        db = Database()
        
        # 1. 기본적인 정보 가져오기
        problem_image = request.files['problem_image']
        user_image = request.files['user_image']
        html_code = request.form['html_code']
        css_code = request.form['css_code']
        js_code = request.form['js_code']
        problem_id = 1                # 임시 번호             # session.get('problem_id')      # 세션에 저장된 problem_id
        user_id = "WinterHana"        # 임시 ID               # session['id']     # 로그인 완전히 구현될 때까지 이 이름으로 고정
        submission_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    
        # 2. 이미지 유사도 결과를 가져오고 성공과 실패 여부를 확인한다.
        files = {
            'problem' : problem_image,
            'submit' : user_image
        }
        server_url = 'http://13.125.148.109//compare'
        image_similarity = requests.post(server_url, files = files)
        result = image_similarity.json()
        image_url = result['image']
        print(result)
        
        ## 230530 : url db에 추가해서 더해주기!
        
        # 2-1. 오류가 났을 때를 대비해서 예외처리
        if 'score' in result:
            score = result['score']
        else:
            return result
        
        # 이미지 유사도 성공 / 실패 판단하기
        if(score >= 0.90): 
            success = True
            fail_reason = '없음'
        else: 
            success = False
            fail_reason = '이미지 유사도'
        
        # 4. lighthouse_report에 코드를 전달해서 결과값을 가져온다.
        try:
            
            lighthouse_url = 'http://15.164.150.247:3000/api/judge'
            files = {
                "html" : render_template('lighthouse_1.html' , html = html_code, css = css_code, js = js_code)
            }
            
            lighthouse_report = requests.post(lighthouse_url, files = files)
            print(files)
            
        except requests.exceptions.ConnectionError as e:
            # 4 - 1서버가 연결되지 않으면 예외처리
            return module.error_handler.errer_message("Lighthouse 서버가 OFF된 상태입니다.") 
        
        # 4 - 2 lighthouse_report를 .html 파일로 변환하기
        lighthouse_report = lighthouse_report.json()
        # print(lighthouse_report)
        
        # 이름은 날짜 순으로 정렬
        time_string = time.strftime('%Y%m%d-%H%M%S')
        with open(os.getcwd() + "/app/static/" + time_string + "report.html", "w", encoding="utf-8") as file:
            file.write(lighthouse_report['html'])

        report_url = url_for('static', filename = time_string + 'report.html', _external=True)
        
        # 5. DB에 저장하기
        sql = '''
            INSERT INTO `fps`.`SUBMIT`
            (`problem_id`,`user_id`,`HTML_code`,`CSS_code`,`JS_code`,`submission_date`,
            `success`,`fail_reason`,`lighthouse_report`,`diff_image_url`,`similarity`,`report_url`)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        '''
        
        val = (problem_id, user_id, html_code, css_code, js_code, submission_date, 
               success, fail_reason, lighthouse_report['report'], image_url, score, report_url)
        
        db.execute_all(sql, val)
        db.commit()
        
        return module.error_handler.success_message("OK")
    
@problem.route('/submit/<int:problem_id>')
class problem_submit_id(Resource):
    def get(self, problem_id):
        """GET : 주어진 번호의 문제에 대한 제출 내용을 가져옵니다.."""
        db = Database()
        
        sql = '''
            SELECT * FROM SUBMIT where problem_id = %s;
        '''
        val = (problem_id)
        
        result = db.execute_all(sql, val)
        
        db.commit()

        return jsonify(result)
    