"""
STUDENT NEXT.AI BACKEND SERVER
==============================
Flask + SQLAlchemy backend for the University Finder rebuild.

To run:
    pip install -r requirements.txt
    python seed.py     # populate the dataset (safe to re-run) — 410 universities, 137 countries
    python app.py
Server starts at http://127.0.0.1:5000

v3 CHANGES:
    - Removed /api/auth/google (Google sign-in button removed from the
      front page), /api/transcript/* (My Transcript feature removed),
      /api/youtube/scan (YouTube Study Videos removed), /api/skills
      (Skills Roadmap removed), and /api/user/reco-prefs (tied to the
      removed country dropdown + transcript auto-search flow).
    - Added /api/advisor/recommend (the new University Finder AI
      recommendation engine, see advisor.py), /api/universities/directory
      (the Guide platform's full university directory), and
      /api/universities/featured (a small random sample for the home page).
"""

import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

from models import init_db, get_db, Country, TestInfo, Scholarship, University
from chatbot import get_chatbot_response
from university_matcher import (
    search_universities, list_countries_summary, get_formulas_for_country,
    evaluate_formula, get_university_directory, list_all_country_names,
)
from advisor import get_recommendation
from emailer import send_welcome_email, send_password_reset_email
import auth

app = Flask(__name__)
CORS(app)

init_db()


def get_user_from_request():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    return auth.get_user_from_token(token)


# ─────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json or {}
    result = auth.register_user(
        name=data.get("name"), email=data.get("email"), phone=data.get("phone", ""),
        password=data.get("password"),
        subject_interest=data.get("subject_interest", ""), education_level=data.get("education_level", ""),
    )
    if result["success"]:
        send_welcome_email(data.get("email"), data.get("name"))
    return jsonify(result), (200 if result["success"] else 400)


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    result = auth.login_user(
        identifier=data.get("identifier"), method=data.get("method", "email"),
        password=data.get("password")
    )
    return jsonify(result), (200 if result["success"] else 401)


@app.route("/api/auth/verify", methods=["GET"])
def verify_session():
    user = get_user_from_request()
    if not user:
        return jsonify({"valid": False}), 401
    return jsonify({"valid": True, "user": user.to_public_dict()})


