/* ═══════════════════════════════════════════
   STUDENT NEXT.AI — MAIN APP LOGIC
   v3: University Finder AI advisor + Guide directory.
   Sidebar is now a persistent 30/70 split at every
   screen size (icon-rail below 640px) instead of a
   mobile drawer — see style.css — so there's no
   open/close state to manage here anymore.
   ═══════════════════════════════════════════ */

/* ─── MOBILE SIDEBAR DRAWER (hamburger menu) ── */
function openSidebar() {
  document.getElementById('sidebar')?.classList.add('open');
  document.getElementById('sidebarOverlay')?.classList.add('open');
}
function closeSidebar() {
  document.getElementById('sidebar')?.classList.remove('open');
  document.getElementById('sidebarOverlay')?.classList.remove('open');
}
function toggleSidebar() {
  const sb = document.getElementById('sidebar');
  if (!sb) return;
  sb.classList.contains('open') ? closeSidebar() : openSidebar();
}

/* ─── SCREEN NAVIGATION ─────────────────── */
function go(id, btn) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
  const s = document.getElementById('s-' + id);
  if (s) s.classList.add('active');
  if (btn) btn.classList.add('active');
  closeSidebar(); // auto-close the drawer on mobile once a section is chosen

  // Lazy-load each screen's data the first time it's opened
  if (id === 'search' && !window._advisorInit) { window._advisorInit = true; loadCountryDatalist(); }
  if (id === 'countries') loadCountriesGrid();
  if (id === 'calculator' && !window._calcInit) { window._calcInit = true; loadCalculatorCountries(); }
  if (id === 'guides' && !window._guidesInit) { window._guidesInit = true; loadDirectoryCountries(); }
  if (id === 'notifications') loadNotifications();
  if (id === 'history') loadSearchHistory();
}

/* ─── TAB BARS (Search: AI vs Manual — Guides: Directory vs Articles) ── */
function switchSearchTab(tab) {
  document.getElementById('searchTab-ai').classList.toggle('on', tab === 'ai');
  document.getElementById('searchTab-manual').classList.toggle('on', tab === 'manual');
  document.getElementById('searchPane-ai').style.display = tab === 'ai' ? 'block' : 'none';
  document.getElementById('searchPane-manual').style.display = tab === 'manual' ? 'block' : 'none';
  if (tab === 'manual' && !window._searchInit) { window._searchInit = true; loadCountriesPicker(); }
}

function switchGuidesTab(tab) {
  document.getElementById('guidesTab-directory').classList.toggle('on', tab === 'directory');
  document.getElementById('guidesTab-articles').classList.toggle('on', tab === 'articles');
  document.getElementById('guidesPane-directory').style.display = tab === 'directory' ? 'block' : 'none';
  document.getElementById('guidesPane-articles').style.display = tab === 'articles' ? 'block' : 'none';
}

/* ─── TOGGLE FILTER GROUPS (degree level) ── */
function tgl(btn, groupId) {
  document.querySelectorAll('#' + groupId + ' .tbtn').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
}

function qs(text) {
  const inp = document.getElementById('sq');
  if (inp) { inp.value = text; inp.focus(); }
}

function escapeHTML(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

/* ─── CURRENT USER / AUTH HEADERS ────────── */
function currentUser() {
  try { return JSON.parse(localStorage.getItem('sn_user') || 'null'); }
  catch (e) { return null; }
}
function authHeaders() {
  const token = localStorage.getItem('sn_token') || '';
  return { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token };
}

/* ─── LOAD REAL LOGGED-IN USER + VERIFY SESSION ── */
async function loadCurrentUser() {
  const user = currentUser();
  if (!user) return null;

  const nameEl = document.getElementById('userName');
  const emailEl = document.getElementById('userEmail');
  const avEl = document.getElementById('userAvatar');
  if (nameEl) nameEl.textContent = user.name || 'User';
  if (emailEl) emailEl.textContent = user.email || '';
  if (avEl) avEl.textContent = (user.name || 'U').split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);

  const greet = document.getElementById('homeGreeting');
  if (greet) {
    const hour = new Date().getHours();
    const part = hour < 12 ? 'morning' : hour < 18 ? 'afternoon' : 'evening';
    const firstName = (user.name || 'there').split(' ')[0];
    greet.textContent = `Good ${part}, ${firstName} 👋`;
  }

  try {
    const res = await fetch(BACKEND_URL + '/api/auth/verify', { headers: authHeaders() });
    if (res.status === 401) {
      showToast('Your session is no longer valid — please sign in again', 'error');
      setTimeout(signOut, 1400);
      return null;
    }
    const data = await res.json();
    if (data.user) {
      localStorage.setItem('sn_user', JSON.stringify(data.user));
      populateSettingsForm(data.user);
      const advName = document.getElementById('advName');
      if (advName && !advName.value) advName.value = data.user.name || '';
    }
  } catch (e) {
    console.log('Could not verify session — backend may be offline:', e);
  }

  return user;
}

function populateSettingsForm(user) {
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.value = val ?? ''; };
  set('setName', user.name);
  set('setEmail', user.email);
  set('setSubject', user.subject_interest);
  set('setEduLevel', user.education_level);
}

