"""
Reference/lookup tables. Jobs and worker profiles still store `category`
and `service_area` as plain strings (so every existing template keeps
rendering unchanged), but these tables give the admin a real place to
manage the canonical list instead of it being hardcoded in every template.
"""

from app.extensions import db
from app.models.user import DictLikeMixin


class Category(db.Model, DictLikeMixin):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    icon_svg = db.Column(db.Text)  # inline <path> data reused by templates
    duration_estimate = db.Column(db.String(40))  # e.g. "30–60 min"
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Category {self.name}>"


class ServiceArea(db.Model, DictLikeMixin):
    __tablename__ = "service_areas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<ServiceArea {self.name}>"
