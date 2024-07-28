from logging import getLogger
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('projects', __name__, url_prefix='/projects')

##############################
# REPOSITORY

class ProjectRepository:
    """Project repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_paged_records(self,page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT id, title FROM project
ORDER BY title ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM project;""").fetchone()['count']
        return (records, total_record_count)
        
    def get_record(self, id):
        db = get_db()
        record = db.execute("""
SELECT id, title FROM project WHERE id = ?;
""", (id,)).fetchone()
        return record

    def add_new_record(self, projects_title):
        db = get_db()
        db.execute('INSERT INTO project (title) VALUES (?);',
            (projects_title,)
        )
        db.commit()

    def update_record(self, id, projects_title):
        db = get_db()
        db.execute('UPDATE project SET title = ? WHERE id = ?;',
            (projects_title, id)
        )
        db.commit()

    def delete_record(self, id):
        db = get_db()
        db.execute('DELETE FROM project WHERE id = ?;',
            (id,)
        )
        db.commit()

##############################
# ROUTES

project_repository = ProjectRepository()

@bp.route('/')
@bp.route('/<int:page_number>')
def index(page_number=1):
    (records, total_record_count) = project_repository.get_paged_records(page_number)
    return render_template('projects/index.html', 
        records=records,
        total_record_count=total_record_count,
        page_number=page_number)


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
            project_repository.add_new_record(project_title)
            return redirect(url_for('projects.index'))

    return render_template('projects/register.html')


@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    if request.method == 'POST':
        project_title = request.form['project_title']
        action = request.form['action']
        #role_description = request.form['role_description']
        error = None

        if not project_title:
            error = 'Topic title is required.'

        if error is not None:
            flash(error)
        else:
            if action == 'Delete':
                project_repository.delete_record(id)
            else:
                project_repository.update_record(id, project_title)
            return redirect(url_for('projects.index'))
    record = project_repository.get_record(id)
    return render_template('projects/edit.html', record=record)

