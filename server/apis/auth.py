from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

import functools


from module.database import Database;
import module.error_handler

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup/', methods=('POST'))
def signup():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        nickname = request.form['nickname']

        db = Database()

        try:
            # user 테이블 생성
            sql='''
            CREATE TABLE IF NOT EXISTS `user` (
            `id` VARCHAR(30) NOT NULL,
            `password` VARCHAR(30) NOT NULL,
            `nickname` VARCHAR(30) NOT NULL,
            PRIMARY KEY (`user_id`));
            '''
            db.execute(sql)
            db.commit()

            # 회원가입시 새로운 유저 정보 등록
            sql = '''INSERT INTO user_tb VALUES (%s,%s,%s);'''

            db.execute(sql,(id,password,nickname))
            db.commit()
        except:
            return module.error_handler.errer_message("Bad Request")


@bp.route('/login/', methods=('POST'))
def login():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']

        db = Database()

        sql = '''SELECT * user WHERE id = %s and password = %s;'''

        user_info = db.execute_one(sql, (id, password))

        db.commit()

        return jsonify(user_info)

@bp.route('/logout/', methods=('POST'))
def logout():
    try:
        session.clear()
        return module.error_handler.success_message("OK")
    except:
        return module.error_handler.errer_message("Bad Request")
