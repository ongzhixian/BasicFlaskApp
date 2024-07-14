from logging import getLogger
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('tools', __name__, url_prefix='/tools')

##############################
# REPOSITORY

class ToolRepository:
    """A simple example class"""
    i = 12345
    page_size = 6
    log = getLogger(__name__)

    def get_all_tools(self,page_number):
        offset = (page_number - 1) * 6
        print(f"get_all_tools {page_number}")
        self.log.info(f"LOGINFO get_all_tools {page_number}")
        db = get_db()
        tools = db.execute("""
SELECT 	t.id, t.name, t.description, t.url
FROM 	tool t 
ORDER BY t.name ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM tool""").fetchone()['count']
        return (tools, total_record_count)
        
    def seed(self, item_count=16):
        tool_description = 'I am a very simple card. I am good at containing small bits of information. I am convenient because I require little markup to use effectively.'
        user_id = 0
        tool_url = f'tools.index'
        db = get_db()
        for i in range (1, item_count + 1):
            tool_name = f"Tool {i:03d}"
            db.execute(
                'INSERT INTO tool (name, description, url, user_id)'
                ' VALUES (?, ?, ?, ?)',
                (tool_name, tool_description, tool_url, g.user['id'])
            )
        db.commit()
        

##############################
# ROUTES

tool_repository = ToolRepository()

@bp.route('/')
@bp.route('/<int:page_number>')
@login_required
def index(page_number=1):
    #tool_repository.seed(10)
    (tools, total_record_count) = tool_repository.get_all_tools(page_number)
    #print(f"page_number is {page_number}")
    return render_template('tools/index.html', tools=tools, 
        total_record_count=total_record_count,page_number=page_number)

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
    print(tool['description'].encode('unicode_escape'))
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


