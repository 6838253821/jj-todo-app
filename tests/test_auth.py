import pytest
from werkzeug.security import check_password_hash
from app.db import get_db, init_db
from conftest import login, post, register

def test_registration_login_logout(app, client):
    assert register(client).status_code == 302
    with app.app_context():
        user = get_db().execute('SELECT * FROM users').fetchone()
        assert user['password_hash'] != 'password123'
        assert user['password_hash'].startswith('scrypt:')
        assert check_password_hash(user['password_hash'], 'password123')
        init_db()
        assert get_db().execute('SELECT count(*) FROM users').fetchone()[0] == 1
    assert login(client).status_code == 302
    with client.session_transaction() as session:
        assert session['user_id'] == user['id']
    assert client.get('/tasks').status_code == 200
    assert post(client, '/logout').status_code == 302
    with client.session_transaction() as session:
        assert 'user_id' not in session
    assert client.get('/tasks').status_code == 302

@pytest.mark.parametrize('username,password', [('alice', 'wrong'), ('missing', 'password123'), ("' OR 1=1 --", 'password123')])
def test_invalid_login(client, username, password):
    register(client)
    assert login(client, username, password).status_code == 401
    with client.session_transaction() as session:
        assert 'user_id' not in session

def test_registration_validation(client):
    assert post(client, '/register', {'username': ' ', 'password': 'password123'}).status_code == 400
    assert post(client, '/register', {'username': 'alice', 'password': 'short'}).status_code == 400
    assert register(client).status_code == 302
    assert register(client).status_code == 400

@pytest.mark.parametrize('path', ['/register', '/login', '/logout', '/tasks', '/tasks/1/complete', '/tasks/1/delete'])
def test_csrf_required(client, path):
    assert client.post(path, data={'username': 'alice', 'password': 'password123', 'title': 'Task'}).status_code == 400
