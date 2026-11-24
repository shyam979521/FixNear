"""
Review service — creating reviews and computing average ratings.
"""

from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models import Review, Job


def create_review(reviewer, reviewee_id, rating, body, job_id=None):
    """
    Creates a review. Returns (review, errors) — `review` is None if
    validation failed, in which case `errors` is a non-empty list of
    human-readable messages.

    SECURITY: prior to this fix, `/reviews/submit/<reviewee_id>` had no
    checks at all beyond being logged in — verified exploitable: any user
    could review themselves repeatedly with 5 stars and inflate their own
    average rating, or spam a competitor with fake 1-star reviews, with no
    real transaction behind any of it. Reviews must now reference a real
    job that actually completed, and the reviewer/reviewee must have
    actually been the two participants on that job.
    """
    errors = []

    if reviewer.id == reviewee_id:
        errors.append("You can't review yourself.")

    job = db.session.get(Job, job_id) if job_id else None
    if not job:
        errors.append("A completed job is required to leave a review.")
    elif job.status != "Completed":
        errors.append("You can only review a job after it's completed.")
    else:
        participants = {job.customer_id, job.worker_id}
        if reviewer.id not in participants or reviewee_id not in participants:
            errors.append("You can only review someone you actually worked with on this job.")
        elif Review.query.filter_by(reviewer_id=reviewer.id, reviewee_id=reviewee_id, job_id=job.id).first():
            errors.append("You've already reviewed this job.")

    if errors:
        return None, errors

    rating = max(1, min(5, int(rating)))
    review = Review(reviewer_id=reviewer.id, reviewee_id=reviewee_id, rating=rating, body=body, job_id=job_id)
    db.session.add(review)
    db.session.commit()
    return review, []


def get_reviews_for(user, limit=10):
    return (
        Review.query.options(joinedload(Review.reviewer))
        .filter_by(reviewee_id=user.id)
        .order_by(Review.id.desc())
        .limit(limit)
        .all()
    )


def average_rating_for(user):
    reviews = Review.query.filter_by(reviewee_id=user.id).all()
    if not reviews:
        return None
    return round(sum(r.rating for r in reviews) / len(reviews), 1)


def rating_breakdown_for(user):
    """Returns {5: pct, 4: pct, 3: pct, 2: pct, 1: pct} for the star-bar UI."""
    reviews = Review.query.filter_by(reviewee_id=user.id).all()
    total = len(reviews)
    breakdown = {star: 0 for star in range(5, 0, -1)}
    if total == 0:
        return breakdown
    for r in reviews:
        breakdown[r.rating] += 1
    return {star: round((count / total) * 100) for star, count in breakdown.items()}
