"""
First-run seed data. Every insert here is guarded by an emptiness check,
so re-running this against an already-populated database (e.g. the
workers.db shipped from earlier phases) is always a safe no-op.
"""

import logging
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import Worker, User, Category
from app.utils.helpers import DEFAULT_CATEGORIES

logger = logging.getLogger(__name__)


def seed_database():
    _seed_legacy_workers()
    _seed_demo_admin()
    _seed_categories()


def _seed_legacy_workers():
    if Worker.query.count() > 0:
        return
    db.session.add_all([
        Worker(name="Ramesh", work="Plumber", price="₹300", location="Lucknow"),
        Worker(name="Suresh", work="Electrician", price="₹400", location="Lucknow"),
        Worker(name="Amit", work="Carpenter", price="₹500", location="Barabanki"),
        Worker(name="Rahul", work="Painter", price="₹350", location="Lucknow"),
    ])
    db.session.commit()
    logger.info("Seeded default worker listings")


def _seed_demo_admin():
    if User.query.filter_by(role="admin").count() > 0:
        return
    admin = User(
        full_name="Admin",
        email="admin@fixnear.com",
        phone="",
        password_hash=generate_password_hash("admin123"),
        role="admin",
        location="",
    )
    db.session.add(admin)
    db.session.commit()
    logger.info("Seeded demo admin account (admin@fixnear.com / admin123)")


def _seed_categories():
    if Category.query.count() > 0:
        return
    icon_map = {
        "Electrician": '<path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/>',
        "Plumber": '<path d="M14 4v6l3 3-6 6-3-3H2V4h12z"/><path d="M18 8h4v12h-4z"/>',
        "Carpenter": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
        "Painter": '<path d="M18.37 2.63 14 7l-1.59-1.59a2 2 0 0 0-2.82 0L8 7l9 9 1.59-1.59a2 2 0 0 0 0-2.82L17 10l4.37-4.37a2.12 2.12 0 1 0-3-3z"/>',
        "Furniture Repair": '<path d="M20 9V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v3"/><path d="M2 11v5a1 1 0 0 0 1 1h1v3h2v-3h12v3h2v-3h1a1 1 0 0 0 1-1v-5a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2z"/>',
        "Bike Repair": '<circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M12 17.5V14l-3-3 4-3 2 3h2"/>',
        "Car Repair": '<path d="M14 16.5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"/><path d="M4.5 16.5h-2v-5l2-5h10l3.5 5H21v5h-2"/><path d="M17 16.5h-3"/>',
        "Cleaning": '<path d="M3 3l3 3"/><path d="M14 6l7 7-8 8-7-7z"/><path d="M6 6 17.5 17.5"/>',
        "AC Repair": '<path d="M12 2v20"/><path d="M2 12h20"/><path d="M20 16 4 8"/><path d="M4 16 20 8"/>',
        "Home Appliance Repair": '<rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="7" x2="16" y2="7"/><circle cx="12" cy="15" r="3"/>',
    }
    for name, duration in DEFAULT_CATEGORIES:
        db.session.add(Category(
            name=name, duration_estimate=duration, icon_svg=icon_map.get(name, "")
        ))
    db.session.commit()
    logger.info("Seeded %d service categories", len(DEFAULT_CATEGORIES))