/* ─── USER DROPDOWN MENU ────────────────── */
function toggleUserMenu() {
  const dd = document.getElementById('userDropdown');
  if (dd) dd.style.display = dd.style.display === 'none' ? 'flex' : 'none';
}

/* ─── SIGN OUT ───────────────────────────── */
function signOut() {
  localStorage.removeItem('sn_token');
  localStorage.removeItem('sn_user');
  localStorage.removeItem('sn_login_time');
  window.location.href = 'pages/login.html';
}

/* ─── PROGRAM RENDERING (Manual Browse results) ── */
function programCardHTML(p) {
  const initials = (p.university || '?').slice(0, 2).toUpperCase();
  const match = p.match ? `<span class="job-match">${p.match} match</span>` : '';
  const fee = p.fee_amount ? `${p.fee_amount} ${p.fee_currency} ${p.fee_period}` : (p.fee_note || 'Fee: verify on official site');
  const agg = p.aggregate_required_min ? `Aggregate needed: ${p.aggregate_required_min}%` : (p.aggregate_note || '');
  return `
    <div class="job-card">
      <div class="job-logo" style="background:linear-gradient(135deg,#4f46e5,#14b8a6)">${initials}</div>
      <div class="job-info">
        <div class="job-title">${escapeHTML(p.university)} — ${escapeHTML(p.name)}</div>
        <div class="job-meta">
          <span>${escapeHTML(p.country || '')}</span>
          <span>${escapeHTML(p.city || '')}</span>
          <span class="job-rate">${escapeHTML(fee)}</span>
          <span>${escapeHTML(agg)}</span>
          ${p.test ? `<span>${escapeHTML(p.test)}</span>` : ''}
          ${match}
        </div>
      </div>
      <button class="btn-apply" onclick="window.open('${p.admission_source_url || '#'}','_blank')">Details →</button>
    </div>`;
}

function renderProgramList(programs, listEl, countEl) {
  if (!listEl) return;
  if (countEl) countEl.textContent = programs.length;
  if (programs.length === 0) {
    listEl.innerHTML = '<div style="padding:20px;color:#94a3b8;font-size:13px">No programs found — try different keywords, widen your country selection, or check back once the dataset grows.</div>';
    return;
  }
  listEl.innerHTML = programs.map(programCardHTML).join('');
}

/* ─── UNIVERSITY CARDS (AI Finder + Directory + Home featured) ── */
let UNI_CACHE = {};
function cacheUni(u) { if (u && u.id != null) UNI_CACHE[u.id] = u; }

function renderUniCard(uni, badge) {
  cacheUni(uni);
  const initials = (uni.name || '?').slice(0, 2).toUpperCase();
  const prog = (uni.programs && uni.programs[0]) || null;
  return `
    <div class="uni-card fade-up">
      ${badge ? `<div class="uni-badge">${escapeHTML(badge)}</div>` : ''}
      <div class="uni-card-top">
        <div class="uni-logo">${initials}</div>
        <div class="uni-card-info">
          <div class="uni-name">${escapeHTML(uni.name)}</div>
          <div class="uni-loc">${escapeHTML(uni.city || '')}${uni.country ? ', ' + escapeHTML(uni.country) : ''}</div>
        </div>
      </div>
      <p class="uni-desc">${escapeHTML(uni.description || '')}</p>
      ${prog ? `<div class="uni-tags">${prog.field ? `<span class="uni-tag">${escapeHTML(prog.field)}</span>` : ''}${prog.test ? `<span class="uni-tag alt">${escapeHTML(prog.test)}</span>` : ''}</div>` : ''}
      <button class="btn-outline sm" onclick="openUniModal(${uni.id})">View admission guide →</button>
    </div>`;
}

