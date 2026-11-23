#!/usr/bin/env python3
"""Build ../index.html from the readable sources in this folder.

Sources:  data.json (listings)  providers.json (AI providers)  config.py (name, intro, SEO text, FAQ)
          css.css  core.js  app.js (readable source; the build only strips comments/indentation when --min is given)
The static (no-script) list is the only copy of the listings; the script reads it from the DOM.
"""
import json, os, re, html, sys
from urllib.parse import urlparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import config as C

OUT = os.environ.get('OUT', os.path.join(HERE, '..', 'index.html'))
MIN = '--min' in sys.argv
data = json.load(open(os.path.join(HERE, 'data.json')))
TABS = C.TABS
assert [t['k'] for t in data] == [t[0] for t in TABS], 'tab order changed'
assert len(C.TITLE) <= 60 and len(C.DESC) <= 160

E = lambda x: html.escape('' if x is None else str(x), quote=True)
def safe_url(u):
    u = (u or '').strip(); pr = urlparse(u)
    return u if pr.scheme in ('http', 'https') and pr.netloc else ''
def link(u, text, cls=None):
    h = safe_url(u)
    return f'<a{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} href="{E(h)}" target="_blank" rel="noopener noreferrer">{text}</a>' if h else text
def tel_href(p):
    raw = str(p)
    m = re.search(r'(?:ext\.?|x)\s*(\d{1,6})', raw, re.I)
    d = re.sub(r'^1', '', re.sub(r'[^\d+]', '', raw), count=1)
    if not d: return ''
    if raw.strip().startswith('0') or not re.fullmatch(r'\d{10}', d): return 'tel:' + re.sub(r'[^\d+]', '', raw)
    return 'tel:+1' + d + (';ext=' + m.group(1) if m else '')
def tel_link(p):
    h = tel_href(p)
    return f'<a href="{E(h)}">{E(p)}</a>' if h else E(p)
NP = '<span class="muted">Not published</span>'
def contact_block(x):
    c = x['ct']
    phone = NP if not c['p'] else tel_link(c['p']) + ('; ' + tel_link(c['p2']) if c['p2'] else '')
    web = link(c['w'], E(c['w'])) if c['w'] else '<span class="muted">Not confirmed</span>'
    em = ', '.join(f'<a href="mailto:{E(e)}">{E(e)}</a>' for e in c['e']) if c['e'] else NP
    srcs = [u for u in c['srcs'] if safe_url(u)]
    src = ' '.join(link(u, 'contact source' + (f' {i + 1}' if len(srcs) > 1 else ''), 'csrc') for i, u in enumerate(srcs))
    return (f'<div class="ct"><div class="lbl">Contact</div><ul class="ctul"><li><span class="ck">Address</span> {E(c["a"]) if c["a"] else NP}</li>'
            f'<li><span class="ck">Phone</span> {phone}</li><li><span class="ck">Website</span> {web}</li><li><span class="ck">Email</span> {em}</li></ul>{src}</div>')
def item_html(x, i):
    free = x['p'] == 'Free'
    ex = ('<div class="lbl">EXAMPLE USE:</div><ul>' + ''.join(f'<li>{E(e)}</li>' for e in x['e']) + '</ul>') if x['e'] else ''
    cond = f'<div><span class="lbl">{"Eligibility" if free else "Conditions"}:</span> {E(x["x"])}</div>' if x['x'] else ''
    price = '<span class="price free">Free</span>' if free else f'<span class="price">{E(x["p"])}</span><span class="src">price read from official page {E(x.get("pd") or "Nov 1, 2026")}</span>'
    site = safe_url(x['u'])
    go = f'<a class="go" href="{E(site)}" target="_blank" rel="noopener noreferrer">Open site ↗<span class="sr"> (opens in a new tab): {E(x["n"])}</span></a>' if site else ''
    pa = '' if x['u'] == x['ct']['w'] else f'<div class="pa">Link: {E(x["u"])}</div>'  # only when the Website row above shows a different address
    return (f'<details class="item glass sitem"><summary class="hd"><span class="num">{i}</span><span class="mid"><span class="nm">{E(x["n"])}</span>'
            f'<span class="ds">{E(x["d"])}</span></span><span class="tag">{E(x["c"])}</span><span class="ch" aria-hidden="true">▾</span></summary>'
            f'<div class="in"><div>{E(x["s"])}</div>{ex}{cond}{contact_block(x)}{price}{go}{pa}</div></details>')

def grouped(items):
    """Group listings by subcategory (order of first appearance); order inside a subcategory is unchanged."""
    order = []
    for x in items:
        if x['c'] not in order: order.append(x['c'])
    return [(c, [x for x in items if x['c'] == c]) for c in order]
