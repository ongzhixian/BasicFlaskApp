from logging import getLogger
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

import markdown

bp = Blueprint('notes', __name__, url_prefix='/notes')

##############################
# REPOSITORY

class NoteRepository:
    """Database repository for user notes"""
    page_size = 10
    log = getLogger(__name__)

    def get_user_notes(self, user_id, page_number = 1):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT n.id, n.update_ts, n.title, n.content FROM note n WHERE n.user_id = ?
ORDER BY n.update_ts DESC, n.title ASC
LIMIT ? OFFSET ?;
""", (user_id, self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM note n WHERE n.user_id = ?""",(user_id,)).fetchone()['count']
        return (records, total_record_count)
        
    def get_user_note(self, user_id, id):
        db = get_db()
        record = db.execute("""
SELECT n.id, n.update_ts, n.title, n.content FROM note n WHERE n.user_id = ? AND id = ?;
""", (user_id, id)).fetchone()
        return record
        
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

note_repository = NoteRepository()

@bp.route('/')
@bp.route('/<int:page_number>')
@login_required
def index(page_number=1):
    (notes, total_record_count) = note_repository.get_user_notes(g.user['id'], page_number)
    return render_template('notes/index.html', notes=notes, 
        total_record_count=total_record_count,page_number=page_number)


@bp.route('/view/<int:id>')
@login_required
def view(id=1):
    note = note_repository.get_user_note(g.user['id'], id)
    
    htmlContent = markdown.markdown(note['content'])
    return render_template('notes/view.html', note=note, content=htmlContent)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        note_title = request.form['note_title']
        note_content = request.form['note_content']
        error = None

        if not note_title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO note (title, content, user_id)'
                ' VALUES (?, ?, ?)',
                (note_title, note_content, g.user['id'])
            )
            db.commit()
            return redirect(url_for('notes.index'))

    return render_template('notes/create.html')

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

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    
    if request.method == 'POST':
        note_title = request.form['note_title']
        note_content = request.form['note_content']
        error = None

        if not note_title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE note SET title = ?, content = ?'
                ' WHERE id = ? AND user_id = ?',
                (note_title, note_content, id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('notes.index'))

    note = note_repository.get_user_note(g.user['id'], id)
    return render_template('notes/update.html', note=note)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