function universityModalHTML(uni) {
  const progs = uni.programs || [];
  const progHtml = progs.map(p => `
    <div class="guide-prog-block">
      <h4>${escapeHTML(p.name)}${p.field ? ` <span class="uni-tag">${escapeHTML(p.field)}</span>` : ''}</h4>
      ${p.test ? `<p><strong>Test:</strong> ${escapeHTML(p.test)}</p>` : ''}
      ${p.syllabus_summary ? `<p><strong>Syllabus:</strong> ${escapeHTML(p.syllabus_summary)}</p>` : ''}
      ${p.aggregate_note ? `<p><strong>Aggregate / requirement:</strong> ${escapeHTML(p.aggregate_note)}</p>` : ''}
      ${p.how_to_apply ? `<p><strong>How to apply:</strong> ${escapeHTML(p.how_to_apply)}</p>` : ''}
      ${p.fee_note ? `<p><strong>Fees:</strong> ${escapeHTML(p.fee_note)}</p>` : ''}
      ${p.admission_source_url ? `<a href="${p.admission_source_url}" target="_blank" class="btn-outline sm">Official admissions page →</a>` : ''}
    </div>`).join('');
  const scholarships = (uni.scholarships || []).map(s => `
    <p style="font-size:12.5px;color:#64748b;margin:4px 0"><strong>${escapeHTML(s.name)}:</strong> ${escapeHTML(s.coverage)} — ${escapeHTML(s.eligibility)} <span style="color:#94a3b8">(deadline: ${escapeHTML(s.deadline)})</span></p>`).join('');
  return `
    <h2 style="margin-top:0">${escapeHTML(uni.name)}</h2>
    <p style="color:#64748b;margin-top:-6px">${escapeHTML(uni.city || '')}${uni.country ? ', ' + escapeHTML(uni.country) : ''}${uni.rank_in_country ? ` · #${uni.rank_in_country} in ${escapeHTML(uni.country)}` : ''}</p>
    <p>${escapeHTML(uni.description || '')}</p>
    ${uni.website ? `<a href="${uni.website}" target="_blank" style="font-size:12.5px;color:#4f46e5">${escapeHTML(uni.website)}</a>` : ''}
    <hr style="margin:16px 0;border:none;border-top:1px solid #e2e8f0"/>
    ${progHtml || '<p style="color:#94a3b8;font-size:13px">No admission guide on file yet for this university.</p>'}
    ${scholarships ? `<hr style="margin:16px 0;border:none;border-top:1px solid #e2e8f0"/><div class="sec-title" style="margin-bottom:8px">Scholarships</div>${scholarships}` : ''}
  `;
}

function openUniModal(id) {
  const uni = UNI_CACHE[id];
  if (!uni) return;
  document.getElementById('modal-body').innerHTML = universityModalHTML(uni);
  document.getElementById('modal').classList.add('open');
}

/* ─── UNIVERSITY FINDER — AI RECOMMENDATION ── */
async function loadCountryDatalist() {
  const dl = document.getElementById('countryList');
  if (!dl || dl.dataset.loaded) return;
  try {
    const res = await fetch(BACKEND_URL + '/api/countries/names');
    const data = await res.json();
    dl.innerHTML = (data.countries || []).map(c => `<option value="${escapeHTML(c)}">`).join('');
    dl.dataset.loaded = '1';
  } catch (e) { /* datalist just stays empty — text inputs still work fine */ }
}

async function runAdvisor() {
  const resultBox = document.getElementById('advisorResult');
  const name = document.getElementById('advName').value.trim();
  const education_level = document.getElementById('advEduLevel').value;
  const marks_obtained = document.getElementById('advMarksObtained').value;
  const marks_total = document.getElementById('advMarksTotal').value;
  const interest = document.getElementById('advInterest').value.trim();
  const country = document.getElementById('advCountry').value.trim();
  const target_country = document.getElementById('advTargetCountry').value.trim();

  if (!name || !education_level || !marks_obtained || !marks_total || !interest || !country) {
    showToast('Please fill in your name, education level, marks, interest, and country', 'error');
    return;
  }

  resultBox.innerHTML = '<div style="padding:20px;color:#64748b;font-size:13px;display:flex;align-items:center;gap:8px"><div class="spin"></div>Matching you against the database…</div>';

  const user = currentUser();
  try {
    const res = await fetch(BACKEND_URL + '/api/advisor/recommend', {
      method: 'POST', headers: authHeaders(),
      body: JSON.stringify({
        name, education_level, marks_obtained, marks_total, interest, country, target_country,
        email: user ? user.email : null,
      }),
    });
    const data = await res.json();
    if (!data.success) {
      resultBox.innerHTML = `<p style="color:#dc2626;font-size:13px;padding:14px 0">${escapeHTML(data.message || 'Could not get a recommendation')}</p>`;
      return;
    }
    renderAdvisorResult(data.result);
    refreshHomeStats();
    loadSearchHistory();
  } catch (e) {
    resultBox.innerHTML = '<p style="color:#dc2626;font-size:13px;padding:14px 0">Could not reach the backend. Is it running?</p>';
  }
}

function renderAdvisorResult(r) {
  const box = document.getElementById('advisorResult');
  const pct = r.profile_summary.percentage != null ? r.profile_summary.percentage + '%' : '—';

  let html = `
    <div class="advisor-summary fade-up">
      <div class="advisor-summary-row">
        <span>Hi ${escapeHTML(r.profile_summary.name)} — your score: <strong>${pct}</strong></span>
        ${r.ai_powered ? '<span class="ai-badge">🤖 AI-powered</span>' : '<span class="ai-badge alt">⚡ Rule-based match</span>'}
      </div>
      <h3>Suggested field: ${escapeHTML(r.field)}</h3>
      <p>${escapeHTML(r.scope)}</p>
    </div>`;

  html += '<div class="uni-card-grid" style="margin-top:14px">';
  if (r.home_pick) {
    html += renderUniCard(r.home_pick, `🏠 Best in ${r.home_country_resolved}`);
  } else if (r.home_country_input) {
    html += `<div class="uni-card"><p class="uni-desc">Couldn't match "${escapeHTML(r.home_country_input)}" to a country in the database — check the spelling, or browse manually.</p></div>`;
  }
  if (r.target_pick) {
    const label = r.used_default_abroad_country ? `✈️ Popular pick: ${r.target_country_resolved}` : `✈️ Best in ${r.target_country_resolved}`;
    html += renderUniCard(r.target_pick, label);
  }
  html += '</div>';

  const more = [...(r.home_alternatives || []), ...(r.target_alternatives || [])];
  if (more.length) {
    html += `<div class="sec-title" style="margin-top:18px">More top-ranked options</div><div class="uni-card-grid">`;
    html += more.map(u => renderUniCard(u)).join('');
    html += '</div>';
  }

  box.innerHTML = html;
}

