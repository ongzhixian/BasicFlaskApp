from logging import getLogger
import requests
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

# sg_ultraviolet_index_api
bp = Blueprint('random-user-api', __name__, url_prefix='/random-user-api')

##############################
# REPOSITORY


# Function to get live stock data for a symbol
def get_random_user():
    url = "https://randomuser.me/api/"
    request_headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=request_headers)
    if response.status_code == 200:
        json_data = response.json()
        return json_data['results'][0]
    return None

##############################
# ROUTES



@bp.route('/')
@bp.route('/<int:page_number>')
def index(page_number=1):
    record = get_random_user()
    return render_template('random-user-api/index.html', record=record)
    


