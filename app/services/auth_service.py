"""
Authentication service — registration and credential checking. Kept
separate from the route so the route stays thin (parse request -> call
service -> handle result), matching the rest of the codebase.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import User
from app.utils.validators import validate_registration_form


def email_taken(email):
    return User.query.filter_by(email=email).first() is not None


def register_user(role, full_name, email, phone, password, confirm_password, **profile_fields):
    """
    Validates and creates a new user. Returns (user, errors) — `user` is
    None if validation failed, in which case `errors` is a non-empty list
    of human-readable messages.
    """
    email = (email or "").strip().lower()
    errors = validate_registration_form(full_name, email, phone, password, confirm_password)

    # SECURITY: public self-registration must never be allowed to create an
    # admin account. Verified exploitable prior to this fix — a POST to
    # /register with role=admin created a fully privileged admin account
    # with no gatekeeping at all. Admin accounts are provisioned via the
    # seeded demo account / a real admin creating one through internal
    # tooling, never through the public sign-up form.
    if role == "admin":
        errors.append("Admin accounts can't be created through public registration.")
        role = "customer"
    elif role not in ("customer", "worker"):
        role = "customer"

    if email and email_taken(email):
        errors.append("An account with this email already exists.")

    if errors:
        return None, errors

    user = User(
        full_name=full_name.strip(),
        email=email,
        phone=phone,
        password_hash=generate_password_hash(password),
        role=role,
        created_at=datetime.now().isoformat(),
        **profile_fields,
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        # BUG FOUND & FIXED: the email_taken() check above and this commit
        # aren't atomic — two near-simultaneous registrations with the same
        # email could both pass the pre-check and only get caught by the
        # database's unique constraint at commit time. Verified this raised
        # an uncaught IntegrityError straight to a generic 500 page; now
        # it's handled the same way as the normal "email already exists"
        # validation error.
        db.session.rollback()
        return None, ["An account with this email already exists."]

    return user, []


def authenticate(email, password):
    """Returns the User if credentials are valid, else None."""
    email = (email or "").strip().lower()
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None
