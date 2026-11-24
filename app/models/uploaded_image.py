"""
UploadedImage — an audit trail of every file saved through the upload
helper (profile photos, job photos). The actual Job/User rows still keep
a simple `image_path` / `profile_photo` string column for direct template
rendering (zero template changes needed); this table is the "proper"
normalized record used for admin auditing, size/type tracking, and future
multi-image support.
"""

from datetime import datetime
from app.extensions import db
from app.models.user import DictLikeMixin


class UploadedImage(db.Model, DictLikeMixin):
    __tablename__ = "uploaded_images"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255))
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=True)
    mime_type = db.Column(db.String(80))
    size_bytes = db.Column(db.Integer)
    created_at = db.Column(db.String(40), nullable=False, default=lambda: datetime.now().isoformat())

    def __repr__(self):
        return f"<UploadedImage {self.filename}>"
