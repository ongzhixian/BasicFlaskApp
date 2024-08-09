from logging import getLogger
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('workspaces', __name__, url_prefix='/workspaces')

##############################
# REPOSITORY

class WorkspaceRepository:
    """Workspace repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_paged_records(self,page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT id, title FROM workspace
ORDER BY title ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM workspace;""").fetchone()['count']
        return (records, total_record_count)
        
    def get_record(self, id):
        db = get_db()
        record = db.execute("""
SELECT id, title FROM workspace WHERE id = ?;
""", (id,)).fetchone()
        return record

    def add_new_record(self, workspace_title):
        db = get_db()
        db.execute('INSERT INTO workspace (title) VALUES (?);',
            (workspace_title,)
        )
        db.commit()

    def update_record(self, id, workspace_title):
        db = get_db()
        db.execute('UPDATE workspace SET title = ? WHERE id = ?;',
            (workspace_title, id)
        )
        db.commit()

    def delete_record(self, id):
        db = get_db()
        db.execute('DELETE FROM workspace WHERE id = ?;',
            (id,)
        )
        db.commit()

##############################
# ROUTES

workspace_repository = WorkspaceRepository()

@bp.route('/')
@bp.route('/<int:page_number>')
def index(page_number=1):
    (records, total_record_count) = workspace_repository.get_paged_records(page_number)
    return render_template('workspaces/index.html', 
        records=records,
        total_record_count=total_record_count,
        page_number=page_number)


@bp.route('/register', methods=('GET', 'POST'))
@login_required
def register():
    if request.method == 'POST':
        workspace_title = request.form['workspace_title']
        #role_description = request.form['role_description']
        error = None

        if not workspace_title:
            error = 'Project title is required.'

        if error is not None:
            flash(error)
        else:
            workspace_repository.add_new_record(workspace_title)
            return redirect(url_for('workspaces.index'))

    return render_template('workspaces/register.html')


@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    if request.method == 'POST':
        workspace_title = request.form['workspace_title']
        action = request.form['action']
        #role_description = request.form['role_description']
        error = None

        if not workspace_title:
            error = 'Topic title is required.'

        if error is not None:
            flash(error)
        else:
            if action == 'Delete':
                workspace_repository.delete_record(id)
            else:
                workspace_repository.update_record(id, workspace_title)
            return redirect(url_for('workspaces.index'))
    record = workspace_repository.get_record(id)
    return render_template('workspaces/edit.html', record=record)

