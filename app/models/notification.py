"""
Notification model — real, persisted notifications (replacing the
request-time-derived lists used in earlier phases). Designed to be
future-ready for real-time delivery (e.g. via WebSockets/SSE) since each
row already has a stable id, read state and timestamp.
"""

from datetime import datetime
from app.extensions import db
from app.models.user import DictLikeMixin

NOTIFICATION_TYPES = ("new_work", "work_accepted", "reminder", "system", "profile_update")


class Notification(db.Model, DictLikeMixin):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    type = db.Column(db.String(30), nullable=False, default="system")
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(255))
    icon = db.Column(db.Text)  # inline SVG path data, rendered directly in the template
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.String(40), nullable=False, default=lambda: datetime.now().isoformat())

    @property
    def unread(self):
        """Template compatibility: earlier phases used `n.unread` (truthy)."""
        return not self.is_read

    @property
    def time(self):
        """Template compatibility: earlier phases used `n.time` as a short date."""
        return self.created_at[:10] if self.created_at else ""

    def __repr__(self):
        return f"<Notification {self.id} user={self.user_id} {self.type}>"
