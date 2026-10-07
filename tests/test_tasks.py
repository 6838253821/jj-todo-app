import pytest
from app.db import get_db
from conftest import login, post, register

def test_task_lifecycle(app, client):
    register(client)
    login(client)
    assert 'Add your first task' in client.get('/tasks').text
    assert post(client, '/tasks', {'title': ' Buy groceries '}).status_code == 302
    with app.app_context():
        task = get_db().execute('SELECT * FROM tasks').fetchone()
        assert task['title'] == 'Buy groceries'
        assert task['completed'] == 0
    assert 'Buy groceries' in client.get('/tasks').text
    assert post(client, f"/tasks/{task['id']}/complete").status_code == 302
    assert 'Completed' in client.get('/tasks').text
    with app.app_context():
        assert get_db().execute('SELECT completed FROM tasks').fetchone()[0] == 1
    assert post(client, f"/tasks/{task['id']}/delete").status_code == 302
    assert 'Buy groceries' not in client.get('/tasks').text
    with app.app_context():
        assert get_db().execute('SELECT count(*) FROM tasks').fetchone()[0] == 0

def test_user_isolation(app, client):
    register(client)
    login(client)
    post(client, '/tasks', {'title': 'Alice private task'})
    with app.app_context():
        task = dict(get_db().execute('SELECT * FROM tasks').fetchone())
    other = app.test_client()
    register(other, 'bob')
    login(other, 'bob')
    post(other, '/tasks', {'title': 'Bob private task', 'user_id': task['user_id']})
    assert 'Alice private task' not in other.get('/tasks').text
    assert 'Bob private task' not in client.get('/tasks').text
    for action in ('complete', 'delete'):
        assert post(other, f"/tasks/{task['id']}/{action}").status_code == 404
        assert post(other, f'/tasks/99999/{action}').status_code == 404
    with app.app_context():
        assert dict(get_db().execute('SELECT * FROM tasks WHERE id = ?', (task['id'],)).fetchone()) == task
        assert get_db().execute('SELECT user_id FROM tasks WHERE title = ?', ('Bob private task',)).fetchone()[0] != task['user_id']

@pytest.mark.parametrize('path', ['/tasks', '/tasks/1/complete', '/tasks/1/delete'])
def test_actions_require_login(client, path):
    response = post(client, path, {'title': 'No access'})
    assert response.status_code == 302
    assert response.location.endswith('/login')

@pytest.mark.parametrize('title', ['', '   ', 'x' * 201])
def test_invalid_title(app, client, title):
    register(client)
    login(client)
    assert post(client, '/tasks', {'title': title}).status_code == 400
    with app.app_context():
        assert get_db().execute('SELECT count(*) FROM tasks').fetchone()[0] == 0

def test_html_escaping(client):
    register(client)
    login(client)
    post(client, '/tasks', {'title': '<script>alert(1)</script>'})
    response = client.get('/tasks')
    assert '<script>alert(1)</script>' not in response.text
    assert '&lt;script&gt;' in response.text
