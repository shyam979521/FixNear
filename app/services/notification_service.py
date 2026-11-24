"""
Notification service — every place in the app that should notify a user
calls one of these functions, instead of hand-rolling INSERT statements
in the route. Keeps the "what triggers a notification" logic in one file.
"""

from app.extensions import db
from app.models import Notification, User

ICONS = {
    "new_work": '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    "work_accepted": '<path d="M20 6 9 17l-5-5"/>',
    "reminder": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "system": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "profile_update": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>',
}


def notify(user_id, type_, title, subtitle=""):
    notification = Notification(
        user_id=user_id, type=type_, title=title, subtitle=subtitle, icon=ICONS.get(type_, ICONS["system"]),
    )
    db.session.add(notification)
    db.session.commit()
    return notification


def notify_job_posted(job):
    """Notifies workers whose service category matches the new job."""
    matching_workers = User.query.filter_by(role="worker", service_category=job.category).all()
    for worker in matching_workers:
        notify(worker.id, "new_work", f"New {job.category} job available", job.location)


def notify_job_accepted(job):
    notify(job.customer_id, "work_accepted", f"{job.worker_name} accepted your job", f"{job.category} · {job.location}")


def notify_job_completed(job):
    notify(job.customer_id, "system", f"{job.category} job marked completed", job.location)


def notify_profile_updated(user):
    notify(user.id, "profile_update", "Your profile was updated", "Changes are now live on your public profile.")


def get_notifications_for(user, limit=20):
    return (
        Notification.query.filter_by(user_id=user.id)
        .order_by(Notification.id.desc())
        .limit(limit)
        .all()
    )


def unread_count_for(user):
    return Notification.query.filter_by(user_id=user.id, is_read=False).count()


def mark_all_read(user):
    Notification.query.filter_by(user_id=user.id, is_read=False).update({"is_read": True})
    db.session.commit()
