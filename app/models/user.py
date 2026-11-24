"""
User model.

A single `users` table backs Customer, Worker and Admin accounts,
distinguished by the `role` column. This matches the table that already
exists in the shipped `workers.db`, so no data migration is required.

Worker-specific fields (service_category, experience, service_area,
availability) are nullable columns on the same row — simplest possible
design for now. A future refactor could split these into a separate
`worker_profiles` table with a one-to-one relationship if the schema
grows further; the DictLikeMixin below would make that change transparent
to templates as long as the same keys stay accessible.
"""

from datetime import datetime
from flask_login import UserMixin
from app.extensions import db


class DictLikeMixin:
    """
    Lets SQLAlchemy model instances be accessed like the sqlite3.Row objects
    used in earlier phases (`user['full_name']`, `job['category']`, ...).
    This means every existing Jinja template keeps working unchanged.
    """

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def keys(self):
        return [c.key for c in self.__table__.columns]


class User(db.Model, DictLikeMixin, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(30))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer", index=True)  # customer | worker | admin
    location = db.Column(db.String(160))
    profile_photo = db.Column(db.String(255))
    bio = db.Column(db.Text)
    service_category = db.Column(db.String(80))
    experience = db.Column(db.String(40))
    service_area = db.Column(db.String(160))
    availability = db.Column(db.String(40))
    # Stored as ISO-format text (not a native DateTime) so existing templates
    # that slice it directly, e.g. `user['created_at'][:10]`, keep working.
    created_at = db.Column(db.String(40), nullable=False, default=lambda: datetime.now().isoformat())

    jobs_posted = db.relationship("Job", foreign_keys="Job.customer_id", backref="customer", lazy="dynamic")
    jobs_assigned = db.relationship("Job", foreign_keys="Job.worker_id", backref="worker", lazy="dynamic")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    saved_jobs = db.relationship("SavedJob", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.id} {self.email} ({self.role})>"
