"""
STUDENT NEXT.AI SEED SCRIPT
Run with: python seed.py
Safe to re-run — looks up existing rows by name before inserting.

SCOPE NOTE: Pakistan's NUST and FAST-NUCES aggregate formulas were
confirmed against each university's own published admission criteria —
these are the only two "verified weighted formula" entries in the whole
dataset. Every fee figure is left blank with a note, since fees change
yearly and weren't independently verified for this seed.

v3 (AI University Finder rebuild): expanded from 15 countries / 31
universities to 137 countries / 410 universities — a curated top-5 (or
fewer, where a country genuinely doesn't have 5 widely-recognized
research universities) list per country. The original 15 countries'
31 hand-written entries below (COUNTRIES / AGGREGATE_FORMULAS / TESTS /
UNIVERSITIES) are unchanged from the earlier verified pass. Everything
from "UNIVERSITY FINDER EXPANSION" onward is new: it follows the exact
same honesty discipline as the original 31 — every country's real,
named admission system (Gaokao, Bagrut+PET, ENEM, WASSCE, YKS, and so
on) gets a plain-language aggregate_note instead of an invented
per-university formula or a fabricated cutoff percentage. This is a
well-researched starting map, not a live feed — admission rules and
cutoffs change every year, so treat the "official site" link on every
card as the actual source of truth, and verify before applying.
"""

from datetime import datetime
from models import init_db, get_db, Country, AggregateFormula, TestInfo, University, Program, Scholarship

TODAY = datetime(2026, 7, 14)

COUNTRIES = [
    {"name": "Pakistan", "education_system": "Matric (O-level equiv.) + FSc/A-level (intermediate) + university entry test", "grading_scale": "Percentage (0-100%)"},
    {"name": "United States", "education_system": "High school GPA + SAT/ACT (often test-optional) + holistic review", "grading_scale": "GPA (0-4.0) and percentile test scores"},
    {"name": "United Kingdom", "education_system": "A-levels (or equivalent) + UCAS application, sometimes a subject admissions test", "grading_scale": "A-level grades (A*-E) and UCAS tariff points"},
    {"name": "Canada", "education_system": "Provincial high school average + holistic review; no centralized national test", "grading_scale": "Percentage or GPA, varies by province"},
    {"name": "Australia", "education_system": "Senior secondary results converted into an ATAR + course prerequisites", "grading_scale": "ATAR (0.00-99.95)"},
    {"name": "Germany", "education_system": "Abitur + Numerus Clausus (NC) restrictions for competitive subjects", "grading_scale": "German grade scale (1.0 best - 4.0 passing)"},
    {"name": "China", "education_system": "Gaokao score is the primary admission factor for most universities", "grading_scale": "Gaokao score, out of 750 in most provinces"},
    {"name": "India", "education_system": "Class 12 board result, plus a competitive entrance exam (e.g. JEE) for top programs", "grading_scale": "Percentage / CGPA, plus entrance exam rank"},
    {"name": "France", "education_system": "Baccalaureat + Parcoursup centralized application; Grandes Ecoles use separate concours", "grading_scale": "Baccalaureat, out of 20"},
    {"name": "Japan", "education_system": "Common Test for University Admissions + individual university entrance exams", "grading_scale": "Common Test score (out of 900) + university-specific exam score"},
    {"name": "South Korea", "education_system": "CSAT (Suneung) score + school records, weighted differently by university", "grading_scale": "CSAT standard score / percentile + GPA"},
    {"name": "Netherlands", "education_system": "VWO diploma + numerus fixus (weighted selection) for competitive programs", "grading_scale": "Dutch grading scale, 1-10"},
    {"name": "Sweden", "education_system": "Upper secondary grades (meritvarde) + national test scores, via antagning.se", "grading_scale": "Swedish grading scale A-F, converted to meritvarde points"},
    {"name": "Switzerland", "education_system": "Swiss Matura + subject-specific entrance requirements", "grading_scale": "Swiss grading scale, 1-6"},
    {"name": "New Zealand", "education_system": "NCEA Level 3 with University Entrance (UE) requirement + course prerequisites", "grading_scale": "NCEA Achievement Standards"},
]

AGGREGATE_FORMULAS = [
    {"country": "Pakistan", "name": "NUST undergraduate merit formula",
     "components": [{"key": "matric_pct", "label": "Matric %", "weight": 0.10}, {"key": "intermediate_pct", "label": "FSc Part-1 %", "weight": 0.15}, {"key": "test_pct", "label": "NET %", "weight": 0.75}],
     "source_url": "https://nust.edu.pk", "last_verified": TODAY},
    {"country": "Pakistan", "name": "FAST-NUCES undergraduate merit formula",
     "components": [{"key": "matric_pct", "label": "Matric %", "weight": 0.10}, {"key": "intermediate_pct", "label": "FSc %", "weight": 0.40}, {"key": "test_pct", "label": "Entry Test %", "weight": 0.50}],
     "source_url": "https://nu.edu.pk", "last_verified": TODAY},
]

TESTS = [
    {"name": "NUST Entry Test (NET)", "subjects": ["Mathematics", "Physics", "English", "Analytical/IQ"], "syllabus_summary": "FSc Part I & II Math/Physics, analytical reasoning, English comprehension.", "official_prep_link": "https://nust.edu.pk/admissions/net/"},
    {"name": "FAST-NUCES Entry Test", "subjects": ["Mathematics", "English", "Analytical/IQ"], "syllabus_summary": "FSc-level math, basic algebra and calculus, analytical reasoning, English.", "official_prep_link": "https://nu.edu.pk/Admissions/EntryTest"},
    {"name": "SAT / ACT (US, optional at many schools)", "subjects": ["Math", "Evidence-Based Reading & Writing"], "syllabus_summary": "US college admissions test; increasingly optional — check each school's current policy.", "official_prep_link": "https://satsuite.collegeboard.org"},
    {"name": "UCAS Application (UK)", "subjects": [], "syllabus_summary": "Centralized UK undergraduate application system. Personal statement + predicted grades + reference.", "official_prep_link": "https://www.ucas.com"},
    {"name": "Canadian Provincial Application", "subjects": [], "syllabus_summary": "No centralized test — admission is based on provincial average plus supplementary essays. OUAC handles Ontario.", "official_prep_link": "https://www.ouac.on.ca"},
    {"name": "ATAR (Australia)", "subjects": [], "syllabus_summary": "A rank (0.00-99.95) from Year 11-12 results, not a single exam. Calculation varies by state.", "official_prep_link": "https://www.uac.edu.au"},
    {"name": "Abitur + Numerus Clausus (Germany)", "subjects": [], "syllabus_summary": "Abitur grade + NC restrictions for competitive subjects. International applicants apply via uni-assist.", "official_prep_link": "https://www.uni-assist.de"},
    {"name": "Gaokao (China)", "subjects": ["Chinese", "Mathematics", "Foreign language", "Electives"], "syllabus_summary": "China's National College Entrance Examination, covering the national curriculum.", "official_prep_link": None},
    {"name": "JEE Main / Advanced (India)", "subjects": ["Physics", "Chemistry", "Mathematics"], "syllabus_summary": "JEE Main qualifies for NITs; JEE Advanced determines IIT admission by all-India rank.", "official_prep_link": "https://jeemain.nta.nic.in"},
    {"name": "Baccalaureat + Parcoursup (France)", "subjects": [], "syllabus_summary": "Parcoursup is the centralized application system; Grandes Ecoles use separate concours.", "official_prep_link": "https://www.parcoursup.fr"},
    {"name": "Common Test for University Admissions (Japan)", "subjects": ["Japanese", "Mathematics", "Science", "Foreign language"], "syllabus_summary": "A standardized test taken by most applicants, followed by individual university exams.", "official_prep_link": None},
    {"name": "CSAT / Suneung (South Korea)", "subjects": ["Korean", "Mathematics", "English", "Electives"], "syllabus_summary": "South Korea's national entrance exam, weighted alongside school records.", "official_prep_link": None},
    {"name": "VWO + Numerus Fixus (Netherlands)", "subjects": [], "syllabus_summary": "A VWO diploma is required; competitive programs use numerus fixus selection.", "official_prep_link": None},
    {"name": "Swedish Upper Secondary Grades (antagning.se)", "subjects": [], "syllabus_summary": "Based on upper secondary grades (meritvarde) or the Hogskoleprovet, via antagning.se.", "official_prep_link": "https://www.antagning.se"},
    {"name": "Swiss Matura", "subjects": [], "syllabus_summary": "A recognized Swiss Matura generally grants direct admission; others may need a supplementary exam.", "official_prep_link": None},
    {"name": "NCEA + University Entrance (New Zealand)", "subjects": [], "syllabus_summary": "NCEA Level 3 plus the UE literacy/numeracy requirement is the baseline.", "official_prep_link": "https://www.nzqa.govt.nz"},
]

GENERIC_AID_NOTE = "Merit and need-based scholarships are typically available — check the university's official financial aid page for current schemes and coverage."

