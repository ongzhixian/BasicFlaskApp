import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,current_app
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('test-module5', __name__, url_prefix='/test-module5')

@bp.route('/', methods=['GET', 'POST'])
def index():
    #if request.method == 'POST':
    #    card_quantity = int(request.form['card_quantity'])
    #    tool_repository.seed(card_quantity)
    return render_template('test-module5/index.html')