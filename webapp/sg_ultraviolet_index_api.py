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
bp = Blueprint('sg-ultraviolet-index-api', __name__, url_prefix='/sg-ultraviolet-index-api')

##############################
# REPOSITORY


# Function to get live stock data for a symbol
def get_latest_day_uvi():
    url = "https://api-open.data.gov.sg/v2/real-time/api/uv"
    request_headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=request_headers)
    if response.status_code == 200:
        json_data = response.json()
        if json_data['code'] == 0:
            # Return the list of records instead of whole json structure
            return json_data['data']['records'][0]['index']
        
    return None
    
def get_latest_uvi():
    records = get_latest_day_uvi()
    if records is None:
        return None
    import pdb
    pdb.set_trace()
    return records[0]

    

##############################
# ROUTES

#topics_repository = TopicsRepository()

@bp.route('/')
@bp.route('/<int:page_number>')
def index(page_number=1):
    records = get_latest_day_uvi()
    return render_template('sg-ultraviolet-index-api/index.html', records=records)
    


