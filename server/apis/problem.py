# 문제 테이블 컨트롤 view입니다.
# flask_restx Namespace를 이용해 Rest API를 구성했습니다.

from flask import request, jsonify, Blueprint
from flask_restx import Resource, Namespace, fields

from module.database import Database;

import pymysql
import datetime

problem = Namespace(name='problems', description="문제 DB 관리")

insert_fields = problem.model( 'insert', {
    'id' : fields.String(description='문제 번호, PK입니다.', required=True, example='0'),
    'title' : fields.String(description='문제 제목', required=True, example='테스트 문제'),
    'description' : fields.String(description='문제 제목', required=True, example='테스트 중입니다'),
    'HTML_code' : fields.String(description='HTML 코드입니다.', required=True, example='Hello, world!'),
    'CSS_code' : fields.String(description='CSS 코드입니다.', required=True, example='-'),
    'JS_code' : fields.String(description='JS 코드입니다.', required=True, example='-'),
    'uploader' : fields.String(description='문제를 업로드한 사람의 닉네임입니다.', required=True, example='WinterHana'),
    'image_id' : fields.String(description='문제를 랜더링한 이미지 번호입니다. 이미지 테이블과 FK 관계입니다.', required=True, example='0')
})

delete_fields = problem.model('delete', {
    'id' : fields.String(description='문제 번호', required=True, example='0')
})

@problem.route('')
class problem_list(Resource):
    @problem.response(200, '전체 내용을 가져옵니다.')
    def get(self):
        """GET : 모든 테이블 내의 컬럼을 JSON으로 가져옵니다 테이블이 없으면 새로 생성합니다."""
        db = Database()
        
        # 만약 테이블이 없으면 새로 생성
        sql = '''
        CREATE TABLE IF NOT EXISTS `fps`.`PROBLEM` (
            `id` INT NOT NULL COMMENT '문제 번호',
            `title` VARCHAR(100) NOT NULL COMMENT '문제 제목',
            `description` VARCHAR(1000) NULL COMMENT '문제 설명',
            `HTML_code` TEXT(60000) NULL COMMENT 'HTML 코드 내용',
            `CSS_code` TEXT(60000) NULL COMMENT 'CSS 코드 내용',
            `JS_code` TEXT(60000) NULL COMMENT 'JS 코드 내용',
            `registration_date` DATE NOT NULL COMMENT '업로드한 날짜',
            `uploader` VARCHAR(100) NOT NULL COMMENT '업로드한 사람',
            `image_id` INT NOT NULL COMMENT '랜더링한 이미지 번호',
            PRIMARY KEY (`id`))
        '''
        db.execute_all(sql)
        db.commit()
        
        # 테이블 내의 모든 정보 가져오기
        sql = "SELECT * FROM PROBLEM"
        row = db.execute_all(sql)
        db.commit()
        
        return jsonify(row)
    
@problem.route('/create')
class problem_create(Resource):
    @problem.expect(insert_fields)
    @problem.response(200, '문제 추가 완료!')
    def post(self):
        """POST : 테이블 내의 칼럼을 하나 추가합니다 json 형식으로 받습니다."""
        db = Database()
    
        problem = request.get_json()
        
        try:
            sql = "INSERT INTO PROBLEM VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
            val = (int(problem['id']), problem['title'], problem['description'], problem['HTML_code'], 
                   problem['CSS_code'], problem['JS_code'], datetime.date.today(), problem['uploader'], int(problem['image_id']))
    
            db.execute_all(sql, val)
            db.commit()
            
        except pymysql.err.IntegrityError as e:
            return "이미 있는 번호의 문제입니다."
        
        return "문제 추가 완료!"

@problem.route('/<int:problem_id>')
class problem_id(Resource):
    def get(self, problem_id):
        """GET 문제 가져오기 : 문제 번호가 주어지면 그 문제 번호의 정보를 가져옵니다."""
        db = Database()
        try:
            sql = "SELECT id, description, HTML_code, CSS_code, JS_code FROM PROBLEM WHERE id = %s"
            val = (problem_id)
        
            result = db.execute_all(sql, val)
            db.commit()
        except pymysql.err.IntegrityError as e:
            return "유효한 번호가 아닙니다."
        
        return jsonify(result)
    
    @problem.response(200, '문제 삭제 완료!')
    def delete(self, problem_id):
        """DELETE 문제 내용 삭제하기 : 문제 번호가 주어지면 그 번호의 문제를 삭제합니다."""
        db = Database()
        try:
            sql = "DELETE FROM PROBLEM WHERE id = %s"
            val = (problem_id)
        
            db.execute_all(sql, val)
            db.commit()
        except pymysql.err.IntegrityError as e:
            return "유효한 번호가 아닙니다."
        
        return "문제 삭제 완료!", 200

@problem.route('/submit/<int:problem_id>')
class problem_submit(Resource):
    def post(self, problem_id):
        """POST 지정된 문제 번호에 정답 제출 : 제출한 답안을 DB에 저장합니다."""
        db = Database()
        
        submit = request.get_json()
        
        # 만약 처음 제출한 문제라면 테이블 생성하기
        sql = '''
            CREATE TABLE IF NOT EXISTS `fps`.`SUBMIT` (
            `problem_id` INT PRIMARY KEY NOT NULL COMMENT '문제의 번호', 
            `user_id` VARCHAR(100) NOT NULL COMMENT '유저의 ID',
            `HTML_code` TEXT(60000) NULL,
            `CSS_code` TEXT(60000) NULL,
            `JS_code` TEXT(60000) NULL,
            `submit_date` DATE NULL COMMENT '제출한 날짜',
            CONSTRAINT `problem_id`
            FOREIGN KEY (`problem_id`)
            REFERENCES `fps`.`PROBLEM` (`id`)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION)
        '''
        db.execute_all(sql)
        db.commit()
        
        sql = '''
        INSERT INTO SUBMIT VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE HTML_code = %s, CSS_code = %s, JS_code = %s, submit_date = %s
        '''
    
        val = (problem_id, submit['user_id'], 
               submit['HTML_code'], submit['CSS_code'], submit['JS_code'], datetime.date.today(),
               submit['HTML_code'], submit['CSS_code'], submit['JS_code'], datetime.date.today())
    
        db.execute_all(sql, val)
        db.commit()
        
        return "OK", 200
        