import sqlite3

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    app.config["DATABASE_PATH"].parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_url TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'queued',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                summary TEXT,
                findings TEXT,
                risk_score INTEGER DEFAULT 0,
                metadata TEXT
            )
            """
        )
        db.commit()

    app.teardown_appcontext(close_db)
