from flask import Blueprint, render_template

bp = Blueprint('main', __name__, url_prefix='/')

# test
@bp.route('/')
def index():
    return render_template('index.html')
    