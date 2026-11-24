"""
Message model — future-ready backend for the chat UI mockup built in
Phase 5 (`/messages`). That page intentionally stays a frontend-only
preview this phase; this table exists so real messaging can be wired up
later without another schema change.
"""

from datetime import datetime
from app.extensions import db
from app.models.user import DictLikeMixin


class Message(db.Model, DictLikeMixin):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=True)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.String(40), nullable=False, default=lambda: datetime.now().isoformat())

    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])

    def __repr__(self):
        return f"<Message {self.sender_id}->{self.receiver_id}>"
