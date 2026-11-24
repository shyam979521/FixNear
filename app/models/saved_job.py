"""
SavedJob — persisted bookmark, replacing the Phase-5 localStorage-only
implementation. One row per (user, job) bookmark.
"""

from datetime import datetime
from app.extensions import db
from app.models.user import DictLikeMixin


class SavedJob(db.Model, DictLikeMixin):
    __tablename__ = "saved_jobs"
    __table_args__ = (db.UniqueConstraint("user_id", "job_id", name="uq_saved_job_per_user"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    created_at = db.Column(db.String(40), nullable=False, default=lambda: datetime.now().isoformat())

    job = db.relationship("Job")

    def __repr__(self):
        return f"<SavedJob user={self.user_id} job={self.job_id}>"
