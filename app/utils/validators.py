"""
Small, dependency-free validation helpers used across the auth and
profile forms. Kept as plain functions (rather than a full WTForms form
class per page) so the existing hand-written HTML forms don't need to
change — only the view functions that call these validators changed.
"""

import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9+\-\s()]{7,20}$")


def is_valid_email(email):
    return bool(email) and bool(EMAIL_RE.match(email.strip()))


def is_valid_phone(phone):
    """Phone is optional in a couple of forms — only validate if provided."""
    if not phone:
        return True
    return bool(PHONE_RE.match(phone.strip()))


def password_strength_errors(password):
    """
    Returns a list of human-readable problems with the password, or an
    empty list if it passes. Intentionally lenient (this is a local
    services marketplace, not a bank) but blocks the weakest passwords.
    """
    errors = []
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters long.")
    if password and password.isdigit():
        errors.append("Password can't be only numbers.")
    if password and password.lower() in ("password", "123456", "qwerty"):
        errors.append("That password is too common — please choose another.")
    return errors


def validate_registration_form(full_name, email, phone, password, confirm_password):
    """Shared validation for the registration form, regardless of role."""
    errors = []

    if not full_name or not full_name.strip():
        errors.append("Full name is required.")
    if not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    if not is_valid_phone(phone):
        errors.append("Please enter a valid phone number.")
    if password != confirm_password:
        errors.append("Passwords do not match.")
    errors.extend(password_strength_errors(password))

    return errors
