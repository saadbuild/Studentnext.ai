"""
STUDENT NEXT.AI CHATBOT

WORTH KNOWING (ported honestly from the Jobsk pattern): the default "AI
Agent Chat" here is a rule-based keyword matcher, not a real language
model -- fast, free, works offline. If you set ANTHROPIC_API_KEY in .env,
it calls the real Claude API instead, grounded in your actual seeded
dataset (see _build_context below) rather than answering from general
training knowledge -- so it won't invent a fee or aggregate cutoff that
isn't in your database.

    pip install anthropic   (already in requirements.txt)
    .env:  ANTHROPIC_API_KEY=sk-ant-...

Real per-message cost once you add a key -- small, but not zero.
"""

import os
import json

"""
STUDENT NEXT.AI CHATBOT

WORTH KNOWING: the default "AI Agent Chat" here is a rule-based keyword
matcher, not a real language model -- fast, free, works offline. If you
set ANTHROPIC_API_KEY in .env, it calls the real Claude API instead,
grounded in your actual seeded dataset (see _build_context below)
rather than answering from general training knowledge -- so it won't
invent a fee or aggregate cutoff that isn't in your database. The same
grounding technique now also powers advisor.py (the University Finder).

    pip install anthropic   (already in requirements.txt)
    .env:  ANTHROPIC_API_KEY=sk-ant-...

Real per-message cost once you add a key -- small, but not zero.
"""

import os
import json

RESPONSES = {
    "aggregate": """How the aggregate calculator works:

1. Pick your country on the Calculator page
2. Enter your scores for each component it asks for (e.g. Matric %, FSc %, entry test %)
3. It multiplies each score by that component's real published weight and adds them up

Only Pakistan's NUST and FAST-NUCES have a verified weighted formula in the
calculator right now -- most other countries (US, UK, Gaokao, JEE, ATAR...)
use holistic or rank-based admission instead of a simple percentage, so
those show an explanation rather than a fake formula.""",

    "test": """Admission tests vary a lot by country -- we've got real ones
seeded for 137 countries now (Gaokao, JEE, YKS, ENEM, WASSCE, Bagrut + PET,
and more). Use University Finder and tell it your country to see the exact
test name, subjects, and syllabus summary for your top local universities,
or check the Guide tab's University Directory to browse any country directly.""",

    "scholarship": """Scholarships in the dataset are tagged per university —
check a university's card in the Guide directory or University Finder
results. Most fall into two categories: need-based (income-driven, no fixed
amount) and merit-based (tied to your aggregate or rank). Coverage and
deadlines vary a lot by country and university, so always confirm on the
official page before assuming eligibility.""",

    "default": """I can help with:
- How the aggregate calculator works
- What test a country/university requires
- Scholarships and how they're structured
- Using the University Finder to get a personalized recommendation

What would you like to know more about?"""
}


def _rule_based_response(message):
    msg = message.lower()
    if any(w in msg for w in ["aggregate", "calculat", "formula", "weight"]):
        return RESPONSES["aggregate"]
    if any(w in msg for w in ["test", "exam", "net", "jee", "gaokao", "sat", "ucas", "csat"]):
        return RESPONSES["test"]
    if any(w in msg for w in ["scholarship", "financial aid", "funding"]):
        return RESPONSES["scholarship"]
    return RESPONSES["default"]


def _build_context(user_email=None):
    """Pulls a small, relevant slice of the real dataset so the LLM answers
    are grounded in what's actually in the database, not invented."""
    from models import get_db, Program, User

    db = get_db()
    try:
        field = None
        if user_email:
            user = db.get(User, user_email)
            if user:
                field = user.subject_interest

        query = db.query(Program)
        programs = query.limit(40).all()
        if field:
            narrowed = [p for p in programs if field.lower() in (p.field or "").lower()]
            if narrowed:
                programs = narrowed

        context = {
            "matching_programs": [
                {
                    "university": p.university.name, "country": p.university.country.name,
                    "program": p.name, "test": p.test.name if p.test else None,
                    "aggregate_required_min": p.aggregate_required_min,
                    "aggregate_note": p.aggregate_note,
                    "fee_note": p.fee_note or f"{p.fee_amount} {p.fee_currency}" if p.fee_amount else p.fee_note,
                }
                for p in programs[:8]
            ],
        }
        return json.dumps(context, indent=2)
    finally:
        db.close()


def _claude_response(message, user_email=None):
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    context = _build_context(user_email)
    system = (
        "You are the Student Next.ai assistant. Help students with universities, "
        "aggregate calculations, admission tests, and scholarships. "
        "Ground factual claims (fees, aggregates, tests, deadlines) ONLY in the "
        "DATASET_CONTEXT below -- if it's not covered, say so and suggest checking "
        "the official university site rather than guessing a number.\n\n"
        f"DATASET_CONTEXT:\n{context}\n\n"
        "Keep answers concise, concrete, and encouraging."
    )
    resp = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=500,
        system=system,
        messages=[{"role": "user", "content": message}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")


def get_chatbot_response(message, user_email=None):
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if api_key:
        try:
            return _claude_response(message, user_email)
        except Exception as e:
            print(f"[chatbot] Claude API call failed, falling back to rule-based: {e}")
    return _rule_based_response(message)