radios, labels, panes = [], [], []
for i, (tab, (k, label, name, sub, intro)) in enumerate(zip(data, TABS)):
    radios.append(f'<input class="tr" type="radio" name="stab" id="r{i}"{" checked" if i == 0 else ""}>')
    labels.append(f'<label class="tab" for="r{i}">{E(label)}</label>')
    body, num = '', 0
    for cat, xs in grouped(tab['items']):
        body += f'<h4 class="sech">{E(cat.upper())}</h4>'
        for x in xs:
            num += 1; body += item_html(x, num)
    panes.append(f'<section class="pane" id="p{i}" data-k="{k}" data-t="{E(label)}" aria-label="{E(label)}">'
                 f'<div class="phead"><h2 class="ptab">{E(name)}</h2><h3 class="psub">{E(sub)}</h3><p class="tabintro">{E(intro)}</p></div>{body}</section>')
n = len(data)
sel = lambda f: ','.join(f(i) for i in range(n))
CSS = (open(os.path.join(HERE, 'css.css')).read()
       .replace('/*ON_SEL*/', sel(lambda i: f'#r{i}:checked~.snav label[for=r{i}]'))
       .replace('/*PANE_SEL*/', sel(lambda i: f'#r{i}:checked~.panes #p{i}'))
       .replace('/*FOCUS_SEL*/', sel(lambda i: f'#r{i}:focus-visible~.snav label[for=r{i}]')))
STATIC = ('<div id="static"><p id="jserr" class="jserr glass" hidden></p><div class="tabsys">' + ''.join(radios)
          + '<nav class="snav tabnav" aria-label="Resource categories">' + ''.join(labels) + '</nav><div class="panes">' + ''.join(panes) + '</div></div></div>')

# JSON-LD: WebSite + ItemList (name/url only) + FAQPage (the same Q&A that is visible on the page)
items = [x for t in data for x in t['items']]
LD = json.dumps({'@context': 'https://schema.org', '@graph': [
    {'@type': 'WebSite', 'name': C.NAME, 'inLanguage': 'en-US', 'dateModified': C.STAMP,
     'description': C.DESC, 'about': 'Assistance programs and resources in Arizona'},
    {'@type': 'ItemList', 'name': C.NAME + ' listings', 'numberOfItems': len(items),
     'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': x['n'], 'url': x['u']} for i, x in enumerate(items)]},
    {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in C.FAQ]},
], }, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

