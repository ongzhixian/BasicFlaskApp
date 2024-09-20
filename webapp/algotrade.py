from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('algotrade', __name__, url_prefix='/algotrade')

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form['action']
        error = None

        if not action:
            error = 'Action is required.'

        if error is not None:
            flash(error)
        else:
            print(f'Do {action}')
            pass
            # db = get_db()
            # db.execute(
            #     'INSERT INTO post (title, body, author_id)'
            #     ' VALUES (?, ?, ?)',
            #     (title, body, g.user['id'])
            # )
            # db.commit()
            # return redirect(url_for('blog.index'))

    return render_template('algotrade/index.html')


@bp.route('/trade-oanda.html', methods=['GET', 'POST'])
def trade_oanda():
    return render_template('algotrade/trade-oanda.html')

@bp.route('/market-oanda.html', methods=['GET', 'POST'])
def market_oanda():
    return render_template('algotrade/market-oanda.html')



# CHART PAGES

@bp.route('/sample-ohlc/chartjs.html', methods=['GET', 'POST'])
def sample_ohlc_chartjs():
    return render_template('algotrade/sample-ohlc-chartjs.html')

@bp.route('/sample-ohlc/techanjs.html', methods=['GET', 'POST'])
def sample_ohlc_techanjs():
    return render_template('algotrade/sample-ohlc-techanjs.html')

@bp.route('/sample-ohlc/amcharts.html', methods=['GET', 'POST'])
def sample_ohlc_amcharts():
    return render_template('algotrade/sample-ohlc-amcharts.html')

@bp.route('/sample-ohlc/highcharts.html', methods=['GET', 'POST'])
def sample_ohlc_highcharts():
    return render_template('algotrade/sample-ohlc-highcharts.html')

@bp.route('/sample-ohlc/anycharts.html', methods=['GET', 'POST'])
def sample_ohlc_anycharts():
    return render_template('algotrade/sample-ohlc-anycharts.html')

@bp.route('/sample-ohlc/plotly.html', methods=['GET', 'POST'])
def sample_ohlc_plotly():
    return render_template('algotrade/sample-ohlc-plotly.html')


# @bp.route('/create', methods=('GET', 'POST'))
# @login_required
# def create():
#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'INSERT INTO post (title, body, author_id)'
#                 ' VALUES (?, ?, ?)',
#                 (title, body, g.user['id'])
#             )
#             db.commit()
#             return redirect(url_for('blog.index'))

#     return render_template('blog/create.html')


# def get_post(id, check_author=True):
#     post = get_db().execute(
#         'SELECT p.id, title, body, created, author_id, username'
#         ' FROM post p JOIN user u ON p.author_id = u.id'
#         ' WHERE p.id = ?',
#         (id,)
#     ).fetchone()

#     if post is None:
#         abort(404, f"Post id {id} doesn't exist.")

#     if check_author and post['author_id'] != g.user['id']:
#         abort(403)

#     return post

# @bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def update(id):
#     post = get_post(id)

#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'UPDATE post SET title = ?, body = ?'
#                 ' WHERE id = ?',
#                 (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for('blog.index'))

#     return render_template('blog/update.html', post=post)

# @bp.route('/<int:id>/delete', methods=('POST',))
# @login_required
# def delete(id):
#     get_post(id)
#     db = get_db()
#     db.execute('DELETE FROM post WHERE id = ?', (id,))
#     db.commit()
#     return redirect(url_for('blog.index'))

