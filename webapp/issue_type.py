from logging import getLogger
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('issue-type', __name__, url_prefix='/issue-type')

##############################
# REPOSITORY

class IssueTypeRepository:
    """Issue status repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_paged_records(self,page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT id, title, weight FROM issue_type 
ORDER BY weight DESC, title ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM issue_type;""").fetchone()['count']
        return (records, total_record_count)
        
    def get_record(self, id):
        db = get_db()
        record = db.execute("""
SELECT id, title, weight FROM issue_type WHERE id = ?;
""", (id,)).fetchone()
        return record

    def add_new_record(self, issue_type_title, issue_type_weight):
        db = get_db()
        db.execute('INSERT INTO issue_type (title, weight) VALUES (?, ?);',
            (issue_type_title,issue_type_weight)
        )
        db.commit()

    def update_record(self, id, issue_type_title, issue_type_weight):
        db = get_db()
        db.execute('UPDATE issue_type SET title = ?, weight = ? WHERE id = ?;',
            (issue_type_title, issue_type_weight, id)
        )
        db.commit()

    def delete_record(self, id):
        db = get_db()
        db.execute('DELETE FROM issue_type WHERE id = ?;',
            (id,)
        )
        db.commit()

##############################
# ROUTES

issue_type_repository = IssueTypeRepository()

@bp.route('/')
@bp.route('/<int:page_number>')
def index(page_number=1):
    (records, total_record_count) = issue_type_repository.get_paged_records(page_number)
    return render_template('issue-type/index.html', 
        records=records,
        total_record_count=total_record_count,
        page_number=page_number)


@bp.route('/register', methods=('GET', 'POST'))
@login_required
def register():
    if request.method == 'POST':
        issue_type_title = request.form['issue_type_title']
        issue_type_weight = request.form['issue_type_weight']
        #role_description = request.form['role_description']
        error = None

        if not issue_type_title:
            error = 'Issue type title is required.'

        if error is not None:
            flash(error)
        else:
            issue_type_repository.add_new_record(issue_type_title, issue_type_weight)
            return redirect(url_for('issue-type.index'))

    return render_template('issue-type/register.html')


@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    if request.method == 'POST':
        issue_type_title = request.form['issue_type_title']
        issue_type_weight = request.form['issue_type_weight']
        action = request.form['action']
        #role_description = request.form['role_description']
        error = None

        if not issue_type_title:
            error = 'Issue type title is required.'

        if error is not None:
            flash(error)
        else:
            if action == 'Delete':
                issue_type_repository.delete_record(id)
            else:
                issue_type_repository.update_record(id, issue_type_title, issue_type_weight)
            return redirect(url_for('issue-type.index'))
    record = issue_type_repository.get_record(id)
    return render_template('issue-type/edit.html', record=record)