@app.route("/api/auth/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json or {}
    email = (data.get("email") or "").strip()
    frontend_url = (data.get("frontend_url") or "").rstrip("/")

    token = auth.request_password_reset(email)
    if token and frontend_url:
        reset_link = f"{frontend_url}/reset-password.html?token={token}"
        send_password_reset_email(email, reset_link)
    return jsonify({"success": True, "message": "If that email has an account, a reset link is on its way."})


@app.route("/api/auth/reset-password", methods=["POST"])
def do_reset_password():
    data = request.json or {}
    token = data.get("token")
    password = data.get("password")
    if not token or not password or len(password) < 8:
        return jsonify({"success": False, "message": "Please provide a token and an 8+ character password"}), 400
    result = auth.reset_password(token, password)
    return jsonify(result), (200 if result["success"] else 400)


# ─────────────────────────────────────────────
# PROFILE ROUTES
# ─────────────────────────────────────────────

@app.route("/api/user/profile", methods=["PUT"])
def update_profile():
    user = get_user_from_request()
    if not user:
        return jsonify({"success": False, "message": "Not signed in"}), 401
    data = request.json or {}
    result = auth.update_profile(
        email=user.email, name=data.get("name"), new_email=data.get("email"),
        subject_interest=data.get("subject_interest"),
        education_level=data.get("education_level"), new_password=data.get("password") or None,
    )
    return jsonify(result), (200 if result["success"] else 400)


# ─────────────────────────────────────────────
# CHATBOT
# ─────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user = get_user_from_request()
    return jsonify({"response": get_chatbot_response(data.get("message", ""), user.email if user else None)})


# ─────────────────────────────────────────────
# UNIVERSITY FINDER (AI ADVISOR) — the new core feature
# ─────────────────────────────────────────────

@app.route("/api/advisor/recommend", methods=["POST"])
def advisor_recommend():
    data = request.json or {}
    required_missing = [k for k in ("name", "education_level", "marks_obtained", "marks_total", "interest", "country") if not str(data.get(k, "")).strip()]
    if required_missing:
        return jsonify({"success": False, "message": f"Please fill in: {', '.join(required_missing)}"}), 400

    result = get_recommendation(data)

    email = data.get("email")
    if email:
        label = f"AI Recommendation: {result.get('field', data.get('interest'))}"
        count = (1 if result.get("home_pick") else 0) + (1 if result.get("target_pick") else 0)
        auth.add_search_to_history(email, label, [c for c in [result.get("home_country_resolved"), result.get("target_country_resolved")] if c], count)

    return jsonify({"success": True, "result": result})


# ─────────────────────────────────────────────
# UNIVERSITY SEARCH + DIRECTORY + COUNTRIES + CALCULATOR + TESTS + SCHOLARSHIPS
# ─────────────────────────────────────────────

@app.route("/api/universities/search", methods=["POST"])
def search():
    data = request.json or {}
    query = data.get("query", "")
    countries = data.get("countries") or None
    field = data.get("field", "all")
    degree_level = data.get("degree_level", "all")
    email = data.get("email")

    programs = search_universities(query, countries, field, degree_level)

    if email:
        auth.add_search_to_history(email, query, countries or [], len(programs))

    return jsonify({"programs": programs, "count": len(programs)})


@app.route("/api/universities/directory", methods=["GET"])
def directory():
    country = request.args.get("country")
    return jsonify({"directory": get_university_directory(country)})


@app.route("/api/universities/featured", methods=["GET"])
def featured():
    """A handful of #1-ranked universities from different countries, for the
    home page's 'Explore the database' preview — not personalized, just a
    rotating sample so the home page doesn't always show the same 6."""
    db = get_db()
    try:
        top_ones = db.query(University).filter(University.rank_in_country == 1).all()
        sample = random.sample(top_ones, min(6, len(top_ones)))
        return jsonify({"universities": [u.to_dict(include_programs=True) for u in sample]})
    finally:
        db.close()


@app.route("/api/countries", methods=["GET"])
def countries():
    return jsonify({"countries": list_countries_summary()})


@app.route("/api/countries/names", methods=["GET"])
def country_names():
    return jsonify({"countries": list_all_country_names()})


@app.route("/api/countries/<country_name>/formulas", methods=["GET"])
def country_formulas(country_name):
    return jsonify({"formulas": get_formulas_for_country(country_name)})


@app.route("/api/calculator", methods=["POST"])
def calculator():
    data = request.json or {}
    result = evaluate_formula(data.get("formula_id"), data.get("scores", {}))
    return jsonify(result), (200 if result.get("success") else 400)


@app.route("/api/tests", methods=["GET"])
def tests():
    db = get_db()
    try:
        rows = db.query(TestInfo).order_by(TestInfo.name).all()
        return jsonify({"tests": [{
            "id": t.id, "name": t.name, "subjects": t.subjects,
            "syllabus_summary": t.syllabus_summary, "official_prep_link": t.official_prep_link,
        } for t in rows]})
    finally:
        db.close()


@app.route("/api/scholarships", methods=["GET"])
def scholarships():
    country = request.args.get("country")
    db = get_db()
    try:
        q = db.query(Scholarship).join(University).join(Country)
        if country:
            q = q.filter(Country.name.ilike(f"%{country}%"))
        rows = q.all()
        return jsonify({"scholarships": [{
            "id": s.id, "name": s.name, "university": s.university.name,
            "coverage": s.coverage, "eligibility": s.eligibility, "deadline": s.deadline,
        } for s in rows]})
    finally:
        db.close()


# ─────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────

@app.route("/api/notifications", methods=["GET"])
def get_notifications():
    user = get_user_from_request()
    if not user:
        return jsonify({"notifications": []})
    return jsonify({"notifications": auth.get_notifications(user.email)})


@app.route("/api/notifications/read", methods=["POST"])
def mark_notifications_read():
    user = get_user_from_request()
    if not user:
        return jsonify({"success": False}), 401
    auth.mark_notifications_read(user.email)
    return jsonify({"success": True})


# ─────────────────────────────────────────────
# SEARCH HISTORY
# ─────────────────────────────────────────────

@app.route("/api/search/history", methods=["GET"])
def search_history():
    email = request.args.get("email")
    if not email:
        return jsonify({"history": []})
    return jsonify({"history": auth.get_search_history(email)})


@app.route("/api/search/history", methods=["DELETE"])
def delete_search_history():
    user = get_user_from_request()
    if not user:
        return jsonify({"success": False, "message": "Not signed in"}), 401
    auth.clear_search_history(user.email)
    return jsonify({"success": True})


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({
        "status": "Student Next.ai backend is running",
        "database": os.getenv("DATABASE_URL", "sqlite (local file)"),
        "endpoints": [
            "/api/auth/register", "/api/auth/login", "/api/auth/verify",
            "/api/auth/forgot-password", "/api/auth/reset-password",
            "/api/user/profile",
            "/api/chat", "/api/advisor/recommend",
            "/api/universities/search", "/api/universities/directory", "/api/universities/featured",
            "/api/countries", "/api/countries/names", "/api/calculator",
            "/api/tests", "/api/scholarships",
            "/api/notifications", "/api/notifications/read",
            "/api/search/history",
        ]
    })


if __name__ == "__main__":
    print("=" * 50)
    print("  STUDENT NEXT.AI BACKEND SERVER STARTING")
    print("  Visit: http://127.0.0.1:5000/api/health")
    print("=" * 50)
    app.run(debug=True, port=5000, use_reloader=False)
