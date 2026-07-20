/* ═══════════════════════════════════════════
   STUDENT NEXT.AI — AUTHENTICATION LOGIC
   Handles: email/phone login, signup (subject interest +
   education level instead of a fixed country dropdown —
   the University Finder now asks for country fresh on
   every search instead), session storage
   ═══════════════════════════════════════════ */

let currentLoginMethod = 'email';

/* ─── TAB SWITCHING ─────────────────────── */
function showTab(tab) {
  document.getElementById('formSignin').style.display = tab === 'signin' ? 'block' : 'none';
  document.getElementById('formSignup').style.display = tab === 'signup' ? 'block' : 'none';
  document.getElementById('tabSignin').classList.toggle('active', tab === 'signin');
  document.getElementById('tabSignup').classList.toggle('active', tab === 'signup');
  hideMsgs();
}
if (window.location.hash === '#signup') showTab('signup');

function setLoginMethod(method, btn) {
  currentLoginMethod = method;
  document.querySelectorAll('.lm-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('siEmailGroup').style.display = method === 'email' ? 'flex' : 'none';
  document.getElementById('siPhoneGroup').style.display = method === 'phone' ? 'flex' : 'none';
}

/* ─── MESSAGES ──────────────────────────── */
function showErr(msg) {
  const el = document.getElementById('authError');
  el.textContent = msg; el.style.display = 'block';
  document.getElementById('authSuccess').style.display = 'none';
}
function showOk(msg) {
  const el = document.getElementById('authSuccess');
  el.textContent = msg; el.style.display = 'block';
  document.getElementById('authError').style.display = 'none';
}
function hideMsgs() {
  document.getElementById('authError').style.display = 'none';
  document.getElementById('authSuccess').style.display = 'none';
}

/* ─── VALIDATION HELPERS ────────────────── */
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
function isValidPhone(phone) {
  return /^\+?[0-9\s\-]{8,15}$/.test(phone);
}

/* ─── SESSION STORAGE ───────────────────── */
function saveSession(user, token) {
  localStorage.setItem('sn_token', token);
  localStorage.setItem('sn_user', JSON.stringify(user));
  localStorage.setItem('sn_login_time', new Date().toISOString());
}

/* ─── EMAIL/PHONE SIGN IN ───────────────── */
async function doSignIn() {
  const identifier = currentLoginMethod === 'email'
    ? document.getElementById('siEmail').value.trim()
    : document.getElementById('siPhone').value.trim();
  const password = document.getElementById('siPassword').value;

  if (!identifier || !password) { showErr('Please fill in all fields'); return; }
  if (currentLoginMethod === 'email' && !isValidEmail(identifier)) { showErr('Please enter a valid email'); return; }
  if (currentLoginMethod === 'phone' && !isValidPhone(identifier)) { showErr('Please enter a valid phone number'); return; }

  try {
    const res = await fetch(BACKEND_URL + '/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identifier, method: currentLoginMethod, password })
    });
    const data = await res.json();

    if (data.success) {
      saveSession(data.user, data.token);
      showOk('Welcome back! Redirecting...');
      setTimeout(() => window.location.href = '../index.html', 800);
    } else {
      showErr(data.message || 'Invalid credentials');
    }
  } catch (e) {
    showErr('Could not reach the server. Is the backend running at ' + BACKEND_URL + '?');
  }
}

/* ─── SIGN UP (subject interest + education level) ───── */
async function doSignUp() {
  const name = document.getElementById('suName').value.trim();
  const email = document.getElementById('suEmail').value.trim();
  const phone = document.getElementById('suPhone').value.trim();
  const password = document.getElementById('suPassword').value;
  const subjectInterest = document.getElementById('suSubject').value.trim();
  const educationLevel = document.getElementById('suEduLevel').value;
  const agreed = document.getElementById('agreeTerms').checked;

  if (!name || !email || !password) { showErr('Please fill in all required fields'); return; }
  if (!isValidEmail(email)) { showErr('Please enter a valid email address'); return; }
  if (phone && !isValidPhone(phone)) { showErr('Please enter a valid phone number, or leave it blank'); return; }
  if (password.length < 8) { showErr('Password must be at least 8 characters'); return; }
  if (!agreed) { showErr('Please agree to the Terms of Service to continue'); return; }

  try {
    const res = await fetch(BACKEND_URL + '/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name, email, phone, password,
        subject_interest: subjectInterest, education_level: educationLevel
      })
    });
    const data = await res.json();

    if (data.success) {
      saveSession(data.user, data.token);
      showOk('Account created! Redirecting to your dashboard...');
      setTimeout(() => window.location.href = '../index.html', 1000);
    } else {
      showErr(data.message || 'Registration failed. Please try again.');
    }
  } catch (e) {
    showErr('Could not reach the server. Is the backend running at ' + BACKEND_URL + '?');
  }
}


/* ─── FORGOT PASSWORD (real — sends an actual email via emailer.py) ───
   Uses a plain browser prompt() to keep this file small; swap for a
   proper inline form if you want nicer UX. */
async function forgotPassword() {
  const email = (document.getElementById('siEmail')?.value || '').trim()
    || window.prompt('Enter the email address on your account:');
  if (!email) return;
  if (!isValidEmail(email)) { showErr('Please enter a valid email address'); return; }

  try {
    const frontend_url = window.location.origin + window.location.pathname.replace(/login\.html$/, '');
    const res = await fetch(BACKEND_URL + '/api/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, frontend_url }),
    });
    const data = await res.json();
    showOk(data.message || 'If that email has an account, a reset link is on its way.');
  } catch (e) {
    showErr('Could not reach the server. Is the backend running at ' + BACKEND_URL + '?');
  }
}

/* ─── TOAST (shared with main app) ──────── */
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

/* ─── ENTER KEY SUBMIT ──────────────────── */
document.addEventListener('keypress', e => {
  if (e.key === 'Enter') {
    const signinVisible = document.getElementById('formSignin').style.display !== 'none';
    signinVisible ? doSignIn() : doSignUp();
  }
});
