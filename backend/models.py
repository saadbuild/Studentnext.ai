"""
STUDENT NEXT.AI DATABASE MODELS
================================
Real database (SQLite by default, Postgres if you set DATABASE_URL)
instead of JSON files, because free hosts wipe local disk on every
restart/redeploy.

DATABASE_URL env var:
    - Not set -> local SQLite file studentnext.db (fine for dev, and for
      production if your host gives you a persistent disk).
    - Set to a Postgres URL (Supabase, Neon, Render Postgres free tier) ->
      uses that instead, so accounts survive restarts on a free host.

v3 CHANGES (AI University Finder rebuild):
    - Removed User.country / reco_country / reco_field — the old rigid
      15-item country dropdown collected once at signup. The University
      Finder now asks for "home country" and "target country" fresh on
      every search instead (free text, works for any of the 100+ countries
      in the dataset, not just a hardcoded 15).
    - Removed User.last_transcript_subjects and the transcript-matching
      pipeline entirely (My Transcript feature removed at the user's
      request) — TF-IDF/pypdf/python-docx dependencies dropped too.
    - Removed the Skill / roadmap model (Skills Roadmap feature removed).
    - Country / University / Program / Test / Scholarship / AggregateFormula
      remain — this is the real local dataset (now ~410 universities
      across 100+ countries, see seed.py) that every factual claim in the
      app (fees, aggregates, tests, admission steps) is grounded in.
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Load .env here, first, before DATABASE_URL is read below. Previously only
# emailer.py called load_dotenv(), which ran too late (after this module had
# already fallen back to SQLite) or not at all (seed.py never imports
# emailer.py) -- so a DATABASE_URL set only in .env was silently ignored.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    db_path = os.path.join(os.path.dirname(__file__), "studentnext.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# ─────────────────────────────────────────────
# AUTH / ACCOUNT TABLES
# ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True)
    name = Column(String, nullable=False, default="")
    phone = Column(String, default="")
    password_hash = Column(String, nullable=True)  # null for Google-only accounts
    provider = Column(String, default="email")
    created_at = Column(DateTime, default=datetime.utcnow)

    subject_interest = Column(String, default="")
    education_level = Column(String, default="")

    def to_public_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "provider": self.provider,
            "subject_interest": self.subject_interest,
            "education_level": self.education_level,
        }


class Session(Base):
    __tablename__ = "sessions"

    token = Column(String, primary_key=True)
    email = Column(String, ForeignKey("users.email"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)


class SearchHistoryItem(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, ForeignKey("users.email"), nullable=False)
    query = Column(String, default="")
    countries = Column(String, default="[]")  # JSON list
    result_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, ForeignKey("users.email"), nullable=False)
    title = Column(String, default="")
    body = Column(Text, default="")
    kind = Column(String, default="info")  # info | transcript
    created_at = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)


class PasswordReset(Base):
    __tablename__ = "password_resets"

    token = Column(String, primary_key=True)
    email = Column(String, ForeignKey("users.email"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)


# ─────────────────────────────────────────────
# EDUCATION DATASET TABLES
# ─────────────────────────────────────────────

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    education_system = Column(String, default="")
    grading_scale = Column(String, default="")

    universities = relationship("University", back_populates="country")
    formulas = relationship("AggregateFormula", back_populates="country")


class AggregateFormula(Base):
    """A real, verified weighted formula. Only wired up where a university
    actually publishes one (see seed.py docstring) -- everything else uses
    aggregate_note on Program instead of a fake formula."""
    __tablename__ = "aggregate_formulas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    name = Column(String, nullable=False)
    components = Column(JSON, nullable=False)  # [{key, label, weight}, ...]
    source_url = Column(String, default="")
    last_verified = Column(DateTime, nullable=True)

    country = relationship("Country", back_populates="formulas")


class TestInfo(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    subjects = Column(JSON, default=list)
    syllabus_summary = Column(Text, default="")
    official_prep_link = Column(String, default="")


class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    name = Column(String, nullable=False)
    city = Column(String, default="")
    address = Column(String, default="")
    website = Column(String, default="")
    description = Column(Text, default="")
    rank_in_country = Column(Integer, default=1)  # 1 = top-ranked in that country, within our seeded top-5

    country = relationship("Country", back_populates="universities")
    programs = relationship("Program", back_populates="university")
    scholarships = relationship("Scholarship", back_populates="university")

    def to_dict(self, include_programs=True):
        out = {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "country": self.country.name if self.country else "",
            "address": self.address,
            "website": self.website,
            "description": self.description,
            "rank_in_country": self.rank_in_country,
        }
        if include_programs:
            out["programs"] = [p.to_dict() for p in self.programs]
            out["scholarships"] = [{
                "name": s.name, "coverage": s.coverage,
                "eligibility": s.eligibility, "deadline": s.deadline,
            } for s in self.scholarships]
        return out


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=True)
    formula_id = Column(Integer, ForeignKey("aggregate_formulas.id"), nullable=True)

    name = Column(String, nullable=False)
    field = Column(String, default="")
    degree_level = Column(String, default="Undergraduate")
    duration_years = Column(Float, nullable=True)

    fee_amount = Column(Float, nullable=True)
    fee_currency = Column(String, default="")
    fee_period = Column(String, default="")
    fee_note = Column(String, default="")

    aggregate_required_min = Column(Float, nullable=True)
    aggregate_note = Column(Text, default="")

    admission_opens = Column(String, default="")
    admission_closes = Column(String, default="")
    how_to_apply = Column(Text, default="")
    admission_source_url = Column(String, default="")

    university = relationship("University", back_populates="programs")
    test = relationship("TestInfo")
    formula = relationship("AggregateFormula")

    def to_dict(self):
        return {
            "id": self.id,
            "university": self.university.name,
            "university_id": self.university_id,
            "city": self.university.city,
            "country": self.university.country.name,
            "name": self.name,
            "field": self.field,
            "degree_level": self.degree_level,
            "duration_years": self.duration_years,
            "fee_amount": self.fee_amount,
            "fee_currency": self.fee_currency,
            "fee_period": self.fee_period,
            "fee_note": self.fee_note,
            "aggregate_required_min": self.aggregate_required_min,
            "aggregate_note": self.aggregate_note,
            "test": self.test.name if self.test else None,
            "test_subjects": (self.test.subjects if self.test else []) or [],
            "syllabus_summary": (self.test.syllabus_summary if self.test else "") or "",
            "official_prep_link": (self.test.official_prep_link if self.test else "") or "",
            "formula_id": self.formula_id,
            "admission_opens": self.admission_opens,
            "admission_closes": self.admission_closes,
            "how_to_apply": self.how_to_apply,
            "admission_source_url": self.admission_source_url,
        }


class Scholarship(Base):
    __tablename__ = "scholarships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    name = Column(String, nullable=False)
    coverage = Column(String, default="")
    eligibility = Column(Text, default="")
    deadline = Column(String, default="")
    source_url = Column(String, default="")

    university = relationship("University", back_populates="scholarships")


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    return SessionLocal()
