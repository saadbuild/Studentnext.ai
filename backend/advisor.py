"""
STUDENT NEXT.AI — UNIVERSITY FINDER ADVISOR
=============================================
The engine behind the "University Finder" screen. The person fills in a
short form (name, education level, marks obtained / marks total, field
of interest, home country, and optionally a target country to study
abroad in) and this module returns:

    1. A suggested field of study (matched from their stated interest)
       plus a short note on that field's real-world scope/demand.
    2. The best-ranked university FOR THAT FIELD in their home country,
       pulled from the real seeded dataset (see seed.py) — never invented.
    3. The best-ranked university in their chosen abroad country (or a
       sensible popular-destination default if they didn't pick one),
       same grounding rule.
    4. A full admission guide for each pick: test name, aggregate note,
       syllabus summary, how to apply, and the official link.

GROUNDING RULE (same discipline as chatbot.py): every specific university
name, test name, and admission fact returned to the person comes from the
local database (seed.py's 410 universities / 137 countries) — never from
the LLM's own "knowledge" of universities that might be outdated, wrong,
or outright invented. The optional Claude call below is used only to (a)
map free-text "interest" onto a sensible field of study and (b) write a
short, encouraging "scope" paragraph — both general-knowledge career
advice, not factual claims about a specific institution. If no
ANTHROPIC_API_KEY is set, a rule-based keyword matcher handles the field
mapping instead and a short canned scope note is used — still fully
functional, just less nuanced.
"""

import os
import json
import re

from models import get_db, Country, University, Program
from university_matcher import get_top_universities, list_all_country_names

FIELD_KEYWORDS = {
    "Computer Science": ["computer", "programming", "software", "coding", "code", "web", "app development", "cs", "it", "information technology", "developer", "tech"],
    "Artificial Intelligence & Data Science": ["ai", "artificial intelligence", "machine learning", "data science", "data analytics", "ml", "robot", "algorithm"],
    "Engineering": ["engineer", "mechanical", "electrical", "civil", "robotics", "electronics", "build things", "machines", "construction"],
    "Medicine & Health Sciences": ["medicine", "doctor", "medical", "health", "nursing", "nurse", "pharmacy", "dentist", "surgeon", "mbbs", "sick people", "human body", "hospital", "patient", "cure", "treat", "biology", "anatomy", "helping people heal"],
    "Business Administration": ["business", "management", "entrepreneur", "marketing", "mba", "commerce", "start a company", "run a company", "startup"],
    "Economics & Finance": ["finance", "economics", "banking", "accounting", "investment", "financial", "money", "stock market", "trading"],
    "Law": ["law", "legal", "lawyer", "llb", "justice", "courtroom", "advocate", "attorney"],
    "Natural Sciences": ["physics", "chemistry", "science", "research", "lab", "experiments", "space", "astronomy"],
    "Social Sciences": ["psychology", "sociology", "political", "international relations", "social work", "anthropology", "helping people", "mental health", "counseling", "human behavior"],
    "Architecture & Design": ["architecture", "design", "interior", "urban planning", "graphic design", "buildings", "creative", "drawing"],
    "Agriculture & Environmental Science": ["agriculture", "farming", "environment", "climate", "sustainability", "ecology", "plants", "nature"],
    "Arts & Humanities": ["art", "history", "literature", "philosophy", "language", "humanities", "media", "journalism", "writing", "storytelling", "film"],
}

FIELD_SCOPE_FALLBACK = {
    "Computer Science": "Computer Science remains one of the highest-demand fields worldwide — software, cloud, and IT roles are hiring across almost every industry and country, with strong remote/freelance options too.",
    "Artificial Intelligence & Data Science": "AI and Data Science are among the fastest-growing fields globally right now, with strong demand in tech, finance, healthcare, and research — though it's also increasingly competitive at the entry level.",
    "Engineering": "Engineering (mechanical, electrical, civil, and beyond) has stable, broad global demand — infrastructure, energy, and manufacturing all need engineers, and it's a strong base for further specialization.",
    "Medicine & Health Sciences": "Medicine and health sciences have very high, stable global demand (aging populations, healthcare expansion) but require a long, competitive, and expensive training pathway — plan for that upfront.",
    "Business Administration": "Business Administration is broadly useful and globally portable, with demand across every industry — outcomes vary a lot by specialization (finance/consulting pay more than generalist management roles).",
    "Economics & Finance": "Economics & Finance graduates are in strong demand in banking, consulting, and policy roles worldwide, especially with quantitative skills layered on top.",
    "Law": "Law is a respected, stable field, but it's highly jurisdiction-specific — qualifications usually don't transfer across countries without additional local exams, so plan around where you actually want to practice.",
    "Natural Sciences": "Natural Sciences (physics, chemistry, biology) are foundational for research and R&D-heavy industries — strong for further postgraduate study, though undergraduate-only roles are narrower than applied fields.",
    "Social Sciences": "Social Sciences graduates work across NGOs, government, research, HR, and media — broad and globally relevant, though often benefiting from a postgraduate specialization for stronger job prospects.",
    "Architecture & Design": "Architecture & Design have steady demand tied to construction and urbanization — strong in fast-growing cities, with design skills increasingly valuable in tech/product roles too.",
    "Agriculture & Environmental Science": "Agriculture & Environmental Science are growing fields globally as climate and food-security concerns rise — strong government and NGO demand alongside private-sector agri-tech roles.",
    "Arts & Humanities": "Arts & Humanities open doors into media, education, publishing, and culture — outcomes vary widely by specialization, and many graduates pair it with a professional postgraduate qualification.",
}

