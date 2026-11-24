"""
Legacy "simple worker listing" models — the original Phase-1 feature set
(Register Worker / Book Worker) kept fully intact alongside the newer
account-based marketplace.
"""

from app.extensions import db
from app.models.user import DictLikeMixin


class Worker(db.Model, DictLikeMixin):
    __tablename__ = "workers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    work = db.Column(db.String(80), nullable=False)
    price = db.Column(db.String(40), nullable=False)
    location = db.Column(db.String(160), nullable=False)

    def __repr__(self):
        return f"<Worker {self.id} {self.name} ({self.work})>"


class Booking(db.Model, DictLikeMixin):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    worker_name = db.Column(db.String(120), nullable=False)
    work_type = db.Column(db.String(80), nullable=False)
    service_date = db.Column(db.String(20), nullable=False)
    service_time = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    problem = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")

    def __repr__(self):
        return f"<Booking {self.id} {self.customer_name} -> {self.worker_name}>"
