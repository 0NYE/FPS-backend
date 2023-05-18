# 문제 테이블 컨트롤 view입니다.
# flask_restx Namespace를 이용해 Rest API를 구성했습니다.

from flask import request, jsonify, Blueprint
from flask_restx import Resource, Namespace, fields

from module.database import Database;

import pymysql
import datetime

# bp = Blueprint('problem', __name__, url_prefix='/api/problem')

problem = Namespace(name='problem', description="문제 DB 관리")

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
class problem_manager(Resource):
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
    
    @problem.expect(delete_fields)
    @problem.response(200, '문제 삭제 완료!')
    def delete(self):
        """DELETE 문제 내용 삭제하기 : 문제 번호가 주어지면 그 번호의 문제를 삭제합니다."""
        db = Database()
        
        num = request.get_json()
        
        try:
            sql = "DELETE FROM PROBLEM WHERE id = %s"
            val = (int(num['id']))
        
            db.execute_all(sql, val)
            db.commit()
        except pymysql.err.IntegrityError as e:
            return "유효한 번호가 아닙니다."
        
        return "문제 삭제 완료!"
    