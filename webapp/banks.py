from logging import getLogger
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('banks', __name__, url_prefix='/banks')

##############################
# REPOSITORY

class BankRepository:
    """Bank repository"""
    page_size = 10
    log = getLogger(__name__)

    def get_paged_records(self,page_number):
        offset = (page_number - 1) * self.page_size
        db = get_db()
        records = db.execute("""
SELECT id, title FROM bank
ORDER BY title ASC
LIMIT ? OFFSET ?;
""", (self.page_size, offset)).fetchall()
        total_record_count = db.execute("""SELECT COUNT(id) count FROM bank;""").fetchone()['count']
        return (records, total_record_count)
        
    def get_record(self, id):
        db = get_db()
        record = db.execute("""
SELECT id, title FROM bank WHERE id = ?;
""", (id,)).fetchone()
        return record

    def add_new_record(self, banks_title):
        db = get_db()
        db.execute('INSERT INTO bank (title) VALUES (?);',
            (banks_title,)
        )
        db.commit()

    def update_record(self, id, banks_title):
        db = get_db()
        db.execute('UPDATE bank SET title = ? WHERE id = ?;',
            (banks_title, id)
        )
        db.commit()

    def delete_record(self, id):
        db = get_db()
        db.execute('DELETE FROM bank WHERE id = ?;',
            (id,)
        )
        db.commit()

##############################
# ROUTES

bank_repository = BankRepository()

@bp.route('/')
@bp.route('/<int:page_number>')
def index(page_number=1):
    (records, total_record_count) = bank_repository.get_paged_records(page_number)
    return render_template('banks/index.html', 
        records=records,
        total_record_count=total_record_count,
        page_number=page_number)


@bp.route('/register', methods=('GET', 'POST'))
@login_required
def register():
    if request.method == 'POST':
        bank_title = request.form['bank_title']
        #role_description = request.form['role_description']
        error = None

        if not bank_title:
            error = 'Bank title is required.'

        if error is not None:
            flash(error)
        else:
            bank_repository.add_new_record(bank_title)
            return redirect(url_for('banks.index'))

    return render_template('banks/register.html')


@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    if request.method == 'POST':
        bank_title = request.form['bank_title']
        action = request.form['action']
        #role_description = request.form['role_description']
        error = None

        if not bank_title:
            error = 'Bank title is required.'

        if error is not None:
            flash(error)
        else:
            if action == 'Delete':
                bank_repository.delete_record(id)
            else:
                bank_repository.update_record(id, bank_title)
            return redirect(url_for('banks.index'))
    record = bank_repository.get_record(id)
    return render_template('banks/edit.html', record=record)

