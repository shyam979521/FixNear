"""
Main / legacy routes — the homepage, and the original Phase-1 simple
worker-listing + booking flow (Register Worker / Book Worker), kept
fully intact.

Routes are registered via plain `@app.route` (not a Blueprint) so every
endpoint keeps its original name (e.g. `home`, `workers`, `book_worker`).
That means every `url_for(...)` call already in the templates keeps
working without a single template edit.
"""

import logging
from flask import render_template, request, redirect, url_for
from app.extensions import db
from app.services import booking_service
from app.models import Worker

logger = logging.getLogger(__name__)


def register_main_routes(app):

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/workers")
    def workers():
        search = request.args.get("search", "").strip().lower()
        workers_data = booking_service.search_workers(search)
        return render_template("workers.html", workers=workers_data, search=search)

    @app.route("/register-worker", methods=["GET", "POST"])
    def register_worker():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            work = request.form.get("work", "").strip()
            price = request.form.get("price", "").strip()
            location = request.form.get("location", "").strip()

            if not all([name, work, price, location]):
                from flask import flash
                flash("Please fill in every field.", "error")
                return render_template("register_worker.html")

            booking_service.register_worker_listing(name, work, price, location)
            logger.info("New quick-listing worker registered: %s (%s)", name, work)
            return redirect(url_for("workers"))

        return render_template("register_worker.html")

    @app.route("/book/<int:worker_id>", methods=["GET", "POST"])
    def book_worker(worker_id):
        selected_worker = db.session.get(Worker, worker_id)
        if selected_worker is None:
            return render_template("errors/404.html"), 404

        if request.method == "POST":
            customer_name = request.form.get("customer_name", "").strip()
            phone = request.form.get("phone", "").strip()
            service_date = request.form.get("service_date", "").strip()
            service_time = request.form.get("service_time", "").strip()
            address = request.form.get("address", "").strip()
            problem = request.form.get("problem", "").strip()

            booking_service.create_booking(
                selected_worker, customer_name, phone, service_date, service_time, address, problem
            )
            logger.info("New booking: %s -> %s", customer_name, selected_worker.name)

            return render_template(
                "booking_success.html",
                customer_name=customer_name,
                service_date=service_date,
                service_time=service_time,
                address=address,
                problem=problem,
                worker=selected_worker,
            )

        return render_template("booking.html", worker=selected_worker)
