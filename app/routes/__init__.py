"""
Registers every route module against the Flask app. Called once from
the application factory (`app/__init__.py`).
"""

from app.routes.main_routes import register_main_routes
from app.routes.auth_routes import register_auth_routes
from app.routes.profile_routes import register_profile_routes
from app.routes.job_routes import register_job_routes
from app.routes.dashboard_routes import register_dashboard_routes
from app.routes.marketplace_routes import register_marketplace_routes


def register_all_routes(app):
    register_main_routes(app)
    register_auth_routes(app)
    register_profile_routes(app)
    register_job_routes(app)
    register_dashboard_routes(app)
    register_marketplace_routes(app)
