from logging import getLogger

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

import markdown

bp = Blueprint('blog', __name__, url_prefix='/blog')

##############################
# REPOSITORY

class BlogRepository:
    """Database repository for blog posts"""
    page_size = 5
    log = getLogger(__name__)

    def get_user_blog_posts(self, user_id, page_number = 1):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT p.id, p.update_ts, p.content, p.user_id, u.username FROM blog_post p 
JOIN user u on p.user_id = u.id
WHERE p.user_id = ?
ORDER BY p.update_ts DESC
LIMIT ? OFFSET ?;
""", (user_id, self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM blog_post p WHERE p.user_id = ?""",(user_id,)).fetchone()['count']
        return (records, total_record_count)

        
    def get_user_blog_post(self, user_id, id):
        db = get_db()
        record = db.execute("""
SELECT p.id, p.update_ts, p.content, p.user_id FROM blog_post p WHERE p.user_id = ? AND p.id = ?;
""", (user_id, id)).fetchone()
        return record


    def add_user_blog_post(self, blog_content, user_id):
        db = get_db()
        db.execute(
            'INSERT INTO blog_post (content, user_id)'
            ' VALUES (?, ?)',
            (blog_content, user_id)
        )
        db.commit()
        
        
    def update_user_blog_post(self, blog_content, user_id, id):
        db = get_db()
        db.execute(
            'UPDATE blog_post SET content = ?, update_ts=DATETIME() WHERE user_id = ? AND id = ?',
            (blog_content, user_id, id)
        )
        db.commit()
        
        
    def delete_user_blog_post(self, user_id, id):
        db = get_db()
        record = db.execute("""DELETE blog_post WHERE user_id = ? AND id = ?';""", (user_id, id)).fetchone()
        return record        



##############################
# ROUTES

blog_repository = BlogRepository()


@bp.route('/')
@bp.route('/<int:page_number>')
@login_required
def index(page_number=1):
    (posts, total_record_count) = blog_repository.get_user_blog_posts(g.user['id'], page_number)
    # htmlContent = markdown.markdown(note['content'])
    # p.id, p.update_ts, p.content, p.user_id, u.username
    post_list = []
    for post in posts:
        post_list.append({
            'id' : post['id'],
            'update_ts' : post['update_ts'],
            'content' : markdown.markdown(post['content']),
            'user_id' : post['user_id'],
            'username' : post['username'],
        })
    return render_template('blog/index.html', posts=post_list, 
        total_record_count=total_record_count, page_number=page_number)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        blog_content = request.form['blog_content']
        error = None

        if not blog_content:
            error = 'Blog content is required.'

        if error is not None:
            flash(error)
        else:
            blog_repository.add_user_blog_post(blog_content, g.user['id'])
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    if request.method == 'POST':
        blog_content = request.form['blog_content']
        error = None

        if not blog_content:
            error = 'Blog content is required.'

        if error is not None:
            flash(error)
        else:
            blog_repository.update_user_blog_post(blog_content, g.user['id'], id)
            return redirect(url_for('blog.index'))

    
    post = blog_repository.get_user_blog_post(g.user['id'], id)
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

