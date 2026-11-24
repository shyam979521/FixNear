# migrations/

Reserved for Flask-Migrate (Alembic) migration scripts.

This project currently uses `db.create_all()` at startup, which safely
creates any missing tables without touching ones that already exist —
sufficient for the current stage of the project.

Once the schema needs a real migration (e.g. renaming a column, changing
a type), run:

```bash
flask db init      # one-time setup, creates the alembic env in this folder
flask db migrate -m "describe the change"
flask db upgrade
```
