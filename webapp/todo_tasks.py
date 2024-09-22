import json
from logging import getLogger
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from flask_cors import cross_origin
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('todo-tasks', __name__, url_prefix='/todo-tasks')

##############################
# REPOSITORY

class TodoTaskRepository:
    """TodoTask repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_tasks_by_user_id(self, user_id):
        db = get_db()
        records = db.execute("""
SELECT t.id, t.title, t.description, t.status, t.priority
FROM task t
WHERE t.user_id = ?
ORDER BY t.status, t.priority, t.title;
""", (user_id,)).fetchall()
        return records
    
    def add_new_record(self, task_title, task_description, user_id):
        db = get_db()
        db.execute("""INSERT INTO task (title, description, status, user_id) VALUES (?, ?, ?, ?);""",
            (task_title, task_description, 'NEW', user_id)
        )
        db.commit()

    def get_paged_records(self,page_number):
        offset = (page_number - 1) * self.page_size
        print(offset)
        db = get_db()
        records = db.execute("""
SELECT i.id, i.update_ts, i.title, ty.title issue_type, st.title issue_status, pr.title issue_priority
FROM task i
JOIN issue_type ty ON i.type_id = ty.id
JOIN issue_status st ON i.status_id = st.id
JOIN issue_priority pr ON i.priority_id = pr.id
ORDER BY (pr.weight * st.weight * ty.weight) DESC, i.title ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(i.id) count FROM task i
JOIN issue_type ty ON i.type_id = ty.id
JOIN issue_status st ON i.status_id = st.id""").fetchone()['count']
        return (records, total_record_count)
        
        
    def get_issue(self, id):
        db = get_db()
        record = db.execute("""
