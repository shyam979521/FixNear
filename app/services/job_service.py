"""
Job service — search/filtering, pagination, and the accept/complete/cancel
status transitions used by the marketplace routes.
"""

from app.extensions import db
from app.models import Job, JobApplication
from app.services.notification_service import notify_job_posted, notify_job_accepted, notify_job_completed

PER_PAGE = 9


def create_job(customer, category, description, budget, location, preferred_date, preferred_time, image_filename=None):
    job = Job(
        customer_id=customer.id,
        customer_name=customer.full_name,
        category=category,
        description=description,
        budget=budget,
        location=location,
        preferred_date=preferred_date,
        preferred_time=preferred_time,
        image_path=image_filename,
        status="Open",
    )
    db.session.add(job)
    db.session.commit()

    notify_job_posted(job)
    return job


def search_jobs(search="", category="", budget="", location="", sort="newest", page=1, per_page=PER_PAGE, status="Open"):
    """
    Central search/filter/sort/pagination for Find Work. Returns a
    Flask-SQLAlchemy Pagination object so templates can render page
    numbers, next/prev state, etc.

    Built with SQLAlchemy 2.0-style `select()` (rather than the legacy
    `Model.query` API) since `db.paginate()` expects a Select construct.
    """
    stmt = db.select(Job).where(Job.status == status)

    if search:
        like = f"%{search.lower()}%"
        stmt = stmt.where(
            db.or_(
                db.func.lower(Job.description).like(like),
                db.func.lower(Job.category).like(like),
            )
        )
    if category:
        stmt = stmt.where(Job.category == category)
    if budget:
        stmt = stmt.where(Job.budget == budget)
    if location:
        stmt = stmt.where(db.func.lower(Job.location).like(f"%{location.lower()}%"))

    stmt = stmt.order_by(Job.created_at.asc() if sort == "oldest" else Job.created_at.desc())

    return db.paginate(stmt, page=page, per_page=per_page, error_out=False)


def accept_job(job, worker):
    """First-to-accept assignment, with an audit row in job_applications."""
    if job.status != "Open":
        return False

    job.worker_id = worker.id
    job.worker_name = worker.full_name
    job.status = "Accepted"

    application = JobApplication(job_id=job.id, worker_id=worker.id, status="Accepted")
    db.session.add(application)
    db.session.commit()

    notify_job_accepted(job)
    return True


def cancel_job(job, customer):
    if job.customer_id != customer.id or job.status not in ("Open", "Accepted"):
        return False
    job.status = "Cancelled"
    db.session.commit()
    return True


def complete_job(job, worker):
    if job.worker_id != worker.id or job.status != "Accepted":
        return False
    job.status = "Completed"
    db.session.commit()
    notify_job_completed(job)
    return True


def related_jobs_for(job, limit=3):
    return (
        Job.query.filter(Job.category == job.category, Job.id != job.id, Job.status == "Open")
        .order_by(Job.created_at.desc())
        .limit(limit)
        .all()
    )


def sync_denormalized_name(user):
    """
    `Job.customer_name`/`Job.worker_name` are intentionally denormalized
    snapshots (kept so every existing template/route can read a plain
    string without a relationship join — changing that would mean editing
    every template that reads `job['customer_name']`, which is out of
    scope here).

    BUG FOUND & FIXED: nothing ever kept those snapshots in sync — verified
    that renaming a profile left every one of that user's past and future
    job listings showing the old name forever. This updates every job row
    where this user is the customer or worker whenever their name actually
    changes, without touching the schema or any template.
    """
    updated = False
    for job in Job.query.filter_by(customer_id=user.id).all():
        if job.customer_name != user.full_name:
            job.customer_name = user.full_name
            updated = True
    for job in Job.query.filter_by(worker_id=user.id).all():
        if job.worker_name != user.full_name:
            job.worker_name = user.full_name
            updated = True
    if updated:
        db.session.commit()
