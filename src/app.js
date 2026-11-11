const PROV = __PROV__;
// ---------- storage: never throws; falls back to memory if localStorage is blocked ----------
const MEM = {};
let storageOK = true;
const lsGet = (k) => { try { return localStorage.getItem(k); } catch { return Object.prototype.hasOwnProperty.call(MEM, k) ? MEM[k] : null; } };
const lsSet = (k, v) => { try { localStorage.setItem(k, v); } catch { storageOK = false; MEM[k] = v; } };
const lsDel = (k) => { try { localStorage.removeItem(k); } catch { /* ignore */ } delete MEM[k]; };
const NS = ['hub55_', 'hub5_', 'hub4_', 'hub3_']; // newest first; older versions' settings are migrated forward
function LS(k) {
  for (const ns of NS) {
    const raw = lsGet(ns + k);
    if (raw == null) continue;
    try { return JSON.parse(raw); } catch { lsDel(ns + k); } // corrupted value: drop it and fall back
  }
  return null;
}
const SS = (k, v) => lsSet(NS[0] + k, JSON.stringify(v));
(function migrate() { // copy hub5_cfg / hub4_cfg / hub3_cfg to hub55_cfg5_cfg once (the old key is left untouched)
  if (lsGet('hub55_cfg') != null) return;
  const old = LS('cfg');
  if (old && typeof old === 'object') SS('cfg', old);
})();

const STAMP = '__STAMP__';
const ALL = [...PROV.keyless.map((p) => ({ ...p, kl: 1 })), ...PROV.keyed];
const DEF = {};
ALL.forEach((p) => { DEF[p.id] = p.models[0]; });
const KNOWN = new Set(ALL.map((p) => p.id));
const plainObj = (o) => (o && typeof o === 'object' && !Array.isArray(o) ? o : {});
function cfg() {
  const c = plainObj(LS('cfg'));
  const out = { on: {}, model: {}, key: {}, check: c.check === true };
  Object.entries(plainObj(c.on)).forEach(([k, v]) => { if (KNOWN.has(k) && typeof v === 'boolean') out.on[k] = v; });
  Object.entries(plainObj(c.model)).forEach(([k, v]) => { if (KNOWN.has(k) && typeof v === 'string') out.model[k] = v; });
  Object.entries(plainObj(c.key)).forEach(([k, v]) => { if (KNOWN.has(k) && typeof v === 'string' && v.trim()) out.key[k] = v.trim(); });
  return out;
}
let CF = cfg();
const place = (id, l) => (l.includes(DEF[id]) ? [DEF[id], ...l.filter((x) => x !== DEF[id])] : l); // keep the tested default first
(function applyStoredModels() {
  const st = LS('models');
  if (!st || st.stamp !== STAMP || !plainObj(st.lists)) return;
  ALL.forEach((p) => {
    const l = st.lists[p.id];
    if (Array.isArray(l) && l.length && l.every((x) => typeof x === 'string')) p.models = place(p.id, l);
  });
})();
const isOn = (p) => CF.on[p.id] !== false;
const modelOf = (p) => (p.models.includes(CF.model[p.id]) ? CF.model[p.id] : p.models[0]);
function order() {
  // providers with your own key go first (most reliable), then the no-key chain in order
  return [
    ...ALL.filter((p) => !p.kl && CF.key[p.id] && isOn(p)),
    ...ALL.filter((p) => p.kl && isOn(p))
  ];
}

