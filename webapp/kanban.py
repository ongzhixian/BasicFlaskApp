from logging import getLogger
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('kanban', __name__, url_prefix='/kanban')

##############################
# REPOSITORY

class KanbanRepository:
    """User profile repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_paged_records(self,page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT id, title FROM kanban
ORDER BY title ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM kanban;""").fetchone()['count']
        return (records, total_record_count)
        
    def get_record_by_user_id(self, user_id):
        db = get_db()
        record = db.execute("""
SELECT * FROM kanban WHERE user_id = ?;
""", (user_id,)).fetchone()
        return record

    def add_new_record(self, projects_title):
        db = get_db()
        db.execute('INSERT INTO project (title) VALUES (?);',
            (projects_title,)
        )
        db.commit()

    def update_record(self, user_id, first_name, last_name):
        db = get_db()
        db.execute("""INSERT INTO kanban(first_name, last_name, user_id)
VALUES(?, ?, ?)
ON CONFLICT(user_id) 
DO 
UPDATE 
SET first_name = ?
	, last_name = ?
    , update_ts = CURRENT_TIMESTAMP
;
""",
            (first_name, last_name, user_id, first_name, last_name)
        )
        db.commit()

    def delete_record(self, id):
        db = get_db()
        db.execute('DELETE FROM kanban WHERE id = ?;',
            (id,)
        )
        db.commit()

##############################
# ROUTES

kanban_repository = KanbanRepository()

@bp.route('/')
def index():
    #(records, total_record_count) = kanban_repository.get_paged_records(page_number)
    # record = kanban_repository.get_record_by_user_id(g.user['id'])
    return render_template('kanban/index.html')


@bp.route('/register', methods=('GET', 'POST'))
@login_required
def register():
    if request.method == 'POST':
        project_title = request.form['project_title']
        #role_description = request.form['role_description']
        error = None

        if not project_title:
            error = 'Project title is required.'

        if error is not None:
            flash(error)
        else:
            kanban_repository.add_new_record(project_title)
            return redirect(url_for('projects.index'))

    return render_template('kanban/register.html')


@bp.route('/edit', methods=('GET', 'POST'))
@login_required
def edit():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        action = request.form['action']
        
        error = None

        if not first_name:
            error = 'First name is required.'

        if error is not None:
            flash(error)
        else:
            # if action == 'Delete':
            #     kanban_repository.delete_record(id)
            # else:
            kanban_repository.update_record(g.user['id'], first_name, last_name)
            return redirect(url_for('kanban.index'))
    record = kanban_repository.get_record_by_user_id(g.user['id'])
    return render_template('kanban/edit.html', record=record)

