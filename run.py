"""
Entry point for running the app locally:

    python run.py

For production, use a real WSGI server instead, e.g.:

    gunicorn "run:app"
"""

import os
from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True))
