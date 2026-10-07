import os
import secrets
import tempfile
from pathlib import Path

from flask import Flask
from flask_wtf.csrf import CSRFProtect


def create_app(test_config=None):
    vercel = os.environ.get('VERCEL') == '1'
    instance_path = str(Path(tempfile.gettempdir()) / 'jj-todo-app') if vercel else None
    app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    secret = os.environ.get('TODO_SECRET_KEY')
    if vercel and not secret:
        raise RuntimeError('Set TODO_SECRET_KEY in Vercel environment variables before deploying.')
    if not secret:
        secret_path = Path(app.instance_path) / 'secret_key'
        try:
            with open(secret_path, 'x', opener=lambda path, flags: os.open(path, flags, 0o600)) as file:
                file.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        secret = secret_path.read_text().strip()
    app.config.from_mapping(
        SECRET_KEY=secret,
        DATABASE=str(Path(app.instance_path) / 'todo.sqlite'),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=vercel,
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    CSRFProtect(app)
    from . import auth, db, tasks
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(tasks.bp)
    return app