// ---------- overlays: focus, Escape, inert background, cancel in-flight AI on close ----------
let lastFocus = null;
const ovEls = () => document.querySelectorAll('.ov');
function ov(id) {
  const wasAI = $('#aiov').classList.contains('on');
  const wasOpen = [...ovEls()].some((o) => o.classList.contains('on'));
  ovEls().forEach((o) => o.classList.remove('on'));
  if (wasAI && id !== 'aiov') cancelRun();
  const wrap = $('.wrap');
  if (id) {
    if (!wasOpen) lastFocus = document.activeElement;
    $('#' + id).classList.add('on');
    wrap.inert = true;
    const f = $('#' + id + ' .pnl');
    if (f) f.focus();
  } else {
    wrap.inert = false;
    if (lastFocus && lastFocus.isConnected) lastFocus.focus();
    lastFocus = null;
  }
}
document.querySelectorAll('[data-close]').forEach((b) => { b.addEventListener('click', () => ov()); });
ovEls().forEach((o) => { o.addEventListener('mousedown', (e) => { if (e.target === o) ov(); }); });
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && [...ovEls()].some((o) => o.classList.contains('on'))) { e.preventDefault(); ov(); }
});

// ---------- settings ----------
function sw(id, on, label) {
  return `<label class="sw"><input type="checkbox" data-on="${id}" aria-label="${esc(label)}" ${on ? 'checked' : ''}><span></span></label>`;
}
function msel(p) {
  const m = modelOf(p);
  return `<select data-model="${p.id}" aria-label="Model for ${esc(p.name)}">${p.models.map((x) => `<option ${x === m ? 'selected' : ''}>${esc(x)}</option>`).join('')}</select>`;
}
function renderSettings() {
  let h = `<div class="sec">Check &amp; refresh</div><p><button class="btn" id="sttest" type="button">Test providers</button> <button class="btn" id="strefresh" type="button">Refresh model lists</button></p><p class="hint">Both buttons also save the settings shown below.</p><div id="pvtest" class="hint" aria-live="polite"></div>`;
  h += '<div class="sec">1 · Works out of the box (no key)</div><p class="hint">Tried in order from top to bottom (providers where you saved a key go first). If one fails (429, 401, 5xx, timeout or empty answer) the next enabled provider is used automatically.</p>';
  ALL.filter((p) => p.kl).forEach((p) => {
    h += `<div class="pv"><h3>${esc(p.name)} ${sw(p.id, isOn(p), 'Use ' + p.name)}</h3><p class="hint">${esc(p.note)} · ${link(p.site, 'site')}</p>${p.nomodel ? '' : msel(p)}</div>`;
  });
  h += '<div class="sec">2 · Free-tier / trial developer keys (paste your own)</div><p class="hint">Recommended for reliability: a free Gemini or Groq key takes about a minute.</p>';
  ALL.filter((p) => !p.kl).forEach((p) => {
    h += `<div class="pv"><h3>${esc(p.name)} ${sw(p.id, isOn(p), 'Use ' + p.name)}</h3>${msel(p)}<input type="password" data-key="${p.id}" aria-label="API key for ${esc(p.name)}" placeholder="Paste API key (stored only on this device)" value="${esc(CF.key[p.id] || '')}" autocomplete="off" spellcheck="false"><p class="hint">${link(p.key, 'Get free key ↗')}</p><ol>${p.steps.map((s) => `<li>${esc(s)}</li>`).join('')}</ol><p class="hint"><b>Free tier:</b> ${esc(p.limits)}</p><p class="hint"><b>Browser CORS:</b> ${esc(p.cors)}</p></div>`;
  });
  h += '<div class="sec">3 · Checked but not preloaded</div>';
  PROV.blocked.forEach((p) => {
    h += `<div class="pv"><h3>${esc(p.name)}</h3><p class="hint">${esc(p.why)} ${link(p.site, 'source')}</p></div>`;
  });
  h += `<div class="sec">Options</div><div class="pv"><h3>Quick link check on AI results ${sw('__check', CF.check, 'Quick link check on AI results')}</h3><p class="hint">Browsers block reading other sites' responses (CORS), so this can only tell "host answered" vs "not confirmed" — it cannot confirm the exact page exists. Treat it as a hint. Off by default; when on, blocked checks may log browser network errors in the console.</p></div><p><button class="btn" id="stsave" type="button">Save settings</button> <button class="btn" id="streset" type="button">Reset to defaults</button> <span id="stmsg" class="ok" role="status"></span></p>`;
  $('#stbody').innerHTML = h;
}
function saveForm() {
  Object.keys(COOL).forEach((k) => delete COOL[k]);
  document.querySelectorAll('#stbody [data-on]').forEach((i) => {
    if (i.dataset.on === '__check') CF.check = i.checked;
    else CF.on[i.dataset.on] = i.checked;
  });
  document.querySelectorAll('#stbody [data-model]').forEach((s) => { CF.model[s.dataset.model] = s.value; });
  document.querySelectorAll('#stbody [data-key]').forEach((i) => {
    const v = i.value.trim();
    if (v) CF.key[i.dataset.key] = v;
    else delete CF.key[i.dataset.key];
  });
  SS('cfg', CF);
}
const stNote = () => (storageOK ? '' : ' — note: this browser blocked saving, so settings last only until you close this page');
$('#stbody').addEventListener('click', (e) => {
  const id = e.target.closest('button') && e.target.closest('button').id;
  if (id === 'stsave') {
    saveForm();
    $('#stmsg').textContent = 'Saved on this device ✓ (' + (order().map((p) => p.name).join(' → ') || 'no provider on') + ')' + stNote();
  } else if (id === 'streset') {
    NS.forEach((ns) => lsDel(ns + 'cfg'));
    CF = cfg();
    renderSettings();
    $('#stmsg').textContent = 'Reset ✓';
  } else if (id === 'sttest') testProviders();
  else if (id === 'strefresh') refreshModels();
});
$('#gear').addEventListener('click', () => { renderSettings(); ov('stov'); });

