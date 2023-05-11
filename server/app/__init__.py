# install : flask, scikit, opencv, matplotlib
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # test
    @app.route('/')
    def hello_flask():
        return 'Hello, flask!'
    
    # blueprint-image
    from image_similarity import image_similarity_visual
    app.register_blueprint(image_similarity_visual.bp)
    
    
    return app