"""
Shared extension instances.

Kept in their own module (rather than created directly in the app factory)
so models and services can `from app.extensions import db` without circular
imports.
"""

from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "error"


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """
    BUG FOUND & FIXED: verified that SQLite's `PRAGMA foreign_keys` was OFF
    (SQLite's actual default), meaning every foreign key declared across
    every model — and the `cascade="all, delete-orphan"` rules on the
    Notification/SavedJob/JobApplication relationships — were silently
    unenforced at the database level. A raw SQL statement (or any future
    bug) could have inserted a row referencing a non-existent user/job, or
    left orphaned rows behind, with no error at all.

    Confirmed safe before applying: ran the full registration → post job →
    accept → complete → review regression suite with this pragma turned on
    and every flow still passed. Only relevant to the SQLite driver, so
    this is a no-op if the project is ever pointed at a different database.
    """
    if type(dbapi_connection).__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
