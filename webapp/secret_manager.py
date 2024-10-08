from logging import getLogger
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('secret-manager', __name__, url_prefix='/secret-manager')

##############################
# REPOSITORY

class UserSecretRepository:
    """User secret repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_paged_records(self, user_id, page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT id, title, content, update_ts FROM user_secret 
WHERE user_id = ? AND is_sysgen = 0
ORDER BY title ASC
LIMIT ? OFFSET ?;
""", (user_id, self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM user_secret;""").fetchone()['count']
        return (records, total_record_count)
        
    def get_record(self, id, is_sysgen = 0):
        db = get_db()
        record = db.execute("""
SELECT id, title, content FROM user_secret WHERE id = ? AND is_sysgen = ?;
""", (id,is_sysgen)).fetchone()
        return record

    def add_new_record(self, secret_title, secret_content, user_id, is_sysgen = 0):
        db = get_db()
        db.execute('INSERT INTO user_secret (title, content, user_id, is_sysgen) VALUES (?, ?, ?, ?);',
            (secret_title, secret_content, user_id, is_sysgen)
        )
        db.commit()

    def update_record(self, id, secret_content, is_sysgen = 0):
        db = get_db()
        db.execute('UPDATE user_secret SET content = ?, update_ts = CURRENT_TIMESTAMP WHERE id = ? AND is_sysgen = ?;',
            (secret_content, id, is_sysgen)
        )
        db.commit()

    def delete_record(self, id, is_sysgen = 0):
        db = get_db()
        db.execute('DELETE FROM user_secret WHERE id = ? AND is_sysgen = ?;',
            (id,is_sysgen)
        )
        db.commit()

    # Enhance

    def find_record(self, title, user_id, is_sysgen = 0):
        db = get_db()
        record = db.execute("""
SELECT id, title, content FROM user_secret WHERE title = ? AND user_id = ? AND is_sysgen = ?;
""", (title, user_id, is_sysgen)).fetchone()
        return record
    
    def add_if_not_exists(self, secret_title, secret_content, user_id, is_sysgen = 0):
        self.log.info('add_if_not_exists called')
        db = get_db()
        db.execute("""
INSERT INTO user_secret (title, content, user_id, is_sysgen)
SELECT ? title, ? content, ? user_id, ? is_sysgen 
WHERE NOT EXISTS (SELECT 1 FROM user_secret WHERE title = ? AND user_id = ? AND is_sysgen = ?)
""",
            (secret_title, secret_content, user_id, is_sysgen, 
             secret_title, user_id, is_sysgen)
        )
        db.commit()

    def update_system_record(self, secret_title, secret_content, user_id):
        db = get_db()
        db.execute('UPDATE user_secret SET content = ?, update_ts = CURRENT_TIMESTAMP WHERE title = ? AND user_id = ? AND is_sysgen = 1 ;',
            (secret_content, secret_title, user_id)
        )
        db.commit()

    def get_system_record(self, title, user_id):
        db = get_db()
        record = db.execute("""
SELECT id, title, content FROM user_secret WHERE title = ? AND user_id = ? AND is_sysgen = 1;
""", (title, user_id)).fetchone()
        return record


##############################
# ROUTES

user_secret_repository = UserSecretRepository()

@bp.route('/')
@bp.route('/<int:page_number>')
def index(page_number=1):
    (records, total_record_count) = user_secret_repository.get_paged_records(g.user['id'], page_number)
    return render_template('secret-manager/index.html', 
        records=records,
        total_record_count=total_record_count,
        page_number=page_number)


@bp.route('/register', methods=('GET', 'POST'))
@login_required
def register():
    if request.method == 'POST':
        secret_title = request.form['secret_title']
        secret_content = request.form['secret_content']
        #role_description = request.form['role_description']
        error = None

        if not secret_title:
            error = 'Secret title is required.'

        if error is not None:
            flash(error)
        else:
            user_secret_repository.add_new_record(secret_title, secret_content, g.user['id'])
            return redirect(url_for('secret-manager.index'))

    return render_template('secret-manager/register.html')


@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    if request.method == 'POST':
        secret_title = request.form['secret_title']
        secret_content = request.form['secret_content']
        action = request.form['action']
        #role_description = request.form['role_description']
        error = None

        if not secret_title:
            error = 'Secret title is required.'

        if error is not None:
            flash(error)
        else:
            if action == 'Delete':
                user_secret_repository.delete_record(id)
            else:
                user_secret_repository.update_record(id, secret_content)
            return redirect(url_for('secret-manager.index'))
    record = user_secret_repository.get_record(id)
    return render_template('secret-manager/edit.html', record=record)

