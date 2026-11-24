"""
Backward-compatible entry point.

The project was refactored in Phase 6 into a proper `app/` package
(models/routes/services/utils — see README.md). This file exists purely
so the old habit of running `python app.py` still works exactly as
before; `run.py` is the new "official" entry point going forward.
"""

from run import app

if __name__ == "__main__":
    app.run(debug=True)
