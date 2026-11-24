"""
Application factory.

`templates/` and `static/` are kept at the project root (sibling to this
`app/` package) rather than nested inside it, so none of the existing
template files needed to move — only their absolute path is configured
here.
"""

import os
from flask import Flask
from flask_login import current_user

from app.config import config_by_name
from app.extensions import db, login_manager, csrf
from app.logging_config import configure_logging
from app.error_handlers import register_error_handlers
from app.utils.helpers import is_urgent_date, duration_estimate_for

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app(env=None):
    env = env or os.environ.get("FLASK_ENV", "development")

    app = Flask(
        __name__,
        template_folder=os.path.join(PROJECT_ROOT, "templates"),
        static_folder=os.path.join(PROJECT_ROOT, "static"),
        instance_path=os.path.join(PROJECT_ROOT, "instance"),
    )
    app.config.from_object(config_by_name.get(env, config_by_name["default"]))
    _validate_production_secret_key(app, env)

    _init_extensions(app)
    _register_jinja_globals(app)
    _register_context_processors(app)

    configure_logging(app)
    register_error_handlers(app)
    _register_security_headers(app)

    from app.routes import register_all_routes
    register_all_routes(app)

    with app.app_context():
        db.create_all()
        from app.seed import seed_database
        seed_database()

    return app


def _register_security_headers(app):
    """
    SECURITY: verified before this fix that the app sent zero hardening
    headers at all (checked actual response headers directly). This adds
    the standard set that's safe to add without breaking anything.

    The CSP intentionally still allows 'unsafe-inline' for script-src and
    style-src — the templates use ~160 inline `style="..."` attributes and
    one inline `<script>` block, so a strict CSP would break real pages
    today. Even with 'unsafe-inline', this CSP still blocks the more
    dangerous gaps: loading scripts/images/fonts from arbitrary untrusted
    domains, <object>/<embed> plugins, base-tag hijacking, and framing by
    other sites. Tightening this further (nonces + moving inline styles to
    real CSS classes) is a good future follow-up, not a quick safe fix.
    """
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'self';"
        )
        if app.config.get("SESSION_COOKIE_SECURE"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


def _validate_production_secret_key(app, env):
    """
    Fails loudly at startup rather than silently running an insecure
    production deployment — much better than discovering this after a
    security incident.
    """
    if env == "production" and app.config["SECRET_KEY"] in (None, "", "dev-insecure-secret-key-change-me"):
        raise RuntimeError(
            "SECRET_KEY environment variable must be set to a real random value "
            "in production. Generate one with:\n"
            '  python -c "import secrets; print(secrets.token_hex(32))"'
        )


def _init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import flash, redirect, url_for
        flash("Please log in to continue.", "error")
        return redirect(url_for("login"))


def _register_jinja_globals(app):
    app.jinja_env.globals["is_urgent_date"] = is_urgent_date
    app.jinja_env.globals["duration_estimate_for"] = duration_estimate_for


def _register_context_processors(app):
    @app.context_processor
    def inject_current_user():
        # Preserves the exact template variable name used throughout every
        # existing template (`{% if logged_in_user %}`), so nothing there
        # needed to change when auth moved to Flask-Login.
        return {"logged_in_user": current_user if current_user.is_authenticated else None}
