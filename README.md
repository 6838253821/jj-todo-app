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

## Vercel

The root `index.py` exports the Flask `app` for Vercel's Flask framework detection
and initializes missing database tables without deleting existing data. Select
the Flask framework preset and use this repository root as the project root.
No custom build or output directory is needed.

Before deployment, set `TODO_SECRET_KEY` to a securely generated random value in
Vercel's environment settings. Generate it with
`python3 -c 'import secrets; print(secrets.token_hex(32))'`. Keep it secret and
stable across instances. Vercel sessions use HTTPS-only cookies.

**SQLite on Vercel is demo-only.** When `VERCEL=1`, the app stores its database in
the writable temporary directory (`/tmp/jj-todo-app`), because deployed source
files are read-only. Temporary storage is not durable or shared across function
instances: users and tasks may disappear on cold starts or redeploys, and different
instances can have different data. For reliable accounts and task persistence,
host this SQLite app on a server with a persistent disk, or separately migrate
to a shared database suitable for Vercel. Local storage remains in `instance/`.

The local Flask server is for development. Public hosting also needs login rate
limiting and a database backup strategy. Adding this entrypoint does not deploy
the app.
