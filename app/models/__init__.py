"""
Importing this package registers every model with SQLAlchemy's metadata,
so `db.create_all()` (called once at startup) knows about all tables.
"""

from app.models.user import User, DictLikeMixin
from app.models.booking import Worker, Booking
from app.models.job import Job, JobApplication, JOB_STATUSES
from app.models.notification import Notification, NOTIFICATION_TYPES
from app.models.saved_job import SavedJob
from app.models.review import Review
from app.models.category import Category, ServiceArea
from app.models.message import Message
from app.models.uploaded_image import UploadedImage

__all__ = [
    "User", "DictLikeMixin",
    "Worker", "Booking",
    "Job", "JobApplication", "JOB_STATUSES",
    "Notification", "NOTIFICATION_TYPES",
    "SavedJob",
    "Review",
    "Category", "ServiceArea",
    "Message",
    "UploadedImage",
]