/* ─── COUNTRIES PICKER (Manual Browse tab) ── */
let ALL_COUNTRIES = [];

async function loadCountriesPicker() {
  const picker = document.getElementById('ppicker');
  if (!picker) return;
  try {
    const res = await fetch(BACKEND_URL + '/api/countries');
    const data = await res.json();
    ALL_COUNTRIES = data.countries || [];
    picker.innerHTML = ALL_COUNTRIES.map(c => `
      <label class="pp">
        <input type="checkbox" value="${escapeHTML(c.name)}" checked onchange="countCountries()">
        <div class="pp-in"><div class="pp-logo" style="background:#4f46e5">${c.name.slice(0,2).toUpperCase()}</div><span>${escapeHTML(c.name)}</span></div>
      </label>`).join('');
    countCountries();
  } catch (e) {
    picker.innerHTML = '<p style="color:#dc2626;font-size:13px">Could not load countries — is the backend running?</p>';
  }
}

function selectAllCountries() {
  const boxes = document.querySelectorAll('#ppicker input[type=checkbox]');
  const allChecked = Array.from(boxes).every(b => b.checked);
  boxes.forEach(b => { b.checked = !allChecked; });
  countCountries();
  const btn = document.getElementById('selAllBtn');
  if (btn) btn.textContent = allChecked ? 'Select all' : 'Deselect all';
}

function countCountries() {
  const count = document.querySelectorAll('#ppicker input:checked').length;
  const msg = document.getElementById('pcount');
  if (msg) msg.textContent = count === 0
    ? '0 countries selected — select at least one'
    : count + ' countr' + (count > 1 ? 'ies' : 'y') + ' selected';
}

/* ─── SEARCH UNIVERSITIES (Manual Browse — real backend, real local dataset) ── */
async function doSearch() {
  const q = (document.getElementById('sq') || {}).value || '';
  const resultsBox = document.getElementById('results');
  const rlist = document.getElementById('rlist');
  const rcnt = document.getElementById('rcnt');
  if (!resultsBox) return;

  const countries = Array.from(document.querySelectorAll('#ppicker input:checked')).map(i => i.value);
  const degreeBtn = document.querySelector('#dg .tbtn.on');
  const degreeText = degreeBtn ? degreeBtn.textContent.trim().toLowerCase() : 'all levels';
  const degreeLevel = degreeText.includes('all') ? 'all' : degreeText.includes('undergrad') ? 'undergraduate' : 'graduate';

  resultsBox.style.display = 'block';
  rlist.innerHTML = '<div style="padding:14px;color:#64748b;font-size:13px;display:flex;align-items:center;gap:8px"><div class="spin"></div>Searching the dataset…</div>';

  const user = currentUser();

  try {
    const res = await fetch(BACKEND_URL + '/api/universities/search', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({
        query: q, countries, field: 'all', degree_level: degreeLevel,
        email: user ? user.email : null,
      }),
    });
    const data = await res.json();
    renderProgramList(data.programs || [], rlist, rcnt);
    refreshHomeStats();
    loadSearchHistory();
  } catch (e) {
    rlist.innerHTML = '<div style="padding:14px;color:#dc2626;font-size:13px">Could not reach the backend at ' + BACKEND_URL + '. Is it running? (see README)</div>';
  }
}

/* ─── HOME: FEATURED UNIVERSITIES ────────── */
async function loadHomeFeatured() {
  const list = document.getElementById('homeFeatured');
  if (!list) return;
  list.innerHTML = '<p style="color:#94a3b8;font-size:13px">Loading…</p>';
  try {
    const res = await fetch(BACKEND_URL + '/api/universities/featured');
    const data = await res.json();
    const unis = data.universities || [];
    if (unis.length === 0) { list.innerHTML = '<p style="color:#94a3b8;font-size:13px">No data yet — run the seed script.</p>'; return; }
    list.innerHTML = unis.map(u => renderUniCard(u, `#${u.rank_in_country} in ${u.country}`)).join('');
  } catch (e) {
    list.innerHTML = '<p style="color:#dc2626;font-size:13px">Could not reach the backend.</p>';
  }
}

