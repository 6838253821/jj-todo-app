import re
import pytest
from app import create_app
from app.db import init_db

@pytest.fixture
def app(tmp_path):
    app = create_app({'TESTING': True, 'SECRET_KEY': 'test-only', 'DATABASE': str(tmp_path / 'test.sqlite')})
    with app.app_context():
        init_db()
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def post(client, path, data=None):
    token = re.search(r'name="csrf_token" value="([^"]+)"', client.get('/login').text).group(1)
    return client.post(path, data={**(data or {}), 'csrf_token': token})

def register(client, username='alice'):
    return post(client, '/register', {'username': username, 'password': 'password123'})

def login(client, username='alice', password='password123'):
    return post(client, '/login', {'username': username, 'password': password})
