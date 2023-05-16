from flask import Flask
from flask_restx import Api, Resource

from apis.image_similarity_visual import compare
from apis.problem_view import problem

app = Flask(__name__)
api = Api(app)

api.add_namespace(compare, '/compare')
api.add_namespace(problem, '/problem')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)