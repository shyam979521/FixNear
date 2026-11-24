# FixNear — Local Worker Booking & Job Marketplace

A Flask-based marketplace connecting customers with local service workers
(electricians, plumbers, carpenters, and more), plus a full job-posting
marketplace (post work, find work, accept/complete jobs, reviews,
notifications, and dashboards for customers, workers and admins).

---

## Requirements

- Python 3.10+
- pip

## Installation

```bash
# 1. Clone / unzip the project, then from the project root:
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# edit .env and set a real SECRET_KEY, especially before deploying

# 4. Run the app
python run.py
# (python app.py also still works — kept for backward compatibility)
```

The app runs at **http://127.0.0.1:5000**.

On first run, the app automatically:
- Creates any missing database tables (existing tables/data are left untouched)
- Seeds the four demo worker listings (if the `workers` table is empty)
- Seeds a demo admin account (if no admin exists yet): **admin@fixnear.com / admin123**
- Seeds the 10 default service categories

---

## Folder Structure

```
project/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── config.py            # Development / Production / Testing configs
│   ├── extensions.py        # db, login_manager, csrf — shared instances
│   ├── error_handlers.py    # 404 / 403 / 413 / 500 handlers
│   ├── logging_config.py    # Rotating file logger setup
│   ├── seed.py               # First-run seed data (idempotent)
│   ├── models/                # SQLAlchemy models (one concern per file)
│   │   ├── user.py            # User (customer/worker/admin, single table)
│   │   ├── booking.py         # Worker, Booking (legacy Phase-1 flow)
│   │   ├── job.py              # Job, JobApplication
│   │   ├── notification.py     # Notification
│   │   ├── saved_job.py         # SavedJob (bookmarks)
│   │   ├── review.py            # Review (ratings + reviews)
│   │   ├── category.py           # Category, ServiceArea (reference data)
│   │   ├── message.py             # Message (future-ready chat backend)
│   │   └── uploaded_image.py      # UploadedImage (upload audit trail)
│   ├── routes/                # Thin Flask view functions
│   │   ├── main_routes.py       # Home, legacy worker listing/booking
│   │   ├── auth_routes.py       # Register, login, logout, admin login
│   │   ├── profile_routes.py    # Profile view/edit
│   │   ├── job_routes.py         # Post/find/accept/cancel/complete jobs
│   │   ├── dashboard_routes.py    # Customer/Worker/Admin dashboards
│   │   └── marketplace_routes.py  # Saved jobs, notifications, history, reviews
│   ├── services/                # Business logic + queries (called by routes)
│   │   ├── auth_service.py
│   │   ├── job_service.py         # search/filter/paginate, status transitions
│   │   ├── notification_service.py
│   │   ├── review_service.py
│   │   ├── upload_service.py       # secure image upload validation/saving
│   │   └── booking_service.py       # legacy worker/booking flow
│   └── utils/
│       ├── decorators.py            # role_required, admin_required, etc.
│       ├── validators.py             # email/phone/password validation
│       └── helpers.py                 # is_urgent_date, category durations
├── templates/                # Jinja templates (unchanged from earlier phases)
├── static/
│   └── uploads/                 # User-uploaded images
├── instance/                  # Reserved for instance-specific config
├── migrations/                # Reserved for Flask-Migrate (see Roadmap)
├── logs/
│   └── app.log                 # Rotating application log
├── run.py                     # New entry point — `python run.py`
├── app.py                     # Thin backward-compatible shim for `python app.py`
├── requirements.txt
├── .env.example
└── workers.db                 # SQLite database (unchanged location/data)
```

**Why templates/static stay at the project root:** every existing page
was hand-built across five earlier phases. Moving them into `app/` would
have meant touching 25+ files for zero functional benefit, so the app
factory simply points Flask at their existing location instead.

**Why one `User` table instead of separate Customer/Worker/Admin tables:**
the original Phase 3 schema already used a single `users` table with a
`role` column, and real data already lives there. Splitting it into three
tables now would require a data migration with real risk of data loss.
Every model exposes the same fields either way; see *Roadmap* below for
the future normalization path.

---

## Architecture Notes

- **Routes are plain functions, not Blueprints.** Every route keeps its
  original endpoint name (`home`, `find_work`, `job_details`, …) so all
  25+ templates' `url_for(...)` calls keep working without any edits.
  Each `app/routes/*.py` file exposes a `register_*_routes(app)` function
  instead.
- **Templates access model objects like dictionaries** (`job['category']`,
  `user['full_name']`) exactly as they did with the old raw `sqlite3.Row`
  objects. This works because every model mixes in `DictLikeMixin`
  (`app/models/user.py`), so nothing in `templates/` needed to change.
- **`created_at` columns are stored as ISO-format strings**, not native
  `DateTime` — several templates slice them directly (`job['created_at'][:10]`).
  Switching to a real `DateTime` column would require adding `.strftime()`
  filters across many templates; kept as-is deliberately for this phase.

---

## Security

- Passwords hashed with Werkzeug's `generate_password_hash` (PBKDF2).
- CSRF protection via Flask-WTF on every real POST form (registration,
  login, admin login, forgot password, post-work, profile edit, booking,
  quick worker registration). State-changing GET links (accept/cancel/
  complete a job, confirm/delete a booking) are not form-based and Flask-
  WTF's CSRF checks don't apply to GET requests by design.
- Session cookies are `HttpOnly` + `SameSite=Lax`; `Secure` is enabled
  automatically in `ProductionConfig`.
- File uploads: extension allow-list, size limit (`MAX_CONTENT_LENGTH`,
  5MB), and the original filename is never trusted for the save path —
  only its extension is read, and a fresh UUID filename is generated.
- `SECRET_KEY` and the database URL are read from environment variables
  (`.env` in development) — see `.env.example`.
- Admin actions (confirm/delete bookings) and the admin dashboard now
  require an authenticated admin session — this was previously
  completely open in earlier phases and has been hardened here.

---

## Running Tests / Sanity-Checking

There's no formal test suite yet (see Roadmap), but every route was
manually smoke-tested with Flask's test client during development —
registration for all 3 roles, login/logout, posting and accepting jobs,
cancelling/completing jobs, booking a legacy worker, admin confirm/delete,
saved jobs, notifications, and access-control redirects.

---

## Roadmap / Future Work

- **Formal migrations:** introduce Flask-Migrate (`flask db init/migrate/upgrade`)
  once the schema needs to evolve further. `db.create_all()` is used for
  now since it's a safe no-op against tables that already exist.
- **Split `User` into `users` + `worker_profiles`:** move worker-only
  columns (service_category, experience, service_area, availability) into
  a related table once the profile grows further.
- **Multi-worker bidding:** `JobApplication` already records every accept
  action; a future version could let customers choose between multiple
  applicants instead of first-to-accept.
- **Real-time notifications:** the `Notification` model is already a
  proper persisted table with read state — a good foundation for adding
  WebSockets/Server-Sent Events later.
- **Wire up the Messages page:** the `Message` model exists; the `/messages`
  UI is still a frontend-only preview per Phase 5's scope.
- **REST API:** because business logic already lives in `app/services/`
  rather than inline in routes, a `/api/v1/...` Blueprint can call the
  same service functions and return JSON without duplicating logic.
