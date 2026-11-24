"""
Saved Jobs (now backed by a real database table instead of the Phase-5
localStorage-only approach), the Notification Center, the Messages
preview page, Work History, and review submission.
"""

import logging
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Job, SavedJob, User
from app.services.notification_service import get_notifications_for, mark_all_read
from app.services.review_service import create_review

logger = logging.getLogger(__name__)


def register_marketplace_routes(app):

    @app.route("/saved-jobs")
    @login_required
    def saved_jobs():
        saved = (
            SavedJob.query.filter_by(user_id=current_user.id)
            .order_by(SavedJob.id.desc())
            .all()
        )
        jobs = [s.job for s in saved if s.job is not None]
        return render_template("saved_jobs.html", user=current_user, jobs=jobs)

    @app.route("/saved-jobs/toggle/<int:job_id>", methods=["POST"])
    @login_required
    def toggle_saved_job(job_id):
        """AJAX endpoint used by the bookmark button on every job card."""
        existing = SavedJob.query.filter_by(user_id=current_user.id, job_id=job_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return jsonify({"saved": False})

        job = db.get_or_404(Job, job_id)
        db.session.add(SavedJob(user_id=current_user.id, job_id=job.id))
        try:
            db.session.commit()
        except IntegrityError:
            # Same check-then-insert race as registration, here a rapid
            # double-click on the bookmark button rather than a duplicate
            # email. The unique constraint already prevented a duplicate
            # row; treat it as "already saved" instead of a 500.
            db.session.rollback()
        return jsonify({"saved": True})

    @app.route("/api/saved-jobs")
    @login_required
    def saved_job_ids():
        """Returns the current user's saved job ids, for the bookmark icons to sync on page load."""
        ids = [s.job_id for s in SavedJob.query.filter_by(user_id=current_user.id).all()]
        return jsonify({"saved_ids": ids})

    @app.route("/notifications")
    @login_required
    def notifications_center():
        notifications = get_notifications_for(current_user, limit=30)
        return render_template("notifications.html", user=current_user, notifications=notifications)

    @app.route("/notifications/mark-all-read", methods=["POST"])
    @login_required
    def mark_notifications_read():
        mark_all_read(current_user)
        return jsonify({"status": "ok"})

    @app.route("/messages")
    @login_required
    def messages():
        return render_template("messages.html", user=current_user)

    @app.route("/history")
    @login_required
    def work_history():
        if current_user.role == "worker":
            jobs = Job.query.filter_by(worker_id=current_user.id).order_by(Job.created_at.desc()).all()
        else:
            jobs = Job.query.filter_by(customer_id=current_user.id).order_by(Job.created_at.desc()).all()
        return render_template("history.html", user=current_user, jobs=jobs)

    @app.route("/reviews/submit/<int:reviewee_id>", methods=["POST"])
    @login_required
    def submit_review(reviewee_id):
        """
        Real review-submission endpoint. Not yet wired to the "Write a
        Review" modal's JS (which still shows a frontend-only preview per
        the Phase 5 scope) — exists and works so that integration is a
        small follow-up rather than another backend change.
        """
        reviewee = db.get_or_404(User, reviewee_id)
        rating = request.form.get("rating", 5, type=int)
        body = request.form.get("body", "").strip()
        job_id = request.form.get("job_id", type=int)

        review, errors = create_review(current_user, reviewee.id, rating, body, job_id=job_id)

        if errors:
            for e in errors:
                flash(e, "error")
        else:
            logger.info("Review submitted: %s -> %s (%s★)", current_user.email, reviewee.email, rating)
            flash("Thanks for the feedback!", "success")

        return redirect(request.referrer or url_for("profile"))
