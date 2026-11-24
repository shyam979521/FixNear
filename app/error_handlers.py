"""
Centralized error handling — custom pages for 404/403/500, plus a 413
handler for oversized file uploads. Every unhandled exception is logged
before showing the generic 500 page (never leaking a stack trace to
visitors).
"""

import logging
from flask import render_template, flash, redirect, url_for
from app.extensions import db

logger = logging.getLogger(__name__)


def register_error_handlers(app):

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(413)
    def payload_too_large(error):
        flash("That file is too large — please upload an image under 5MB.", "error")
        return redirect(url_for("home"))

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.exception("Unhandled server error")
        return render_template("errors/500.html"), 500