/* ─── HOME STATS (real numbers, not hardcoded) ── */
async function refreshHomeStats() {
  const user = currentUser();
  if (!user) return;

  try {
    const [historyRes, notifRes, countriesRes] = await Promise.all([
      fetch(BACKEND_URL + '/api/search/history?email=' + encodeURIComponent(user.email)),
      fetch(BACKEND_URL + '/api/notifications', { headers: authHeaders() }),
      fetch(BACKEND_URL + '/api/countries'),
    ]);
    const historyData = await historyRes.json();
    const notifData = await notifRes.json();
    const countriesData = await countriesRes.json();
    const countries = countriesData.countries || [];

    const searchesEl = document.getElementById('statSearches');
    if (searchesEl) searchesEl.textContent = (historyData.history || []).length;

    const countriesEl = document.getElementById('statCountries');
    if (countriesEl) countriesEl.textContent = countries.length;

    const uniTotal = countries.reduce((sum, c) => sum + (c.university_count || 0), 0);
    const uniEl = document.getElementById('statUniversities');
    if (uniEl) uniEl.textContent = uniTotal;

    const navCB = document.getElementById('navCountriesBadge');
    const navCS = document.getElementById('navCountriesSub');
    if (navCB) navCB.textContent = countries.length;
    if (navCS) navCS.textContent = countries.length + ' education systems';

    const unread = (notifData.notifications || []).filter(n => !n.read).length;
    const notifsEl = document.getElementById('statNotifs');
    if (notifsEl) notifsEl.textContent = unread;

    const badge = document.getElementById('navNotifBadge');
    const sub = document.getElementById('navNotifSub');
    if (badge) { badge.style.display = unread > 0 ? 'flex' : 'none'; badge.textContent = unread; }
    if (sub) sub.textContent = unread + ' new';
  } catch (e) {
    console.log('Could not refresh home stats:', e);
  }
}

/* ─── COUNTRIES SCREEN ──────────────────── */
async function loadCountriesGrid() {
  const grid = document.getElementById('pgrid');
  if (!grid || grid.dataset.loaded) return;
  try {
    const res = await fetch(BACKEND_URL + '/api/countries');
    const data = await res.json();
    const countries = data.countries || [];
    document.getElementById('countriesSubHead').textContent =
      `${countries.length} countries seeded — university count and formula-verification status below`;
    grid.innerHTML = countries.map(c => {
      const cat = c.has_verified_formula ? 'verified' : 'holistic';
      const badgeStyle = c.has_verified_formula ? 'background:#f0fdf4;color:#15803d' : 'background:#f1f5f9;color:#64748b';
      const badgeText = c.has_verified_formula ? 'Verified formula' : 'Holistic / rank-based';
      return `
      <div class="pcard" data-c="${cat}">
        <div class="pc-top">
          <div class="pc-logo" style="background:linear-gradient(135deg,#4f46e5,#14b8a6)">${c.name.slice(0,2).toUpperCase()}</div>
          <div class="pc-info"><div class="pc-name">${escapeHTML(c.name)}</div><div class="pc-type">${c.university_count} universit${c.university_count===1?'y':'ies'} seeded</div></div>
          <div class="pc-right"><div class="pc-jobs">${c.university_count} seeded</div><div class="pc-live" style="${badgeStyle}">${badgeText}</div></div>
        </div>
        <p class="pc-desc">${escapeHTML(c.education_system)}</p>
      </div>`;
    }).join('');
    grid.dataset.loaded = '1';
  } catch (e) {
    grid.innerHTML = '<p style="color:#dc2626;font-size:13px">Could not load countries.</p>';
  }
}

function fc(cat, btn) {
  document.querySelectorAll('.ftab').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  document.querySelectorAll('.pcard').forEach(card => {
    card.classList.toggle('hidden', !(cat === 'all' || card.dataset.c === cat));
  });
}

/* ─── GUIDE PLATFORM: UNIVERSITY DIRECTORY ── */
async function loadDirectoryCountries() {
  const sel = document.getElementById('dirCountry');
  if (!sel || sel.dataset.loaded) return;
  try {
    const res = await fetch(BACKEND_URL + '/api/countries/names');
    const data = await res.json();
    sel.innerHTML = (data.countries || []).map(c => `<option>${escapeHTML(c)}</option>`).join('');
    sel.dataset.loaded = '1';
    if ([...sel.options].some(o => o.value === 'Pakistan')) sel.value = 'Pakistan';
    loadDirectoryCountry();
  } catch (e) {
    sel.innerHTML = '<option>Could not load</option>';
  }
}

async function loadDirectoryCountry() {
  const country = document.getElementById('dirCountry').value;
  const box = document.getElementById('dirResults');
  box.innerHTML = '<p style="color:#94a3b8;font-size:13px">Loading…</p>';
  try {
    const res = await fetch(BACKEND_URL + '/api/universities/directory?country=' + encodeURIComponent(country));
    const data = await res.json();
    const entry = (data.directory || [])[0];
    if (!entry || !entry.universities.length) {
      box.innerHTML = '<p style="color:#94a3b8;font-size:13px">No universities found for this country.</p>';
      return;
    }
    box.innerHTML = `<p style="font-size:12.5px;color:#94a3b8;margin:-4px 0 14px">${escapeHTML(entry.education_system)}</p><div class="uni-card-grid">` +
      entry.universities.map(u => renderUniCard(u, `#${u.rank_in_country} in ${country}`)).join('') + '</div>';
  } catch (e) {
    box.innerHTML = '<p style="color:#dc2626;font-size:13px">Could not load directory.</p>';
  }
}

