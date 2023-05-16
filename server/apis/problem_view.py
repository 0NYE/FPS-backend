# 문제 테이블 컨트롤 view입니다.
# flask_restx Namespace를 이용해 Rest API를 구성했습니다.

from flask import request, jsonify, Blueprint
from flask_restx import Resource, Namespace

from module.database import Database;

import pymysql

# bp = Blueprint('problem', __name__, url_prefix='/api/problem')

problem = Namespace('problem', description="문제 DB 관리")

@problem.route('')
class problem_manager(Resource):
    def get(self):
        """GET : 모든 테이블 내의 컬럼을 JSON으로 가져옵니다."""
        db = Database()
    
        sql = "SELECT * FROM PROBLEM"
    
        row = db.execute_all(sql)
        db.commit()
        print(row)
        
        return jsonify(row)

    
    def post(self):
        """POST : 테이블 내의 칼럼을 하나 추가합니다."""
        db = Database()
    
        problem = request.get_json()
        
        try:
            sql = "INSERT INTO PROBLEM VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
            val = (int(problem['id']), problem['title'], problem['description'], "test", "test", "test", "2023-05-16", "test", 1)
    
            db.execute_all(sql, val)
            db.commit()
        except pymysql.err.IntegrityError as e:
            return "이미 있는 번호의 문제입니다."
        
        return "문제 추가 완료!"
    
    
    def delete(self):
        """DELETE 문제 내용 삭제하기 : 문제 번호가 주어지면 그 번호의 문제를 삭제합니다."""
        db = Database()
        
        num = request.get_json()
        
        try:
            sql = "DELETE FROM PROBLEM WHRER id = %s"
            val = (num['id'])
        
            db.execute_all(sql, val)
            db.commit()
        except pymysql.err.IntegrityError as e:
            return "유효한 번호가 아닙니다."
        
        return "문제 삭제 완료!"
    