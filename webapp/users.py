from logging import getLogger
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('users', __name__, url_prefix='/users')

##############################
# REPOSITORY

class UserRepository:
    """User repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_paged_records(self,page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT 	u.id, u.username
FROM 	user u 
ORDER BY u.username ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM user""").fetchone()['count']
        return (records, total_record_count)
        
        
    def search(self, query):    
        db = get_db()
        records = db.execute("""
SELECT u.id, u.username 
FROM user u 
WHERE username LIKE ?
ORDER BY u.username ASC
LIMIT 10;
""", (query,)).fetchall()
        return records
        
        
    def seed(self, item_count=16):
        db = get_db()
        for i in range (1, item_count + 1):
            username = f"testuser{i:03d}"
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, generate_password_hash(username)),
            )
        db.commit()
        

    


##############################
# ROUTES

user_repository = UserRepository()

@bp.route('/api/search')
def api_search():
    query = request.args.get('query')
    print(f"api search for {query}")
    records = user_repository.search(f"%{query}%")
    return jsonify([dict(record) for record in records])
    

@bp.route('/')
@bp.route('/<int:page_number>')
def index(page_number=1):
    #user_repository.seed(16)
    (user_records, total_record_count) = user_repository.get_paged_records(page_number)
    return render_template('users/index.html', 
        users=user_records, 
        total_record_count=total_record_count,
        page_number=page_number)
    

@bp.route('/register', methods=('GET', 'POST'))
@login_required
def register():
    if request.method == 'POST':
        tool_name = request.form['tool_name']
        tool_description = request.form['tool_description']
        tool_url = request.form['tool_url']
        error = None

        if not tool_name:
            error = 'Tool name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tool (name, description, url, user_id)'
                ' VALUES (?, ?, ?, ?)',
                (tool_name, tool_description, tool_url, g.user['id'])
            )
            db.commit()
            return redirect(url_for('tools.index'))

    return render_template('tools/register.html')


@bp.route('/edit/<string:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    print(f"editing tool {id}")
    if request.method == 'POST':
        tool_name = request.form['tool_name']
        tool_description = request.form['tool_description']
        tool_url = request.form['tool_url']
        error = None

        if not tool_name:
            error = 'Tool name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("""
                UPDATE tool 
                SET name = ?
                    , description = ?
                    , url = ?
                    , update_ts = current_timestamp
                WHERE id = ?;
                """,
                (tool_name, tool_description, tool_url, id)
            )
            db.commit()
            return redirect(url_for('tools.index'))

    db = get_db()
    tool = db.execute(
        'select t.id, t.name, t.description, t.url from tool t where t.id = ?',
        (id,)
    ).fetchone()
    return render_template('tools/edit.html', tool=tool)


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