SELECT i.id, i.update_ts, i.title, i.description, i.type_id, i.status_id, i.priority_id
FROM task i
WHERE i.id = ?;
""", (id,)).fetchone()
        return record

    def get_issue_types(self):
        db = get_db()
        records = db.execute("""SELECT id, title FROM task_type;""").fetchall()
        return records
        
    def get_issue_statuses(self):
        db = get_db()
        records = db.execute("""SELECT id, title FROM task_status;""").fetchall()
        return records
    
    def get_issue_priorities(self):
        db = get_db()
        records = db.execute("""SELECT id, title FROM task_priority ORDER BY weight DESC;""").fetchall()
        return records
        
        
    def add_issue(self, type_id, priority_id, title, description, user_id):
        db = get_db()
        issue_status_id = 1
        db.execute("""INSERT INTO issue (type_id, priority_id, title, description, status_id, user_id) VALUES (?, ?, ?, ?, ?, ?);""",
            (type_id, priority_id, title, description, issue_status_id, user_id)
        )
        db.commit()
        
    def update_issue(self, issue_type_id, issue_title, issue_description, issue_status_id, issue_priority_id, id):
        db = get_db()
        db.execute("""UPDATE issue SET type_id = ?, title = ?, description = ?, status_id = ?, priority_id = ?, update_ts = CURRENT_TIMESTAMP WHERE id = ?;""",
            (issue_type_id, issue_title, issue_description, issue_status_id, issue_priority_id, id)
        )
        db.commit()
        
    def delete_user_blog_post(self, user_id, id):
        db = get_db()
        record = db.execute("""DELETE blog_post WHERE user_id = ? AND id = ?';""", (user_id, id)).fetchone()
        return record    
    
    
    def seed(self, item_count=16):
        db = get_db()
        for i in range (1, item_count + 1):
            username = f"testuser{i:03d}"
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, generate_password_hash(username)),
            )
        db.commit()
        
    # MAIN

    def get_all(self, wildcard_query, page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT  id, description, is_completed, priority 
FROM    todo_task  
WHERE   description LIKE ?
ORDER BY priority;
""", (wildcard_query,)).fetchall()
        print(wildcard_query)
#         records = db.execute("""
# SELECT  id, description is_completed, priority 
# FROM    todo_task  
# ORDER BY priority;
# """, (wildcard_query, self.page_size, offset)).fetchall()
#         total_record_count = db.execute("""SELECT COUNT(i.id) count FROM task i
# JOIN issue_type ty ON i.type_id = ty.id
# JOIN issue_status st ON i.status_id = st.id
# JOIN issue_priority pr ON i.priority_id = pr.id
# WHERE i.title LIKE ?""", (wildcard_query,)).fetchone()['count']
        print(len(records))
        return (records)


    def add_new_record(self, task_description):
        db = get_db()
        db.execute("""INSERT INTO todo_task (description) VALUES (?);""",
            (task_description,)
        )
        db.commit()

    def delete_record(self, id):
        db = get_db()
        db.execute("""DELETE FROM todo_task WHERE id = ?;""",
            (id,)
        )
        db.commit()

    def update_record(self, description, is_completed, priority, id):
        db = get_db()
        db.execute("""
UPDATE 	todo_task
SET		description     = ?
		, is_completed  = ?
		, priority      = ?
WHERE 	id = ?;""",
            (description, is_completed, priority, id)
        )
        db.commit()


##############################
# ROUTES
from webapp import serializer
todo_task_repository = TodoTaskRepository()

# WEB API ROUTES

@bp.route('/api/todo-task', methods=['GET'])
@cross_origin()
def api_list():
    query = request.args.get('filter')
    page = 1 if request.args.get('page') is None else int(request.args.get('page'))
    # print(f"api search for {query} on page {page}")
    # (records, total_record_count) = todo_task_repository.search(f"%{query}%", page)
    (records) = todo_task_repository.get_all(f"%{query}%", page)
    response = {
        'records': [dict(record) for record in records],
        # 'total_record_count': total_record_count,
        # 'page': page
    }
    #print([dict(record) for record in records])
    print(json.dumps([dict(record) for record in records], default=serializer))
    return json.dumps([dict(record) for record in records], default=serializer)

@bp.route('/api/todo-task', methods=['POST'])
@cross_origin()
def api_add():
    if request.is_json:
        request_json = request.json
        todo_task_repository.add_new_record(request_json['description'])
        return "OK"
    #if request.method == 'POST':
    #    card_quantity = int(request.form['card_quantity'])
    #    tool_repository.seed(card_quantity)
    # query = request.args.get('query')
    # page = 1 if request.args.get('page') is None else int(request.args.get('page'))
    # # print(f"api search for {query} on page {page}")
    # # (records, total_record_count) = todo_task_repository.search(f"%{query}%", page)
    # (records) = todo_task_repository.get_all(f"%{query}%", page)
    # response = {
    #     'records': [dict(record) for record in records],
    #     # 'total_record_count': total_record_count,
    #     # 'page': page
    # }
    # return json.dumps([dict(record) for record in records], default=serializer)
    return abort(400, 'Bad request') 

@bp.route('/api/todo-task/<int:id>', methods=['PUT'])
@cross_origin()
def api_put_todo_task(id=None):
    if id is not None and request.is_json:
        request_json = request.json
        print(request_json)
        # import pdb
        # pdb.set_trace()
        todo_task_repository.update_record(request_json['description'], request_json['is_completed'], request_json['priority'], request_json['id'])
        return "OK"

    # if request.is_json:
    #     request_json = request.json
    #     todo_task_repository.add_new_record(request_json['description'])
    #     return "OK"
    #if request.method == 'POST':
    #    card_quantity = int(request.form['card_quantity'])
    #    tool_repository.seed(card_quantity)
    # query = request.args.get('query')
    # page = 1 if request.args.get('page') is None else int(request.args.get('page'))
    # # print(f"api search for {query} on page {page}")
    # # (records, total_record_count) = todo_task_repository.search(f"%{query}%", page)
    # (records) = todo_task_repository.get_all(f"%{query}%", page)
    # response = {
    #     'records': [dict(record) for record in records],
    #     # 'total_record_count': total_record_count,
    #     # 'page': page
    # }
    # return json.dumps([dict(record) for record in records], default=serializer)
    return abort(400, 'Bad request') 
    

@bp.route('/api/todo-task/<int:id>', methods=['DELETE'])
@cross_origin()
def api_delete_todo_task(id=None):
    if id is not None:
        todo_task_repository.delete_record(id)
        return "OK"

    # if request.is_json:
    #     request_json = request.json
    #     todo_task_repository.add_new_record(request_json['description'])
    #     return "OK"
    #if request.method == 'POST':
    #    card_quantity = int(request.form['card_quantity'])
    #    tool_repository.seed(card_quantity)
    # query = request.args.get('query')
    # page = 1 if request.args.get('page') is None else int(request.args.get('page'))
    # # print(f"api search for {query} on page {page}")
    # # (records, total_record_count) = todo_task_repository.search(f"%{query}%", page)
    # (records) = todo_task_repository.get_all(f"%{query}%", page)
    # response = {
    #     'records': [dict(record) for record in records],
    #     # 'total_record_count': total_record_count,
    #     # 'page': page
    # }
    # return json.dumps([dict(record) for record in records], default=serializer)
    return abort(400, 'Bad request') 
    

# @bp.route('/api/search')
# def api_search():
#     query = request.args.get('query')
#     page = 1 if request.args.get('page') is None else int(request.args.get('page'))
#     print(f"api search for {query} on page {page}")
#     (records, total_record_count) = todo_task_repository.search(f"%{query}%", page)
#     response = {
#         'total_record_count': total_record_count,
#         'records': [dict(record) for record in records],
#         'page': page
#     }
#     return json.dumps(response, default=serializer)
#     #return jsonify([dict(record) for record in records])
    
