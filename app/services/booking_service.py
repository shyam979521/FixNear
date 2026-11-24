"""
Legacy simple worker-listing/booking service (Phase 1 feature set),
kept fully functional alongside the newer account-based marketplace.
"""

from app.extensions import db
from app.models import Worker, Booking


def search_workers(search=""):
    query = Worker.query
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            db.or_(
                db.func.lower(Worker.name).like(like),
                db.func.lower(Worker.work).like(like),
                db.func.lower(Worker.location).like(like),
            )
        )
    return query.all()


def register_worker_listing(name, work, price, location):
    worker = Worker(name=name, work=work, price=price, location=location)
    db.session.add(worker)
    db.session.commit()
    return worker


def create_booking(worker, customer_name, phone, service_date, service_time, address, problem):
    booking = Booking(
        customer_name=customer_name,
        phone=phone,
        worker_name=worker.name,
        work_type=worker.work,
        service_date=service_date,
        service_time=service_time,
        address=address,
        problem=problem,
        status="Pending",
    )
    db.session.add(booking)
    db.session.commit()
    return booking


def confirm_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if booking:
        booking.status = "Confirmed"
        db.session.commit()
    return booking


def delete_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if booking:
        db.session.delete(booking)
        db.session.commit()
    return booking
