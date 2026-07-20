# Student Next.ai — University Finder edition

An AI-powered university-matching platform: a student fills in their
marks, interest, and country, and the **University Finder** suggests a
field of study, its real-world global scope, and the best-matched real
university at home and abroad — pulled from a local dataset of **410
universities across 137 countries** (a curated top-5, or fewer where a
country genuinely doesn't have 5, per country), not invented on the fly.

Single Flask app + vanilla HTML/CSS/JS frontend, SQLAlchemy models,
no build step.

## Project structure

```
studentnext-vercel/
├── app.py                 Flask routes
├── auth.py                 Registration, login, sessions, password reset
├── models.py               SQLAlchemy models (users + education dataset)
├── seed.py                 Populates the 137-country / 410-university dataset
├── advisor.py              University Finder AI recommendation engine (NEW)
├── chatbot.py              Rule-based fallback + optional real Claude API
├── emailer.py              Welcome + password-reset email (Gmail SMTP)
├── university_matcher.py   Search + directory + calculator logic
├── requirements.txt
├── vercel.json             Routes /api/* to Flask, everything else to public/
└── public/                 Static frontend (no build step)
    ├── index.html
    ├── css/style.css
    ├── js/{config,auth,main}.js
    └── pages/{login,reset-password}.html
```

## Quick start (local)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # optional — every integration degrades gracefully without it
python seed.py            # populates 137 countries / 410 universities, safe to re-run
python app.py
```

Then open `public/index.html` directly in a browser, or serve `public/`
with any static server. `config.js`'s `BACKEND_URL = ''` assumes both are
reachable on the same origin (true once deployed via `vercel.json`); for
local dev, run `python -m http.server` inside `public/` and set
`BACKEND_URL = 'http://127.0.0.1:5000'` in `config.js`.

## Deploying

**Option A — everything on Vercel** (what `vercel.json` sets up): routes
`/api/*` to the Flask app as a Python serverless function, everything else
to the static `public/` folder. Set `DATABASE_URL` to a hosted Postgres
(Supabase/Neon free tier) in Vercel's environment variables — serverless
functions have no persistent disk, so SQLite would reset on every cold start.

**Option B — split hosting**: deploy `public/` to Vercel as a static site,
deploy the Flask app to Railway/Render (persistent disk, no cold-start
resets), and set `BACKEND_URL` in `public/js/config.js` to the backend's URL.

## What changed in this rebuild

- **University Finder (new core feature)** — replaces the old plain
  keyword search as the primary way to use the app. Fill in your name,
  education level, marks obtained/out of total, field of interest, home
  country, and (optionally) a country to study abroad in. `advisor.py`
  suggests a field of study and its real-world scope, then grounds its
  **best in your country** / **best abroad** picks in the actual seeded
  database — never an invented university. The old keyword/country/field
  search still exists, one tab over ("Browse Manually").
- **410 universities / 137 countries** (up from 31 / 15) — a curated top-5
  (or fewer, for countries without 5) per country, each with a real named
  admission system (Gaokao, JEE, YKS, ENEM, WASSCE, Bagrut+PET, CUET, and
  100+ more), plain-language aggregate guidance, syllabus summary, how to
  apply, and an official link.
- **Guide Platform** now has two tabs: the original test/application
  how-to articles, plus a new **University Directory** — browse any of
  the 137 countries and see its full top-5 with the same admission-guide
  detail as the Finder.
- **Removed:** Google sign-in (front page), My Transcript (upload +
  TF-IDF matching), Skills Roadmap, YouTube Study Videos, and the fixed
  15-item Country dropdown at signup — the Finder now asks for country
  fresh on every search instead of once at signup, which works for any
  of the 137 countries rather than a hardcoded 15.
- **Redesigned frontend** — new indigo/teal color system, a Sora display
  font for headings, subtle fade-in animations, a "what we offer" chip
  row on the home page, and a sidebar that stays a persistent 30%/70%
  split at every screen size (a compact icon-only rail below 640px,
  rather than a mobile drawer).

## Read this before you show it to real students

- **Verified**: NUST's and FAST-NUCES's aggregate formulas — checked
  against each university's own published admission criteria. These are
  the only two "exact weighted formula" entries in the whole dataset.
- **Deliberately blank**: every fee figure, and any per-university
  numeric aggregate cutoff beyond NUST/FAST — fees and cutoffs change
  yearly and weren't individually re-verified for 410 institutions. The
  UI shows a plain-language note ("check the official merit list/cutoff")
  instead of a number it can't stand behind.
- **Correctly modeled as non-percentage systems**: Gaokao, JEE, ATAR,
  Parcoursup, CSAT, ENEM, YKS, and 100+ more are rank/holistic-based —
  described in `aggregate_note` rather than forced into the
  weighted-percentage calculator, which would misrepresent how admission
  actually works there.
- The University Finder's "field of study" and "global scope" text is
  general career-advice content (from Claude if `ANTHROPIC_API_KEY` is
  set, or a rule-based keyword match otherwise) — it is **not** a
  factual claim about a specific institution. Only the university name,
  test, and admission guidance shown alongside it come from the seeded
  database.
- No past papers included — official entrance-test past papers are
  typically copyrighted by the issuing exam board; this repo links to
  official sources and writes original guide content instead.
- Full detail lives in the docstrings at the top of `seed.py` and `advisor.py`.

## Security notes

- Passwords are salted-hashed (see `auth.hash_password` — swap for
  bcrypt/argon2 before a real launch, noted inline in the code).
- Sessions are server-side tokens in a database table, not client-trusted JWTs.
- Password reset uses a one-time token, hashed at rest, expiring in 1 hour.
- CORS is open (`flask-cors` default) for simplicity — restrict
  `Access-Control-Allow-Origin` to your actual frontend domain before a
  public launch.
- Nothing secret (Anthropic key, DB credentials, SMTP password) ever reaches
  the frontend — all read from backend environment variables.

## Known simplifications (flagged, not hidden)

- SQLite by default — fine for local dev; use `DATABASE_URL` with a hosted
  Postgres for anything with real, persistent user accounts.
- The chatbot's and University Finder's rule-based fallbacks are
  intentionally simple keyword matching — set `ANTHROPIC_API_KEY` for
  real, nuanced field-matching and career-scope write-ups.
- University websites are included where independently confirmed; where
  not, the admission link falls back to a Google search for the
  university's official site rather than guessing a domain.
