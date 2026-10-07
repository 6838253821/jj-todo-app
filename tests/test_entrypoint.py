import importlib
import sys

import pytest

from app import create_app
from app.db import get_db
from conftest import login, post, register


def test_vercel_entrypoint(monkeypatch, tmp_path):
    monkeypatch.setenv('VERCEL', '1')
    monkeypatch.setenv('TODO_SECRET_KEY', 'test-deployment-secret')
    monkeypatch.setattr('app.tempfile.gettempdir', lambda: str(tmp_path))
    sys.modules.pop('index', None)
    module = importlib.import_module('index')
    try:
        app = module.app
        assert app.instance_path == str(tmp_path / 'jj-todo-app')
        assert app.config['SESSION_COOKIE_SECURE'] is True
        client = app.test_client()
        assert client.get('/login', base_url='https://localhost').status_code == 200
        assert client.get('/static/style.css').status_code == 200
        assert register(client).status_code == 302
        assert login(client).status_code == 302
        assert post(client, '/tasks', {'title': 'Deployment task'}).status_code == 302
        assert 'Deployment task' in client.get('/tasks').text
        with app.app_context():
            assert get_db().execute('SELECT count(*) FROM tasks').fetchone()[0] == 1
        # A new application instance keeps the stable signing key and existing data.
        reloaded = importlib.reload(module)
        with reloaded.app.app_context():
            assert get_db().execute('SELECT count(*) FROM tasks').fetchone()[0] == 1
        assert reloaded.app.config['SECRET_KEY'] == 'test-deployment-secret'
    finally:
        sys.modules.pop('index', None)


def test_vercel_requires_stable_secret(monkeypatch):
    monkeypatch.setenv('VERCEL', '1')
    monkeypatch.delenv('TODO_SECRET_KEY', raising=False)
    with pytest.raises(RuntimeError, match='TODO_SECRET_KEY'):
        create_app()
