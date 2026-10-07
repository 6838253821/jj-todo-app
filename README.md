# Todo

Flask and SQLite task app with registration, username/password login, and private
 task lists. Passwords use Werkzeug scrypt hashes. Forms require CSRF tokens;
parameterized SQL and owner checks protect task reads and mutations.

## Run locally

Requires Python 3.12 or later. From the repository directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m flask --app app init-db
.venv/bin/python -m flask --app app run --host 127.0.0.1 --port 5000
```

Create an account in the app. Passwords must contain 8–128 characters and usernames
1–50 characters. Usernames are case-sensitive. Task titles allow 1–200 characters.

The database is `instance/todo.sqlite`. Initialization creates missing tables
without deleting data. A random session signing key is retained in
`instance/secret_key` with owner-only permissions; alternatively set
`TODO_SECRET_KEY`. Never commit keys or databases.

## Tests

```sh
.venv/bin/python -m pytest -q
```

Tests use temporary databases and real CSRF-protected forms. They cover password
hashing, login/logout, validation, task actions, HTML escaping, and user isolation.

The Flask server is for local development. No deployment is configured. Public
hosting would require HTTPS, secure cookies, a production WSGI server, login rate
limiting, and database backups.