UNIVERSITIES = [
    {"country": "Pakistan", "name": "NUST Islamabad", "city": "Islamabad", "address": "H-12, Islamabad, Pakistan", "website": "https://nust.edu.pk",
     "description": "Public research university, consistently ranked among Pakistan's top engineering and CS schools.",
     "programs": [{"name": "BS Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check nust.edu.pk/admissions/fee-structure",
         "aggregate_note": "Closing merit varies by year and campus; check the latest NUST merit list.",
         "test": "NUST Entry Test (NET)", "formula": "NUST undergraduate merit formula",
         "admission_opens": "May (typical)", "admission_closes": "July (typical)",
         "how_to_apply": "Apply online via NUST's admissions portal, book and take the NET, submit Matric/FSc transcripts.",
         "admission_source_url": "https://nust.edu.pk/admissions/"}],
     "scholarships": [{"name": "NUST Need-Based Financial Assistance", "coverage": "Partial to full tuition, income-based", "eligibility": "Demonstrated financial need", "deadline": "Rolling, apply after admission"}]},

    {"country": "Pakistan", "name": "FAST-NUCES Lahore", "city": "Lahore", "address": "852, B Block, Faisal Town, Lahore, Pakistan", "website": "https://nu.edu.pk",
     "description": "Private university known for computer science and business programs across multiple Pakistani campuses.",
     "programs": [{"name": "BS Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check nu.edu.pk fee structure page.",
         "aggregate_note": "Varies by campus and year; check the latest FAST merit list.",
         "test": "FAST-NUCES Entry Test", "formula": "FAST-NUCES undergraduate merit formula",
         "admission_opens": "May (typical)", "admission_closes": "July (typical)",
         "how_to_apply": "Apply online via FAST admissions portal, take the entry test, submit transcripts.",
         "admission_source_url": "https://nu.edu.pk/Admissions"}],
     "scholarships": [{"name": "FAST Need-Based Aid", "coverage": "Partial tuition waiver, income-based", "eligibility": "Demonstrated financial need", "deadline": "With admission application"}]},

    {"country": "Pakistan", "name": "LUMS", "city": "Lahore", "address": "Sector U, DHA, Lahore, Pakistan", "website": "https://lums.edu.pk",
     "description": "Private university using holistic admissions rather than a fixed weighted aggregate.",
     "programs": [{"name": "BS Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check lums.edu.pk admissions pages.",
         "aggregate_note": "LUMS uses holistic review (own test + interview + academic record), not a published weighted percentage.",
         "test": None, "formula": None,
         "admission_opens": "Check lums.edu.pk (varies by cycle)", "admission_closes": "Check lums.edu.pk (varies by cycle)",
         "how_to_apply": "Apply via LUMS's own admissions portal; test/SAT + interview + academic record reviewed holistically.",
         "admission_source_url": "https://lums.edu.pk/admissions"}],
     "scholarships": [{"name": "LUMS National Outreach Programme (NOP)", "coverage": "Up to 100% financial aid for eligible students", "eligibility": "Financial need + academic merit", "deadline": "With admission application"}]},

    {"country": "United States", "name": "MIT", "city": "Cambridge, Massachusetts", "address": "77 Massachusetts Ave, Cambridge, MA 02139, USA", "website": "https://mit.edu",
     "description": "Private research university; admissions are holistic and need-blind for US applicants.",
     "programs": [{"name": "BS Computer Science (Course 6-3)", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check MIT Student Financial Services for current cost of attendance.",
         "aggregate_note": "Holistic review — no single weighted formula.",
         "test": "SAT / ACT (US, optional at many schools)", "formula": None,
         "admission_opens": "Early Aug (Common App opens)", "admission_closes": "Early Jan (Regular Decision, typical)",
         "how_to_apply": "Apply via the Common App or MIT's own application, essays + recommendations + optional test scores.",
         "admission_source_url": "https://mitadmissions.org"}],
     "scholarships": [{"name": "MIT Need-Based Financial Aid", "coverage": "Meets 100% of demonstrated need", "eligibility": "Demonstrated financial need", "deadline": "With financial aid application"}]},

    {"country": "United States", "name": "Stanford University", "city": "Stanford, California", "address": "450 Jane Stanford Way, Stanford, CA 94305, USA", "website": "https://stanford.edu",
     "description": "Private research university with one of the largest computer science departments in the US.",
     "programs": [{"name": "BS Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check Stanford financial aid office for current cost of attendance.",
         "aggregate_note": "Holistic review — no single weighted formula.",
         "test": "SAT / ACT (US, optional at many schools)", "formula": None,
         "admission_opens": "Early Aug (Common App opens)", "admission_closes": "Early Jan (Regular Decision, typical)",
         "how_to_apply": "Apply via the Common App, essays + recommendations + optional test scores.",
         "admission_source_url": "https://admission.stanford.edu"}],
     "scholarships": [{"name": "Stanford Financial Aid", "coverage": "Need-based, meets full demonstrated need", "eligibility": "Demonstrated financial need", "deadline": "With financial aid application"}]},

    {"country": "United Kingdom", "name": "University of Oxford", "city": "Oxford", "address": "University Offices, Wellington Square, Oxford OX1 2JD, UK", "website": "https://ox.ac.uk",
     "description": "Collegiate research university; admission via UCAS plus college interviews and, for some subjects, an admissions test.",
     "programs": [{"name": "BA Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — check Oxford's official fees page.",
         "aggregate_note": "Typical offers are A-level grades (e.g. A*A*A), not a percentage aggregate.",
         "test": "UCAS Application (UK)", "formula": None,
         "admission_opens": "Sept (UCAS opens)", "admission_closes": "Mid-Oct (Oxford's earlier UCAS deadline)",
         "how_to_apply": "Apply via UCAS, personal statement, subject admissions test, college interview if shortlisted.",
         "admission_source_url": "https://ox.ac.uk/admissions"}],
     "scholarships": [{"name": "Oxford Bursaries / Reach Oxford Scholarship", "coverage": "Varies — income-based (UK) or full-cost (international, competitive)", "eligibility": "Household income thresholds or demonstrated need", "deadline": "Varies by scheme"}]},

    {"country": "United Kingdom", "name": "University of Cambridge", "city": "Cambridge", "address": "The Old Schools, Trinity Ln, Cambridge CB2 1TN, UK", "website": "https://cam.ac.uk",
     "description": "Collegiate research university; the Computer Science Tripos is one of the oldest CS degrees in the world.",
     "programs": [{"name": "Computer Science Tripos", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — check Cambridge's official fees page.",
         "aggregate_note": "Typical offers are A-level grades plus the CSAT admissions test — not a percentage aggregate.",
         "test": "UCAS Application (UK)", "formula": None,
         "admission_opens": "Sept (UCAS opens)", "admission_closes": "Mid-Oct (Cambridge's earlier UCAS deadline)",
         "how_to_apply": "Apply via UCAS, sit the Computer Science Admissions Test (CSAT), college interview if shortlisted.",
         "admission_source_url": "https://undergraduate.study.cam.ac.uk"}],
     "scholarships": [{"name": "Cambridge Bursary Scheme / Cambridge Trust scholarships", "coverage": "Varies by household income or scheme", "eligibility": "Household income thresholds or demonstrated need/merit", "deadline": "Varies by scheme"}]},

    {"country": "Canada", "name": "University of Toronto", "city": "Toronto, Ontario", "address": "Toronto, Ontario, Canada", "website": "https://utoronto.ca",
     "description": "Canada's largest research university, with a computer science program ranked among the country's top.",
     "programs": [{"name": "BSc Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check UofT's official fees page.",
         "aggregate_note": "Based on provincial average plus a supplementary application; not a fixed percentage cutoff.",
         "test": "Canadian Provincial Application", "formula": None,
         "admission_opens": "Sept-Oct (OUAC opens, Ontario)", "admission_closes": "Jan 15 (typical Ontario deadline)",
         "how_to_apply": "Apply via OUAC (Ontario) or your province's portal, transcripts + supplementary application.",
         "admission_source_url": "https://future.utoronto.ca"}],
     "scholarships": [{"name": "University of Toronto entrance scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Academic merit, some need-based", "deadline": "With admission application"}]},

    {"country": "Canada", "name": "University of British Columbia", "city": "Vancouver, British Columbia", "address": "Vancouver, British Columbia, Canada", "website": "https://ubc.ca",
     "description": "Major public research university on Canada's west coast, with a well-regarded computer science department.",
     "programs": [{"name": "BSc Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check UBC's official fees page.",
         "aggregate_note": "Based on provincial average plus a personal profile submission; not a fixed percentage cutoff.",
         "test": "Canadian Provincial Application", "formula": None,
         "admission_opens": "Oct (UBC's own application opens)", "admission_closes": "Jan 15 (typical deadline)",
         "how_to_apply": "Apply directly via UBC's application portal, transcripts + personal profile.",
         "admission_source_url": "https://you.ubc.ca"}],
     "scholarships": [{"name": "UBC entrance scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Academic merit, some need-based", "deadline": "With admission application"}]},

    {"country": "Australia", "name": "University of Melbourne", "city": "Melbourne, Victoria", "address": "Parkville, Melbourne, Victoria, Australia", "website": "https://unimelb.edu.au",
     "description": "One of Australia's leading research universities, offering computer science through its Bachelor of Science.",
     "programs": [{"name": "Bachelor of Science (Computer Science major)", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — check the university's official fees page.",
         "aggregate_note": "ATAR-based (varies by year); check the current ATAR cutoff on the official course page.",
         "test": "ATAR (Australia)", "formula": None,
         "admission_opens": "Aug (typical, varies by state)", "admission_closes": "Dec-Jan (main round, varies by state/VTAC)",
         "how_to_apply": "Apply via VTAC (Victoria) or your state's tertiary admissions center, based on your ATAR.",
         "admission_source_url": "https://study.unimelb.edu.au"}],
     "scholarships": [{"name": "Melbourne scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Academic merit, some need-based", "deadline": "Varies"}]},

    {"country": "Australia", "name": "Australian National University", "city": "Canberra", "address": "Canberra, Australian Capital Territory, Australia", "website": "https://anu.edu.au",
     "description": "Australia's national research university, based in the capital, with a strong computer science school.",
     "programs": [{"name": "Bachelor of Advanced Computing", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check ANU's official fees page.",
         "aggregate_note": "ATAR-based (varies by year); check the current ATAR cutoff on the official course page.",
         "test": "ATAR (Australia)", "formula": None,
         "admission_opens": "Aug (typical)", "admission_closes": "Dec-Jan (main round)",
         "how_to_apply": "Apply directly via ANU or through UAC, based on your ATAR.",
         "admission_source_url": "https://anu.edu.au/study"}],
     "scholarships": [{"name": "ANU scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Academic merit, some need-based", "deadline": "Varies"}]},

    {"country": "Germany", "name": "Technical University of Munich", "city": "Munich", "address": "Munich, Bavaria, Germany", "website": "https://tum.de",
     "description": "One of Germany's leading technical universities, especially strong in engineering and computer science.",
     "programs": [{"name": "BSc Informatik (Computer Science)", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — public universities often charge low/no tuition but a semester fee; check TUM's page.",
         "aggregate_note": "Abitur grade + Numerus Clausus restrictions may apply; not a simple weighted percentage.",
         "test": "Abitur + Numerus Clausus (Germany)", "formula": None,
         "admission_opens": "May (typical, winter semester)", "admission_closes": "Mid-July (typical, varies by year)",
         "how_to_apply": "International applicants typically apply via uni-assist; secondary school certificate + language proof.",
         "admission_source_url": "https://www.tum.de/en/studies"}],
     "scholarships": [{"name": "TUM / DAAD scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Academic merit, some need-based", "deadline": "Varies"}]},

    {"country": "Germany", "name": "Heidelberg University", "city": "Heidelberg", "address": "Heidelberg, Baden-Wurttemberg, Germany", "website": "https://uni-heidelberg.de",
     "description": "Germany's oldest university, with a well-regarded computer science faculty.",
     "programs": [{"name": "BSc Informatik (Computer Science)", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — check the university's official page for current semester contribution.",
         "aggregate_note": "Abitur grade + Numerus Clausus restrictions may apply; not a simple weighted percentage.",
         "test": "Abitur + Numerus Clausus (Germany)", "formula": None,
         "admission_opens": "May (typical, winter semester)", "admission_closes": "Mid-July (typical, varies by year)",
         "how_to_apply": "International applicants typically apply via uni-assist; secondary school certificate + language proof.",
         "admission_source_url": "https://www.uni-heidelberg.de/en/study"}],
     "scholarships": [{"name": "Heidelberg / DAAD scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Academic merit, some need-based", "deadline": "Varies"}]},

    {"country": "China", "name": "Tsinghua University", "city": "Beijing", "address": "Haidian District, Beijing, China", "website": "https://tsinghua.edu.cn",
     "description": "Consistently ranked as one of the top universities in China and Asia, especially for engineering and CS.",
     "programs": [{"name": "BEng Computer Science and Technology", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check Tsinghua's official international admissions page.",
         "aggregate_note": "Domestic admission is Gaokao-score based (varies by province); international students apply separately.",
         "test": "Gaokao (China)", "formula": None,
         "admission_opens": "June (Gaokao sat)", "admission_closes": "Late June-July (result-based application)",
         "how_to_apply": "Domestic: Gaokao score to provincial admission system. International: apply via Tsinghua's international office.",
         "admission_source_url": "https://www.tsinghua.edu.cn/en/Admissions.htm"}],
     "scholarships": [{"name": "Chinese Government Scholarship / Tsinghua scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for international students on CSC", "deadline": "Varies"}]},

    {"country": "China", "name": "Peking University", "city": "Beijing", "address": "Haidian District, Beijing, China", "website": "https://pku.edu.cn",
     "description": "One of China's oldest and most prestigious universities, with a strong computer science program.",
     "programs": [{"name": "BSc Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check PKU's official international admissions page.",
         "aggregate_note": "Domestic admission is Gaokao-score based (varies by province); international students apply separately.",
         "test": "Gaokao (China)", "formula": None,
         "admission_opens": "June (Gaokao sat)", "admission_closes": "Late June-July (result-based application)",
         "how_to_apply": "Domestic: Gaokao score to provincial admission system. International: apply via PKU's international office.",
         "admission_source_url": "https://www.pku.edu.cn/"}],
     "scholarships": [{"name": "Chinese Government Scholarship / PKU scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for international students on CSC", "deadline": "Varies"}]},

    {"country": "India", "name": "IIT Bombay", "city": "Mumbai, Maharashtra", "address": "Powai, Mumbai, Maharashtra, India", "website": "https://iitb.ac.in",
     "description": "One of India's most selective engineering institutes, admitting undergraduates via JEE Advanced rank.",
     "programs": [{"name": "BTech Computer Science and Engineering", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check IIT Bombay's official fee structure page.",
         "aggregate_note": "Admission is by all-India JEE Advanced rank via JoSAA counseling — CS is typically the most competitive branch.",
         "test": "JEE Main / Advanced (India)", "formula": None,
         "admission_opens": "Jan (JEE Main session 1)", "admission_closes": "June (JEE Advanced results & JoSAA counseling)",
         "how_to_apply": "Qualify JEE Main, sit JEE Advanced, participate in JoSAA counseling/seat allocation by rank.",
         "admission_source_url": "https://www.iitb.ac.in/en/education/admissions"}],
     "scholarships": [{"name": "Merit-cum-Means Scholarship / institute aid", "coverage": GENERIC_AID_NOTE, "eligibility": "Household income thresholds + academic performance", "deadline": "After admission"}]},

    {"country": "India", "name": "IIT Delhi", "city": "New Delhi", "address": "Hauz Khas, New Delhi, India", "website": "https://home.iitd.ac.in",
     "description": "One of India's premier engineering institutes, admitting undergraduates via JEE Advanced rank.",
     "programs": [{"name": "BTech Computer Science and Engineering", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check IIT Delhi's official fee structure page.",
         "aggregate_note": "Admission is by all-India JEE Advanced rank via JoSAA counseling — CS is typically the most competitive branch.",
         "test": "JEE Main / Advanced (India)", "formula": None,
         "admission_opens": "Jan (JEE Main session 1)", "admission_closes": "June (JEE Advanced results & JoSAA counseling)",
         "how_to_apply": "Qualify JEE Main, sit JEE Advanced, participate in JoSAA counseling/seat allocation by rank.",
         "admission_source_url": "https://home.iitd.ac.in/admissions.php"}],
     "scholarships": [{"name": "Merit-cum-Means Scholarship / institute aid", "coverage": GENERIC_AID_NOTE, "eligibility": "Household income thresholds + academic performance", "deadline": "After admission"}]},

    {"country": "France", "name": "Sorbonne Universite", "city": "Paris", "address": "Paris, France", "website": "https://sorbonne-universite.fr",
     "description": "One of France's largest research universities, formed from the merger of several historic Paris institutions.",
     "programs": [{"name": "Licence Informatique (Computer Science)", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — French public university fees are typically low; check official page for international rates.",
         "aggregate_note": "Admission via Parcoursup (French/EU students) or a separate international process; not a percentage aggregate.",
         "test": "Baccalaureat + Parcoursup (France)", "formula": None,
         "admission_opens": "Jan (Parcoursup opens)", "admission_closes": "Mid-March (Parcoursup wishes deadline)",
         "how_to_apply": "French/EU students apply via Parcoursup; others typically via Etudes en France / Campus France.",
         "admission_source_url": "https://www.sorbonne-universite.fr/en"}],
     "scholarships": [{"name": "French government / Sorbonne scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Academic merit, some need-based", "deadline": "Varies"}]},

    {"country": "France", "name": "Ecole Polytechnique", "city": "Palaiseau", "address": "Palaiseau, France", "website": "https://polytechnique.edu",
     "description": "A top French Grande Ecole for engineering, admitting most students through competitive entrance exams after preparatory classes.",
     "programs": [{"name": "Ingenieur Polytechnicien (Computer Science track)", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — check Ecole Polytechnique's official admissions page.",
         "aggregate_note": "Admission via competitive concours after classes preparatoires, or a separate international track — not a percentage aggregate.",
         "test": "Baccalaureat + Parcoursup (France)", "formula": None,
         "admission_opens": "Varies by track", "admission_closes": "Varies by track — check official page",
         "how_to_apply": "Domestic: classes preparatoires then concours. International: Ecole Polytechnique's international admissions track.",
         "admission_source_url": "https://www.polytechnique.edu/en/admissions"}],
     "scholarships": [{"name": "Ecole Polytechnique / Eiffel Excellence scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for international students", "deadline": "Varies"}]},

    {"country": "Japan", "name": "University of Tokyo", "city": "Tokyo", "address": "Bunkyo City, Tokyo, Japan", "website": "https://u-tokyo.ac.jp",
     "description": "Japan's top-ranked university, admitting most domestic students via the Common Test plus its own second-stage exam.",
     "programs": [{"name": "BSc Information Science (structure varies by department)", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check the university's official admissions page.",
         "aggregate_note": "Domestic admission combines Common Test + second-stage exam; international students use a separate program (e.g. PEAK).",
         "test": "Common Test for University Admissions (Japan)", "formula": None,
         "admission_opens": "Sept (Common Test registration)", "admission_closes": "Jan (Common Test) + Feb-March (individual exams)",
         "how_to_apply": "Domestic: Common Test then second-stage exam. International: dedicated international admissions program.",
         "admission_source_url": "https://www.u-tokyo.ac.jp/en/admissions/"}],
     "scholarships": [{"name": "MEXT scholarship / university aid", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for international students on MEXT", "deadline": "Varies"}]},

    {"country": "Japan", "name": "Kyoto University", "city": "Kyoto", "address": "Kyoto, Japan", "website": "https://kyoto-u.ac.jp",
     "description": "One of Japan's top research universities, known for a research-oriented undergraduate culture.",
     "programs": [{"name": "BSc Computer Science (structure varies by department)", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check the university's official admissions page.",
         "aggregate_note": "Domestic admission combines Common Test + second-stage exam; international students use a separate program.",
         "test": "Common Test for University Admissions (Japan)", "formula": None,
         "admission_opens": "Sept (Common Test registration)", "admission_closes": "Jan (Common Test) + Feb-March (individual exams)",
         "how_to_apply": "Domestic: Common Test then second-stage exam. International: dedicated international admissions program.",
         "admission_source_url": "https://www.kyoto-u.ac.jp/en/admissions"}],
     "scholarships": [{"name": "MEXT scholarship / university aid", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for international students on MEXT", "deadline": "Varies"}]},

    {"country": "South Korea", "name": "Seoul National University", "city": "Seoul", "address": "Gwanak-gu, Seoul, South Korea", "website": "https://snu.ac.kr",
     "description": "South Korea's top-ranked national university, admitting domestic students via CSAT plus school records.",
     "programs": [{"name": "BS Computer Science and Engineering", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — check SNU's official admissions page.",
         "aggregate_note": "Domestic admission weighs CSAT and school records differently by track (Susi vs. Jeongsi); international students apply separately.",
         "test": "CSAT / Suneung (South Korea)", "formula": None,
         "admission_opens": "Sept (CSAT registration)", "admission_closes": "Nov (CSAT date) + Dec-Jan (admission tracks)",
         "how_to_apply": "Domestic: Susi (school-record) or Jeongsi (CSAT) track. International: SNU international admissions office.",
         "admission_source_url": "https://admission.snu.ac.kr/"}],
     "scholarships": [{"name": "Korean Government Scholarship Program / SNU aid", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for international students on KGSP", "deadline": "Varies"}]},

    {"country": "South Korea", "name": "KAIST", "city": "Daejeon", "address": "Daejeon, South Korea", "website": "https://kaist.ac.kr",
     "description": "A leading science and technology-focused university, with most students on full-tuition scholarships.",
     "programs": [{"name": "BS Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 4,
         "fee_note": "Not verified this session — many KAIST undergraduates receive tuition waivers; check official page.",
         "aggregate_note": "Domestic admission weighs CSAT and school records; international students apply separately.",
         "test": "CSAT / Suneung (South Korea)", "formula": None,
         "admission_opens": "Sept (CSAT registration)", "admission_closes": "Nov (CSAT date) + Dec-Jan (admission tracks)",
         "how_to_apply": "Domestic: school-record or CSAT-based tracks. International: KAIST international admissions office.",
         "admission_source_url": "https://admission.kaist.ac.kr/"}],
     "scholarships": [{"name": "KAIST tuition waiver / KGSP", "coverage": "Most undergraduates receive a tuition waiver — check current policy", "eligibility": "Enrolled KAIST undergraduate / KGSP students", "deadline": "Varies"}]},

    {"country": "Netherlands", "name": "University of Amsterdam", "city": "Amsterdam", "address": "Amsterdam, Netherlands", "website": "https://uva.nl",
     "description": "A leading Dutch research university, offering computer science with instruction available in English.",
     "programs": [{"name": "BSc Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — EU vs. non-EU rates differ significantly, check UvA's official fees page.",
         "aggregate_note": "Requires a VWO diploma or recognized equivalent; some programs use numerus fixus selection.",
         "test": "VWO + Numerus Fixus (Netherlands)", "formula": None,
         "admission_opens": "Oct (Studielink opens)", "admission_closes": "May 1 (numerus fixus) / Jun-Jul (standard)",
         "how_to_apply": "Apply via Studielink, secondary school certificate + any numerus fixus materials.",
         "admission_source_url": "https://www.uva.nl/en/programmes"}],
     "scholarships": [{"name": "Amsterdam Merit Scholarship / UvA aid", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for non-EU/EEA students", "deadline": "Varies"}]},

    {"country": "Netherlands", "name": "Delft University of Technology", "city": "Delft", "address": "Delft, Netherlands", "website": "https://tudelft.nl",
     "description": "The Netherlands' largest and oldest technical university, highly ranked for computer science and engineering.",
     "programs": [{"name": "BSc Computer Science and Engineering", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — EU vs. non-EU rates differ significantly, check TU Delft's official fees page.",
         "aggregate_note": "Requires a VWO diploma or recognized equivalent; some programs use numerus fixus selection.",
         "test": "VWO + Numerus Fixus (Netherlands)", "formula": None,
         "admission_opens": "Oct (Studielink opens)", "admission_closes": "May 1 (numerus fixus) / Jun-Jul (standard)",
         "how_to_apply": "Apply via Studielink, secondary school certificate + any numerus fixus materials.",
         "admission_source_url": "https://www.tudelft.nl/en/education"}],
     "scholarships": [{"name": "TU Delft Justus & Louise van Effen Excellence Scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for non-EU/EEA students", "deadline": "Varies"}]},

    {"country": "Sweden", "name": "Lund University", "city": "Lund", "address": "Lund, Sweden", "website": "https://lu.se",
     "description": "One of Scandinavia's largest and highest-ranked universities, offering computer science programs in English.",
     "programs": [{"name": "BSc Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — tuition is free for EU/EEA/Swiss students; non-EU should check Lund's fees page.",
         "aggregate_note": "Based on meritvarde (upper secondary grades) or the Hogskoleprovet, via antagning.se — not a simple percentage.",
         "test": "Swedish Upper Secondary Grades (antagning.se)", "formula": None,
         "admission_opens": "Mid-March (antagning.se autumn-intake opens)", "admission_closes": "Mid-April (typical deadline)",
         "how_to_apply": "Apply via antagning.se (or universityadmissions.se for international), secondary school transcripts.",
         "admission_source_url": "https://www.lunduniversity.lu.se/"}],
     "scholarships": [{"name": "Swedish Institute Scholarships / Lund scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for non-EU/EEA students", "deadline": "Varies"}]},

    {"country": "Sweden", "name": "KTH Royal Institute of Technology", "city": "Stockholm", "address": "Stockholm, Sweden", "website": "https://kth.se",
     "description": "Sweden's largest technical university, with strong computer science and engineering programs.",
     "programs": [{"name": "Civilingenjor Datateknik (Computer Engineering, 5-year integrated)", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 5,
         "fee_note": "Not verified this session — tuition is free for EU/EEA/Swiss students; non-EU should check KTH's fees page.",
         "aggregate_note": "Based on meritvarde (upper secondary grades) or the Hogskoleprovet, via antagning.se — not a simple percentage.",
         "test": "Swedish Upper Secondary Grades (antagning.se)", "formula": None,
         "admission_opens": "Mid-March (antagning.se autumn-intake opens)", "admission_closes": "Mid-April (typical deadline)",
         "how_to_apply": "Apply via antagning.se (or universityadmissions.se for international), secondary school transcripts.",
         "admission_source_url": "https://www.kth.se/en/studies"}],
     "scholarships": [{"name": "Swedish Institute Scholarships / KTH scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for non-EU/EEA students", "deadline": "Varies"}]},

    {"country": "Switzerland", "name": "ETH Zurich", "city": "Zurich", "address": "Ramistrasse 101, 8092 Zurich, Switzerland", "website": "https://ethz.ch",
     "description": "Switzerland's top-ranked technical university, with a globally recognized computer science department.",
     "programs": [{"name": "BSc Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — Swiss public universities charge relatively low semester fees; check ETH's page.",
         "aggregate_note": "A recognized Swiss Matura generally grants direct admission; others may need a supplementary exam.",
         "test": "Swiss Matura", "formula": None,
         "admission_opens": "Nov-Dec (typical)", "admission_closes": "Apr 30 (typical deadline for many programs)",
         "how_to_apply": "Apply directly via ETH's admissions office, Matura (or recognized equivalent) + any required exam.",
         "admission_source_url": "https://ethz.ch/en/studies/registration-application.html"}],
     "scholarships": [{"name": "ETH Excellence Scholarship & Opportunity Programme", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for master's students", "deadline": "Varies"}]},

    {"country": "Switzerland", "name": "EPFL", "city": "Lausanne", "address": "Lausanne, Switzerland", "website": "https://epfl.ch",
     "description": "Switzerland's other leading technical university, strong in computer science and engineering.",
     "programs": [{"name": "BSc Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — Swiss public universities charge relatively low semester fees; check EPFL's page.",
         "aggregate_note": "A recognized Swiss Matura generally grants direct admission; others may need a supplementary exam.",
         "test": "Swiss Matura", "formula": None,
         "admission_opens": "Nov-Dec (typical)", "admission_closes": "Apr 30 (typical deadline for many programs)",
         "how_to_apply": "Apply directly via EPFL's admissions office, Matura (or recognized equivalent) + any required exam.",
         "admission_source_url": "https://www.epfl.ch/education/admission/"}],
     "scholarships": [{"name": "EPFL Excellence Fellowships", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for master's students", "deadline": "Varies"}]},

    {"country": "New Zealand", "name": "University of Auckland", "city": "Auckland", "address": "Auckland, New Zealand", "website": "https://auckland.ac.nz",
     "description": "New Zealand's largest university, ranked highly for computer science.",
     "programs": [{"name": "BSc Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — domestic vs. international rates differ, check official fees page.",
         "aggregate_note": "Requires NCEA Level 3 with University Entrance (or recognized equivalent); not a percentage aggregate.",
         "test": "NCEA + University Entrance (New Zealand)", "formula": None,
         "admission_opens": "Aug (typical)", "admission_closes": "Dec (typical, varies by programme)",
         "how_to_apply": "Apply directly via the university's application portal, NCEA results (or recognized equivalent).",
         "admission_source_url": "https://www.auckland.ac.nz/en/study.html"}],
     "scholarships": [{"name": "University of Auckland International Excellence Scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for international students", "deadline": "Varies"}]},

    {"country": "New Zealand", "name": "University of Otago", "city": "Dunedin", "address": "Dunedin, New Zealand", "website": "https://otago.ac.nz",
     "description": "New Zealand's oldest university, offering computer science through its Bachelor of Science.",
     "programs": [{"name": "BSc Computer Science", "field": "Computer Science", "degree_level": "Undergraduate", "duration_years": 3,
         "fee_note": "Not verified this session — check the university's official fees page.",
         "aggregate_note": "Requires NCEA Level 3 with University Entrance (or recognized equivalent); not a percentage aggregate.",
         "test": "NCEA + University Entrance (New Zealand)", "formula": None,
         "admission_opens": "Aug (typical)", "admission_closes": "Dec (typical, varies by programme)",
         "how_to_apply": "Apply directly via the university's application portal, NCEA results (or recognized equivalent).",
         "admission_source_url": "https://www.otago.ac.nz/study"}],
     "scholarships": [{"name": "University of Otago International scholarships", "coverage": GENERIC_AID_NOTE, "eligibility": "Mainly for international students", "deadline": "Varies"}]},
]
TEST_INFO = {
    "United Arab Emirates": ("EmSAT + Secondary School Certificate (UAE)", ["English", "Math", "Arabic"], "Emirates Standardized Test (EmSAT) subject scores combined with your secondary certificate; requirements vary by university and program.", None),
    "Qatar": ("Qatar Secondary Certificate + University Placement", ["Arabic", "English", "Math"], "General Secondary School Certificate plus university-specific placement/English tests (e.g. for Qatar University).", None),
    "Saudi Arabia": ("Tawjihi + Qiyas Qudurat/Tahsili (Saudi Arabia)", ["General aptitude", "Achievement (subject-based)"], "General Secondary Certificate (Tawjihi) plus the national Qudurat (aptitude) and Tahsili (achievement) tests run by Qiyas.", "https://etec.gov.sa"),
    "Egypt": ("Thanaweya Amma (Egypt)", ["Arabic", "Math/Science track", "English"], "Egypt's General Secondary Education Certificate; university/program placement is centralized by total score (\"coordination office\").", None),
    "Nigeria": ("UTME / JAMB (Nigeria)", ["English", "3 subjects in your chosen field"], "The Unified Tertiary Matriculation Examination run by JAMB, plus each university's own post-UTME screening.", "https://jamb.gov.ng"),
    "Kenya": ("KCSE (Kenya)", ["English", "Math", "Sciences", "Humanities"], "Kenya Certificate of Secondary Education mean grade and cluster subject weighting via KUCCPS placement.", "https://kuccps.net"),
    "Ghana": ("WASSCE (Ghana)", ["Core subjects", "Elective subjects"], "West African Senior School Certificate Examination — aggregate of best 6 subjects determines eligibility.", None),
    "Morocco": ("Baccalaureat marocain", ["Track-specific subjects"], "Moroccan Baccalaureate score; competitive schools (Grandes Ecoles) add their own entrance exam (concours).", None),
    "South Africa": ("NSC + APS (South Africa)", ["Home language", "Math", "5-6 more subjects"], "National Senior Certificate results converted into an Admission Point Score (APS); each faculty sets its own APS cutoff.", None),
    "Bangladesh": ("HSC + University Admission Test (Bangladesh)", ["Subject-specific"], "Higher Secondary Certificate result qualifies you to sit each university/cluster's own admission test (e.g. GST cluster, DU, BUET).", None),
    "Sri Lanka": ("GCE Advanced Level (Sri Lanka)", ["3 A-Level subjects"], "GCE A-Level Z-score and district quota determine placement through the UGC's centralized university admission process.", None),
    "Nepal": ("NEB Grade 12 + Entrance Exam (Nepal)", ["Subject-specific"], "National Examinations Board Grade 12 result, plus a subject entrance exam for competitive fields (e.g. IOE for engineering).", None),
    "Indonesia": ("UTBK-SNBT (Indonesia)", ["Scholastic potential", "Academic literacy"], "Computer-based national university entrance test (UTBK) feeding into the SNBT selection path, alongside the school-record SNBP path.", None),
    "Malaysia": ("STPM / Matriculation + UPU (Malaysia)", ["Subject-specific"], "STPM, Matriculation, or A-Level results submitted through UPU (public) or direct application (private); merit varies by program.", None),
    "Singapore": ("GCE A-Level / IB (Singapore)", ["3-4 A-Level or IB subjects"], "Local GCE A-Level or IB Diploma score submitted directly to each university (NUS/NTU/SMU each set their own indicative ranges.)", None),
    "Thailand": ("TCAS (GAT/PAT, O-NET)", ["General aptitude", "Professional/academic aptitude"], "Thailand's centralized admission system (TCAS), combining GPAX, GAT/PAT scores, and sometimes O-NET.", None),
    "Vietnam": ("THPT National High School Exam (Vietnam)", ["Math", "Literature", "Chosen combination"], "The national high-school graduation exam doubles as the main university entrance score, via the national portal.", None),
    "Philippines": ("University-specific entrance exam (Philippines)", ["Verbal", "Math", "Science"], "Each university runs its own entrance exam (e.g. UPCAT for University of the Philippines); no single national test.", None),
    "Poland": ("Matura (Poland)", ["Extended-level subjects relevant to your field"], "Polish Matura exam results (extended level in relevant subjects) are the primary admission criterion at public universities.", None),
    "Czech Republic": ("Maturita (Czech Republic)", ["Subject-specific"], "Czech Maturita school-leaving exam, plus many faculties run their own entrance exam or interview.", None),
    "Austria": ("Matura/Reifeprufung (Austria)", ["Subject-specific"], "Austrian Matura (Reifeprufung) generally grants access; some competitive fields (Medicine) add an aptitude test (e.g. MedAT).", None),
    "Belgium": ("Secondary Diploma + Entrance Exam where required (Belgium)", ["Subject-specific"], "A recognized secondary diploma is generally sufficient, except Medicine/Dentistry which require a national entrance exam.", None),
    "Denmark": ("Danish Upper Secondary Grade Point Average", ["Subject-specific"], "Grade point average from your upper-secondary diploma, submitted through the Danish national admission system (KOT).", None),
    "Norway": ("Norwegian Upper Secondary Grades (Samordna opptak)", ["Subject-specific"], "Upper-secondary grade average plus bonus points, submitted through Samordna opptak, Norway's joint admission service.", None),
    "Finland": ("Finnish Matriculation Examination", ["Subject-specific"], "Finnish Matriculation Exam grades and/or an entrance/aptitude exam set by the individual university or programme.", None),
    "Ireland": ("Leaving Certificate + CAO Points (Ireland)", ["6 best subjects"], "Irish Leaving Certificate converted into CAO points; each course publishes a points cutoff (\"points race\") each year.", "https://www.cao.ie"),
    "Portugal": ("Exames Nacionais (Portugal)", ["Subject-specific national exams"], "National exams (Exames Nacionais) combined with your secondary-school average, submitted through the DGES national portal.", "https://www.dges.gov.pt"),
    "Greece": ("Panhellenic Exams (Greece)", ["Subject-specific"], "The Panhellenic Examinations rank all applicants nationally by score for a place in each field of study.", None),
    "Hungary": ("Erettsegi (Hungary)", ["Subject-specific"], "Hungarian Matura (erettsegi) exam score converted into points through the national Felvi admission system.", None),
    "Romania": ("Bacalaureat (Romania)", ["Subject-specific"], "Romanian Baccalaureate average, often combined with a university-set admission exam or interview for competitive faculties.", None),
    "Israel": ("Bagrut + Psychometric Entrance Test (Israel)", ["Verbal reasoning", "Quantitative reasoning", "English"], "Combines your Bagrut (matriculation) average with the Psychometric Entrance Test (PET/\"Psychometri\") score into a single index.", None),
    "Iran": ("Konkur (Iran)", ["Subject-specific"], "Iran's national university entrance exam (Konkur); national rank determines which university/program you can enter.", None),
    "Iraq": ("Iraqi Baccalaureate (Iraq)", ["Subject-specific"], "Ministry of Education Baccalaureate score, centrally allocated to university seats via the Central Admission system.", None),
    "Jordan": ("Tawjihi (Jordan)", ["Subject-specific"], "General Secondary Education Certificate Examination (Tawjihi); score determines eligible programs via the unified admission portal.", None),
    "Lebanon": ("Lebanese Baccalaureate", ["Subject-specific"], "Official Lebanese Baccalaureate, or an equivalent (e.g. French Bac, SAT) accepted by many private Lebanese universities.", None),
    "Kuwait": ("Kuwait General Secondary Certificate", ["Subject-specific"], "General Secondary Education Certificate score, plus English placement tests for some programs.", None),
    "Oman": ("Oman General Education Diploma", ["Subject-specific"], "General Education Diploma score submitted through Oman's central admissions system for public universities.", None),
    "Bahrain": ("Bahrain Secondary School Certificate", ["Subject-specific"], "Secondary School Certificate score plus program-specific requirements set by each university.", None),
    "Taiwan": ("GSAT (Taiwan)", ["Chinese", "English", "Math", "Social studies", "Science"], "General Scholastic Ability Test (GSAT) or Advanced Subjects Test, feeding into Taiwan's multi-channel admission system.", None),
    "Hong Kong": ("HKDSE (Hong Kong)", ["Chinese Language", "English Language", "Math", "Citizenship & Social Development", "Electives"], "Hong Kong Diploma of Secondary Education score, submitted through JUPAS (local) or direct international-student admission.", None),
    "Ukraine": ("ZNO/NMT (Ukraine)", ["Ukrainian language", "Math", "Subject-specific"], "The National Multi-subject Test (NMT, formerly ZNO) score is the primary basis for public-university admission.", None),
    "Kazakhstan": ("UNT (Kazakhstan)", ["Reading literacy", "Math literacy", "Subject-specific"], "Unified National Testing (UNT) score determines eligibility for state grants and university placement.", None),
    "Uzbekistan": ("National University Entrance Test (Uzbekistan)", ["Subject-specific"], "A centrally administered entrance test in your chosen subjects; some universities also run their own additional test.", None),
    "Azerbaijan": ("State Exam (Azerbaijan)", ["Subject-specific"], "Centralized State Examination Center (DIM) test; national rank determines your university and program placement.", None),
    "Georgia": ("Unified National Exams (Georgia)", ["Georgian language", "Subject-specific"], "Unified National Exams administered by the National Assessment and Examinations Center determine university placement.", None),
    "Armenia": ("Unified Exams (Armenia)", ["Armenian language", "Subject-specific"], "Combined school-leaving and university-entrance exams; score determines eligibility for state-funded places.", None),
    "Serbia": ("Matura + Entrance Exam (Serbia)", ["Subject-specific"], "Serbian secondary-school diploma plus a faculty-specific entrance exam (\"prijemni ispit\").", None),
    "Croatia": ("Drzavna matura (Croatia)", ["Subject-specific"], "State Matura exam results submitted through the centralized postani-student.hr admission portal.", None),
    "Slovenia": ("Matura (Slovenia)", ["Subject-specific"], "Slovenian Matura exam score, submitted through the centralized higher-education application portal.", None),
    "Slovakia": ("Maturita (Slovakia)", ["Subject-specific"], "Slovak Maturita school-leaving exam; many faculties add their own entrance exam or interview.", None),
    "Bulgaria": ("Matura (Bulgaria)", ["Bulgarian language", "Subject-specific"], "Bulgarian State Matriculation Exam, often combined with a university-set entrance exam for competitive faculties.", None),
    "Estonia": ("Riigieksamid (Estonia)", ["Subject-specific"], "Estonian state exams (riigieksamid), submitted through the national SAIS application system.", None),
    "Latvia": ("Centralised Exams (Latvia)", ["Subject-specific"], "Latvian centralised secondary exams; universities set their own weighting per program.", None),
    "Lithuania": ("Brandos egzaminai (Lithuania)", ["Subject-specific"], "Lithuanian State Matura exams, converted into a competitive score via the LAMA BPO admission system.", None),
    "Iceland": ("Studentsprof (Iceland)", ["Subject-specific"], "Icelandic matriculation examination (studentsprof); most programs admit directly on this qualification.", None),
    "Luxembourg": ("Diplome de fin d'etudes secondaires (Luxembourg)", ["Subject-specific"], "Luxembourgish secondary-school diploma or a recognized equivalent (French Bac, German Abitur, IB).", None),
    "Cyprus": ("Apolytirion + Pancyprian Exams (Cyprus)", ["Subject-specific"], "Secondary-school leaving certificate (Apolytirion), with Pancyprian Examinations required for public universities.", None),
    "Malta": ("MATSEC (Malta)", ["Subject-specific"], "Matriculation and Secondary Education Certificate (MATSEC) — Advanced and Intermediate level subject passes.", None),
    "Turkey": ("YKS (Turkey)", ["TYT (basic skills)", "AYT (field-specific)"], "Two-stage national university entrance exam (Higher Education Institutions Examination); national rank determines placement.", None),
    "Brazil": ("ENEM / Vestibular (Brazil)", ["Languages", "Human sciences", "Natural sciences", "Math", "Essay"], "Exame Nacional do Ensino Medio (ENEM) score, used directly by many public universities or alongside a university's own vestibular exam.", None),
    "Mexico": ("EXANI-II (Mexico)", ["Verbal", "Math", "Subject modules"], "Ceneval's EXANI-II general admission exam, or a university's own entrance exam (e.g. UNAM's own exam).", None),
    "Argentina": ("CBC / Curso de Ingreso (Argentina)", ["Subject-specific"], "Most public universities (e.g. UBA) require a preparatory admission course/cycle (Ciclo Basico Comun) rather than a single test.", None),
    "Chile": ("PAES (Chile)", ["Competencia lectora", "Math", "Science/History electives"], "Prueba de Acceso a la Educacion Superior (PAES) score, submitted through the centralized admission system.", None),
    "Colombia": ("Saber 11 / ICFES (Colombia)", ["Reading", "Math", "Social studies", "Science", "English"], "ICFES Saber 11 exam score is the main national admission criterion, alongside university-specific weighting.", None),
    "Peru": ("University Admission Exam (Peru)", ["Subject-specific"], "Each Peruvian university runs its own entrance exam (examen de admision); no single national test.", None),
    "Venezuela": ("PNA (Venezuela)", ["Subject-specific"], "Prueba Nacional de Aptitud academic aptitude test, feeding into the national OPSU admission system.", None),
    "Ecuador": ("EAES / Ser Bachiller (Ecuador)", ["Verbal", "Math", "Abstract reasoning"], "National standardized exam score (EAES), used by SENESCYT's centralized public-university admission process.", None),
    "Uruguay": ("Bachillerato (Uruguay)", ["Subject-specific"], "Uruguayan secondary diploma (Bachillerato); admission to UDELAR (public) is largely open, with course-specific limits.", None),
    "Bolivia": ("University Admission Exam (Bolivia)", ["Subject-specific"], "Each Bolivian public university runs its own entrance exam (examen de ingreso/curso preuniversitario).", None),
    "Panama": ("University Admission Exam (Panama)", ["Subject-specific"], "Each Panamanian university sets its own admission exam and secondary-school GPA requirement.", None),
    "Costa Rica": ("Prueba de Aptitud Academica (Costa Rica)", ["Verbal", "Math"], "Academic Aptitude Test used by public universities (e.g. University of Costa Rica), plus secondary-school GPA.", None),
    "Cuba": ("Pruebas de Ingreso (Cuba)", ["Math", "Spanish/Literature", "Subject-specific"], "National entrance exams (pruebas de ingreso) plus secondary-school average determine placement.", None),
    "Dominican Republic": ("POMA / University Admission Test (Dominican Republic)", ["Verbal", "Math"], "University-specific admission/orientation test (e.g. POMA), plus secondary-school GPA.", None),
    "Jamaica": ("CAPE / CSEC (Jamaica)", ["Subject-specific"], "Caribbean Advanced Proficiency Examination (CAPE) or CSEC results, assessed by each university's admissions office.", None),
    "Guatemala": ("University Admission Exam (Guatemala)", ["Subject-specific"], "Each Guatemalan university sets its own admission/placement exam alongside the secondary-school diploma.", None),
    "Honduras": ("PAA (Honduras)", ["Verbal", "Math"], "Prueba de Aptitud Academica used by Honduran public universities, alongside secondary-school GPA.", None),
    "El Salvador": ("University Admission Exam (El Salvador)", ["Subject-specific"], "Each Salvadoran university runs its own admission/placement exam.", None),
    "Nicaragua": ("University Admission Exam (Nicaragua)", ["Subject-specific"], "Each Nicaraguan university runs its own admission/placement exam alongside the secondary diploma.", None),
    "Paraguay": ("Curso de Admision (Paraguay)", ["Subject-specific"], "Preparatory admission course/exam (curso de admision) run by each Paraguayan public university.", None),
    "Ethiopia": ("Ethiopian University Entrance Exam (EUEE)", ["Subject-specific"], "Ethiopian General Secondary Education Certificate Examination score determines placement via the Ministry of Education.", None),
    "Tanzania": ("ACSEE (Tanzania)", ["Subject-specific"], "Advanced Certificate of Secondary Education Examination points, submitted through TCU's central admission system.", None),
    "Uganda": ("UACE (Uganda)", ["Subject-specific"], "Uganda Advanced Certificate of Education points determine weighted admission points at each public university.", None),
    "Rwanda": ("Rwanda A-Level National Exam", ["Subject-specific"], "Rwandan Advanced Level national examination results, processed through the Higher Education Council placement system.", None),
    "Zimbabwe": ("ZIMSEC A-Level (Zimbabwe)", ["Subject-specific"], "Zimbabwe School Examinations Council Advanced Level points required for university entry.", None),
    "Zambia": ("Zambia School Certificate / GCE", ["Subject-specific"], "Zambia School Certificate/GCE O-Level results (5 credits including English/Math) required, program-specific cutoffs vary.", None),
    "Botswana": ("BGCSE (Botswana)", ["Subject-specific"], "Botswana General Certificate of Secondary Education points, assessed against each program's entry requirements.", None),
    "Namibia": ("NSSCAS (Namibia)", ["Subject-specific"], "Namibia Senior Secondary Certificate (Advanced Subsidiary) points required for university entry.", None),
    "Senegal": ("Baccalaureat senegalais", ["Subject-specific"], "Senegalese Baccalaureate score; competitive fields may require an additional concours (entrance exam).", None),
    "Ivory Coast": ("Baccalaureat ivoirien", ["Subject-specific"], "Ivorian Baccalaureate score; some Grandes Ecoles-style programs require an additional concours.", None),
    "Cameroon": ("GCE A-Level / Baccalaureat (Cameroon)", ["Subject-specific"], "Anglophone GCE Advanced Level or Francophone Baccalaureate, depending on the university/track.", None),
    "Tunisia": ("Baccalaureat tunisien", ["Subject-specific"], "Tunisian Baccalaureate score, allocated to university places through the national orientation system.", None),
    "Algeria": ("Baccalaureat algerien (BAC)", ["Subject-specific"], "Algerian Baccalaureate score, allocated to university places through the national ONOU orientation system.", None),
    "Libya": ("Libyan Secondary Education Certificate", ["Subject-specific"], "Libyan Secondary Education Certificate score required for university entry, per faculty cutoffs.", None),
    "Sudan": ("Sudan School Certificate", ["Subject-specific"], "Sudan School Certificate score, centrally allocated to university places by the Admission Committee.", None),
    "Mozambique": ("Mozambique Secondary Certificate", ["Subject-specific"], "12th-grade secondary certificate plus each university's own entrance exam (exame de admissao).", None),
    "Malawi": ("MSCE (Malawi)", ["Subject-specific"], "Malawi School Certificate of Education results, centrally processed for public-university placement.", None),
    "Afghanistan": ("Kankor (Afghanistan)", ["Subject-specific"], "The Kankor national university entrance exam; score and rank determine public-university placement.", None),
    "Mongolia": ("Unified National Exam (Mongolia)", ["Subject-specific"], "Mongolia's centrally administered entrance examination for public and many private universities.", None),
    "Myanmar": ("Matriculation Exam (Myanmar)", ["Subject-specific"], "Basic Education High School Examination (matriculation) score; competitive fields need higher aggregate marks.", None),
    "Cambodia": ("Baccalaureate Exam (Cambodia)", ["Subject-specific"], "National Baccalaureate (Bac II) examination score required for university entry.", None),
    "Laos": ("Secondary School Certificate (Laos)", ["Subject-specific"], "Lao secondary-school completion certificate; some faculties add their own entrance test.", None),
    "Brunei": ("A-Level / IB (Brunei)", ["Subject-specific"], "GCE A-Level or IB results, similar to the wider Commonwealth system used in neighboring Malaysia/Singapore.", None),
    "Papua New Guinea": ("Grade 12 Certificate (Papua New Guinea)", ["Subject-specific"], "National Grade 12 Certificate results, centrally processed for public-university placement.", None),
    "Fiji": ("Fiji Year 13 Certificate", ["Subject-specific"], "Fiji Year 13 Certificate results, assessed against each university's own entry requirements.", None),
    "Bhutan": ("Bhutan Certificate of Secondary Education", ["Subject-specific"], "Bhutan Higher Secondary Education Certificate results required for entry to the Royal University of Bhutan.", None),
    "Maldives": ("A-Level / Higher Secondary (Maldives)", ["Subject-specific"], "GCE A-Level or equivalent Higher Secondary results required for entry to the Maldives National University.", None),
    "Timor-Leste": ("Secondary Certificate (Timor-Leste)", ["Subject-specific"], "National secondary-school completion certificate, assessed against each faculty's entry requirements.", None),
    "North Macedonia": ("Drzhavna matura (North Macedonia)", ["Subject-specific"], "State Matura exam results, submitted through the centralized university-application portal.", None),
    "Bosnia and Herzegovina": ("Matura (Bosnia and Herzegovina)", ["Subject-specific"], "Secondary-school Matura results, plus a faculty-specific qualifying/entrance exam.", None),
    "Montenegro": ("Matura (Montenegro)", ["Subject-specific"], "Montenegrin State Matura results, plus program-specific requirements.", None),
    "Albania": ("Matura Shteterore (Albania)", ["Subject-specific"], "Albanian State Matriculation Exam score, submitted through the national university-application portal.", None),
    "Moldova": ("Bacalaureat (Moldova)", ["Subject-specific"], "Moldovan Baccalaureate exam results required for university admission.", None),
    "Kyrgyzstan": ("ORT (Kyrgyzstan)", ["Subject-specific"], "General Republican Testing (ORT) used for state-university placement.", None),
    "Tajikistan": ("National University Entrance Test (Tajikistan)", ["Subject-specific"], "Centralized university entrance testing administered by the Ministry of Education and Science.", None),
    "Turkmenistan": ("University Entrance Exam (Turkmenistan)", ["Subject-specific"], "Each Turkmen university administers its own entrance exam alongside the secondary-school certificate.", None),
    "Yemen": ("Yemen Secondary School Certificate", ["Subject-specific"], "Yemeni Secondary School Certificate score, assessed against each faculty's entry requirements.", None),
    "Syria": ("Syrian Baccalaureate", ["Subject-specific"], "Syrian Baccalaureate (scientific/literary branch) score, centrally allocated to university places.", None),
    "Palestine": ("Tawjihi (Palestine)", ["Subject-specific"], "Palestinian General Secondary Education Certificate Examination (Tawjihi) score required for university entry.", None),
    "Angola": ("Exame de Admissao (Angola)", ["Subject-specific"], "Secondary-school certificate plus each university's own admission exam (exame de admissao).", None),
    "Spain": ("Selectividad / EBAU (Spain)", ["Subject-specific"], "Evaluacion de Bachillerato para el Acceso a la Universidad (EBAU/Selectividad) score combined with your Bachillerato GPA.", None),
    "Italy": ("Diploma di Maturita + TOLC where required (Italy)", ["Subject-specific"], "Italian Diploma di Maturita generally grants access; Medicine and some competitive courses require a national admissions test (TOLC).", None),
    "Russia": ("EGE — Unified State Exam (Russia)", ["Subject-specific"], "Russia's Unified State Examination (EGE) score is the main basis for public-university budget-funded places.", None),
}
# ═══════════════════════════════════════════════════════════════════
# UNIVERSITY FINDER EXPANSION
# Adds 122 more countries and fills every "core" country out to a top-5
# (see CORE_EXTRA / NEW_COUNTRY_UNIS below), for 410 universities total
# across 137 countries. Same honesty rules as the original 31: no
# invented per-university formulas, no fabricated cutoff percentages —
# just each country's real, named admission system.
# ═══════════════════════════════════════════════════════════════════

FIELD_CYCLE = [
    "Computer Science", "Business Administration", "Engineering", "Medicine & Health Sciences",
    "Economics & Finance", "Law", "Natural Sciences", "Social Sciences",
    "Architecture & Design", "Agriculture & Environmental Science",
]

# A few well-known institutions get a field that actually matches their real-world
# reputation instead of the generic rotation.
CUSTOM_FIELD = {
    "California Institute of Technology": "Engineering", "KAUST": "Engineering",
    "King Fahd University of Petroleum and Minerals": "Engineering",
    "Karolinska Institute": "Medicine & Health Sciences", "London School of Economics": "Economics & Finance",
    "Sciences Po Paris": "Social Sciences", "American University of Beirut": "Medicine & Health Sciences",
    "Weizmann Institute of Science": "Natural Sciences", "Technion Israel Institute of Technology": "Engineering",
    "Karlsruhe Institute of Technology": "Engineering", "Imperial College London": "Engineering",
    "University of Waterloo": "Computer Science", "Delft University of Technology": "Engineering",
    "Singapore Management University": "Business Administration", "INSEAD": "Business Administration",
    "Copenhagen Business School": "Economics & Finance", "BI Norwegian Business School": "Economics & Finance",
    "Instituto Politecnico Nacional": "Engineering", "Tecnologico de Monterrey": "Engineering",
    "Semmelweis University": "Medicine & Health Sciences", "American University in Cairo": "Social Sciences",
    "Bahir Dar University": "Engineering", "IPB University": "Agriculture & Environmental Science",
    "Sokoine University of Agriculture": "Agriculture & Environmental Science",
    "Gulf University for Science and Technology": "Business Administration",
    "Harvard University": "Medicine & Health Sciences", "Princeton University": "Natural Sciences",
    "UCL (University College London)": "Medicine & Health Sciences", "Johns Hopkins University": "Medicine & Health Sciences",
    "Yale University": "Law", "Stanford University": "Computer Science",
}

# Where the country's generic test entry would be factually wrong for that specific
# university, give it its own accurate test/admission-system entry instead.
TEST_OVERRIDE = {
    "University of Delhi": ("CUET-UG (India)", ["Language", "Domain subjects", "General Test"],
        "Common University Entrance Test for Undergraduates — most Delhi University UG programs now admit via CUET-UG score rather than JEE.", "https://cuet.samarth.ac.in"),
    "University of the Punjab": ("Pakistan Public-Sector University Merit (varies by university)", ["Matric/FSc percentage", "University entry test (where applicable)"],
        "Public-sector Pakistani universities generally combine Matric and FSc/intermediate percentages with their own entry test; exact weighting is set by each university/department and isn't a single confirmed formula.", None),
    "Quaid-i-Azam University": ("Pakistan Public-Sector University Merit (varies by university)", ["Matric/FSc percentage", "University entry test (where applicable)"],
        "Public-sector Pakistani universities generally combine Matric and FSc/intermediate percentages with their own entry test; exact weighting is set by each university/department and isn't a single confirmed formula.", None),
}

CUSTOM_BLURBS = {
    "Harvard University": "The oldest university in the US and one of the world's most selective, with need-blind, need-based financial aid for all admitted students.",
    "California Institute of Technology": "A small, intensely research-focused institute renowned for physics, engineering, and space science (it manages NASA's Jet Propulsion Laboratory).",
    "Princeton University": "An Ivy League research university known for its strong undergraduate focus and a senior thesis required of every student.",
    "Imperial College London": "A London-based STEM specialist consistently ranked among the world's best for engineering, medicine, and natural sciences.",
    "UCL (University College London)": "London's largest university by enrollment, with one of the broadest subject ranges of any UK institution.",
    "London School of Economics": "A specialist social-science institution — economics, politics, and law — with an unusually international student body.",
    "McGill University": "One of Canada's oldest and most internationally recognized universities, based in Montreal.",
    "University of Waterloo": "Canada's best-known school for computer science and engineering, famous for its co-op (work-integrated learning) program.",
    "McMaster University": "A major Ontario research university especially well regarded for health sciences and engineering.",
    "University of Sydney": "Australia's oldest university, a member of the Group of Eight research-intensive universities.",
    "UNSW Sydney": "A leading Group of Eight university especially strong in engineering, business, and law.",
    "University of Queensland": "A Group of Eight research university in Brisbane, strong in biosciences and engineering.",
    "LMU Munich": "One of Germany's oldest and most prestigious universities, with a very broad range of faculties.",
    "Karlsruhe Institute of Technology": "A merger of a technical university and a national research center — one of Germany's leading engineering schools.",
    "Humboldt University of Berlin": "A historic Berlin research university that shaped the modern research-university model worldwide.",
    "Fudan University": "One of China's oldest and most prestigious comprehensive universities, based in Shanghai.",
    "Shanghai Jiao Tong University": "A top Chinese research university, especially known for engineering, medicine, and business.",
    "Zhejiang University": "One of China's largest and highest-funded research universities, based in Hangzhou.",
    "Indian Institute of Science Bangalore": "India's top-ranked institution for scientific and engineering research, with a research-heavy undergraduate program.",
    "IIT Madras": "Consistently rated India's top engineering institute in the National Institutional Ranking Framework.",
    "University of Delhi": "One of India's largest and oldest universities, with dozens of affiliated colleges across the capital.",
    "PSL University": "An alliance of elite Parisian research and Grande Ecole institutions, ranked among the top universities in France.",
    "Sciences Po Paris": "France's leading institution for political science, international relations, and public affairs.",
    "CentraleSupelec": "A top French engineering Grande Ecole, admitting most students through the classes preparatoires + concours system.",
    "Osaka University": "One of Japan's largest and most research-intensive national universities.",
    "Tokyo Institute of Technology": "Japan's leading specialist science and engineering university (merged into Institute of Science Tokyo in 2024).",
    "Tohoku University": "A top Japanese research university known for materials science and being the first in Japan to admit women.",
    "Korea University": "One of South Korea's oldest and most prestigious private research universities.",
    "Yonsei University": "A leading private South Korean university, part of the informal \"SKY\" group of top institutions.",
    "POSTECH": "A small, research-intensive South Korean science and technology university with a very high faculty-to-student ratio.",
    "Utrecht University": "One of the Netherlands' largest research universities, strong across sciences and humanities.",
    "Leiden University": "The Netherlands' oldest university, especially known for law and the humanities.",
    "Erasmus University Rotterdam": "A Dutch university especially well known for its business school and economics programs.",
    "Karolinska Institute": "One of the world's top medical universities and the institution that awards the Nobel Prize in Physiology or Medicine.",
    "Uppsala University": "Sweden's oldest university, with a strong reputation across sciences and humanities.",
    "University of Zurich": "Switzerland's largest university, with strengths across medicine, law, and the sciences.",
    "University of Geneva": "A leading Swiss research university with strong international relations and science programs, in a global-diplomacy hub city.",
    "University of Bern": "A comprehensive Swiss research university known for space science (Bernese space research helped build Apollo-era instruments).",
    "Victoria University of Wellington": "A New Zealand university based in the capital, well regarded for law, public policy, and the humanities.",
    "University of Canterbury": "A New Zealand university known for engineering and being the birthplace of Ernest Rutherford's scientific career.",
    "Massey University": "New Zealand's largest university by enrollment, with strengths in agriculture, veterinary science, and business.",
    "University of the Punjab": "Pakistan's oldest and one of its largest public universities, with a wide range of faculties in Lahore.",
    "Quaid-i-Azam University": "A leading Pakistani public research university in Islamabad, particularly strong in the natural sciences.",
}

DEFAULT_BLURB = "One of {country}'s widely recognized universities, drawing strong national reputation and graduate outcomes. Offers undergraduate and graduate programs across many fields; the guide below covers general admission requirements — check the official site for specific program details."
CORE_EXTRA = {'Australia': [('University of Sydney', 'Sydney', 'https://sydney.edu.au'),
               ('UNSW Sydney', 'Sydney', 'https://unsw.edu.au'),
               ('University of Queensland', 'Brisbane', 'https://uq.edu.au')],
 'Canada': [('McGill University', 'Montreal, Quebec', 'https://mcgill.ca'),
            ('University of Waterloo', 'Waterloo, Ontario', 'https://uwaterloo.ca'),
            ('McMaster University', 'Hamilton, Ontario', 'https://mcmaster.ca')],
 'China': [('Fudan University', 'Shanghai', 'https://fudan.edu.cn'),
           ('Shanghai Jiao Tong University', 'Shanghai', 'https://sjtu.edu.cn'),
           ('Zhejiang University', 'Hangzhou', 'https://zju.edu.cn')],
 'France': [('PSL University', 'Paris', 'https://psl.eu'),
            ('Sciences Po Paris', 'Paris', 'https://sciencespo.fr'),
            ('CentraleSupelec', 'Gif-sur-Yvette', 'https://centralesupelec.fr')],
 'Germany': [('LMU Munich', 'Munich', 'https://lmu.de'),
             ('Karlsruhe Institute of Technology', 'Karlsruhe', 'https://kit.edu'),
             ('Humboldt University of Berlin', 'Berlin', 'https://hu-berlin.de')],
 'India': [('Indian Institute of Science Bangalore', 'Bangalore, Karnataka', 'https://iisc.ac.in'),
           ('IIT Madras', 'Chennai, Tamil Nadu', 'https://iitm.ac.in'),
           ('University of Delhi', 'New Delhi', 'https://du.ac.in')],
 'Japan': [('Osaka University', 'Osaka', 'https://osaka-u.ac.jp'),
           ('Tokyo Institute of Technology', 'Tokyo', 'https://titech.ac.jp'),
           ('Tohoku University', 'Sendai', 'https://tohoku.ac.jp')],
 'Netherlands': [('Utrecht University', 'Utrecht', 'https://uu.nl'),
                 ('Leiden University', 'Leiden', 'https://universiteitleiden.nl'),
                 ('Erasmus University Rotterdam', 'Rotterdam', 'https://eur.nl')],
 'New Zealand': [('Victoria University of Wellington', 'Wellington', 'https://wgtn.ac.nz'),
                 ('University of Canterbury', 'Christchurch', 'https://canterbury.ac.nz'),
                 ('Massey University', 'Palmerston North', 'https://massey.ac.nz')],
 'Pakistan': [('University of the Punjab', 'Lahore', 'https://pu.edu.pk'),
              ('Quaid-i-Azam University', 'Islamabad', 'https://qau.edu.pk')],
 'South Korea': [('Korea University', 'Seoul', 'https://korea.ac.kr'),
                 ('Yonsei University', 'Seoul', 'https://yonsei.ac.kr'),
                 ('POSTECH', 'Pohang', 'https://postech.ac.kr')],
 'Sweden': [('Karolinska Institute', 'Stockholm', 'https://ki.se'), ('Uppsala University', 'Uppsala', 'https://uu.se')],
 'Switzerland': [('University of Zurich', 'Zurich', 'https://uzh.ch'),
                 ('University of Geneva', 'Geneva', 'https://unige.ch'),
                 ('University of Bern', 'Bern', 'https://unibe.ch')],
 'United Kingdom': [('Imperial College London', 'London', 'https://imperial.ac.uk'),
                    ('UCL (University College London)', 'London', 'https://ucl.ac.uk'),
                    ('London School of Economics', 'London', 'https://lse.ac.uk')],
 'United States': [('Harvard University', 'Cambridge, Massachusetts', 'https://harvard.edu'),
                   ('California Institute of Technology', 'Pasadena, California', 'https://caltech.edu'),
                   ('Princeton University', 'Princeton, New Jersey', 'https://princeton.edu')]}
NEW_COUNTRY_UNIS = {'Afghanistan': [('Kabul University', 'Kabul', ''), ('American University of Afghanistan', 'Kabul', '')],
 'Albania': [('University of Tirana', 'Tirana', 'https://unitir.edu.al')],
 'Algeria': [('University of Science and Technology Houari Boumediene', 'Algiers', ''),
             ('University of Algiers', 'Algiers', '')],
 'Angola': [('Agostinho Neto University', 'Luanda', '')],
 'Argentina': [('University of Buenos Aires', 'Buenos Aires', 'https://uba.ar'),
               ('Universidad Nacional de Cordoba', 'Cordoba', 'https://unc.edu.ar'),
               ('Universidad Torcuato Di Tella', 'Buenos Aires', 'https://utdt.edu'),
               ('Universidad Nacional de La Plata', 'La Plata', 'https://unlp.edu.ar')],
 'Armenia': [('Yerevan State University', 'Yerevan', 'https://ysu.am'),
             ('American University of Armenia', 'Yerevan', 'https://aua.am')],
 'Austria': [('University of Vienna', 'Vienna', 'https://univie.ac.at'),
             ('TU Wien', 'Vienna', 'https://tuwien.at'),
             ('University of Innsbruck', 'Innsbruck', 'https://uibk.ac.at'),
             ('Graz University of Technology', 'Graz', 'https://tugraz.at'),
             ('University of Salzburg', 'Salzburg', 'https://plus.ac.at')],
 'Azerbaijan': [('Baku State University', 'Baku', 'https://bsu.edu.az'),
                ('Azerbaijan State Oil and Industry University', 'Baku', ''),
                ('ADA University', 'Baku', 'https://ada.edu.az')],
 'Bahrain': [('University of Bahrain', 'Zallaq', 'https://uob.edu.bh'),
             ('Arabian Gulf University', 'Manama', 'https://agu.edu.bh'),
             ('Ahlia University', 'Manama', 'https://ahlia.edu.bh')],
 'Bangladesh': [('University of Dhaka', 'Dhaka', 'https://du.ac.bd'),
                ('BUET', 'Dhaka', 'https://buet.ac.bd'),
                ('North South University', 'Dhaka', 'https://northsouth.edu'),
                ('BRAC University', 'Dhaka', 'https://bracu.ac.bd')],
 'Belgium': [('KU Leuven', 'Leuven', 'https://kuleuven.be'),
             ('Ghent University', 'Ghent', 'https://ugent.be'),
             ('UC Louvain', 'Louvain-la-Neuve', 'https://uclouvain.be'),
             ('Universite Libre de Bruxelles', 'Brussels', 'https://ulb.be'),
             ('Vrije Universiteit Brussel', 'Brussels', 'https://vub.be')],
 'Bhutan': [('Royal University of Bhutan', 'Thimphu', 'https://rub.edu.bt')],
 'Bolivia': [('Universidad Mayor de San Andres', 'La Paz', 'https://umsa.bo'),
             ('Universidad Mayor de San Simon', 'Cochabamba', '')],
 'Bosnia and Herzegovina': [('University of Sarajevo', 'Sarajevo', 'https://unsa.ba')],
 'Botswana': [('University of Botswana', 'Gaborone', 'https://ub.ac.bw')],
 'Brazil': [('University of Sao Paulo', 'Sao Paulo', 'https://usp.br'),
            ('University of Campinas', 'Campinas', 'https://unicamp.br'),
            ('Federal University of Rio de Janeiro', 'Rio de Janeiro', 'https://ufrj.br'),
            ('Federal University of Minas Gerais', 'Belo Horizonte', 'https://ufmg.br')],
 'Brunei': [('Universiti Brunei Darussalam', 'Bandar Seri Begawan', 'https://ubd.edu.bn')],
 'Bulgaria': [('Sofia University', 'Sofia', 'https://uni-sofia.bg'),
              ('Technical University of Sofia', 'Sofia', 'https://tu-sofia.bg'),
              ('American University in Bulgaria', 'Blagoevgrad', 'https://aubg.edu')],
 'Cambodia': [('Royal University of Phnom Penh', 'Phnom Penh', 'https://rupp.edu.kh'),
              ('Institute of Technology of Cambodia', 'Phnom Penh', 'https://itc.edu.kh')],
 'Cameroon': [('University of Yaounde I', 'Yaounde', ''), ('University of Buea', 'Buea', 'https://ubuea.cm')],
 'Chile': [('Pontificia Universidad Catolica de Chile', 'Santiago', 'https://uc.cl'),
           ('Universidad de Chile', 'Santiago', 'https://uchile.cl'),
           ('Universidad de Concepcion', 'Concepcion', 'https://udec.cl'),
           ('Universidad Adolfo Ibanez', 'Santiago', 'https://uai.cl')],
 'Colombia': [('Universidad de los Andes', 'Bogota', 'https://uniandes.edu.co'),
              ('Universidad Nacional de Colombia', 'Bogota', 'https://unal.edu.co'),
              ('Universidad del Rosario', 'Bogota', 'https://urosario.edu.co'),
              ('Universidad de Antioquia', 'Medellin', 'https://udea.edu.co')],
 'Costa Rica': [('University of Costa Rica', 'San Jose', 'https://ucr.ac.cr'),
                ('Instituto Tecnologico de Costa Rica', 'Cartago', 'https://tec.ac.cr')],
 'Croatia': [('University of Zagreb', 'Zagreb', 'https://unizg.hr'),
             ('University of Split', 'Split', 'https://unist.hr'),
             ('University of Rijeka', 'Rijeka', 'https://uniri.hr')],
 'Cuba': [('University of Havana', 'Havana', 'https://uh.cu'), ('Central University of Las Villas', 'Santa Clara', '')],
 'Cyprus': [('University of Cyprus', 'Nicosia', 'https://ucy.ac.cy'),
            ('Cyprus University of Technology', 'Limassol', 'https://cut.ac.cy')],
 'Czech Republic': [('Charles University', 'Prague', 'https://cuni.cz'),
                    ('Czech Technical University in Prague', 'Prague', 'https://cvut.cz'),
                    ('Masaryk University', 'Brno', 'https://muni.cz'),
                    ('Brno University of Technology', 'Brno', 'https://vut.cz')],
 'Denmark': [('University of Copenhagen', 'Copenhagen', 'https://ku.dk'),
             ('Technical University of Denmark', 'Kongens Lyngby', 'https://dtu.dk'),
             ('Aarhus University', 'Aarhus', 'https://au.dk'),
             ('Copenhagen Business School', 'Frederiksberg', 'https://cbs.dk'),
             ('Aalborg University', 'Aalborg', 'https://aau.dk')],
 'Dominican Republic': [('Pontificia Universidad Catolica Madre y Maestra',
                         'Santiago de los Caballeros',
                         'https://pucmm.edu.do'),
                        ('Universidad Autonoma de Santo Domingo', 'Santo Domingo', 'https://uasd.edu.do')],
 'Ecuador': [('Escuela Politecnica Nacional', 'Quito', 'https://epn.edu.ec'),
             ('Universidad San Francisco de Quito', 'Quito', 'https://usfq.edu.ec'),
             ('Universidad de Cuenca', 'Cuenca', 'https://ucuenca.edu.ec')],
 'Egypt': [('American University in Cairo', 'Cairo', 'https://aucegypt.edu'),
           ('Cairo University', 'Giza', 'https://cu.edu.eg'),
           ('Ain Shams University', 'Cairo', 'https://asu.edu.eg'),
           ('Alexandria University', 'Alexandria', 'https://alexu.edu.eg')],
 'El Salvador': [('Universidad Centroamericana Jose Simeon Canas', 'San Salvador', 'https://uca.edu.sv')],
 'Estonia': [('University of Tartu', 'Tartu', 'https://ut.ee'),
             ('Tallinn University of Technology', 'Tallinn', 'https://taltech.ee')],
 'Ethiopia': [('Addis Ababa University', 'Addis Ababa', 'https://aau.edu.et'),
              ('Jimma University', 'Jimma', 'https://ju.edu.et'),
              ('Bahir Dar University', 'Bahir Dar', 'https://bdu.edu.et')],
 'Fiji': [('University of the South Pacific', 'Suva', 'https://usp.ac.fj'),
          ('Fiji National University', 'Suva', 'https://fnu.ac.fj')],
 'Finland': [('University of Helsinki', 'Helsinki', 'https://helsinki.fi'),
             ('Aalto University', 'Espoo', 'https://aalto.fi'),
             ('University of Turku', 'Turku', 'https://utu.fi'),
             ('Tampere University', 'Tampere', 'https://tuni.fi'),
             ('University of Oulu', 'Oulu', 'https://oulu.fi')],
 'Georgia': [('Tbilisi State University', 'Tbilisi', 'https://tsu.ge'),
             ('Ilia State University', 'Tbilisi', 'https://iliauni.edu.ge'),
             ('Georgian Technical University', 'Tbilisi', 'https://gtu.ge')],
 'Ghana': [('University of Ghana', 'Accra', 'https://ug.edu.gh'),
           ('Kwame Nkrumah University of Science and Technology', 'Kumasi', 'https://knust.edu.gh'),
           ('University of Cape Coast', 'Cape Coast', 'https://ucc.edu.gh')],
 'Greece': [('National and Kapodistrian University of Athens', 'Athens', 'https://uoa.gr'),
            ('National Technical University of Athens', 'Athens', 'https://ntua.gr'),
            ('Aristotle University of Thessaloniki', 'Thessaloniki', 'https://auth.gr'),
            ('University of Crete', 'Heraklion', 'https://uoc.gr'),
            ('University of Patras', 'Patras', 'https://upatras.gr')],
 'Guatemala': [('Universidad de San Carlos de Guatemala', 'Guatemala City', 'https://usac.edu.gt'),
               ('Universidad Francisco Marroquin', 'Guatemala City', 'https://ufm.edu')],
 'Honduras': [('Universidad Nacional Autonoma de Honduras', 'Tegucigalpa', 'https://unah.edu.hn')],
 'Hong Kong': [('University of Hong Kong', 'Hong Kong', 'https://hku.hk'),
               ('HKUST', 'Hong Kong', 'https://hkust.edu.hk'),
               ('Chinese University of Hong Kong', 'Hong Kong', 'https://cuhk.edu.hk'),
               ('City University of Hong Kong', 'Hong Kong', 'https://cityu.edu.hk'),
               ('Hong Kong Polytechnic University', 'Hong Kong', 'https://polyu.edu.hk')],
 'Hungary': [('Eotvos Lorand University', 'Budapest', 'https://elte.hu'),
             ('Semmelweis University', 'Budapest', 'https://semmelweis.hu'),
             ('Budapest University of Technology and Economics', 'Budapest', 'https://bme.hu'),
             ('University of Szeged', 'Szeged', 'https://u-szeged.hu')],
 'Iceland': [('University of Iceland', 'Reykjavik', 'https://hi.is'),
             ('Reykjavik University', 'Reykjavik', 'https://ru.is')],
 'Indonesia': [('University of Indonesia', 'Depok', 'https://ui.ac.id'),
               ('Gadjah Mada University', 'Yogyakarta', 'https://ugm.ac.id'),
               ('Institut Teknologi Bandung', 'Bandung', 'https://itb.ac.id'),
               ('Airlangga University', 'Surabaya', 'https://unair.ac.id'),
               ('IPB University', 'Bogor', 'https://ipb.ac.id')],
 'Iran': [('University of Tehran', 'Tehran', 'https://ut.ac.ir'),
          ('Sharif University of Technology', 'Tehran', 'https://sharif.edu'),
          ('Amirkabir University of Technology', 'Tehran', 'https://aut.ac.ir'),
          ('Isfahan University of Technology', 'Isfahan', 'https://iut.ac.ir'),
          ('Shiraz University', 'Shiraz', 'https://shirazu.ac.ir')],
 'Iraq': [('University of Baghdad', 'Baghdad', 'https://uobaghdad.edu.iq'),
          ('University of Mosul', 'Mosul', 'https://uomosul.edu.iq'),
          ('University of Basrah', 'Basra', 'https://uobasrah.edu.iq'),
          ('Al-Nahrain University', 'Baghdad', '')],
 'Ireland': [('Trinity College Dublin', 'Dublin', 'https://tcd.ie'),
             ('University College Dublin', 'Dublin', 'https://ucd.ie'),
             ('University of Galway', 'Galway', 'https://universityofgalway.ie'),
             ('University College Cork', 'Cork', 'https://ucc.ie'),
             ('Dublin City University', 'Dublin', 'https://dcu.ie')],
 'Israel': [('Hebrew University of Jerusalem', 'Jerusalem', 'https://en.huji.ac.il'),
            ('Tel Aviv University', 'Tel Aviv', 'https://tau.ac.il'),
            ('Technion Israel Institute of Technology', 'Haifa', 'https://technion.ac.il'),
            ('Weizmann Institute of Science', 'Rehovot', 'https://weizmann.ac.il'),
            ('Ben-Gurion University of the Negev', 'Beer Sheva', 'https://bgu.ac.il')],
 'Italy': [('University of Bologna', 'Bologna', 'https://unibo.it'),
           ('Sapienza University of Rome', 'Rome', 'https://uniroma1.it'),
           ('Politecnico di Milano', 'Milan', 'https://polimi.it'),
           ('University of Padua', 'Padua', 'https://unipd.it')],
 'Ivory Coast': [('Universite Felix Houphouet-Boigny', 'Abidjan', '')],
 'Jamaica': [('University of the West Indies', 'Kingston', 'https://uwi.edu'),
             ('University of Technology Jamaica', 'Kingston', 'https://utech.edu.jm')],
 'Jordan': [('University of Jordan', 'Amman', 'https://ju.edu.jo'),
            ('Jordan University of Science and Technology', 'Irbid', 'https://just.edu.jo'),
            ('German Jordanian University', 'Amman', 'https://gju.edu.jo')],
 'Kazakhstan': [('Nazarbayev University', 'Astana', 'https://nu.edu.kz'),
                ('Al-Farabi Kazakh National University', 'Almaty', 'https://kaznu.kz'),
                ('Satbayev University', 'Almaty', '')],
 'Kenya': [('University of Nairobi', 'Nairobi', 'https://uonbi.ac.ke'),
           ('Kenyatta University', 'Nairobi', 'https://ku.ac.ke'),
           ('Jomo Kenyatta University of Agriculture and Technology', 'Juja', 'https://jkuat.ac.ke'),
           ('Strathmore University', 'Nairobi', 'https://strathmore.edu')],
 'Kuwait': [('Kuwait University', 'Kuwait City', 'https://ku.edu.kw'),
            ('American University of Kuwait', 'Salmiya', 'https://auk.edu.kw'),
            ('Gulf University for Science and Technology', 'Mishref', 'https://gust.edu.kw')],
 'Kyrgyzstan': [('Kyrgyz National University', 'Bishkek', ''),
                ('American University of Central Asia', 'Bishkek', 'https://auca.kg')],
 'Laos': [('National University of Laos', 'Vientiane', '')],
 'Latvia': [('University of Latvia', 'Riga', 'https://lu.lv'), ('Riga Technical University', 'Riga', 'https://rtu.lv')],
 'Lebanon': [('American University of Beirut', 'Beirut', 'https://aub.edu.lb'),
             ('Lebanese American University', 'Beirut', 'https://lau.edu.lb'),
             ('Saint Joseph University', 'Beirut', 'https://usj.edu.lb'),
             ('Lebanese University', 'Beirut', '')],
 'Libya': [('University of Tripoli', 'Tripoli', ''), ('Benghazi University', 'Benghazi', '')],
 'Lithuania': [('Vilnius University', 'Vilnius', 'https://vu.lt'),
               ('Kaunas University of Technology', 'Kaunas', 'https://ktu.edu')],
 'Luxembourg': [('University of Luxembourg', 'Esch-sur-Alzette', 'https://uni.lu')],
 'Malawi': [('University of Malawi', 'Zomba', '')],
 'Malaysia': [('University of Malaya', 'Kuala Lumpur', 'https://um.edu.my'),
              ('Universiti Kebangsaan Malaysia', 'Bangi', 'https://ukm.my'),
              ('Universiti Putra Malaysia', 'Serdang', 'https://upm.edu.my'),
              ('Universiti Sains Malaysia', 'Penang', 'https://usm.my'),
              ('Universiti Teknologi Malaysia', 'Johor Bahru', 'https://utm.my')],
 'Maldives': [('Maldives National University', 'Male', 'https://mnu.edu.mv')],
 'Malta': [('University of Malta', 'Msida', 'https://um.edu.mt')],
 'Mexico': [('UNAM', 'Mexico City', 'https://unam.mx'),
            ('Tecnologico de Monterrey', 'Monterrey', 'https://tec.mx'),
            ('Instituto Politecnico Nacional', 'Mexico City', 'https://ipn.mx'),
            ('Universidad Iberoamericana', 'Mexico City', 'https://ibero.mx')],
 'Moldova': [('Moldova State University', 'Chisinau', 'https://usm.md')],
 'Mongolia': [('National University of Mongolia', 'Ulaanbaatar', 'https://num.edu.mn'),
              ('Mongolian University of Science and Technology', 'Ulaanbaatar', '')],
 'Montenegro': [('University of Montenegro', 'Podgorica', 'https://ucg.ac.me')],
 'Morocco': [('Mohammed V University', 'Rabat', 'https://um5.ac.ma'),
             ('Al Akhawayn University', 'Ifrane', 'https://aui.ma'),
             ('Hassan II University of Casablanca', 'Casablanca', 'https://univh2c.ma'),
             ('Cadi Ayyad University', 'Marrakesh', '')],
 'Mozambique': [('Eduardo Mondlane University', 'Maputo', 'https://uem.mz')],
 'Myanmar': [('University of Yangon', 'Yangon', ''), ('Mandalay University', 'Mandalay', '')],
 'Namibia': [('University of Namibia', 'Windhoek', 'https://unam.edu.na')],
 'Nepal': [('Tribhuvan University', 'Kathmandu', 'https://tu.edu.np'),
           ('Kathmandu University', 'Dhulikhel', 'https://ku.edu.np'),
           ('Pokhara University', 'Pokhara', '')],
 'Nicaragua': [('Universidad Centroamericana Nicaragua', 'Managua', 'https://uca.edu.ni')],
 'Nigeria': [('University of Ibadan', 'Ibadan', 'https://ui.edu.ng'),
             ('University of Lagos', 'Lagos', 'https://unilag.edu.ng'),
             ('Obafemi Awolowo University', 'Ile-Ife', 'https://oauife.edu.ng'),
             ('Covenant University', 'Ota', 'https://covenantuniversity.edu.ng')],
 'North Macedonia': [('Ss. Cyril and Methodius University', 'Skopje', 'https://ukim.edu.mk')],
 'Norway': [('University of Oslo', 'Oslo', 'https://uio.no'),
            ('Norwegian University of Science and Technology', 'Trondheim', 'https://ntnu.edu'),
            ('University of Bergen', 'Bergen', 'https://uib.no'),
            ('BI Norwegian Business School', 'Oslo', 'https://bi.edu'),
            ('UiT The Arctic University of Norway', 'Tromso', 'https://uit.no')],
 'Oman': [('Sultan Qaboos University', 'Muscat', 'https://squ.edu.om'),
          ('German University of Technology in Oman', 'Muscat', 'https://gutech.edu.om'),
          ('Sohar University', 'Sohar', 'https://soharuni.edu.om')],
 'Palestine': [('Birzeit University', 'Birzeit', 'https://birzeit.edu'),
               ('An-Najah National University', 'Nablus', 'https://najah.edu')],
 'Panama': [('Universidad de Panama', 'Panama City', 'https://up.ac.pa'),
            ('Universidad Tecnologica de Panama', 'Panama City', 'https://utp.ac.pa')],
 'Papua New Guinea': [('University of Papua New Guinea', 'Port Moresby', 'https://upng.ac.pg')],
 'Paraguay': [('Universidad Nacional de Asuncion', 'Asuncion', 'https://una.py')],
 'Peru': [('Pontificia Universidad Catolica del Peru', 'Lima', 'https://pucp.edu.pe'),
          ('Universidad Nacional Mayor de San Marcos', 'Lima', 'https://unmsm.edu.pe'),
          ('Universidad de Lima', 'Lima', 'https://ulima.edu.pe'),
          ('Universidad Peruana Cayetano Heredia', 'Lima', 'https://upch.edu.pe')],
 'Philippines': [('University of the Philippines Diliman', 'Quezon City', 'https://upd.edu.ph'),
                 ('Ateneo de Manila University', 'Quezon City', 'https://ateneo.edu'),
                 ('De La Salle University', 'Manila', 'https://dlsu.edu.ph'),
                 ('University of Santo Tomas', 'Manila', 'https://ust.edu.ph'),
                 ('University of San Carlos', 'Cebu City', 'https://usc.edu.ph')],
 'Poland': [('University of Warsaw', 'Warsaw', 'https://uw.edu.pl'),
            ('Jagiellonian University', 'Krakow', 'https://uj.edu.pl'),
            ('Warsaw University of Technology', 'Warsaw', 'https://pw.edu.pl'),
            ('Adam Mickiewicz University', 'Poznan', 'https://amu.edu.pl'),
            ('AGH University of Krakow', 'Krakow', 'https://agh.edu.pl')],
 'Portugal': [('University of Lisbon', 'Lisbon', 'https://ulisboa.pt'),
              ('University of Porto', 'Porto', 'https://up.pt'),
              ('University of Coimbra', 'Coimbra', 'https://uc.pt'),
              ('NOVA University Lisbon', 'Lisbon', 'https://unl.pt'),
              ('University of Aveiro', 'Aveiro', 'https://ua.pt')],
 'Qatar': [('Qatar University', 'Doha', 'https://qu.edu.qa'),
           ('Hamad Bin Khalifa University', 'Doha', 'https://hbku.edu.qa')],
 'Romania': [('University of Bucharest', 'Bucharest', 'https://unibuc.ro'),
             ('Babes-Bolyai University', 'Cluj-Napoca', 'https://ubbcluj.ro'),
             ('Politehnica University of Timisoara', 'Timisoara', 'https://upt.ro'),
             ('University of Medicine and Pharmacy Carol Davila', 'Bucharest', '')],
 'Russia': [('Lomonosov Moscow State University', 'Moscow', 'https://msu.ru'),
            ('Saint Petersburg State University', 'Saint Petersburg', 'https://spbu.ru'),
            ('Moscow Institute of Physics and Technology', 'Dolgoprudny', 'https://mipt.ru'),
            ('HSE University', 'Moscow', 'https://hse.ru')],
 'Rwanda': [('University of Rwanda', 'Kigali', 'https://ur.ac.rw')],
 'Saudi Arabia': [('King Abdulaziz University', 'Jeddah', 'https://kau.edu.sa'),
                  ('King Fahd University of Petroleum and Minerals', 'Dhahran', 'https://kfupm.edu.sa'),
                  ('King Saud University', 'Riyadh', 'https://ksu.edu.sa'),
                  ('KAUST', 'Thuwal', 'https://kaust.edu.sa')],
 'Senegal': [('Cheikh Anta Diop University', 'Dakar', 'https://ucad.sn'),
             ('Universite Gaston Berger', 'Saint-Louis', '')],
 'Serbia': [('University of Belgrade', 'Belgrade', 'https://bg.ac.rs'),
            ('University of Novi Sad', 'Novi Sad', 'https://uns.ac.rs'),
            ('University of Nis', 'Nis', 'https://ni.ac.rs')],
 'Singapore': [('National University of Singapore', 'Singapore', 'https://nus.edu.sg'),
               ('Nanyang Technological University', 'Singapore', 'https://ntu.edu.sg'),
               ('Singapore Management University', 'Singapore', 'https://smu.edu.sg')],
 'Slovakia': [('Comenius University Bratislava', 'Bratislava', 'https://uniba.sk'),
              ('Slovak University of Technology in Bratislava', 'Bratislava', 'https://stuba.sk')],
 'Slovenia': [('University of Ljubljana', 'Ljubljana', 'https://uni-lj.si'),
              ('University of Maribor', 'Maribor', 'https://um.si')],
 'South Africa': [('University of Cape Town', 'Cape Town', 'https://uct.ac.za'),
                  ('University of the Witwatersrand', 'Johannesburg', 'https://wits.ac.za'),
                  ('Stellenbosch University', 'Stellenbosch', 'https://sun.ac.za'),
                  ('University of Pretoria', 'Pretoria', 'https://up.ac.za')],
 'Spain': [('University of Barcelona', 'Barcelona', 'https://ub.edu'),
           ('Complutense University of Madrid', 'Madrid', 'https://ucm.es'),
           ('Universitat Autonoma de Barcelona', 'Barcelona', 'https://uab.cat'),
           ('Universidad Autonoma de Madrid', 'Madrid', 'https://uam.es')],
 'Sri Lanka': [('University of Colombo', 'Colombo', 'https://cmb.ac.lk'),
               ('University of Peradeniya', 'Kandy', 'https://pdn.ac.lk'),
               ('University of Moratuwa', 'Moratuwa', 'https://mrt.ac.lk'),
               ('University of Kelaniya', 'Kelaniya', 'https://kln.ac.lk')],
 'Sudan': [('University of Khartoum', 'Khartoum', 'https://uofk.edu')],
 'Syria': [('Damascus University', 'Damascus', '')],
 'Taiwan': [('National Taiwan University', 'Taipei', 'https://ntu.edu.tw'),
            ('National Tsing Hua University', 'Hsinchu', 'https://nthu.edu.tw'),
            ('National Cheng Kung University', 'Tainan', 'https://ncku.edu.tw'),
            ('National Yang Ming Chiao Tung University', 'Hsinchu', 'https://nycu.edu.tw'),
            ('National Chengchi University', 'Taipei', 'https://nccu.edu.tw')],
 'Tajikistan': [('Tajik National University', 'Dushanbe', '')],
 'Tanzania': [('University of Dar es Salaam', 'Dar es Salaam', 'https://udsm.ac.tz'),
              ('Sokoine University of Agriculture', 'Morogoro', 'https://sua.ac.tz')],
 'Thailand': [('Chulalongkorn University', 'Bangkok', 'https://chula.ac.th'),
              ('Mahidol University', 'Nakhon Pathom', 'https://mahidol.ac.th'),
              ('Chiang Mai University', 'Chiang Mai', 'https://cmu.ac.th'),
              ('Thammasat University', 'Bangkok', 'https://tu.ac.th'),
              ('Kasetsart University', 'Bangkok', 'https://ku.ac.th')],
 'Timor-Leste': [('National University of Timor Lorosae', 'Dili', '')],
 'Tunisia': [('University of Tunis El Manar', 'Tunis', 'https://utm.rnu.tn'),
             ('University of Carthage', 'Tunis', ''),
             ('University of Sfax', 'Sfax', '')],
 'Turkey': [('Bogazici University', 'Istanbul', 'https://boun.edu.tr'),
            ('Middle East Technical University', 'Ankara', 'https://metu.edu.tr'),
            ('Koc University', 'Istanbul', 'https://ku.edu.tr'),
            ('Istanbul Technical University', 'Istanbul', 'https://itu.edu.tr')],
 'Turkmenistan': [('Turkmen State University', 'Ashgabat', '')],
 'Uganda': [('Makerere University', 'Kampala', 'https://mak.ac.ug'),
            ('Mbarara University of Science and Technology', 'Mbarara', 'https://must.ac.ug')],
 'Ukraine': [('Taras Shevchenko National University of Kyiv', 'Kyiv', 'https://univ.kiev.ua'),
             ('Kyiv Polytechnic Institute', 'Kyiv', 'https://kpi.ua'),
             ('Kharkiv National University', 'Kharkiv', ''),
             ('Lviv Polytechnic National University', 'Lviv', '')],
 'United Arab Emirates': [('Khalifa University', 'Abu Dhabi', 'https://ku.ac.ae'),
                          ('United Arab Emirates University', 'Al Ain', 'https://uaeu.ac.ae'),
                          ('American University of Sharjah', 'Sharjah', 'https://aus.edu'),
                          ('University of Sharjah', 'Sharjah', 'https://sharjah.ac.ae')],
 'Uruguay': [('Universidad de la Republica', 'Montevideo', 'https://udelar.edu.uy'),
             ('Universidad ORT Uruguay', 'Montevideo', 'https://ort.edu.uy')],
 'Uzbekistan': [('National University of Uzbekistan', 'Tashkent', ''),
                ('Tashkent University of Information Technologies', 'Tashkent', ''),
                ('Westminster International University in Tashkent', 'Tashkent', 'https://wiut.uz')],
 'Venezuela': [('Universidad Central de Venezuela', 'Caracas', 'https://ucv.ve'),
               ('Universidad Simon Bolivar', 'Caracas', ''),
               ('Universidad de los Andes Venezuela', 'Merida', '')],
 'Vietnam': [('Vietnam National University Hanoi', 'Hanoi', 'https://vnu.edu.vn'),
             ('Vietnam National University Ho Chi Minh City', 'Ho Chi Minh City', 'https://vnuhcm.edu.vn'),
             ('Hanoi University of Science and Technology', 'Hanoi', 'https://hust.edu.vn'),
             ('Ton Duc Thang University', 'Ho Chi Minh City', 'https://tdtu.edu.vn')],
 'Yemen': [("Sana'a University", 'Sanaa', '')],
 'Zambia': [('University of Zambia', 'Lusaka', 'https://unza.zm'),
            ('Copperbelt University', 'Kitwe', 'https://cbu.ac.zm')],
 'Zimbabwe': [('University of Zimbabwe', 'Harare', 'https://uz.ac.zw'),
              ('National University of Science and Technology Zimbabwe', 'Bulawayo', 'https://nust.ac.zw')]}

def _pick_field(name, rank):
    lname = name.lower()
    if name in CUSTOM_FIELD:
        return CUSTOM_FIELD[name]
    keyword_map = [
        (["institute of technology", "polytechnic", "technical university", "university of technology", "engineering"], "Engineering"),
        (["medical", "medicine", "health sciences"], "Medicine & Health Sciences"),
        (["agricultur", "agriculture and", "veterinary"], "Agriculture & Environmental Science"),
        (["business school", "business university", "management"], "Business Administration"),
        (["economics", "finance"], "Economics & Finance"),
        (["law "], "Law"),
        (["science and technology", "science & technology"], "Natural Sciences"),
    ]
    for keywords, field in keyword_map:
        if any(k in lname for k in keywords):
            return field
    return FIELD_CYCLE[(rank - 1) % len(FIELD_CYCLE)]


def get_or_create(db, model, lookup, defaults=None):
    instance = db.query(model).filter_by(**lookup).first()
    if instance:
        return instance
    instance = model(**{**lookup, **(defaults or {})})
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def _auto_admission_text(test_name):
    label = test_name or "the local admission process"
    aggregate_note = (
        f"Admission is primarily merit-based on {label} results and/or secondary-school marks. "
        f"Exact cutoffs vary by program and year — always check the university's current official "
        f"merit list or cutoff before applying."
    )
    how_to_apply = (
        f"Apply through the university's official admissions portal. Domestic applicants are assessed "
        f"mainly via {label}; international applicants should also confirm equivalency-certification "
        f"and English-language requirements. Check the official page for exact documents and deadlines."
    )
    return aggregate_note, how_to_apply


def run():
    init_db()
    db = get_db()
    try:
        country_lookup = {}
        for c in COUNTRIES:
            country = get_or_create(db, Country, {"name": c["name"]}, {"education_system": c["education_system"], "grading_scale": c["grading_scale"]})
            country_lookup[c["name"]] = country

        formula_lookup = {}
        for f in AGGREGATE_FORMULAS:
            formula = get_or_create(db, AggregateFormula, {"name": f["name"]}, {
                "country_id": country_lookup[f["country"]].id, "components": f["components"],
                "source_url": f["source_url"], "last_verified": f["last_verified"],
            })
            formula_lookup[f["name"]] = formula

        test_lookup = {}
        for t in TESTS:
            test = get_or_create(db, TestInfo, {"name": t["name"]}, {
                "subjects": t["subjects"], "syllabus_summary": t["syllabus_summary"],
                "official_prep_link": t["official_prep_link"],
            })
            test_lookup[t["name"]] = test

        rank_counter = {}

        for u in UNIVERSITIES:
            rank_counter[u["country"]] = rank_counter.get(u["country"], 0) + 1
            uni = get_or_create(db, University, {"name": u["name"]}, {
                "country_id": country_lookup[u["country"]].id, "city": u["city"],
                "address": u["address"], "website": u["website"], "description": u["description"],
                "rank_in_country": rank_counter[u["country"]],
            })

            for p in u["programs"]:
                existing = db.query(Program).filter_by(university_id=uni.id, name=p["name"]).first()
                if existing:
                    continue
                test_obj = test_lookup.get(p.get("test")) if p.get("test") else None
                formula_obj = formula_lookup.get(p.get("formula")) if p.get("formula") else None
                db.add(Program(
                    university_id=uni.id, test_id=test_obj.id if test_obj else None,
                    formula_id=formula_obj.id if formula_obj else None,
                    name=p["name"], field=p["field"], degree_level=p["degree_level"],
                    duration_years=p["duration_years"], fee_note=p["fee_note"],
                    aggregate_note=p["aggregate_note"], admission_opens=p["admission_opens"],
                    admission_closes=p["admission_closes"], how_to_apply=p["how_to_apply"],
                    admission_source_url=p["admission_source_url"],
                ))

            for s in u["scholarships"]:
                existing = db.query(Scholarship).filter_by(university_id=uni.id, name=s["name"]).first()
                if existing:
                    continue
                db.add(Scholarship(
                    university_id=uni.id, name=s["name"], coverage=s["coverage"],
                    eligibility=s["eligibility"], deadline=s["deadline"],
                ))

            db.commit()

        # ---- EXPANSION: register the 122 new countries + their admission-system TestInfo ----
        for country, (test_name, subjects, syllabus, prep_link) in TEST_INFO.items():
            c = get_or_create(db, Country, {"name": country}, {"education_system": syllabus, "grading_scale": test_name})
            country_lookup[country] = c
            test_lookup[test_name] = get_or_create(db, TestInfo, {"name": test_name}, {
                "subjects": subjects, "syllabus_summary": syllabus, "official_prep_link": prep_link,
            })

        # register the two Pakistan/India test overrides too
        for uni_name, (test_name, subjects, syllabus, prep_link) in TEST_OVERRIDE.items():
            test_lookup[test_name] = get_or_create(db, TestInfo, {"name": test_name}, {
                "subjects": subjects, "syllabus_summary": syllabus, "official_prep_link": prep_link,
            })

        def add_auto_universities(country, entries, fallback_test_name):
            for name, city, website in entries:
                rank_counter[country] = rank_counter.get(country, 0) + 1
                rank = rank_counter[country]
                field = _pick_field(name, rank)
                blurb = CUSTOM_BLURBS.get(name, DEFAULT_BLURB.format(country=country))
                website = website or ""

                uni = get_or_create(db, University, {"name": name}, {
                    "country_id": country_lookup[country].id, "city": city,
                    "address": f"{city}, {country}", "website": website, "description": blurb,
                    "rank_in_country": rank,
                })

                if name in TEST_OVERRIDE:
                    test_name = TEST_OVERRIDE[name][0]
                else:
                    test_name = fallback_test_name
                test_obj = test_lookup.get(test_name)
                aggregate_note, how_to_apply = _auto_admission_text(test_name)

                program_name = f"Undergraduate Admission Guide — {field}"
                existing = db.query(Program).filter_by(university_id=uni.id, name=program_name).first()
                if not existing:
                    db.add(Program(
                        university_id=uni.id, test_id=test_obj.id if test_obj else None, formula_id=None,
                        name=program_name, field=field, degree_level="Undergraduate", duration_years=4,
                        fee_note="Not verified this session — check the university's official fees page.",
                        aggregate_note=aggregate_note,
                        admission_opens="Varies by year — check official calendar",
                        admission_closes="Varies by year — check official calendar",
                        how_to_apply=how_to_apply,
                        admission_source_url=website or f"https://www.google.com/search?q={name.replace(' ', '+')}+official+admissions",
                    ))

                existing_s = db.query(Scholarship).filter_by(university_id=uni.id, name="Merit & need-based aid").first()
                if not existing_s:
                    db.add(Scholarship(
                        university_id=uni.id, name="Merit & need-based aid", coverage=GENERIC_AID_NOTE,
                        eligibility="Academic merit, some need-based", deadline="Varies — check official page",
                    ))
                db.commit()

        core_fallback_test = {
            "Pakistan": None,  # Punjab/QAU both hit the TEST_OVERRIDE branch, no fallback needed
            "United States": "SAT / ACT (US, optional at many schools)",
            "United Kingdom": "UCAS Application (UK)",
            "Canada": "Canadian Provincial Application",
            "Australia": "ATAR (Australia)",
            "Germany": "Abitur + Numerus Clausus (Germany)",
            "China": "Gaokao (China)",
            "India": None,  # University of Delhi hits TEST_OVERRIDE; IISc/IIT Madras fall through below
            "France": "Baccalaureat + Parcoursup (France)",
            "Japan": "Common Test for University Admissions (Japan)",
            "South Korea": "CSAT / Suneung (South Korea)",
            "Netherlands": "VWO + Numerus Fixus (Netherlands)",
            "Sweden": "Swedish Upper Secondary Grades (antagning.se)",
            "Switzerland": "Swiss Matura",
            "New Zealand": "NCEA + University Entrance (New Zealand)",
        }
        # IISc Bangalore and IIT Madras use the same JEE-based system as IIT Bombay/Delhi
        india_jee_unis = {"Indian Institute of Science Bangalore", "IIT Madras"}

        for country, entries in CORE_EXTRA.items():
            fallback = core_fallback_test.get(country)
            if country == "India":
                jee_entries = [e for e in entries if e[0] in india_jee_unis]
                other_entries = [e for e in entries if e[0] not in india_jee_unis]
                add_auto_universities(country, jee_entries, "JEE Main / Advanced (India)")
                add_auto_universities(country, other_entries, None)
            else:
                add_auto_universities(country, entries, fallback)

        for country, entries in NEW_COUNTRY_UNIS.items():
            fallback = TEST_INFO[country][0]
            add_auto_universities(country, entries, fallback)

        total_countries = db.query(Country).count()
        total_universities = db.query(University).count()
        print(f"Seed complete: {total_countries} countries, {total_universities} universities.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
