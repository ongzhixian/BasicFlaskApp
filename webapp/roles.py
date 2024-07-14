from logging import getLogger
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('roles', __name__, url_prefix='/roles')

##############################
# REPOSITORY

class RoleRepository:
    """User repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_paged_records(self,page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT 	r.id, r.name, r.description
FROM 	role r 
ORDER BY r.name ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM role;""").fetchone()['count']
        return (records, total_record_count)
        
    def get_role(self, id):
        db = get_db()
        record = db.execute("""
SELECT r.id, r.name, r.description FROM role r WHERE id = ?;
""", (id,)).fetchone()
        return record
        
    def get_users(self, role_id):
        db = get_db()
        records = db.execute("""
SELECT ur.id, u.username FROM user_role ur
JOIN user u 
ON u.id = ur.user_id
WHERE role_id = ?
""", (role_id,))
        return records
        
    def seed(self, item_count=6):
        db = get_db()
        for i in range (1, item_count + 1):
            role_name = f"role{i:03d}"
            db.execute(
                "INSERT INTO role (name) VALUES (?)",
                (role_name,),
            )
        db.commit()
        
        
class UserRoleRepository:
    """User-Role repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_paged_records(self,role_id,page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT u.username, ur.user_id, ur.role_id
FROM user_role ur
JOIN user u 
	ON u.id = ur.user_id
JOIN role r
	ON r.id = ur.role_id
WHERE ur.role_id = ?
ORDER BY u.username ASC
LIMIT ? OFFSET ?;
""", (role_id,self.page_size, offset)).fetchall()
        total_record_count = db.execute("""
SELECT COUNT(u.username) count
FROM user_role ur
JOIN user u 
	ON u.id = ur.user_id
JOIN role r
	ON r.id = ur.role_id
WHERE ur.role_id = ?
""", (role_id,)).fetchone()['count']
        print(f"records count {len(records)}")
        return (records, total_record_count)

##############################
# ROUTES

user_role_repository = UserRoleRepository()
role_repository = RoleRepository()

@bp.route('/')
@bp.route('/<int:page_number>')
def index(page_number=1):
    #role_repository.seed(6)
    (user_records, total_record_count) = role_repository.get_paged_records(page_number)
    return render_template('roles/index.html', 
        records=user_records, 
        total_record_count=total_record_count,
        page_number=page_number)


@bp.route('/register', methods=('GET', 'POST'))
@login_required
def register():
    if request.method == 'POST':
        role_name = request.form['role_name']
        role_description = request.form['role_description']
        error = None

        if not role_name:
            error = 'Role name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO role (name, description)'
                ' VALUES (?, ?)',
                (role_name, role_description)
            )
            db.commit()
            return redirect(url_for('roles.index'))

    return render_template('roles/register.html')


@bp.route('/<int:id>/members/')
@bp.route('/<int:id>/members/<int:page_number>')
def members(id, page_number=1):
    (user_records, total_record_count) = user_role_repository.get_paged_records(id, page_number)
    role_record = role_repository.get_role(id)
    return render_template('roles/members.html', 
        records=user_records, 
        total_record_count=total_record_count,
        page_number=page_number, role=role_record)


@bp.route('/<int:id>/members/add', methods=('GET', 'POST'))
def add_member(id):
    if request.method == 'POST':
        
        role_id = request.form['role_id']
        user_id_list = json.loads(request.form['user_id_list'])
        
        error = None

        if not role_id:
            error = 'Role Id is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            for user_id in user_id_list:
                print(f"user_id {user_id}, role_id {role_id}")
                db.execute("""
INSERT INTO user_role (user_id, role_id)
SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM user_role WHERE user_id = ? and role_id = ?);
""", (user_id, role_id, user_id, role_id))
            db.commit()
            return redirect(url_for('roles.index'))
            
    role_record = role_repository.get_role(id)
    return render_template('roles/add-member.html', role=role_record)


@bp.route('/<int:id>/members/remove', methods=('GET', 'POST'))
def remove_member(id):
    if request.method == 'POST':
        
        role_id = request.form['role_id']
        user_role_id_list = json.loads(request.form['user_role_id_list'])
        
        error = None

        if not role_id:
            error = 'Role Id is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            for user_role_id in user_role_id_list:
                db.execute("""
DELETE FROM user_role WHERE id = ?;
""", (user_role_id,))
            db.commit()
            return redirect(url_for('roles.index'))
          
    role_record = role_repository.get_role(id)
    user_role_records = role_repository.get_users(id)
    return render_template('roles/remove-member.html', role=role_record, user_roles=user_role_records)
    

@bp.route('/edit/<string:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    print(f"editing tool {id}")
    if request.method == 'POST':
        role_name = request.form['role_name']
        role_description = request.form['role_description']
        error = None

        if not role_name:
            error = 'Role name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("""
                UPDATE role
                SET name = ?
                    , description = ?
                WHERE id = ?;
                """,
                (role_name, role_description, id)
            )
            db.commit()
            return redirect(url_for('roles.index'))

    db = get_db()
    role = db.execute(
        'select t.id, t.name, t.description from role t where t.id = ?',
        (id,)
    ).fetchone()
    return render_template('roles/edit.html', role=role)


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