// ---------- AI ----------
function findItem(n) {
  for (const t of D) for (const x of t.items) if (x.n === n) return [x, t];
  return [null, null];
}
function prompt_(ctx) {
  return `You help a person in Tempe, Arizona (USA) find resources. ${ctx}
Return ONLY a JSON array (no markdown, no prose) of 6 objects: {"name":string,"url":string,"why":string (one sentence),"type":"free"|"cheap"}.
Rules: only list real, currently operating services/programs with their official https URL; prefer free options, then cheap ones; prefer national or Arizona/Phoenix-area options; do not invent names, URLs, or prices; if unsure of a URL, use the organization's main homepage.`;
}
const COOL = {}; // provider id -> timestamp until which it is skipped after a 429
const sleep = (ms) => new Promise((z) => setTimeout(z, ms));
function fail(msg, status, cancelled) {
  const e = new Error(msg);
  e.status = status || 0;
  e.cancelled = !!cancelled;
  return e;
}
// One request to one provider. Retries 429 with backoff when p.retry > 0. Throws Error(.status) on any failure.
// o.signal lets the caller cancel (panel closed / new request started).
async function call(p, txt, o = {}) {
  const retry = o.retry != null ? o.retry : (p.retry || 0);
  const h = { 'Content-Type': 'application/json' };
  if (!p.kl) {
    const k = CF.key[p.id] || '';
    if (/[^\x20-\x7e]/.test(k)) throw fail('the saved API key contains characters that are not allowed in a key — re-paste it');
    h.Authorization = 'Bearer ' + k;
  }
  const body = { messages: [{ role: 'user', content: txt }] };
  if (!p.nomodel) body.model = modelOf(p);
  if (p.extra) Object.assign(body, p.extra);
  const cancelled = () => o.signal && o.signal.aborted;
  for (let tr = 0; ; tr++) {
    if (cancelled()) throw fail('cancelled', 0, true);
    const ctl = new AbortController();
    const onAbort = () => ctl.abort();
    if (o.signal) o.signal.addEventListener('abort', onAbort, { once: true });
    const secs = o.timeout || p.timeout || 45;
    const tm = setTimeout(() => ctl.abort(), secs * 1000);
    const done = () => { clearTimeout(tm); if (o.signal) o.signal.removeEventListener('abort', onAbort); };
    let r, j = null;
    try {
      r = await fetch(p.url, { method: 'POST', headers: h, signal: ctl.signal, body: JSON.stringify(body) });
      try { j = await r.json(); } catch (e) {
        if (ctl.signal.aborted) throw e;
        done();
        throw fail('HTTP ' + r.status + ' (reply was not JSON)', r.status);
      }
    } catch (e) {
      done();
      if (e.status != null && e.message && /^HTTP /.test(e.message)) throw e;
      if (cancelled()) throw fail('cancelled', 0, true);
      if (e.name === 'AbortError') throw fail('timed out after ' + secs + 's');
      throw fail('network error or blocked by the browser (' + (e.message || 'fetch failed') + ')');
    }
    done();
    if (r.status === 429) {
      // wait time: Retry-After header (if CORS exposes it) or error.retry_after in the body; long waits = quota, don't retry
      const hv = parseFloat(r.headers.get('retry-after'));
      const bv = j && j.error ? parseFloat(j.error.retry_after) : NaN;
      const wait = !isNaN(hv) ? hv : !isNaN(bv) ? bv : 1.5 * Math.pow(2, tr);
      if (tr < retry && wait <= 6) {
        await sleep(Math.max(wait, 0.5) * 1000);
        continue;
      }
      COOL[p.id] = Date.now() + 90000;
      const em = j && j.error ? (j.error.message || '') : '';
      throw fail('HTTP 429 — ' + (wait > 6 ? 'quota/rate limit (retry after ' + (wait >= 3600 ? Math.round(wait / 3600) + 'h' : Math.round(wait) + 's') + ')' : 'rate limited') + (em && wait <= 6 ? ' — ' + String(em).slice(0, 100) : ''), 429);
    }
    if (!r.ok || !j || !j.choices) {
      if (!p.kl && (r.status === 401 || r.status === 403 || r.status === 400)) COOL[p.id] = Date.now() + 300000;
      if (Array.isArray(j)) j = j[0] || {};
      const em = j && j.error ? (j.error.message || j.error.code || j.error.status || JSON.stringify(j.error)) : '';
      throw fail('HTTP ' + r.status + (em ? ' — ' + String(em).slice(0, 140) : ''), r.status);
    }
    const msg = j.choices[0] && j.choices[0].message;
    const c = msg && typeof msg.content === 'string' ? msg.content.trim() : '';
    if (!c) throw fail('empty answer (HTTP ' + r.status + ')', r.status);
    return c;
  }
}
// Turns the model's text into a clean list. Every URL must parse as http(s); everything else is dropped.
function parse(s) {
  s = String(s).replace(/```(?:json)?/gi, '');
  const tries = [s.trim()];
  const cut = (a, b, add) => { const i = s.indexOf(a), k = s.lastIndexOf(b); if (i >= 0 && k > i) tries.push(s.slice(i, k + add)); };
  cut('[', ']', 1); cut('[{', '}]', 2); cut('{', '}', 1);
  let arr = null;
  for (const t of tries) {
    try {
      let j = JSON.parse(t);
      if (j && !Array.isArray(j) && typeof j === 'object') j = Object.values(j).find(Array.isArray) || null;
      if (Array.isArray(j)) { arr = j; break; }
    } catch { /* try the next candidate */ }
  }
  if (!arr) throw fail('reply was not a JSON list');
  const seen = new Set();
  const clip = (v, n) => String(v == null ? '' : v).replace(/\s+/g, ' ').trim().slice(0, n);
  return arr.filter((o) => o && typeof o === 'object' && typeof o.name === 'string' && o.name.trim() && typeof o.url === 'string').map((o) => ({
    name: clip(o.name, 120), url: safeUrl(o.url), why: clip(o.why, 300), type: clip(o.type, 20).toLowerCase()
  })).filter((o) => {
    if (!o.url || seen.has(o.url)) return false;
    seen.add(o.url);
    return true;
  }).slice(0, 8);
}
async function check(u, el) {
  try {
    await fetch(u, { mode: 'no-cors', cache: 'no-store' });
    if (el && el.isConnected) { el.textContent = '● host answered'; el.className = 'lk ok'; }
  } catch {
    if (el && el.isConnected) { el.textContent = '● not confirmed (blocked or down — open to check)'; el.className = 'lk bad'; }
  }
}
const nice = (p, e) => `${p.name}: ${e.message}`;
let runId = 0, runCtl = null;
function cancelRun() {
  runId++;
  if (runCtl) { runCtl.abort(); runCtl = null; }
}
async function runAI(title, ctx) {
  cancelRun(); // a newer request always replaces an older one (double-click, tab-level then item-level, etc.)
  const me = runId;
  const ctl = new AbortController();
  runCtl = ctl;
  const live = () => me === runId;
  ov('aiov');
  $('#aih').textContent = '✨ ' + title;
  let ps = order();
  const hot = ps.filter((p) => !(COOL[p.id] > Date.now()));
  if (hot.length) ps = hot; // skip providers that just returned 429, unless that leaves none
  if (!ps.length) {
    $('#aibody').innerHTML = '<p>No AI provider is turned on. Open ⚙ Settings and switch one on.</p>';
    $('#aimeta').textContent = '';
    return;
  }
  $('#aibody').innerHTML = '<p><span class="spin" aria-hidden="true"></span> Asking AI… <button class="btn" type="button" id="aistop">Stop</button></p>';
  $('#aimeta').textContent = '';
  const errs = order().filter((p) => !ps.includes(p)).map((p) => p.name + ': skipped (failed a moment ago — rate limit or key problem)');
  const t0 = Date.now();
  for (let i = 0; i < ps.length; i++) {
    const p = ps[i];
    $('#aimeta').textContent = 'Trying ' + p.name + ' · ' + (p.nomodel ? 'auto' : modelOf(p)) + ' (' + (i + 1) + '/' + ps.length + ')' + (errs.length ? ' · skipped ' + errs.length : '');
    try {
      const out = await call(p, prompt_(ctx), { signal: ctl.signal });
      if (!live()) return;
      const arr = parse(out);
      if (!arr.length) throw fail('no usable results in the answer');
      const tag = `lk${me}_`;
      $('#aibody').innerHTML = arr.map((o, k) => {
        const typ = o.type.includes('free') ? 'Free' : o.type.includes('cheap') ? 'Cheap' : '';
        const pill = typ ? `<span class="pill ${typ === 'Free' ? 'pf' : 'pc'}">${typ}</span>` : '';
        return `<div class="res"><b>${esc(o.name)}</b>${pill}<div class="why">${esc(o.why)}</div><a href="${esc(o.url)}" target="_blank" rel="noopener noreferrer">${esc(o.url)}</a><span class="lk" id="${tag}${k}">${CF.check ? 'checking…' : ''}</span></div>`;
      }).join('') + (errs.length ? `<p class="hint">Skipped before this answer: ${esc(errs.join('; '))}</p>` : '');
      $('#aimeta').textContent = 'Answered by ' + p.name + ' · ' + (p.nomodel ? 'auto' : modelOf(p)) + ' · ' + ((Date.now() - t0) / 1000).toFixed(1) + 's';
      runCtl = null;
      if (CF.check) arr.forEach((o, k) => check(o.url, document.getElementById(tag + k)));
      return;
    } catch (e) {
      if (!live() || e.cancelled) {
        if (live()) { // user pressed Stop
          runCtl = null;
          $('#aimeta').textContent = '';
          $('#aibody').innerHTML = '<p class="hint">Stopped. Close this window, or press ✨ again to retry.</p>';
        }
        return;
      }
      errs.push(nice(p, e));
    }
  }
  if (!live()) return;
  runCtl = null;
  $('#aimeta').textContent = '';
  $('#aibody').innerHTML = '<p class="bad">AI is unavailable right now — every enabled provider failed.</p><ul class="hint">' + errs.map((x) => '<li>' + esc(x) + '</li>').join('') + '</ul><p>Quick fix: add a free <b>Gemini</b> or <b>Groq</b> key (about 1 minute) in <button class="btn" type="button" id="aigo">⚙ Settings</button>, or try again in a minute — the no-key services share free quotas and can be busy.</p>';
}
$('#aibody').addEventListener('click', (e) => {
  const b = e.target.closest('button');
  if (!b) return;
  if (b.id === 'aistop') { if (runCtl) runCtl.abort(); }
  else if (b.id === 'aigo') { renderSettings(); ov('stov'); }
});

let busy = false;
async function withBusy(id, fn) {
  if (busy) return;
  busy = true;
  const btns = ['sttest', 'strefresh'].map((i) => document.getElementById(i)).filter(Boolean);
  btns.forEach((b) => { b.disabled = true; });
  try { await fn(); } finally {
    busy = false;
    ['sttest', 'strefresh'].map((i) => document.getElementById(i)).filter(Boolean).forEach((b) => { b.disabled = false; });
  }
}
function testProviders() {
  return withBusy('sttest', async () => {
    saveForm();
    const box = $('#pvtest');
    const rows = ALL.filter((p) => p.kl || CF.key[p.id]);
    const skipped = ALL.filter((p) => !(p.kl || CF.key[p.id]));
    box.innerHTML = rows.map((p) => `<div id="pt-${p.id}"><b>${esc(p.name)}</b> — <span class="spin" aria-hidden="true"></span> testing…</div>`).join('') +
      skipped.map((p) => `<div><b>${esc(p.name)}</b> — <span class="muted">no key saved (not tested)</span></div>`).join('');
    await Promise.all(rows.map(async (p) => {
      const t0 = Date.now();
      let h;
      try {
        const out = await call(p, 'Reply with only the word OK.', { retry: 0, timeout: 75 });
        h = `<span class="ok">✓ working</span> · ${((Date.now() - t0) / 1000).toFixed(1)}s · model ${esc(p.nomodel ? 'auto' : modelOf(p))} · replied “${esc(out.slice(0, 40))}”`;
      } catch (e) {
        h = `<span class="bad">✗ ${esc(e.message)}</span> · ${((Date.now() - t0) / 1000).toFixed(1)}s`;
      }
      const el = document.getElementById('pt-' + p.id);
      if (el) el.innerHTML = `<b>${esc(p.name)}</b> — ${h}`;
    }));
    box.insertAdjacentHTML('beforeend', '<div class="muted">Tested ' + esc(new Date().toLocaleTimeString()) + '. OVH allows only 2 anonymous calls/min per model, so testing it right before using it may show a 429.</div>');
  });
}

const LISTERS = {
  llm7: ['https://api.llm7.io/v1/models', (j) => j.data.filter((m) => m.tier !== 'pro' && m.model_type === 'chat').map((m) => m.id)],
  ovh: ['https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/models', (j) => j.data.map((m) => m.id).filter((id) => !/whisper|stable-diffusion|bge|embedding|tts|guard/i.test(id))],
  poll_text: ['https://text.pollinations.ai/models', (j) => j.filter((m) => m.tier === 'anonymous').map((m) => m.name)],
  openrouter: ['https://openrouter.ai/api/v1/models', (j) => j.data.filter((m) => /:free$/.test(m.id) && (m.architecture && m.architecture.output_modalities || ['text']).join() === 'text').map((m) => m.id).slice(0, 20)]
};
function refreshModels() {
  return withBusy('strefresh', async () => {
    const box = $('#pvtest');
    box.innerHTML = '<span class="spin" aria-hidden="true"></span> Reading live model lists…';
    saveForm();
    const lists = {};
    const out = [];
    await Promise.all(Object.keys(LISTERS).map(async (id) => {
      const p = ALL.find((x) => x.id === id);
      const ctl = new AbortController();
      const tm = setTimeout(() => ctl.abort(), 20000);
      try {
        const r = await fetch(LISTERS[id][0], { signal: ctl.signal });
        if (!r.ok) throw new Error('HTTP ' + r.status);
        const l = LISTERS[id][1](await r.json()).filter((x) => typeof x === 'string' && x);
        if (!l.length) throw new Error('no models returned');
        lists[id] = place(id, l);
        out.push(`<div><b>${esc(p.name)}</b> — <span class="ok">✓ ${l.length} free model${l.length === 1 ? '' : 's'}</span></div>`);
      } catch (e) {
        out.push(`<div><b>${esc(p.name)}</b> — <span class="bad">✗ ${esc(e.name === 'AbortError' ? 'timed out' : e.message)}</span> (keeping built-in list)</div>`);
      } finally { clearTimeout(tm); }
    }));
    const prev = LS('models');
    const st = prev && prev.stamp === STAMP && plainObj(prev.lists) === prev.lists ? prev : { stamp: STAMP, lists: {} };
    Object.assign(st.lists, lists);
    SS('models', st);
    ALL.forEach((p) => { if (lists[p.id]) p.models = lists[p.id]; });
    renderSettings();
    $('#pvtest').innerHTML = out.join('') + '<div class="muted">Model dropdowns updated. Gemini, Groq and Mistral only list models with a key, so those keep the built-in list checked against their docs on Nov 9, 2026.</div>';
  });
}
document.addEventListener('click', (e) => {
  const b = e.target.closest('[data-ai]');
  if (!b) return;
  const [x, t] = findItem(b.dataset.ai);
  if (!x) return;
  runAI('Similar / free alternatives to ' + x.n, `The person is looking at "${x.n}" (${x.d}; category: ${t.t} / ${x.c}; ${x.p === 'Free' ? 'free' : 'price: ' + x.p}). Suggest similar services and free or cheaper alternatives to it, excluding "${x.n}" itself.`);
});
$('#tabai').addEventListener('click', () => {
  const t = D[cur];
  runAI('More free / cheap options for: ' + t.t, `The person is browsing a list titled "${t.t}" which already includes: ${t.items.slice(0, 25).map((x) => x.n).join(', ')}. Suggest additional resources of the same kind that are NOT already in that list.`);
});

// ---------- print ----------
function printMode(all) {
  printing = true;
  const L = $('#list');
  // `all`: every tab; otherwise the whole current tab, ignoring any search/filter, so a printout is never silently partial
  L.innerHTML = (all ? D : [D[cur]]).map((t) => `<h2 class="ptitle">${esc(t.name)}</h2>` + groupedCards(t.items)).join('');
  $('#note').innerHTML = '';
  $('#thead').innerHTML = '';
  $('#pdate').textContent = 'Printed ' + new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) + ' · ' + (all ? 'all ' + D.length + ' tabs' : D[cur].name);
  document.querySelectorAll('.item').forEach((i) => {
    i.classList.add('open');
    const b = i.querySelector('.hd');
    if (b) b.setAttribute('aria-expanded', 'true');
  });
}
function restoreView() {
  if (!printing) return;
  printing = false;
  $('#pdate').textContent = '';
  render();
}
window.addEventListener('afterprint', restoreView);
function doPrint(all) {
  ov();
  printMode(all);
  setTimeout(() => { window.print(); }, 150); // view is restored by the afterprint event
}
$('#prt').addEventListener('click', () => ov('prov'));
$('#pcur').addEventListener('click', () => doPrint(false));
$('#pall').addEventListener('click', () => doPrint(true));

cats();
tabs();
render();
if (location.hash === '#print-all') printMode(true);
else if (/^#print-tab-\d$/.test(location.hash) && +location.hash.slice(-1) < D.length) {
  cur = +location.hash.slice(-1);
  cats();
  tabs();
  printMode(false);
}

// ---------- hand-over from the static (no-JS) list to the interactive view ----------
// Only after everything above ran without error: remove the static list. If anything threw earlier,
// this never runs and the static, script-free list stays on screen.
document.documentElement.classList.add('js');
$('#static').remove();
