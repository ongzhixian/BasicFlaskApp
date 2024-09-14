from logging import getLogger
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('url-mine', __name__, url_prefix='/url-mine')

##############################
# REPOSITORY

class UrlRepository:
    """Url repository"""
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

    def add_new_record(self, href):
        db = get_db()
        db.execute('INSERT INTO url (href) VALUES (?);',
            (href,)
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

url_repository = UrlRepository()

# @bp.route('/api/search')
# def api_search():
#     result = {
#         "is_success": True,
#         "message": "OK world"
#     }
#     return json.dumps(result)
    

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url_text = request.form['url_text']
        #role_description = request.form['role_description']
        error = None

        if not url_text:
            error = 'url_text is required.'

        if error is not None:
            flash(error)
        else:
            # Parse url_text to lines
            # Add each line as a record
            import pdb
            # Trim each line (removing empty strings)
            url_list = filter(None, [split_item.strip() for split_item in url_text.split('\r\n')])
            for url in url_list:
                print(f"Adding {url}")
                url_repository.add_new_record(url)
            
            return redirect(url_for('url-mine.index'))

    return render_template('url-mine/index.html')


# @bp.route('/register', methods=('GET', 'POST'))
# @login_required
# def register():
#     if request.method == 'POST':
#         url_text = request.form['url_text']
#         #role_description = request.form['role_description']
#         error = None

#         if not url_text:
#             error = 'url_text is required.'

#         if error is not None:
#             flash(error)
#         else:
#             # Parse url_text to lines
#             # Add each line as a record
#             import pdb
#             pdb.set_trace()

#             url_repository.add_new_record(url_text)
#             return redirect(url_for('topics.index'))

#     return render_template('url-mine/register.html')


# @bp.route('/edit/<int:id>', methods=('GET', 'POST'))
# @login_required
# def edit(id):
#     if request.method == 'POST':
#         topic_title = request.form['topic_title']
#         action = request.form['action']
#         #role_description = request.form['role_description']
#         error = None

#         if not topic_title:
#             error = 'Topic title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             if action == 'Delete':
#                 url_repository.delete_record(id)
#             else:
#                 url_repository.update_record(id, topic_title)
#             return redirect(url_for('topics.index'))
#     record = url_repository.get_record(id)
#     return render_template('url-mine/edit.html', record=record)

