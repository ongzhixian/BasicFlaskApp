import json
import uuid


from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,current_app
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort

import base64
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES

from webapp.auth import login_required
from webapp.db import get_db
from webapp.secret_manager import UserSecretRepository

bp = Blueprint('aes-tool', __name__, url_prefix='/aes-tool')

##############################
# ROUTES

user_secret_repository = UserSecretRepository()

RECORD_KEY = 'DEFAULT_AES_KEY'

@bp.route('/', methods=['GET', 'POST'])
def index():
    new_uuid = None
    if request.method == 'POST':
        new_uuid = uuid.uuid4()
    #    card_quantity = int(request.form['card_quantity'])
    #    tool_repository.seed(card_quantity)
    record = user_secret_repository.find_record(RECORD_KEY, g.user['id'], 1)
    has_default_aes_key = record is not None
    return render_template('aes-tool/index.html', new_uuid=new_uuid, has_default_aes_key=has_default_aes_key)

    
@bp.route('/api/generate', methods=['POST'])
def api_generate():
    
    # (records, total_record_count) = issue_repository.search(f"%{query}%", page)
    # response = {
    #     'total_record_count': total_record_count,
    #     'records': [dict(record) for record in records],
    #     'page': page
    # }
    # return json.dumps(response, default=serializer)
    #print(g.user['id'])
    # sample_string = "GeeksForGeeks is the best"

    # sample_string_bytes = sample_string.encode("ascii")
    
    aes_key_string = generate_new_aes_string()
    
    user_secret_repository.add_if_not_exists(RECORD_KEY, aes_key_string, g.user['id'], 1)
    
    return '{}'
    #return 'OK', 200

    back = aes_key_string.encode('utf-8')
    print(back)
    #return jsonify([dict(record) for record in records])
    
@bp.route('/api/regenerate', methods=['POST'])
def api_regenerate():
    aes_key_string = generate_new_aes_string()
    user_secret_repository.update_system_record(RECORD_KEY, aes_key_string, g.user['id'])
    return '{}'
    

@bp.route('/api/encrypt-text', methods=['POST'])
def api_encrypt_text():
    # Get the default AES DEFAULT KEY
    record = user_secret_repository.get_system_record(RECORD_KEY, g.user['id'])
    aes_key_bytes = record['content'].encode('utf-8')
    
    target_data = None
    json_data = None

    import pdb
    #pdb.set_trace()

    if request.is_json:
        json_data = request.json
    if 'content' in json_data:
        target_data = json_data['content'].encode('utf-8')
    
    #data = 'secret data to transmit'.encode()

    # TODO: if target_data is None ==> bad request
    # print(target_data)
    
    cipher = AES.new(aes_key_bytes, AES.MODE_CTR)
    cipher_bytes = cipher.encrypt(target_data)
    cipher_nonce_text = base64.b64encode(cipher.nonce).decode('utf-8')
    cipher_text = base64.b64encode(cipher_bytes).decode('utf-8')
    #print(cipher_text, cipher_nonce_text)

    return json.dumps({
        'status': 'OK',
        'content': cipher_text,
        'nonce': cipher_nonce_text
    })


def generate_new_aes_string(number_of_bytes = 16):
    aes_key_bytes = get_random_bytes(number_of_bytes)
    #aes_key_string = base64.b64encode(aes_key_bytes).decode('utf-8')
    return base64.b64encode(aes_key_bytes).decode('utf-8')