/* ─── CHAT ───────────────────────────────── */
function askT(text) {
  const inp = document.getElementById('chatInp');
  inp.value = text;
  sendChat();
}

function appendChatMsg(role, html) {
  const msgs = document.getElementById('chatMsgs');
  const div = document.createElement('div');
  div.className = 'cmsg ' + (role === 'user' ? 'user' : 'bot');
  div.innerHTML = `<div class="cmsg-bbl">${html}</div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

async function sendChat() {
  const inp = document.getElementById('chatInp');
  const message = inp.value.trim();
  if (!message) return;
  appendChatMsg('user', escapeHTML(message));
  inp.value = '';

  appendChatMsg('bot', '<div class="spin"></div>');
  const msgs = document.getElementById('chatMsgs');
  const loadingBubble = msgs.lastChild;

  try {
    const res = await fetch(BACKEND_URL + '/api/chat', {
      method: 'POST', headers: authHeaders(), body: JSON.stringify({ message }),
    });
    const data = await res.json();
    loadingBubble.remove();
    appendChatMsg('bot', escapeHTML(data.response).replace(/\n/g, '<br/>'));
  } catch (e) {
    loadingBubble.remove();
    appendChatMsg('bot', 'Could not reach the server. Is the backend running?');
  }
}

function clearChat() {
  document.getElementById('chatMsgs').innerHTML =
    '<div class="cmsg bot"><div class="cmsg-bbl">Chat cleared. What would you like help with?</div></div>';
}

/* ─── AGGREGATE CALCULATOR ───────────────── */
async function loadCalculatorCountries() {
  const sel = document.getElementById('calcCountry');
  try {
    const res = await fetch(BACKEND_URL + '/api/countries');
    const data = await res.json();
    sel.innerHTML = (data.countries || []).map(c => `<option>${escapeHTML(c.name)}</option>`).join('');
    loadFormulasForCountry();
  } catch (e) {
    sel.innerHTML = '<option>Could not load countries</option>';
  }
}

async function loadFormulasForCountry() {
  const country = document.getElementById('calcCountry').value;
  const formulaSel = document.getElementById('calcFormula');
  try {
    const res = await fetch(BACKEND_URL + '/api/countries/' + encodeURIComponent(country) + '/formulas');
    const data = await res.json();
    if (!data.formulas || data.formulas.length === 0) {
      formulaSel.innerHTML = '<option value="">No verified formula for this country</option>';
      document.getElementById('calcInputs').innerHTML =
        `<p style="color:#94a3b8;font-size:13px;margin-top:10px">${escapeHTML(country)} doesn't publish a single weighted percentage formula — admission is holistic or rank-based. Check the Countries tab for details, or ask the AI agent.</p>`;
      return;
    }
    formulaSel.innerHTML = data.formulas.map(f => `<option value="${f.id}">${escapeHTML(f.name)}</option>`).join('');
    window._formulas = data.formulas;
    renderFormulaInputs();
  } catch (e) {
    formulaSel.innerHTML = '<option value="">Could not load formulas</option>';
  }
}

function renderFormulaInputs() {
  const formulaId = parseInt(document.getElementById('calcFormula').value);
  const formula = (window._formulas || []).find(f => f.id === formulaId);
  const container = document.getElementById('calcInputs');
  if (!formula) { container.innerHTML = ''; return; }

  container.innerHTML = '<div class="form-2col" style="margin-top:14px">' + formula.components.map(c => `
    <div class="fg">
      <label class="fl">${escapeHTML(c.label)} <span style="color:#94a3b8;font-weight:400">(weight ${Math.round(c.weight*100)}%)</span></label>
      <input class="fi" type="number" min="0" max="100" step="0.01" data-key="${c.key}" class="calc-score-input"/>
    </div>`).join('') + '</div>';
  container.querySelectorAll('input').forEach(i => i.classList.add('calc-score-input'));
}

async function runCalculator() {
  const formulaId = parseInt(document.getElementById('calcFormula').value);
  if (!formulaId) { showToast('No formula available for this country', 'error'); return; }

  const scores = {};
  document.querySelectorAll('.calc-score-input').forEach(inp => { scores[inp.dataset.key] = parseFloat(inp.value || 0); });

  try {
    const res = await fetch(BACKEND_URL + '/api/calculator', {
      method: 'POST', headers: authHeaders(),
      body: JSON.stringify({ formula_id: formulaId, scores }),
    });
    const data = await res.json();
    const box = document.getElementById('calcResult');
    if (!data.success) { showToast(data.message || 'Could not calculate', 'error'); return; }

    box.style.display = 'block';
    box.innerHTML = `
      <div style="background:#faeeda;border-radius:12px;padding:16px">
        <p style="font-size:11px;color:#78350f;margin:0 0 2px">Your aggregate</p>
        <p style="font-size:28px;font-weight:600;color:#78350f;margin:0 0 10px">${data.aggregate}%</p>
        ${data.breakdown.map(b => `<p style="font-size:12px;color:#92400e;margin:2px 0">${escapeHTML(b.label)}: ${b.score_pct}% × ${Math.round(b.weight*100)}% = ${b.contribution}</p>`).join('')}
      </div>`;
  } catch (e) {
    showToast('Could not reach the server', 'error');
  }
}

