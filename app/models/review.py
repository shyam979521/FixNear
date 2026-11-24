"""
Review model — backs both "worker ratings" (customer reviews a worker
after a completed job) and "customer ratings" (worker reviews a customer).
Direction is inferred from the reviewer/reviewee roles, so one table
covers both without duplicating structure.
"""

from datetime import datetime
from app.extensions import db
from app.models.user import DictLikeMixin


class Review(db.Model, DictLikeMixin):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    body = db.Column(db.Text)
    is_flagged = db.Column(db.Boolean, nullable=False, default=False)  # future moderation support
    created_at = db.Column(db.String(40), nullable=False, default=lambda: datetime.now().isoformat())

    reviewer = db.relationship("User", foreign_keys=[reviewer_id])
    reviewee = db.relationship("User", foreign_keys=[reviewee_id])

    def __repr__(self):
        return f"<Review {self.id} {self.reviewer_id}->{self.reviewee_id} ({self.rating}★)>"
