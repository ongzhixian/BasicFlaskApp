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
        # Create python file
        module_file_name = to_module_file_name(blueprint_title)
        module_name = to_module_name(blueprint_title)
        create_stub_python_file(module_file_name, module_name)
        # Create template
        create_stub_htmls(blueprint_title, module_name)
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



# CREATE STUB METHODS

def create_stub_htmls(module_title, module_name):
    # create target folder
    target_folder_path = f"webapp/templates/{module_name}"
    if not os.path.exists(target_folder_path):
        os.mkdir(target_folder_path)
    create_stub_index_html(module_title, module_name, target_folder_path)


def create_stub_index_html(module_title, module_name, target_folder_path):
    out_file_path = f"{target_folder_path}/index.html"
    # Read template file
    template_file_path = f"webapp/templates/blueprint-generator/code-templates/stub-index.txt"
    with open(template_file_path, 'r') as in_file:
        template_content = in_file.read()
    # Define template placeholder values
    template_values = {
        'module_title': module_title,
    }
    out_html = replace_template_tokens(template_content, template_values)
    # Write file
    with open(out_file_path, 'w') as file:
        file.write(out_html)


def create_stub_python_file(module_file_name, module_name):
    file_path = f"webapp/{module_file_name}.py"
    # Read template file
    template_file_path = f"webapp/templates/blueprint-generator/code-templates/stub-module.txt"
    with open(template_file_path, 'r') as in_file:
        template_content = in_file.read()
    # Define template placeholder values
    template_values = {
        'module_name': module_name,
    }
    # Write file
    with open(file_path, 'w') as file:
        file.write(template_content.format(**template_values))


# HELPER METHODS

def to_module_file_name(term):
    """Just means replacing whitespace with underscores (_) """
    import re
    whitespace = re.compile(r'\s+')
    new_term = re.sub(whitespace, '_', term).lower()
    print(f"new_term is {new_term}")
    return new_term
    
def to_module_name(term):
    """Just means replacing whitespace with dash (-) """
    import re
    whitespace = re.compile(r'\s+')
    new_term = re.sub(whitespace, '-', term).lower()
    print(f"new_term is {new_term}")
    return new_term
    
def replace_template_tokens(template_content, template_values):
    import pdb
    import re
    new_content = template_content
    for key in template_values:
        # Find a token that looks like "{!module_title}"
        token = f'{{!{key}}}'
        print(f'Replacing {token}')
        new_content = re.sub(token, template_values[key], new_content)
    return new_content
