from logging import getLogger
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('kanban', __name__, url_prefix='/kanban')

##############################
# REPOSITORY

class KanbanRepository:
    """User profile repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_kanban_lanes(self, board_title, user_id):
        db = get_db()
        records = db.execute("""
SELECT 	kb.title as 'board_title'
		, kb.description as 'board_description' 
        , kl.id as 'lane_id'
		, kl.display_order as 'lane_order'
		, kl.title as 'lane_title'
		, kl.description as 'lane_description'
FROM 	kanban_board kb
LEFT JOIN 	kanban_lane kl
		ON kb.id = kl.kanban_board_id
WHERE 	kb.user_id = ? AND kb.title = ?
ORDER BY kl.display_order
""", (user_id, board_title)).fetchall()
        return records

    def get_kanban_lane_items(self, kanban_lane_id):
        db = get_db()
        records = db.execute("""
SELECT 	ki.kanban_lane_id as 'lane_id'
		, ki.id as 'item_id'
		, ki.display_order as 'item_order'
		, ki.title as 'item_title'
		, ki.description as 'item_description'
FROM 	kanban_lane kl
LEFT JOIN	kanban_item ki
		ON kl.id = ki.kanban_lane_id
WHERE 	kl.id = ?
ORDER BY kl.display_order, ki.display_order

""", (kanban_lane_id,)).fetchall()
        return records

    def get_paged_records(self,page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT id, title FROM kanban
ORDER BY title ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM kanban;""").fetchone()['count']
        return (records, total_record_count)
        
    def get_record_by_user_id(self, user_id):
        db = get_db()
        record = db.execute("""
SELECT * FROM kanban WHERE user_id = ?;
""", (user_id,)).fetchone()
        return record

    def add_new_record(self, projects_title):
        db = get_db()
        db.execute('INSERT INTO project (title) VALUES (?);',
            (projects_title,)
        )
        db.commit()

    def update_record(self, user_id, first_name, last_name):
        db = get_db()
        db.execute("""INSERT INTO kanban(first_name, last_name, user_id)
VALUES(?, ?, ?)
ON CONFLICT(user_id) 
DO 
UPDATE 
SET first_name = ?
	, last_name = ?
    , update_ts = CURRENT_TIMESTAMP
;
""",
            (first_name, last_name, user_id, first_name, last_name)
        )
        db.commit()

    def delete_record(self, id):
        db = get_db()
        db.execute('DELETE FROM kanban WHERE id = ?;',
            (id,)
        )
        db.commit()

##############################
# ROUTES

kanban_repository = KanbanRepository()
from webapp.tasks import TaskRepository
task_repository = TaskRepository()

@bp.route('/')
def index():
    #(records, total_record_count) = kanban_repository.get_paged_records(page_number)
    # record = kanban_repository.get_record_by_user_id(g.user['id'])
    return render_template('kanban/index.html')


@bp.route('/api/lanes', methods=['GET', 'POST'])
def api_get_lanes():
    lane_records = kanban_repository.get_kanban_lanes('Tasks', g.user['id'])
    response = {
        'records': [dict(record) for record in lane_records]
    }
    return json.dumps(response)

@bp.route('/api/items', methods=['GET', 'POST'])
def api_get_items():
    if 'id' not in request.args:
        abort(400)
    lane_id = request.args['id']
    lane_records = kanban_repository.get_kanban_lane_items(lane_id)
    response = {
        'records': [dict(record) for record in lane_records]
    }
    return json.dumps(response)


@bp.route('/api/tasks', methods=['GET', 'POST'])
def api_get_tasks():
    #task_records = task_repository.get_tasks_by_user_id(g.user['id'])
    #(records, total_record_count) = kanban_repository.get_paged_records(page_number)
    # record = kanban_repository.get_record_by_user_id(g.user['id'])
    if request.method == 'POST':
        # import pdb
        # pdb.set_trace()
        if not request.is_json:
            abort(400)

        if request.is_json:
            task_title = request.json['task_title']
            task_description = request.json['task_description']

        #project_title = request.form['project_title']
        #role_description = request.form['role_description']
        error = None

        if not task_title:
            error = 'Task title is required.'

        if error is not None:
            abort(400)
        else:
            task_repository.add_new_record(task_title, task_description, g.user['id'])
            return '{}'
            #return redirect(url_for('projects.index'))

    #(records, total_record_count) = issue_repository.search(f"%{query}%", page)
    task_records = task_repository.get_tasks_by_user_id(g.user['id'])
    response = {
        # 'total_record_count': total_record_count,
        'records': [dict(record) for record in task_records]
    }
    return json.dumps(response)
    #return render_template('kanban/index.html', task_records=task_records)
    

@bp.route('/api/add-task', methods=['POST'])
def api_add_task():
    #(records, total_record_count) = kanban_repository.get_paged_records(page_number)
    # record = kanban_repository.get_record_by_user_id(g.user['id'])
    #task_records = task_repository.add_task(g.user['id'])
    #return render_template('kanban/index.html', task_records=task_records)
    pass



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
            kanban_repository.add_new_record(project_title)
            return redirect(url_for('projects.index'))

    return render_template('kanban/register.html')


@bp.route('/edit', methods=('GET', 'POST'))
@login_required
def edit():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        action = request.form['action']
        
        error = None

        if not first_name:
            error = 'First name is required.'

        if error is not None:
            flash(error)
        else:
            # if action == 'Delete':
            #     kanban_repository.delete_record(id)
            # else:
            kanban_repository.update_record(g.user['id'], first_name, last_name)
            return redirect(url_for('kanban.index'))
    record = kanban_repository.get_record_by_user_id(g.user['id'])
    return render_template('kanban/edit.html', record=record)