/* ─── GUIDES (static content, real writing not a stub) ── */
const GUIDES = {
  net: `<h2>NUST Entry Test (NET)</h2><p>The NET is NUST's own admission test, contributing 75% of your final merit — by far the heaviest component. Sections cover Mathematics and Physics at FSc Part I & II level, English comprehension, and analytical/IQ reasoning.</p><p><strong>How to prepare:</strong> start from your FSc textbooks — the math and physics questions closely follow the board syllabus rather than going far beyond it. Practice past papers for timing (the test is dense and time-pressured), and don't neglect the analytical section — many students lose easy marks there simply from lack of practice.</p><p>Since NET carries 75% weight vs. only 10% for Matric and 15% for FSc Part-1, a strong NET score can meaningfully outweigh a mediocre Matric result — worth knowing if you're deciding where to focus your remaining prep time.</p>`,
  fast: `<h2>FAST-NUCES Entry Test</h2><p>FAST's formula is Matric 10% + FSc 40% + Entry Test 50% — more balanced than NUST's, meaning your FSc percentage matters more here. The test covers FSc-level math, basic algebra and calculus, analytical reasoning, and English.</p><p><strong>How to prepare:</strong> because FSc counts for 40%, keep your board exam preparation strong rather than over-indexing on test prep alone. For the test itself, timed mock papers are the highest-value prep — the analytical section rewards speed as much as accuracy.</p><p>FAST also accepts valid SAT/NTS scores in some cases — check the current admissions page for whether that applies to your intended campus and program.</p>`,
  jee: `<h2>JEE Main &amp; Advanced</h2><p>JEE Main is the first stage — qualify here to sit JEE Advanced, which is the exam that actually determines IIT admission by all-India rank through JoSAA counseling. There's no percentage aggregate here at all — everything comes down to your rank relative to that year's applicant pool.</p><p><strong>How to prepare:</strong> Physics, Chemistry, and Mathematics at a depth well beyond standard board exams — most successful candidates study 1-2 years ahead specifically for JEE, often alongside board prep. Past papers and full-length mock tests under real time pressure are essential, since the exam rewards speed and accuracy under pressure as much as raw knowledge.</p><p>Computer Science is typically the most competitive branch at the top IITs — a good JEE Advanced score gets you eligible, but the closing rank for CS specifically shifts every year based on that year's applicant pool.</p>`,
  gaokao: `<h2>Understanding the Gaokao</h2><p>The Gaokao is China's National College Entrance Examination — for most students, it's the single biggest factor in university admission. It's scored out of 750 in most provinces, covering Chinese, Mathematics, a foreign language, and a set of comprehensive/elective subjects that varies by province and student track.</p><p><strong>Structure varies by province</strong> — some provinces use a "3+3" or "3+1+2" subject-selection model rather than the older fixed-track system, so the exact subjects and weighting differ depending on where you sit the exam.</p><p>International students typically apply through a separate admissions process rather than the Gaokao itself — if that's your situation, check each university's international admissions office directly rather than assuming Gaokao rules apply to you.</p>`,
  ucas: `<h2>Applying via UCAS</h2><p>UCAS is the centralized system for UK undergraduate applications — one application, up to five course choices, submitted well before the academic year starts. Oxford and Cambridge have an earlier deadline (mid-October) than most other UK universities.</p><p><strong>The personal statement matters a lot</strong> — it's your main chance to explain your interest in the subject beyond grades. Be specific about what you've read, built, or explored related to your field, rather than generic enthusiasm.</p><p>Offers are usually conditional on specific A-level grades (e.g. A*A*A) rather than a percentage aggregate. Some courses (like Cambridge's Computer Science Tripos) also require sitting a subject-specific admissions test, and competitive courses often require a college interview.</p>`,
  calculator: `<h2>How the aggregate calculator works</h2><p>Pick your country, then a formula if one's available. The calculator multiplies each score you enter by that component's real published weight and adds them up — nothing more, nothing hidden.</p><p><strong>Only two formulas are currently verified</strong>: NUST (Matric 10% + FSc Part-1 15% + NET 75%) and FAST-NUCES (Matric 10% + FSc 40% + Entry Test 50%) — both checked against each university's own published admission criteria.</p><p>Every other country/university in the dataset uses holistic review (US, UK, Canada), a national exam rank (China's Gaokao, India's JEE), or a computed score like ATAR (Australia) or CSAT (South Korea) — none of these reduce to a simple weighted percentage, so forcing them into this calculator would misrepresent how admission actually works. Those show an explanation instead.</p>`,
  scholarships: `<h2>Applying for scholarships</h2><p>Most scholarships in the dataset fall into two broad categories. <strong>Need-based aid</strong> is income-driven — you'll typically need to submit financial documentation, and coverage can range from partial tuition to (in some cases, like MIT or LUMS's National Outreach Programme) meeting 100% of demonstrated need. <strong>Merit-based scholarships</strong> are tied to your academic record, aggregate, or entrance exam rank, and are often more competitive with fixed award amounts.</p><p><strong>Practical tips:</strong> most scholarship deadlines line up with (or shortly follow) the admission deadline — don't wait until after you're admitted to start gathering financial documents. Where a coverage amount or deadline isn't shown in this app, that's a deliberate signal to check the university's official financial aid page rather than assume a number.</p>`,
};