FAQ = '<section class="faq" id="faq" aria-labelledby="faqh"><h2 id="faqh">Frequently asked questions</h2>' + ''.join(
    f'<details class="glass"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in C.FAQ) + '</section>'
LOGO = ('<svg class="logo" viewBox="0 0 48 48" role="img" aria-label="CMD Resource Hub Arizona logo: Arizona assistance programs directory"><title>CMD Resource Hub Arizona logo: Arizona assistance programs directory</title>'
        '<defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#00B4FF"/><stop offset="1" stop-color="#FF7A00"/></linearGradient></defs>'
        '<rect width="48" height="48" rx="12" fill="#05070d" stroke="url(#lg)" stroke-width="2"/><text x="24" y="31" text-anchor="middle" font-size="19" font-weight="700" font-family="system-ui,sans-serif" fill="url(#lg)">CMD</text></svg>')
FOOT = ''.join(f'<p>{E(l)}</p>' for l in C.FOOTER)

JS = open(os.path.join(HERE, 'core.js')).read() + '\n' + open(os.path.join(HERE, 'app.js')).read().replace('__STAMP__', C.STAMP)
JS = JS.replace('__PROV__', json.dumps(json.load(open(os.path.join(HERE, 'providers.json'))), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
if MIN:
    JS = re.sub(r'(?m)^\s*//.*$', '', JS); JS = re.sub(r'\n\s*\n+', '\n', JS)
    CSS = re.sub(r'/\*.*?\*/', '', CSS, flags=re.S); CSS = re.sub(r'\n\s*', '', CSS)

PWA = open(os.path.join(HERE, 'pwa.js')).read()
meta_title, meta_desc = E(C.TITLE), E(C.DESC)
out = f'''<!doctype html>
<html lang="en">
<head>
<!-- CMD Resource Hub Arizona, internal version {C.VERSION}. The version number is not shown anywhere in the page. -->
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{meta_title}</title>
<meta name="description" content="{meta_desc}">
<meta name="robots" content="index,follow,max-snippet:-1">
<meta name="application-name" content="{E(C.NAME)}">
<meta name="generator" content="{E(C.NAME)}">
<meta name="theme-color" content="#05070d">
<meta name="color-scheme" content="dark">
<!-- Canonical placeholder: when this file is published, replace YOUR-DOMAIN and uncomment.
<link rel="canonical" href="https://YOUR-DOMAIN/CMD-Resource-Hub-Arizona.html">
<meta property="og:url" content="https://YOUR-DOMAIN/CMD-Resource-Hub-Arizona.html">
-->
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%2305070d'/%3E%3Ctext x='16' y='22' text-anchor='middle' font-size='16' font-weight='700' font-family='system-ui,sans-serif' fill='%2300B4FF'%3EC%3C/text%3E%3C/svg%3E">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="AZ Resources">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta property="og:title" content="{meta_title}">
<meta property="og:site_name" content="{E(C.NAME)}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{meta_title}">
<meta name="twitter:description" content="{meta_desc}">
<script type="application/ld+json">{LD}</script>
<style>{CSS}</style>
</head>
<body>
<noscript><p class="sr">{E(C.NAME)}: the full list below works without scripts.</p></noscript>
<div class="wrap">
<header>
  <div class="top">
    <div class="brand">{LOGO}<h1>{E(C.H1_TEXT)}</h1></div>
    <div class="topb jsonly">
      <button class="btn" id="prt" type="button">🖨 Print / Save PDF</button>
      <button class="btn" id="gear" type="button">⚙ Settings</button>
    </div>
  </div>
  <p class="intro">{E(C.INTRO)}</p>
  <p class="sub pdate" id="pdate"></p>
</header>
<div class="gsearch glass jsonly"><input id="gq" type="search" placeholder="Search ALL tabs…" aria-label="Global search"></div>
<nav class="tabs tabnav jsonly" id="tabs" aria-label="Resource categories"></nav>
<div id="note" class="jsonly"></div>
<div class="ctl glass jsonly">
  <input id="q" type="search" placeholder="Search this tab…" aria-label="Tab search">
  <select id="cat" aria-label="Subcategory"></select>
  <button class="btn" id="tabai" type="button">✨ Find similar options for this tab</button>
</div>
<div id="count" class="hint count jsonly" role="status" aria-live="polite"></div>
<div id="thead" class="jsonly"></div>
<main id="list" class="jsonly"></main>
{STATIC}
{FAQ}
<footer class="foot">{FOOT}</footer>
</div>
<div class="ov" id="aiov" role="dialog" aria-modal="true" aria-labelledby="aih"><div class="pnl glass" tabindex="-1"><button class="btn x" type="button" data-close>✕ Close<span class="sr"> AI results</span></button><h2 id="aih">AI results</h2><div class="warn">⚠ AI-generated — verify links and prices before relying on them. Results come from the AI provider selected in Settings.</div><div id="aimeta" class="sub" role="status" aria-live="polite"></div><div id="aibody"></div></div></div>
<div class="ov" id="stov" role="dialog" aria-modal="true" aria-labelledby="sth"><div class="pnl glass" tabindex="-1"><button class="btn x" type="button" data-close>✕ Close<span class="sr"> settings</span></button><h2 id="sth">Settings</h2><p class="sub">AI API · keys are saved only in this browser's localStorage on this device and are sent only to the provider you turn on. No keys are built into this file.</p><div id="stbody"></div></div></div>
<div class="ov" id="prov" role="dialog" aria-modal="true" aria-labelledby="prth"><div class="pnl glass" tabindex="-1"><button class="btn x" type="button" data-close>✕ Close<span class="sr"> print dialog</span></button><h2 id="prth">Print / Save as PDF</h2><p class="sub">Prints with every dropdown expanded, light colors and full link URLs. In the print dialog pick "Save as PDF".</p><p><button class="btn" id="pcur" type="button">Print current tab</button> <button class="btn" id="pall" type="button">Print all {n} tabs</button></p></div></div>
<script>
try {{
{JS}
}} catch (err) {{
  // Anything that goes wrong leaves the static, script-free list on screen and says so.
  try {{ console.error(err); var jn = document.getElementById('jserr'); if (jn) {{ jn.hidden = false; jn.textContent = 'Interactive features could not start in this viewer (' + (err && err.message ? err.message : err) + '). The full list below still works.'; }} }} catch {{ /* nothing more can be shown */ }}
}}
</script>
<script>
{PWA}
</script>
</body>
</html>
'''
open(OUT, 'w').write(out)
# Service worker: stamp a version from the shipped files so each rebuild rolls out as a new cache.
import hashlib
ROOT = os.path.dirname(OUT)
h = hashlib.sha256(out.encode())
h.update(open(os.path.join(HERE, 'sw.js'), 'rb').read())
for rel in ['offline.html', 'manifest.webmanifest'] + sorted('icons/' + f for f in os.listdir(os.path.join(ROOT, 'icons'))):
    h.update(open(os.path.join(ROOT, rel), 'rb').read())
SW = open(os.path.join(HERE, 'sw.js')).read().replace('__VERSION__', h.hexdigest()[:12])
open(os.path.join(ROOT, 'sw.js'), 'w').write(SW)
print('wrote sw.js, cache version', h.hexdigest()[:12])
print('wrote', OUT, os.path.getsize(OUT), 'bytes;', len(items), 'items;', {t['k']: len(t['items']) for t in data})