POPULAR_ABROAD_DEFAULTS = ["United States", "United Kingdom", "Canada", "Australia", "Germany"]


def _keyword_match_field(interest_text):
    text = (interest_text or "").lower()
    best_field, best_hits = None, 0
    for field, keywords in FIELD_KEYWORDS.items():
        hits = sum(1 for k in keywords if k in text)
        if hits > best_hits:
            best_field, best_hits = field, hits
    return best_field or "Computer Science"


def _rule_based_recommendation(interest_text):
    field = _keyword_match_field(interest_text)
    return field, FIELD_SCOPE_FALLBACK.get(field, FIELD_SCOPE_FALLBACK["Computer Science"])


def _claude_field_and_scope(profile):
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    known_fields = list(FIELD_KEYWORDS.keys())
    system = (
        "You are a university/career counselor. Given a student's stated interest, marks, and "
        "education level, pick the SINGLE best-matching field of study from this exact list "
        f"(reply with one of these strings verbatim as \"field\"): {known_fields}. "
        "Then write a 2-3 sentence, honest, encouraging note on that field's real-world global "
        "career scope/demand right now — mention both the upside and any realistic caveat "
        "(competitiveness, licensing, length of training, etc). "
        "Reply with ONLY raw JSON, no markdown fences, no preamble: "
        '{"field": "...", "scope": "..."}'
    )
    user_msg = (
        f"Education level: {profile.get('education_level')}\n"
        f"Marks: {profile.get('marks_obtained')} out of {profile.get('marks_total')}\n"
        f"Stated interest: {profile.get('interest')}\n"
    )
    resp = client.messages.create(
        model="claude-sonnet-5", max_tokens=400, system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    data = json.loads(text)
    field = data.get("field") if data.get("field") in FIELD_KEYWORDS else _keyword_match_field(profile.get("interest"))
    scope = data.get("scope") or FIELD_SCOPE_FALLBACK.get(field, "")
    return field, scope


def _pick_best_for_field(universities, field):
    """Prefer a university whose seeded program field matches; otherwise
    just return the top-ranked (#1) university in that country/list —
    still real, still grounded, just not field-specific."""
    if not universities:
        return None
    field_lower = field.lower()
    for u in universities:
        for p in u.get("programs", []):
            if field_lower in (p.get("field") or "").lower():
                return u
    return universities[0]


def get_recommendation(profile):
    """
    profile: {
        "name": str, "education_level": str,
        "marks_obtained": float, "marks_total": float,
        "interest": str, "country": str (home country),
        "target_country": str (optional, abroad country),
    }
    Returns a dict ready to hand straight to the frontend.
    """
    interest = (profile.get("interest") or "").strip()
    home_country_input = (profile.get("country") or "").strip()
    target_country_input = (profile.get("target_country") or "").strip()

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    field, scope = None, None
    if api_key:
        try:
            field, scope = _claude_field_and_scope(profile)
        except Exception as e:
            print(f"[advisor] Claude call failed, falling back to rule-based: {e}")
    if not field:
        field, scope = _rule_based_recommendation(interest)

    percentage = None
    try:
        obtained = float(profile.get("marks_obtained"))
        total = float(profile.get("marks_total"))
        if total > 0:
            percentage = round(obtained / total * 100, 1)
    except (TypeError, ValueError):
        pass

    home_name, home_unis = (None, [])
    if home_country_input:
        home_name, home_unis = get_top_universities(home_country_input, limit=5)
    home_pick = _pick_best_for_field(home_unis, field)

    target_name, target_unis = (None, [])
    tried_defaults = []
    if target_country_input:
        target_name, target_unis = get_top_universities(target_country_input, limit=5)
    if not target_unis:
        # no valid target country given/found — try a few popular study-abroad
        # destinations (skipping the home country itself) until one resolves
        for candidate in POPULAR_ABROAD_DEFAULTS:
            if home_name and candidate.lower() == home_name.lower():
                continue
            tried_defaults.append(candidate)
            target_name, target_unis = get_top_universities(candidate, limit=5)
            if target_unis:
                break
    target_pick = _pick_best_for_field(target_unis, field)

    return {
        "profile_summary": {
            "name": profile.get("name") or "there",
            "education_level": profile.get("education_level") or "",
            "percentage": percentage,
        },
        "field": field,
        "scope": scope,
        "home_country_resolved": home_name,
        "home_country_input": home_country_input,
        "home_pick": home_pick,
        "home_alternatives": [u for u in home_unis if home_pick and u["id"] != home_pick["id"]],
        "target_country_resolved": target_name,
        "target_country_input": target_country_input or None,
        "used_default_abroad_country": bool(target_name and not target_country_input),
        "target_pick": target_pick,
        "target_alternatives": [u for u in target_unis if target_pick and u["id"] != target_pick["id"]],
        "ai_powered": bool(api_key),
    }
