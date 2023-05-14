# install : flask, scikit, opencv, matplotlib
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('APP_CONFIG_FILE')
    
    # blueprint-image
    from views.image_similarity import image_similarity_visual
    app.register_blueprint(image_similarity_visual.bp)
    
    from views import main_views
    app.register_blueprint(main_views.bp)
    
    if __name__ == "__main__":
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    return app