function openGuide(id) {
  document.getElementById('modal-body').innerHTML = GUIDES[id] || '<p>Guide not found.</p>';
  document.getElementById('modal').classList.add('open');
}
function closeModal(event) {
  if (event.target.id === 'modal') closeModalDirect();
}
function closeModalDirect() {
  document.getElementById('modal').classList.remove('open');
}

/* ─── NOTIFICATIONS ──────────────────────── */
async function loadNotifications() {
  const list = document.getElementById('notifList');
  if (!list) return;
  try {
    const res = await fetch(BACKEND_URL + '/api/notifications', { headers: authHeaders() });
    const data = await res.json();
    const notifs = data.notifications || [];

    if (notifs.length === 0) {
      list.innerHTML = '<div class="nitem"><div class="ni-body"><div class="ni-t">No notifications yet</div><div class="ni-p">Run a University Finder recommendation or a search to start generating real activity here.</div></div></div>';
      return;
    }

    list.innerHTML = notifs.map(n => `
      <div class="nitem"><div class="ni-body"><div class="ni-t">${escapeHTML(n.title)}</div><div class="ni-p">${escapeHTML(n.body)}</div><div class="ni-time">${new Date(n.created_at).toLocaleString()}</div></div></div>`).join('');
  } catch (e) {
    list.innerHTML = '<p style="color:#dc2626;font-size:13px">Could not load notifications.</p>';
  }
}

async function markAllRead() {
  try {
    await fetch(BACKEND_URL + '/api/notifications/read', { method: 'POST', headers: authHeaders() });
    loadNotifications();
    refreshHomeStats();
    showToast('All notifications marked as read', 'success');
  } catch (e) {
    showToast('Could not reach the server', 'error');
  }
}

/* ─── SETTINGS ───────────────────────────── */
async function saveProfile() {
  const body = {
    name: document.getElementById('setName').value,
    email: document.getElementById('setEmail').value,
    subject_interest: document.getElementById('setSubject').value,
    education_level: document.getElementById('setEduLevel').value,
    password: document.getElementById('setPassword').value || undefined,
  };
  try {
    const res = await fetch(BACKEND_URL + '/api/user/profile', { method: 'PUT', headers: authHeaders(), body: JSON.stringify(body) });
    const data = await res.json();
    if (data.success) {
      localStorage.setItem('sn_user', JSON.stringify(data.user));
      document.getElementById('setPassword').value = '';
      showToast('Profile saved', 'success');
      loadCurrentUser();
    } else {
      showToast(data.message || 'Could not save profile', 'error');
    }
  } catch (e) {
    showToast('Could not reach the server', 'error');
  }
}

/* ─── SEARCH HISTORY ─────────────────────── */
async function loadSearchHistory() {
  const list = document.getElementById('historyList');
  if (!list) return;
  const user = currentUser();
  if (!user) return;
  try {
    const res = await fetch(BACKEND_URL + '/api/search/history?email=' + encodeURIComponent(user.email));
    const data = await res.json();
    const history = data.history || [];
    if (history.length === 0) {
      list.innerHTML = '<div class="hist-row"><div class="hist-info"><div class="hist-query">No searches yet</div><div class="hist-meta">Run a search to see it appear here</div></div></div>';
      return;
    }
    list.innerHTML = history.map(h => `
      <div class="hist-row"><div class="hist-info">
        <div class="hist-query">${escapeHTML(h.query || '(blank query)')}</div>
        <div class="hist-meta">${(h.countries||[]).join(', ') || 'All countries'} · ${h.result_count} results · ${new Date(h.timestamp).toLocaleString()}</div>
      </div></div>`).join('');
  } catch (e) {
    list.innerHTML = '<p style="color:#dc2626;font-size:13px">Could not load history.</p>';
  }
}

async function clearHistory() {
  try {
    await fetch(BACKEND_URL + '/api/search/history', { method: 'DELETE', headers: authHeaders() });
    loadSearchHistory();
    refreshHomeStats();
    showToast('Search history cleared', 'success');
  } catch (e) {
    showToast('Could not reach the server', 'error');
  }
}

/* ─── TOAST ──────────────────────────────── */
function showToast(message, type = 'info') {
  const icons = { success:'✅', error:'❌', info:'💡' };
  const container = document.getElementById('toasts');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.innerHTML = '<span>' + (icons[type] || '💡') + '</span><span>' + message + '</span>';
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

/* ─── NOTIFICATION POLLING (while tab is open) ── */
setInterval(() => { if (currentUser()) refreshHomeStats(); }, NOTIFICATION_POLL_MS);

/* ─── INIT ───────────────────────────────── */
document.addEventListener('DOMContentLoaded', async () => {
  await loadCurrentUser();
  loadHomeFeatured();
  refreshHomeStats();
});
