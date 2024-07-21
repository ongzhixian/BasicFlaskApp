from logging import getLogger
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('issues', __name__, url_prefix='/issues')

##############################
# REPOSITORY

class IssueRepository:
    """Issue repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_paged_records(self,page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT i.id, i.update_ts, i.title, ty.title issue_type, st.title issue_status 
FROM issue i
JOIN issue_type ty ON i.type_id = ty.id
JOIN issue_status st ON i.status_id = st.id
ORDER BY i.title ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(i.id) count FROM issue i
JOIN issue_type ty ON i.type_id = ty.id
JOIN issue_status st ON i.status_id = st.id""").fetchone()['count']
        return (records, total_record_count)
        
        
    def get_issue(self, id):
        db = get_db()
        record = db.execute("""
SELECT i.id, i.update_ts, i.title, i.description, i.type_id, i.status_id
FROM issue i
WHERE i.id = ?;
""", (id,)).fetchone()
        return record

    def get_issue_types(self):
        db = get_db()
        records = db.execute("""SELECT id, title FROM issue_type;""").fetchall()
        return records
        
    def get_issue_statuses(self):
        db = get_db()
        records = db.execute("""SELECT id, title FROM issue_status;""").fetchall()
        return records
        
        
    def add_issue(self, type_id, title, description, user_id):
        db = get_db()
        issue_status_id = 1
        db.execute("""INSERT INTO issue (type_id, title, description, status_id, user_id) VALUES (?, ?, ?, ?, ?);""",
            (type_id, title, description, issue_status_id, user_id)
        )
        db.commit()
        
    def update_issue(self, issue_type_id, issue_title, issue_description, issue_status_id, id):
        db = get_db()
        db.execute("""UPDATE issue SET type_id = ?, title = ?, description = ?, status_id = ? WHERE id = ?;""",
            (issue_type_id, issue_title, issue_description, issue_status_id, id)
        )
        db.commit()
        
    def delete_user_blog_post(self, user_id, id):
        db = get_db()
        record = db.execute("""DELETE blog_post WHERE user_id = ? AND id = ?';""", (user_id, id)).fetchone()
        return record    
    
    # OBSOLETE
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

issue_repository = IssueRepository()



@bp.route('/')
@bp.route('/<int:page_number>')
def index(page_number=1):
    #user_repository.seed(16)
    (records, total_record_count) = issue_repository.get_paged_records(page_number)
    return render_template('issues/index.html', 
        issues=records, 
        total_record_count=total_record_count,
        page_number=page_number)
    
    
@bp.route('/api/search')
def api_search():
    query = request.args.get('query')
    print(f"api search for {query}")
    records = issue_repository.search(f"%{query}%")
    return jsonify([dict(record) for record in records])
    

@bp.route('/register', methods=('GET', 'POST'))
@login_required
def register():
    if request.method == 'POST':
        issue_type = request.form['issue_type']
        issue_title = request.form['issue_title']
        issue_description = request.form['issue_description']
        
        error = None

        if not issue_title:
            error = 'Issue title is required.'

        if error is not None:
            flash(error)
        else:
            issue_repository.add_issue(issue_type, issue_title, issue_description, g.user['id'])
            return redirect(url_for('issues.index'))

    return render_template('issues/register.html')


@bp.route('/edit/<string:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    if request.method == 'POST':
        issue_status = request.form['issue_status']
        issue_type = request.form['issue_type']
        issue_title = request.form['issue_title']
        issue_description = request.form['issue_description']
        error = None

        if not issue_title:
            error = 'Issue title is required.'

        if error is not None:
            flash(error)
        else:
            issue_repository.update_issue(issue_type, issue_title, issue_description, issue_status, id)
            return redirect(url_for('issues.index'))
    
    issue_statuses = issue_repository.get_issue_statuses()
    issue_types = issue_repository.get_issue_types()
    issue = issue_repository.get_issue(id)
    return render_template('issues/edit.html', issue=issue, issue_types=issue_types, issue_statuses=issue_statuses)
