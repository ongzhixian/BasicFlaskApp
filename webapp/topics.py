from logging import getLogger
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('topics', __name__, url_prefix='/topics')

##############################
# REPOSITORY

class TopicRepository:
    """Issue status repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_paged_records(self,page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT id, title FROM topic
ORDER BY title ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM topic;""").fetchone()['count']
        return (records, total_record_count)
        
    def get_record(self, id):
        db = get_db()
        record = db.execute("""
SELECT id, title FROM topic WHERE id = ?;
""", (id,)).fetchone()
        return record

    def add_new_record(self, topics_title):
        db = get_db()
        db.execute('INSERT INTO topic (title) VALUES (?);',
            (topics_title,)
        )
        db.commit()

    def update_record(self, id, topics_title):
        db = get_db()
        db.execute('UPDATE topic SET title = ? WHERE id = ?;',
            (topics_title, id)
        )
        db.commit()

    def delete_record(self, id):
        db = get_db()
        db.execute('DELETE FROM topic WHERE id = ?;',
            (id,)
        )
        db.commit()

##############################
# ROUTES

topic_repository = TopicRepository()

@bp.route('/api/search')
def api_search():
    result = {
        "is_success": True,
        "message": "OK world"
    }
    return json.dumps(result)
    

@bp.route('/')
@bp.route('/<int:page_number>')
def index(page_number=1):
    (records, total_record_count) = topic_repository.get_paged_records(page_number)
    return render_template('topics/index.html', 
        records=records,
        total_record_count=total_record_count,
        page_number=page_number)


@bp.route('/register', methods=('GET', 'POST'))
@login_required
def register():
    if request.method == 'POST':
        topic_title = request.form['topic_title']
        #role_description = request.form['role_description']
        error = None

        if not topic_title:
            error = 'Issue status title is required.'

        if error is not None:
            flash(error)
        else:
            topic_repository.add_new_record(topic_title)
            return redirect(url_for('topics.index'))

    return render_template('topics/register.html')


@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    if request.method == 'POST':
        topic_title = request.form['topic_title']
        action = request.form['action']
        #role_description = request.form['role_description']
        error = None

        if not topic_title:
            error = 'Topic title is required.'

        if error is not None:
            flash(error)
        else:
            if action == 'Delete':
                topic_repository.delete_record(id)
            else:
                topic_repository.update_record(id, topic_title)
            return redirect(url_for('topics.index'))
    record = topic_repository.get_record(id)
    return render_template('topics/edit.html', record=record)

