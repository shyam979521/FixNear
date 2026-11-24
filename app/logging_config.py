"""
Structured logging — writes to a rotating log file under logs/, and also
to the console in development so `flask run` output stays readable.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

_LOGGING_CONFIGURED = False


def configure_logging(app):
    global _LOGGING_CONFIGURED

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if not app.debug else logging.DEBUG)

    if _LOGGING_CONFIGURED:
        # create_app() can legitimately run more than once in the same
        # process (e.g. a test suite building a fresh app per test, or
        # per-test TestingConfig instances). Without this guard, every
        # extra call attached another RotatingFileHandler to the shared
        # root logger, so a single log line would be written N times and
        # duplicate handlers would accumulate for the life of the process.
        app.logger.debug("Logging already configured for this process — skipping re-attach.")
        return

    os.makedirs(app.config["LOG_DIR"], exist_ok=True)

    file_handler = RotatingFileHandler(
        app.config["LOG_FILE"], maxBytes=1_000_000, backupCount=3
    )
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    root_logger.addHandler(file_handler)
    _LOGGING_CONFIGURED = True

    app.logger.info("Logging configured — writing to %s", app.config["LOG_FILE"])
