from logging import getLogger
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('sprints', __name__, url_prefix='/sprints')

##############################
# REPOSITORY

class SprintRepository:
    """Sprint repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_paged_records(self,page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT id, title, start_date, end_date FROM sprint
ORDER BY title ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM sprint;""").fetchone()['count']
        return (records, total_record_count)
        
    def get_record(self, id):
        db = get_db()
        record = db.execute("""
SELECT id, title, start_date, end_date FROM sprint WHERE id = ?;
""", (id,)).fetchone()
        return record

    def add_new_record(self, sprint_title, start_date, end_date):
        db = get_db()
        db.execute('INSERT INTO sprint (title, start_date, end_date) VALUES (?, ?, ?);',
            (sprint_title, start_date, end_date)
        )
        db.commit()

    def update_record(self, id, sprint_title, start_date, end_date):
        db = get_db()
        db.execute('UPDATE project SET title = ?, start_date = ?, end_date = ? WHERE id = ?;',
            (sprint_title, start_date, end_date, id)
        )
        db.commit()

    def delete_record(self, id):
        db = get_db()
        db.execute('DELETE FROM sprint WHERE id = ?;',
            (id,)
        )
        db.commit()

##############################
# ROUTES

sprint_repository = SprintRepository()

@bp.route('/')
@bp.route('/<int:page_number>')
def index(page_number=1):
    (records, total_record_count) = sprint_repository.get_paged_records(page_number)
    return render_template('sprints/index.html', 
        records=records,
        total_record_count=total_record_count,
        page_number=page_number)


@bp.route('/register', methods=('GET', 'POST'))
@login_required
def register():
    if request.method == 'POST':
        sprint_title = request.form['sprint_title']
        sprint_start_date = request.form['sprint_start_date']
        sprint_end_date = request.form['sprint_end_date']
        #role_description = request.form['role_description']
        error = None

        import pdb
        pdb.set_trace()

        if not sprint_title:
            error = 'Sprint title is required.'

        if error is not None:
            flash(error)
        else:
            sprint_repository.add_new_record(sprint_title, sprint_start_date, sprint_end_date)
            return redirect(url_for('sprints.index'))

    return render_template('sprints/register.html')


@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    if request.method == 'POST':
        sprint_title = request.form['sprint_title']
        action = request.form['action']
        #role_description = request.form['role_description']
        error = None

        if not sprint_title:
            error = 'Sprint title is required.'

        if error is not None:
            flash(error)
        else:
            if action == 'Delete':
                sprint_repository.delete_record(id)
            else:
                sprint_repository.update_record(id, sprint_title)
            return redirect(url_for('sprints.index'))
    record = sprint_repository.get_record(id)
    return render_template('sprints/edit.html', record=record)

