# 문제 테이블 컨트롤 view입니다.
# flask_restx Namespace를 이용해 Rest API를 구성했습니다.

from flask import request, jsonify
from flask_restx import Resource, Namespace

from module.database import Database;

import pymysql
import datetime
import module.error_handler
import json
import ast

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
        
        # 2. 값 받아서 데이터베이스에 넣기
        try:
            sql = '''
            INSERT INTO `fps`.`PROBLEM`
            (`title`, `description`, `HTML_code`, `CSS_code`,`JS_code`, `registration_date`,`modification_date`, `uploader`,`tags`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            '''
    
            val = (problem['title'], problem['description'], problem['html_code'], problem['css_code'], problem['js_code'], 
                   datetime.date.today(), datetime.date.today(), uploarder, tags_string)
    
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
            
            print(result[0])
            
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