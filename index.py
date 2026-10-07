"""Flask WSGI entrypoint discovered by Vercel."""

from app import create_app
from app.db import init_db

app = create_app()

with app.app_context():
    init_db()
