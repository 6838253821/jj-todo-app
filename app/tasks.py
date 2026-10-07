from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from .auth import login_required
from .db import get_db

bp = Blueprint('tasks', __name__)


@bp.get('/')
def home():
    return redirect(url_for('tasks.index'))


@bp.get('/tasks')
@login_required
def index():
    tasks = get_db().execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY completed, id DESC',
                             (g.user['id'],)).fetchall()
    return render_template('tasks.html', tasks=tasks)


@bp.post('/tasks')
@login_required
def add():
    title = request.form.get('title', '').strip()
    if not 1 <= len(title) <= 200:
        flash('Enter a task of 1–200 characters.', 'error')
        return index(), 400
    db = get_db()
    db.execute('INSERT INTO tasks (user_id, title) VALUES (?, ?)', (g.user['id'], title))
    db.commit()
    return redirect(url_for('tasks.index'))


def change_task(task_id, delete=False):
    db = get_db()
    if delete:
        result = db.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, g.user['id']))
    else:
        result = db.execute('UPDATE tasks SET completed = 1 WHERE id = ? AND user_id = ?', (task_id, g.user['id']))
    if result.rowcount == 0:
        abort(404)
    db.commit()
    return redirect(url_for('tasks.index'))


@bp.post('/tasks/<int:task_id>/complete')
@login_required
def complete(task_id):
    return change_task(task_id)


@bp.post('/tasks/<int:task_id>/delete')
@login_required
def delete(task_id):
    return change_task(task_id, delete=True)
