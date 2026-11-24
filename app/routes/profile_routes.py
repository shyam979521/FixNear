"""
Profile view/edit routes, now backed by real review/rating data instead
of the placeholder mock reviews used in Phase 5.
"""

import logging
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job
from app.services.upload_service import save_uploaded_file
from app.services.review_service import get_reviews_for, average_rating_for, rating_breakdown_for
from app.services.notification_service import notify_profile_updated
from app.services.job_service import sync_denormalized_name

logger = logging.getLogger(__name__)


def register_profile_routes(app):

    @app.route("/profile")
    @login_required
    def profile():
        user = current_user

        stats = {}
        if user.role == "worker":
            stats["active_jobs"] = Job.query.filter_by(worker_id=user.id, status="Accepted").count()
            stats["completed_jobs"] = Job.query.filter_by(worker_id=user.id, status="Completed").count()
        else:
            stats["posted_jobs"] = Job.query.filter_by(customer_id=user.id).count()
            stats["completed_jobs"] = Job.query.filter_by(customer_id=user.id, status="Completed").count()

        recent_activity = (
            Job.query.filter(db.or_(Job.customer_id == user.id, Job.worker_id == user.id))
            .order_by(Job.created_at.desc())
            .limit(5)
            .all()
        )

        reviews = get_reviews_for(user)
        average_rating = average_rating_for(user)
        rating_breakdown = rating_breakdown_for(user)

        return render_template(
            "profile.html", user=user, stats=stats, recent_activity=recent_activity,
            reviews=reviews, average_rating=average_rating, rating_breakdown=rating_breakdown,
        )

    @app.route("/profile/edit", methods=["GET", "POST"])
    @login_required
    def profile_edit():
        user = current_user

        if request.method == "POST":
            new_name = request.form.get("full_name", "").strip()
            name_changed = new_name and new_name != user.full_name

            user.full_name = new_name
            user.phone = request.form.get("phone", "").strip()
            user.location = request.form.get("location", "").strip()
            user.bio = request.form.get("bio", "").strip()
            user.service_category = request.form.get("service_category", "").strip()
            user.experience = request.form.get("experience", "").strip()
            user.service_area = request.form.get("service_area", "").strip()
            user.availability = request.form.get("availability", "").strip()

            photo = save_uploaded_file(request.files.get("profile_photo"), uploaded_by=user.id)
            if photo:
                user.profile_photo = photo

            db.session.commit()

            if name_changed:
                sync_denormalized_name(user)

            notify_profile_updated(user)
            logger.info("Profile updated: %s", user.email)

            flash("Profile updated successfully.", "success")
            return redirect(url_for("profile"))

        return render_template("profile_edit.html", user=user)
