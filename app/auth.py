import functools
import sqlite3

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint('auth', __name__)


@bp.before_app_request
def load_user():
    user_id = session.get('user_id')
    g.user = get_db().execute('SELECT id, username FROM users WHERE id = ?', (user_id,)).fetchone() if user_id else None


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not 1 <= len(username) <= 50 or not 8 <= len(password) <= 128:
            flash('Use a username of 1–50 characters and a password of 8–128 characters.', 'error')
            return render_template('register.html'), 400
        try:
            db = get_db()
            db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                       (username, generate_password_hash(password)))
            db.commit()
        except sqlite3.IntegrityError:
            flash('That username is already taken.', 'error')
            return render_template('register.html'), 400
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = get_db().execute('SELECT * FROM users WHERE username = ?',
                                (request.form.get('username', '').strip(),)).fetchone()
        password = request.form.get('password', '')
        if user is None or len(password) > 128 or not check_password_hash(user['password_hash'], password):
            flash('Invalid username or password.', 'error')
            return render_template('login.html'), 401
        session.clear()
        session['user_id'] = user['id']
        return redirect(url_for('tasks.index'))
    return render_template('login.html')


@bp.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
