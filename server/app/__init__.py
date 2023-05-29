from flask import Flask, jsonify
from flask_restx import Api, Resource
from flask_cors import CORS

from apis.image_similarity_visual import compare
# from apis.problem_image import problem
# from apis.problem_lighthouse import problem
from apis.problem import problem

# import apis.auth
app = Flask(__name__)
app.secret_key = 'test'

# from ..apis import auth
from apis import auth
app.register_blueprint(auth.bp)

CORS(app)

api = Api(
    app,
    version='0.2',
    title='fps project API server',
    description='fps project를 위한 서버입니다.'
    )

api.add_namespace(compare, '/compare')      # 이미지 유사도 관련
api.add_namespace(problem, '/problems')     # 문제 관련

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)