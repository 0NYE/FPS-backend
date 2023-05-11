# install : flask, scikit, opencv, matplotlib
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # blueprint-image
    from image_similarity import image_similarity_visual
    app.register_blueprint(image_similarity_visual.bp)
    
    from views import main_views
    app.register_blueprint(main_views.bp)
    
    return app