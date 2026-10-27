from flask import send_from_directory
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import re
import secrets
from pathlib import Path
from functools import wraps

app = Flask(__name__)

# ==============================
# ZONTECH SOLUTIONS CONFIGURATION
# ==============================

app.secret_key = "ZonTech_Secret_Key_Change_This_2026_9xK7mP2q"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ZonTech@Admin2026!"

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "zontech.db"

ALLOWED_SERVICES = {
    "Not sure yet",
    "Web Development",
    "Software Development",
    "Web Design",
    "Cloud Solutions",
    "AI & Machine Learning",
    "Other",
}


# ==============================
# DATABASE
# ==============================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                service TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


# ==============================
# HOME PAGE
# ==============================
@app.route('/google7689d59b4f7702e4.html')
def google_verification():
    return send_from_directory('.', 'google7689d59b4f7702e4.html')

@app.route("/")
def home():
    return render_template("index.html")


# ==============================
# CONTACT FORM API
# ==============================

@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid request. Please try again."
        }), 400

    # Spam protection
    if str(data.get("website", "")).strip():
        return jsonify({
            "success": True,
            "message": "Your inquiry has been received."
        }), 200

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    service = str(data.get("service", "Not sure yet")).strip()
    message = str(data.get("message", "")).strip()

    if not name or not email or not message:
        return jsonify({
            "success": False,
            "message": "Please fill in all required fields."
        }), 400

    if (
        len(name) > 100
        or len(email) > 254
        or len(message) > 5000
    ):
        return jsonify({
            "success": False,
            "message": "Some information is too long."
        }), 400

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    if service not in ALLOWED_SERVICES:
        return jsonify({
            "success": False,
            "message": "Please select a valid service."
        }), 400

    try:
        with get_db_connection() as connection:
            connection.execute("""
                INSERT INTO inquiries
                (name, email, service, message)
                VALUES (?, ?, ?, ?)
            """, (name, email, service, message))

        return jsonify({
            "success": True,
            "message": "Thank you! Your inquiry has been saved."
        }), 201

    except sqlite3.Error:
        app.logger.exception("Database error")
        return jsonify({
            "success": False,
            "message": "Could not save your inquiry. Please try again."
        }), 500


# ==============================
# ADMIN LOGIN PROTECTION
# ==============================

def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped_view


# ==============================
# ADMIN LOGIN PAGE
# ==============================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        submitted_token = request.form.get("csrf_token", "")
        saved_token = session.get("csrf_token", "")

        if (
            not saved_token
            or not secrets.compare_digest(
                submitted_token, saved_token
            )
        ):
            session["csrf_token"] = secrets.token_urlsafe(32)

            return render_template(
                "admin_login.html",
                error="Session expired. Please try again.",
                csrf_token=session["csrf_token"]
            ), 400

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        valid_username = secrets.compare_digest(
            username, ADMIN_USERNAME
        )
        valid_password = secrets.compare_digest(
            password, ADMIN_PASSWORD
        )

        if valid_username and valid_password:
            session.clear()
            session["admin_logged_in"] = True
            session["csrf_token"] = secrets.token_urlsafe(32)

            return redirect(url_for("admin_dashboard"))

        session["csrf_token"] = secrets.token_urlsafe(32)

        return render_template(
            "admin_login.html",
            error="Incorrect username or password.",
            csrf_token=session["csrf_token"]
        ), 401

    session["csrf_token"] = secrets.token_urlsafe(32)

    return render_template(
        "admin_login.html",
        error=None,
        csrf_token=session["csrf_token"]
    )


# ==============================
# ADMIN DASHBOARD
# ==============================

@app.route("/admin")
@admin_required
def admin_dashboard():
    with get_db_connection() as connection:
        inquiries = connection.execute("""
            SELECT id, name, email, service, message, created_at
            FROM inquiries
            ORDER BY id DESC
            LIMIT 500
        """).fetchall()

    return render_template(
        "admin.html",
        inquiries=inquiries,
        total=len(inquiries),
        csrf_token=session["csrf_token"]
    )


# ==============================
# ADMIN LOGOUT
# ==============================

@app.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    submitted_token = request.form.get("csrf_token", "")
    saved_token = session.get("csrf_token", "")

    if (
        not saved_token
        or not secrets.compare_digest(
            submitted_token, saved_token
        )
    ):
        return "Invalid request. Please try again.", 400

    session.clear()
    return redirect(url_for("admin_login"))


# ==============================
# START APPLICATION
# ==============================

create_database()

if __name__ == "__main__":
    app.run(debug=True)
