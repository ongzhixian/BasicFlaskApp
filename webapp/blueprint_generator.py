import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,current_app
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('blueprint-generator', __name__, url_prefix='/blueprint-generator')

@bp.route('/', methods=['GET', 'POST'])
def index():
    #if request.method == 'POST':
    #    card_quantity = int(request.form['card_quantity'])
    #    tool_repository.seed(card_quantity)
    return render_template('blueprint-generator/index.html')

@bp.route('/create-stub', methods=['GET', 'POST'])
def create_stub():
    if request.method == 'POST':
        blueprint_title = request.form['blueprint_title']
        # TODO: Create python file
        module_file_name = to_module_file_name(blueprint_title)
        module_name = to_module_name(blueprint_title)
        create_python_file(module_file_name, module_name)
        # TODO: Create template
        #return render_template('blueprint-generator/create-stub.html')
    #    card_quantity = int(request.form['card_quantity'])
    #    tool_repository.seed(card_quantity)
    return render_template('blueprint-generator/create-stub.html')


@bp.route('/create-data-entry', methods=['GET', 'POST'])
def create_data_entry():
    #if request.method == 'POST':
    #    card_quantity = int(request.form['card_quantity'])
    #    tool_repository.seed(card_quantity)
    return render_template('blueprint-generator/create-data-entry.html')



def to_module_file_name(term):
    import re
    whitespace = re.compile(r'\s+')
    new_term = re.sub(whitespace, '_', term)
    print(f"new_term is {new_term}")
    return new_term
    
def to_module_name(term):
    import re
    whitespace = re.compile(r'\s+')
    new_term = re.sub(whitespace, '-', term)
    print(f"new_term is {new_term}")
    return new_term
    

def create_python_file(module_file_name, module_name):
    file_path = f"webapp/{module_file_name}.py"
    with open(file_path, 'w') as file:
        file.write(f"""import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,current_app
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('{module_name}', __name__, url_prefix='/{module_name}')

@bp.route('/', methods=['GET', 'POST'])
def index():
    #if request.method == 'POST':
    #    card_quantity = int(request.form['card_quantity'])
    #    tool_repository.seed(card_quantity)
    return render_template('{module_name}/index.html')
""")
