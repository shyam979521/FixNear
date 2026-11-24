"""
Job marketplace routes: posting jobs, searching/filtering (with real
pagination), job details, and the accept/cancel/complete/reject status
transitions.
"""

import logging
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job, JobApplication
from app.services import job_service
from app.services.upload_service import save_uploaded_file
from app.utils.decorators import worker_required, customer_required

logger = logging.getLogger(__name__)


def register_job_routes(app):

    @app.route("/post-work", methods=["GET", "POST"])
    @login_required
    def post_work():
        if request.method == "POST":
            category = request.form.get("category", "").strip()
            description = request.form.get("description", "").strip()
            budget = request.form.get("budget", "").strip()
            location = request.form.get("location", "").strip()
            preferred_date = request.form.get("preferred_date", "").strip()
            preferred_time = request.form.get("preferred_time", "").strip()

            if not category or not description or not location:
                flash("Please fill in the category, description and location.", "error")
                return render_template("post_work.html", user=current_user)

            image_filename = save_uploaded_file(request.files.get("image"), uploaded_by=current_user.id)

            job = job_service.create_job(
                current_user, category, description, budget, location,
                preferred_date, preferred_time, image_filename
            )
            logger.info("Job posted: #%s %s by %s", job.id, job.category, current_user.email)

            flash("Your work request has been posted!", "success")
            return redirect(url_for("find_work"))

        return render_template("post_work.html", user=current_user)

    @app.route("/find-work")
    def find_work():
        search = request.args.get("search", "").strip().lower()
        category = request.args.get("category", "").strip()
        budget = request.args.get("budget", "").strip()
        location_filter = request.args.get("location", "").strip().lower()
        sort = request.args.get("sort", "newest")
        page = request.args.get("page", 1, type=int)

        pagination = job_service.search_jobs(
            search=search, category=category, budget=budget,
            location=location_filter, sort=sort, page=page,
        )

        return render_template(
            "find_work.html", jobs=pagination.items, pagination=pagination, search=search,
            category=category, budget=budget, location_filter=location_filter, sort=sort,
        )

    @app.route("/job/<int:job_id>")
    def job_details(job_id):
        job = db.session.get(Job, job_id)
        if not job:
            flash("That job could not be found.", "error")
            return redirect(url_for("find_work"))

        related_jobs = job_service.related_jobs_for(job)
        return render_template("job_details.html", job=job, related_jobs=related_jobs)

    @app.route("/find-work/apply/<int:job_id>")
    @login_required
    @worker_required
    def apply_job(job_id):
        job = db.get_or_404(Job, job_id)
        if job_service.accept_job(job, current_user):
            logger.info("Job #%s accepted by %s", job.id, current_user.email)
            flash("Job accepted! Check your profile for details.", "success")
        else:
            flash("That job is no longer available.", "error")
        return redirect(url_for("find_work"))

    @app.route("/jobs/reject/<int:job_id>")
    @login_required
    @worker_required
    def reject_job(job_id):
        """
        Records that this worker passed on a job (future-ready — doesn't
        change the job itself, since any other matching worker can still
        accept it). Supports the "Reject" button already in the UI.
        """
        job = db.get_or_404(Job, job_id)
        existing = JobApplication.query.filter_by(job_id=job.id, worker_id=current_user.id).first()
        if not existing:
            db.session.add(JobApplication(job_id=job.id, worker_id=current_user.id, status="Rejected"))
            db.session.commit()
        return jsonify({"status": "ok"})

    @app.route("/jobs/cancel/<int:job_id>")
    @login_required
    @customer_required
    def cancel_job(job_id):
        job = db.get_or_404(Job, job_id)
        if job_service.cancel_job(job, current_user):
            flash("Job request cancelled.", "success")
        else:
            flash("That job can no longer be cancelled.", "error")
        return redirect(url_for("customer_dashboard"))

    @app.route("/jobs/complete/<int:job_id>")
    @login_required
    @worker_required
    def complete_job(job_id):
        job = db.get_or_404(Job, job_id)
        if job_service.complete_job(job, current_user):
            logger.info("Job #%s marked completed by %s", job.id, current_user.email)
            flash("Job marked as completed!", "success")
        else:
            flash("That job can't be marked completed right now.", "error")
        return redirect(url_for("worker_dashboard"))
