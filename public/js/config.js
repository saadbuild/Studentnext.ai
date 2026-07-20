/* ═══════════════════════════════════════════
   STUDENT NEXT.AI — SHARED CONFIG
   Change BACKEND_URL here ONLY when you deploy —
   auth.js and main.js both read it from here,
   instead of each having their own copy that could
   drift out of sync.
   ═══════════════════════════════════════════ */
const BACKEND_URL = '';
// Empty string = "same domain as the frontend". On Vercel, the Flask API
// and this static site are served from the same project/domain if you use
// the included vercel.json, so every fetch(BACKEND_URL + '/api/...') call
// just becomes fetch('/api/...'). Only put a URL here if you host the
// backend on a different domain (e.g. Railway/Render) — see README.

// How often the frontend polls for new notifications while a tab is open.
const NOTIFICATION_POLL_MS = 60 * 1000; // 1 minute
