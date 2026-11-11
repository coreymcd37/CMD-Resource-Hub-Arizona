// Listing data is read from the static (no-script) HTML below the header; nothing is stored twice.
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
// Only http(s) URLs are ever turned into links; anything else (javascript:, data:, ...) returns ''.
function safeUrl(u) {
  try {
    const x = new URL(String(u == null ? '' : u).trim());
    return x.protocol === 'http:' || x.protocol === 'https:' ? x.href : '';
  } catch { return ''; }
}
function link(u, text, cls) {
  const h = safeUrl(u);
  return h ? `<a${cls ? ` class="${cls}"` : ''} href="${esc(h)}" target="_blank" rel="noopener noreferrer">${text}</a>` : text;
}
const txt = (el, sel) => { const n = el.querySelector(sel); return n ? n.textContent.trim() : ''; };
const D = [...document.querySelectorAll('#static .pane')].map((p) => ({
  k: p.dataset.k,
  t: p.dataset.t,
  name: txt(p, '.ptab'),
  sub: txt(p, '.psub'),
  intro: txt(p, '.tabintro'),
  items: [...p.querySelectorAll('.sitem')].map((el) => ({
    n: txt(el, '.nm'), d: txt(el, '.ds'), c: txt(el, '.tag'), p: txt(el, '.price'),
    h: el.querySelector('.in').innerHTML,
    q: (el.querySelector('.mid').textContent + ' ' + txt(el, '.tag') + ' ' + el.querySelector('.in').textContent).toLowerCase()
  }))
}));
let cur = 0, glob = '', uid = 0, printing = false;

function tabs() {
  $('#tabs').innerHTML = D.map((t, i) => {
    const on = i === cur && !glob;
    return `<button type="button" class="tab${on ? ' on' : ''}"${on ? ' aria-current="true"' : ''} data-i="${i}">${esc(t.t)}</button>`;
  }).join('');
}
function cats() {
  const s = [...new Set(D[cur].items.map((x) => x.c))].sort();
  $('#cat').innerHTML = '<option value="">All subcategories</option>' + s.map((c) => `<option>${esc(c)}</option>`).join('');
}
function card(x, i, tn) {
  const id = 'bd' + (uid++);
  return `<article class="item glass"><div class="row"><button type="button" class="hd" aria-expanded="false" aria-controls="${id}"><span class="num">${i + 1}</span><span class="mid"><span class="nm">${esc(x.n)}</span><span class="ds">${esc(x.d)}</span></span><span class="tag">${esc(tn ? tn + ' · ' : '')}${esc(x.c)}</span><span class="ch" aria-hidden="true">▾</span></button><button class="aib" type="button" title="Find similar / free alternatives" aria-label="Find similar or free alternatives to ${esc(x.n)}" data-ai="${esc(x.n)}">✨ Similar</button></div><div class="bd" id="${id}"><div class="in">${x.h}</div></div></article>`;
}
// Listings grouped by subcategory: a full-width rule plus an ALL-CAPS heading before each group (items arrive already grouped).
function groupedCards(items) {
  let h = '', last = null;
  items.forEach((x, i) => {
    if (x.c !== last) { h += `<h4 class="sech">${esc(x.c.toUpperCase())}</h4>`; last = x.c; }
    h += card(x, i);
  });
  return h;
}
function render() {
  let h = '', shown = 0, total = 0, filtered = false;
  const head = $('#thead');
  if (glob) {
    D.forEach((t) => t.items.forEach((x) => { total++; if (x.q.includes(glob)) { h += card(x, shown++, t.t); } }));
    $('#note').innerHTML = `<div class="note glass">${shown} results across all tabs for “${esc(glob)}”</div>`;
    head.innerHTML = '';
  } else {
    const t = D[cur], q = $('#q').value.toLowerCase().trim(), c = $('#cat').value;
    const r = t.items.filter((x) => (!q || x.q.includes(q)) && (!c || x.c === c));
    h = groupedCards(r);
    shown = r.length; total = t.items.length; filtered = !!(q || c);
    $('#note').innerHTML = '';
    head.innerHTML = `<div class="phead"><h2 class="ptab">${esc(t.name)}</h2><h3 class="psub">${esc(t.sub)}</h3><p class="tabintro">${esc(t.intro)}</p></div>`;
  }
  $('#count').textContent = filtered ? `Showing ${shown} of ${total} listings` : '';
  $('#list').innerHTML = h || '<div class="empty">No matches.</div>';
}
function openTab(i) {
  cur = i; glob = '';
  $('#gq').value = ''; $('#q').value = '';
  cats(); tabs(); render();
}
// One delegated listener each (no per-render handlers to leak or duplicate).
$('#tabs').addEventListener('click', (e) => {
  const b = e.target.closest('.tab');
  if (b) openTab(+b.dataset.i);
});
$('#list').addEventListener('click', (e) => {
  const b = e.target.closest('.hd');
  if (!b) return;
  const it = b.closest('.item');
  it.classList.toggle('open');
  b.setAttribute('aria-expanded', it.classList.contains('open') ? 'true' : 'false');
});
$('#q').addEventListener('input', render);
$('#cat').addEventListener('change', render);
$('#gq').addEventListener('input', (e) => { glob = e.target.value.toLowerCase().trim(); tabs(); render(); });
