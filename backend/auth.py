"""
STUDENT NEXT.AI AUTHENTICATION MODULE
Registration, login (email/phone), password hashing, session tokens, and
profile updates that actually persist (not a fake "saved!" toast that
touches nothing).

v3 CHANGES: removed Google sign-in (login_or_register_google — the
Google button was removed from the front page/login screen), the
country/reco_country/reco_field profile fields (the University Finder
now asks for "home country" and "target country" fresh on every search
instead of once at signup), and save_transcript_subjects (My Transcript
feature removed).
"""

import hashlib
import json
import secrets
from datetime import datetime, timedelta

from models import get_db, User, Session, SearchHistoryItem, Notification, PasswordReset


def hash_password(password):
    """
    NOTE: for a real production launch, swap this for bcrypt or argon2
    (pip install bcrypt) -- purpose-built to resist offline cracking in a
    way plain salted SHA-256 is not.
    """
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password, stored_hash):
    try:
        salt, hashed = stored_hash.split("$")
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    except Exception:
        return False


def generate_token(email):
    token = secrets.token_urlsafe(32)
    db = get_db()
    try:
        db.add(Session(
            token=token, email=email,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        ))
        db.commit()
    finally:
        db.close()
    return token


def get_user_from_token(token):
    if not token:
        return None
    db = get_db()
    try:
        session = db.get(Session, token)
        if not session or session.expires_at < datetime.utcnow():
            return None
        return db.get(User, session.email)
    finally:
        db.close()


def register_user(name, email, phone, password, subject_interest="", education_level=""):
    db = get_db()
    try:
        if not name or not email or not password:
            return {"success": False, "message": "Please fill in all required fields"}
        if len(password) < 8:
            return {"success": False, "message": "Password must be at least 8 characters"}

        if db.get(User, email):
            return {"success": False, "message": "Email already registered"}

        if phone:
            existing_phone = db.query(User).filter(User.phone == phone).first()
            if existing_phone:
                return {"success": False, "message": "Phone number already registered"}

        user = User(
            name=name, email=email, phone=phone,
            password_hash=hash_password(password),
            provider="email", created_at=datetime.utcnow(),
            subject_interest=subject_interest, education_level=education_level,
        )
        db.add(user)
        db.commit()

        token = generate_token(email)
        return {"success": True, "token": token, "user": user.to_public_dict()}
    finally:
        db.close()


def login_user(identifier, method, password):
    db = get_db()
    try:
        user = None
        if method == "email":
            user = db.get(User, identifier)
        elif method == "phone":
            user = db.query(User).filter(User.phone == identifier).first()

        if not user:
            return {"success": False, "message": "Account not found"}
        if not user.password_hash or not verify_password(password, user.password_hash):
            return {"success": False, "message": "Incorrect password"}

        token = generate_token(user.email)
        return {"success": True, "token": token, "user": user.to_public_dict()}
    finally:
        db.close()


def update_profile(email, name=None, new_email=None, subject_interest=None,
                    education_level=None, new_password=None):
    db = get_db()
    try:
        user = db.get(User, email)
        if not user:
            return {"success": False, "message": "User not found"}

        if new_email and new_email != email:
            if db.get(User, new_email):
                return {"success": False, "message": "That email is already in use"}
            old_sessions = db.query(Session).filter(Session.email == email).all()
            old_history = db.query(SearchHistoryItem).filter(SearchHistoryItem.email == email).all()
            old_notifs = db.query(Notification).filter(Notification.email == email).all()

            new_user = User(**{c.name: getattr(user, c.name) for c in User.__table__.columns})
            new_user.email = new_email
            db.add(new_user)
            db.flush()
            for s in old_sessions:
                s.email = new_email
            for h in old_history:
                h.email = new_email
            for n in old_notifs:
                n.email = new_email
            db.flush()
            db.delete(user)
            user = new_user

        if name:
            user.name = name
        if subject_interest is not None:
            user.subject_interest = subject_interest
        if education_level is not None:
            user.education_level = education_level
        if new_password:
            user.password_hash = hash_password(new_password)

        db.commit()
        return {"success": True, "user": user.to_public_dict()}
    finally:
        db.close()


def add_search_to_history(email, query, countries, result_count):
    db = get_db()
    try:
        if not db.get(User, email):
            return False
        db.add(SearchHistoryItem(
            email=email, query=query, countries=json.dumps(countries),
            result_count=result_count, timestamp=datetime.utcnow()
        ))
        rows = (db.query(SearchHistoryItem)
                .filter(SearchHistoryItem.email == email)
                .order_by(SearchHistoryItem.timestamp.desc()).all())
        for old in rows[50:]:
            db.delete(old)
        db.commit()
        return True
    finally:
        db.close()


def get_search_history(email):
    db = get_db()
    try:
        rows = (db.query(SearchHistoryItem)
                .filter(SearchHistoryItem.email == email)
                .order_by(SearchHistoryItem.timestamp.desc()).limit(50).all())
        return [{
            "query": r.query,
            "countries": json.loads(r.countries or "[]"),
            "result_count": r.result_count,
            "timestamp": r.timestamp.isoformat()
        } for r in rows]
    finally:
        db.close()


def clear_search_history(email):
    db = get_db()
    try:
        db.query(SearchHistoryItem).filter(SearchHistoryItem.email == email).delete()
        db.commit()
        return True
    finally:
        db.close()


def request_password_reset(email):
    db = get_db()
    try:
        user = db.get(User, email)
        if not user:
            return None
        token = secrets.token_urlsafe(32)
        db.add(PasswordReset(
            token=token, email=email, created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1), used=False
        ))
        db.commit()
        return token
    finally:
        db.close()


def reset_password(token, new_password):
    db = get_db()
    try:
        reset = db.get(PasswordReset, token)
        if not reset or reset.used or reset.expires_at < datetime.utcnow():
            return {"success": False, "message": "This reset link is invalid or has expired"}
        user = db.get(User, reset.email)
        if not user:
            return {"success": False, "message": "Account not found"}
        user.password_hash = hash_password(new_password)
        reset.used = True
        db.commit()
        return {"success": True}
    finally:
        db.close()


def add_notification(email, title, body, kind="info"):
    db = get_db()
    try:
        db.add(Notification(email=email, title=title, body=body, kind=kind,
                             created_at=datetime.utcnow(), read=False))
        db.commit()
    finally:
        db.close()


def get_notifications(email, limit=30):
    db = get_db()
    try:
        rows = (db.query(Notification)
                .filter(Notification.email == email)
                .order_by(Notification.created_at.desc()).limit(limit).all())
        return [{
            "id": r.id, "title": r.title, "body": r.body, "kind": r.kind,
            "created_at": r.created_at.isoformat(), "read": r.read
        } for r in rows]
    finally:
        db.close()


def mark_notifications_read(email):
    db = get_db()
    try:
        db.query(Notification).filter(Notification.email == email).update({"read": True})
        db.commit()
        return True
    finally:
        db.close()
