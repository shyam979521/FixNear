"""
Authentication routes: register, login, logout, admin login, forgot
password. Session management and "remember me" are handled by
Flask-Login instead of hand-rolled session keys.
"""

import logging
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.services import auth_service
from app.services.upload_service import save_uploaded_file

logger = logging.getLogger(__name__)


def _dashboard_redirect_for(user):
    if user.role == "admin":
        return redirect(url_for("admin"))
    if user.role == "worker":
        return redirect(url_for("worker_dashboard"))
    return redirect(url_for("customer_dashboard"))


def register_auth_routes(app):

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            role = request.form.get("role", "customer")
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            profile_fields = {
                "location": request.form.get("location", "").strip(),
                "bio": request.form.get("bio", "").strip(),
                "service_category": request.form.get("service_category", "").strip(),
                "experience": request.form.get("experience", "").strip(),
                "service_area": request.form.get("service_area", "").strip(),
                "availability": request.form.get("availability", "").strip(),
            }

            user, errors = auth_service.register_user(
                role, full_name, email, phone, password, confirm_password, **profile_fields
            )

            if errors:
                for e in errors:
                    flash(e, "error")
                return render_template("register.html", form_data=request.form)

            if role == "worker":
                photo = save_uploaded_file(request.files.get("profile_photo_worker"), uploaded_by=user.id)
            else:
                photo = save_uploaded_file(request.files.get("profile_photo"), uploaded_by=user.id)
            if photo:
                user.profile_photo = photo
                db.session.commit()

            login_user(user)
            logger.info("New user registered: %s (%s)", user.email, user.role)
            flash("Welcome to FixNear! Your account has been created.", "success")
            return _dashboard_redirect_for(user)

        return render_template("register.html", form_data={})

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            remember = bool(request.form.get("remember"))

            user = auth_service.authenticate(email, password)
            if user:
                login_user(user, remember=remember)
                logger.info("User logged in: %s", user.email)
                flash(f"Welcome back, {user.full_name}!", "success")
                return _dashboard_redirect_for(user)

            logger.warning("Failed login attempt for email: %s", email)
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        return render_template("login.html")

    @app.route("/admin-login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            user = auth_service.authenticate(email, password)
            if user and user.role == "admin":
                login_user(user)
                logger.info("Admin logged in: %s", user.email)
                flash("Admin access granted.", "success")
                return redirect(url_for("admin"))

            logger.warning("Failed admin login attempt for email: %s", email)
            flash("Invalid admin credentials.", "error")
            return render_template("admin_login.html")

        return render_template("admin_login.html")

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        submitted = False
        if request.method == "POST":
            # No email delivery wired up yet — this always shows the same
            # "check your email" confirmation regardless of whether the
            # address exists, to avoid leaking which emails are registered.
            submitted = True
        return render_template("forgot_password.html", submitted=submitted)

    @app.route("/logout")
    @login_required
    def logout():
        logger.info("User logged out: %s", current_user.email)
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for("home"))
