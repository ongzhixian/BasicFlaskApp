#from logging import getLogger, logging
import logging
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
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

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

#log = current_app.logger

##############################
# ROUTES

user_secret_repository = UserSecretRepository()

RECORD_AES_KEY = 'DEFAULT_AES_KEY'
RECORD_AES_AAD = 'DEFAULT_AES_AAD'

# RECORD_AES_IV is not really used as initialization vector
# Instead we are using it as an additional authenticated data, AAD, or associated data, AD



@bp.route('/', methods=['GET', 'POST'])
def index():
    # new_uuid = None
    # if request.method == 'POST':
    #     new_uuid = uuid.uuid4()
    #    card_quantity = int(request.form['card_quantity'])
    #    tool_repository.seed(card_quantity)
    aes_key_record = user_secret_repository.find_record(RECORD_AES_KEY, g.user['id'], 1)
    aes_aad_record = user_secret_repository.find_record(RECORD_AES_AAD, g.user['id'], 1)
    has_aes_and_aad = aes_key_record is not None and aes_aad_record is not None
    return render_template('aes-tool/index.html', has_default_aes_key=has_aes_and_aad)

    
@bp.route('/api/generate', methods=['POST'])
def api_generate():
    log.info('api_generate called')
    user_secret_repository.add_if_not_exists(RECORD_AES_KEY, generate_random_byte_string(), g.user['id'], 1)
    user_secret_repository.add_if_not_exists(RECORD_AES_AAD, generate_random_byte_string(), g.user['id'], 1)
    return 'OK', 200
    
@bp.route('/api/regenerate', methods=['POST'])
def api_regenerate():
    user_secret_repository.update_system_record(RECORD_AES_KEY, generate_random_byte_string(), g.user['id'])
    user_secret_repository.update_system_record(RECORD_AES_AAD, generate_random_byte_string(), g.user['id'])
    return 'OK', 200

@bp.route('/api/encrypt-text', methods=['POST'])
def api_encrypt_text():
    aes_key_record = user_secret_repository.get_system_record(RECORD_AES_KEY, g.user['id'])
    aes_aad_record = user_secret_repository.get_system_record(RECORD_AES_AAD, g.user['id'])
    aes_key_bytes = aes_key_record['content'].encode('utf-8')
    aes_aad_bytes = aes_aad_record['content'].encode('utf-8')
    
    target_data = None
    json_data = None

    if request.is_json:
        json_data = request.json
    if 'content' in json_data:
        target_data = json_data['content'].encode('utf-8')
    
    # TODO: if target_data is None ==> bad request
    # print(target_data)

    cipher = AES.new(aes_key_bytes, AES.MODE_GCM)
    cipher.update(aes_aad_bytes)
    cipher_bytes, tag_bytes = cipher.encrypt_and_digest(target_data)

    json_k = [ 'nonce', 'cipher_text', 'tag' ]
    json_v = [ base64.b64encode(x).decode('utf-8') for x in (cipher.nonce, cipher_bytes, tag_bytes) ]
    result = json.dumps(dict(zip(json_k, json_v)))
    return result

@bp.route('/api/decrypt-text', methods=['POST'])
def api_decrypt_text():
    # Get the default AES DEFAULT KEY
    aes_key_record = user_secret_repository.get_system_record(RECORD_AES_KEY, g.user['id'])
    aes_iv_record = user_secret_repository.get_system_record(RECORD_AES_AAD, g.user['id'])
    aes_key_bytes = aes_key_record['content'].encode('utf-8')
    aes_iv_bytes = aes_iv_record['content'].encode('utf-8')
    
    target_data = None
    json_data = None

    if request.is_json:
        json_data = request.json
    if 'content' in json_data:
        target_data = json_data['content'].encode('utf-8')
    
    # # TODO: if target_data is None ==> bad request

    b64 = json.loads(target_data)
    json_k = [ 'nonce', 'cipher_text', 'tag' ]
    jv = { k:base64.b64decode(b64[k]) for k in json_k }

    cipher = AES.new(aes_key_bytes, AES.MODE_GCM, nonce=jv['nonce'])
    cipher.update(aes_iv_bytes)
    plaintext = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])
    return plaintext.decode('utf-8')

def generate_random_byte_string(number_of_bytes = 16):
    aes_key_bytes = get_random_bytes(number_of_bytes)
    #aes_key_string = base64.b64encode(aes_key_bytes).decode('utf-8')
    return base64.b64encode(aes_key_bytes).decode('utf-8')