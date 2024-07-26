import os
import uuid
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,current_app
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('uuid-tool', __name__, url_prefix='/uuid-tool')

@bp.route('/', methods=['GET', 'POST'])
def index():
    new_uuid = None
    if request.method == 'POST':
        new_uuid = uuid.uuid4()
    #    card_quantity = int(request.form['card_quantity'])
    #    tool_repository.seed(card_quantity)
    return render_template('uuid-tool/index.html', new_uuid=new_uuid)
