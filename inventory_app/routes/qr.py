from flask import Blueprint, send_file, make_response
from flask_login import login_required
from ..utils import generate_qr
import io

qr_blueprint = Blueprint('qr', __name__)

@qr_blueprint.route('/qr/<data>')
@login_required
def get_qr(data):
    img_data = generate_qr(data)
    response = make_response(img_data)
    response.headers.set('Content-Type', 'image/png')
    return response
