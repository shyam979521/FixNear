"""
Customer, Worker and Admin dashboards, plus the legacy booking
confirm/delete actions used by the admin panel.
"""

import logging
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job, User, Booking
from app.services import booking_service
from app.services.notification_service import get_notifications_for
from app.utils.decorators import admin_required

logger = logging.getLogger(__name__)


def register_dashboard_routes(app):

    @app.route("/customer-dashboard")
    @login_required
    def customer_dashboard():
        if current_user.role == "worker":
            return redirect(url_for("worker_dashboard"))
        if current_user.role == "admin":
            return redirect(url_for("admin"))

        my_jobs = Job.query.filter_by(customer_id=current_user.id).order_by(Job.created_at.desc()).all()

        stats = {
            "open": len([j for j in my_jobs if j.status == "Open"]),
            "accepted": len([j for j in my_jobs if j.status == "Accepted"]),
            "completed": len([j for j in my_jobs if j.status == "Completed"]),
            "cancelled": len([j for j in my_jobs if j.status == "Cancelled"]),
        }

        notifications = get_notifications_for(current_user, limit=5)

        return render_template(
            "customer_dashboard.html", user=current_user, jobs=my_jobs, stats=stats,
            notifications=notifications, dash_role="customer",
        )

    @app.route("/worker-dashboard")
    @login_required
    def worker_dashboard():
        if current_user.role == "customer":
            return redirect(url_for("customer_dashboard"))
        if current_user.role == "admin":
            return redirect(url_for("admin"))

        my_jobs = Job.query.filter_by(worker_id=current_user.id).order_by(Job.created_at.desc()).all()

        available_query = Job.query.filter_by(status="Open")
        if current_user.service_category:
            available_query = available_query.filter_by(category=current_user.service_category)
        available_jobs = available_query.order_by(Job.created_at.desc()).limit(8).all()

        stats = {
            "accepted": len([j for j in my_jobs if j.status == "Accepted"]),
            "completed": len([j for j in my_jobs if j.status == "Completed"]),
            "cancelled": len([j for j in my_jobs if j.status == "Cancelled"]),
            "available": len(available_jobs),
        }

        notifications = get_notifications_for(current_user, limit=5)

        return render_template(
            "worker_dashboard.html", user=current_user, jobs=my_jobs,
            available_jobs=available_jobs, stats=stats,
            notifications=notifications, dash_role="worker",
        )

    @app.route("/admin")
    def admin():
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Please log in as an admin to view the dashboard.", "error")
            return redirect(url_for("admin_login"))

        bookings = Booking.query.order_by(Booking.id.desc()).all()

        stats = {
            "total_users": User.query.count(),
            "total_workers": User.query.filter_by(role="worker").count(),
            "total_customers": User.query.filter_by(role="customer").count(),
            "total_jobs": Job.query.count(),
            "pending_jobs": Job.query.filter_by(status="Open").count(),
            "accepted_jobs": Job.query.filter_by(status="Accepted").count(),
            "completed_jobs": Job.query.filter_by(status="Completed").count(),
            "pending_bookings": Booking.query.filter_by(status="Pending").count(),
        }

        recent_users = User.query.order_by(User.id.desc()).limit(6).all()
        all_users = User.query.order_by(User.id.desc()).all()
        recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(6).all()

        category_counts = (
            db.session.query(User.service_category, db.func.count(User.id).label("worker_count"))
            .filter(User.role == "worker", User.service_category.isnot(None), User.service_category != "")
            .group_by(User.service_category)
            .order_by(db.desc("worker_count"))
            .all()
        )

        notifications = []
        for u in recent_users[:3]:
            notifications.append({
                "icon": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>',
                "title": f"New {u.role} registered",
                "subtitle": u.full_name,
            })
        for j in recent_jobs[:3]:
            notifications.append({
                "icon": '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
                "title": f"New job posted: {j.category}",
                "subtitle": j.location,
            })
        notifications = notifications[:6]

        return render_template(
            "admin.html", bookings=bookings, stats=stats,
            recent_users=recent_users, all_users=all_users, recent_jobs=recent_jobs,
            category_counts=category_counts, notifications=notifications, dash_role="admin",
        )

    @app.route("/confirm/<int:booking_id>")
    @login_required
    @admin_required
    def confirm_booking(booking_id):
        booking_service.confirm_booking(booking_id)
        logger.info("Booking #%s confirmed by admin %s", booking_id, current_user.email)
        return redirect(url_for("admin"))

    @app.route("/delete/<int:booking_id>")
    @login_required
    @admin_required
    def delete_booking(booking_id):
        booking_service.delete_booking(booking_id)
        logger.info("Booking #%s deleted by admin %s", booking_id, current_user.email)
        return redirect(url_for("admin"))
