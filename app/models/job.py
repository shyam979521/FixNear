"""
Job marketplace models: a customer posts a `Job`; workers may `apply`
(recorded in `JobApplication` for future multi-bid support) and one worker
is ultimately assigned directly on the Job row itself (current UX is a
first-to-accept model, matching the existing find_work/apply_job flow).
"""

from datetime import datetime
from app.extensions import db
from app.models.user import DictLikeMixin

JOB_STATUSES = ("Open", "Accepted", "Completed", "Cancelled")


class Job(db.Model, DictLikeMixin):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    customer_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.String(60))
    location = db.Column(db.String(160), nullable=False)
    preferred_date = db.Column(db.String(20))
    preferred_time = db.Column(db.String(20))
    image_path = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default="Open", index=True)
    worker_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    worker_name = db.Column(db.String(120))
    created_at = db.Column(db.String(40), nullable=False, default=lambda: datetime.now().isoformat())

    applications = db.relationship("JobApplication", backref="job", lazy="dynamic", cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="job", lazy="dynamic")

    def __repr__(self):
        return f"<Job {self.id} {self.category} ({self.status})>"


class JobApplication(db.Model, DictLikeMixin):
    """
    Records every accept action for auditing / future multi-worker bidding.
    The current UX still assigns the job directly on `Job.worker_id`
    (first worker to accept wins) — this table exists so a future "let
    the customer pick from multiple applicants" flow can be added without
    another schema migration.
    """
    __tablename__ = "job_applications"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Accepted")  # Applied | Accepted | Rejected
    created_at = db.Column(db.String(40), nullable=False, default=lambda: datetime.now().isoformat())

    def __repr__(self):
        return f"<JobApplication job={self.job_id} worker={self.worker_id} ({self.status})>"
