from flask import Flask
from flask_restx import Api, Resource

from apis.image_similarity_visual import compare
from apis.problem import problem

app = Flask(__name__)
api = Api(
    app,
    version='0.1',
    title='fps project API server',
    description='fps project를 위한 서버입니다.'
    )

api.add_namespace(compare, '/compare')
api.add_namespace(problem, '/problems')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)