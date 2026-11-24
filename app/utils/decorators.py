"""
Route-protection decorators.

`login_required` (from flask_login) already covers "must be logged in".
`role_required` layers role-based authorization on top of that, and
`admin_required` is a convenience shortcut for the most common case.
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*allowed_roles):
    """
    Restricts a view to specific user roles. Redirects to login if the
    visitor isn't authenticated at all, or aborts with 403 if they're
    logged in as the wrong role (handled by the 403 error page).
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to continue.", "error")
                return redirect(url_for("login"))
            if current_user.role not in allowed_roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


def admin_required(view_func):
    return role_required("admin")(view_func)


def worker_required(view_func):
    return role_required("worker")(view_func)


def customer_required(view_func):
    return role_required("customer")(view_func)
