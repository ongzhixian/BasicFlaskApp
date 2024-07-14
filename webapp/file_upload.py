import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,current_app
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('file-upload', __name__, url_prefix='/file-upload')

@bp.route('/', methods=['GET', 'POST'])
def index():
    import pdb
    #pdb.set_trace()
    if request.method == 'POST':
        if 'uploadedFiles' in request.files:
            file_list = request.files.getlist('uploadedFiles')
            for f in file_list:
                filename = secure_filename(f.filename)
                save_folder_path = os.path.join(current_app.instance_path, 'uploads', str(g.user['id']))
                save_file_path = os.path.join(save_folder_path, filename)
                print(f"Saving {filename} to {save_file_path}")
                
                try:
                    if not os.path.exists(save_folder_path):
                        os.makedirs(save_folder_path) 
                    f.save(save_file_path)
                except OSError as err:
                    print(f"Error {err}")
                    
                print(f"{save_file_path} saved")

            # Do something with the file
        
    return render_template('file-upload/index.html')
