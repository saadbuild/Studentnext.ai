"""
STUDENT NEXT.AI UNIVERSITY MATCHER

WHY THIS DOESN'T HIT LIVE EXTERNAL APIS: there is no open, free, keyless
"live university admissions" API the way there is for job boards like
Remotive/RemoteOK. University fees, aggregate cutoffs, and admission
windows are published individually by each institution and change
yearly — the honest approach is a locally-seeded, source-linked dataset
(see seed.py, now 410 universities across 137 countries) rather than
pretending to scrape hundreds of university websites live.
search_universities() below queries that local dataset; get_top_universities()
and get_directory() back the new AI University Finder and the Guide
platform's university directory.

v3 CHANGES: removed the transcript-matching pipeline entirely (TF-IDF
cosine similarity between an uploaded PDF/DOCX and program descriptions)
— the My Transcript feature was removed at the user's request, and
dropping it also removes the pypdf/python-docx/scikit-learn dependencies.
"""

import re

from models import get_db, University, Program, Country


def strip_html(text):
    return re.sub("<[^<]+?>", " ", text or "").strip()


# ─────────────────────────────────────────────
# SEARCH (queries the local seeded dataset)
# ─────────────────────────────────────────────

def search_universities(query="", countries=None, field="all", degree_level="all"):
    db = get_db()
    try:
        q = (db.query(Program))
        programs = q.all()

        results = []
        query_lower = (query or "").lower()
        for p in programs:
            uni = p.university
            country_name = uni.country.name

            if countries and country_name not in countries:
                continue
            if field != "all" and field.lower() not in (p.field or "").lower():
                continue
            if degree_level != "all" and degree_level.lower() not in (p.degree_level or "").lower():
                continue
            if query_lower:
                haystack = f"{uni.name} {p.name} {p.field} {country_name}".lower()
                if query_lower not in haystack and not any(w in haystack for w in query_lower.split()):
                    continue

            results.append(p.to_dict())

        return results
    finally:
        db.close()


def list_countries_summary():
    """Countries grid data: education system + how many universities/
    verified formulas are seeded for each — analog of the Jobsk 'Platforms'
    live-vs-guide-only badge, but honest about dataset depth instead."""
    db = get_db()
    try:
        out = []
        for c in db.query(Country).order_by(Country.name).all():
            uni_count = len(c.universities)
            formula_count = len(c.formulas)
            out.append({
                "name": c.name,
                "education_system": c.education_system,
                "grading_scale": c.grading_scale,
                "university_count": uni_count,
                "has_verified_formula": formula_count > 0,
            })
        return out
    finally:
        db.close()


def get_formulas_for_country(country_name):
    db = get_db()
    try:
        country = db.query(Country).filter(Country.name == country_name).first()
        if not country:
            return []
        return [{
            "id": f.id, "name": f.name, "components": f.components,
            "source_url": f.source_url,
            "last_verified": f.last_verified.isoformat() if f.last_verified else None,
        } for f in country.formulas]
    finally:
        db.close()


def evaluate_formula(formula_id, scores):
    """Generic weighted-formula evaluator — same idea as the Next.js/FastAPI
    version's calculator_service.py, just living here since this is a
    single-file-per-concern Flask app rather than a router-per-file one."""
    from models import AggregateFormula
    db = get_db()
    try:
        formula = db.get(AggregateFormula, formula_id)
        if not formula:
            return {"success": False, "message": "Unknown formula_id"}

        total = 0.0
        breakdown = []
        for component in formula.components:
            key = component["key"]
            weight = component["weight"]
            label = component.get("label", key)
            if key not in scores:
                return {"success": False, "message": f"Missing required score: {key} ({label})"}
            raw_score = float(scores[key])
            if not (0 <= raw_score <= 100):
                return {"success": False, "message": f"{label} must be between 0 and 100"}
            contribution = raw_score * weight
            total += contribution
            breakdown.append({
                "key": key, "label": label, "score_pct": raw_score,
                "weight": weight, "contribution": round(contribution, 2),
            })
        return {"success": True, "aggregate": round(total, 2), "breakdown": breakdown}
    finally:
        db.close()


# ─────────────────────────────────────────────
# UNIVERSITY FINDER (AI advisor) + GUIDE DIRECTORY
# ─────────────────────────────────────────────

def get_top_universities(country_name, limit=5):
    """Top-ranked (rank_in_country order) universities for one country —
    used by the AI advisor to ground its "best in your country" /
    "best in <abroad country>" picks in real seeded data."""
    db = get_db()
    try:
        country = db.query(Country).filter(Country.name.ilike(country_name.strip())).first()
        if not country:
            # loose fallback: partial match, in case of "USA" vs "United States" etc.
            country = db.query(Country).filter(Country.name.ilike(f"%{country_name.strip()}%")).first()
        if not country:
            return None, []
        unis = sorted(country.universities, key=lambda u: (u.rank_in_country or 99))[:limit]
        return country.name, [u.to_dict() for u in unis]
    finally:
        db.close()


def list_all_country_names():
    db = get_db()
    try:
        return [c.name for c in db.query(Country).order_by(Country.name).all()]
    finally:
        db.close()


def get_university_directory(country_name=None):
    """Full guide-platform directory: every seeded university (optionally
    filtered to one country), each with its complete admission guide
    (test, aggregate note, syllabus, how to apply, official link)."""
    db = get_db()
    try:
        q = db.query(Country).order_by(Country.name)
        if country_name:
            q = q.filter(Country.name.ilike(country_name.strip()))
        out = []
        for c in q.all():
            unis = sorted(c.universities, key=lambda u: (u.rank_in_country or 99))
            out.append({
                "country": c.name,
                "education_system": c.education_system,
                "grading_scale": c.grading_scale,
                "universities": [u.to_dict() for u in unis],
            })
        return out
    finally:
        db.close()


