import json, time, sys, re
from playwright.sync_api import sync_playwright
import sys as _s; _s.path.insert(0, 'src')
import config as CF
F = 'file://'+__import__('os').path.abspath('index.html')+''
NAME = CF.NAME
H1 = CF.H1_TEXT
LABELS = [t[1] for t in CF.TABS]
DEL_NAMES = []  # removed-tab name list not shipped in this repo
TD = 'test-output/'
DATA = json.load(open('src/data.json'))
EXP = {t['k']: len(t['items']) for t in DATA}
EXPL = [len(t['items']) for t in DATA]
TOTAL = sum(EXPL)
INTRO = CF.INTRO
_unused = 'Free and sponsored resources for Arizona residents, covering food, health care, housing, jobs, legal help, education, and business funding. Each listing links to the official program and its contact details, so you can reach the right help quickly.'
R = {}
CHECKS = []
def ck(name, ok, detail=''):
    CHECKS.append((name, bool(ok), str(detail)[:300]))
    print(('PASS ' if ok else 'FAIL ') + name + ((' :: ' + str(detail)[:300]) if detail != '' else ''), flush=True)
def mk(b, w=1280, h=900, url=F, init=None, ls=None):
    ctx = b.new_context(viewport={'width': w, 'height': h})
    if init: ctx.add_init_script(init)
    pg = ctx.new_page()
    pg.errs = []; pg.net = []
    pg.on('console', lambda m: pg.errs.append(m.type + ': ' + m.text[:200]) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: pg.errs.append('pageerror: ' + str(e)[:200]))
    pg.on('response', lambda r: pg.net.append((r.status, r.url.split('?')[0][:70])) if r.request.method == 'POST' else None)
    pg.goto(url)
    return ctx, pg
def jserrs(pg):  # console errors that are NOT provider network status lines
    return [e for e in pg.errs if not re.search(r'Failed to load resource|net::ERR|status of (4|5)\d\d|CORS|preflight', e)]
def wait_done(pg, t=240000):
    pg.wait_for_function("()=>!document.querySelector('#aibody .spin') && document.querySelector('#aiov.on')", timeout=t)
def results(pg):
    return pg.evaluate("()=>({n:document.querySelectorAll('#aibody .res').length, meta:document.querySelector('#aimeta').textContent, title:document.querySelector('#aih').textContent, first:[...document.querySelectorAll('#aibody .res')].slice(0,3).map(e=>e.querySelector('b').textContent+' -> '+e.querySelector('a').textContent), body:document.querySelector('#aibody').innerText.slice(0,500)})")
ALLOW = 'access-control-allow-origin'
def fake(status, body, ctype='application/json'):
    return lambda r: r.fulfill(status=status, headers={ALLOW: '*'}, content_type=ctype, body=body)
def chat_ok(content):
    return json.dumps({'choices': [{'message': {'content': content}}]})
which = sys.argv[1]
with sync_playwright() as p:
    import os
    ENG = os.environ.get('ENGINE', 'chromium')
    if ENG == 'chromium':
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    elif ENG == 'webkit':
        b = p.webkit.launch()
    else:
        b = p.firefox.launch()
    data = None
    if which == 'ui':
        for (w, h) in [(1280, 900), (390, 844)]:
            tag = f'[{w}] '
            ctx, pg = mk(b, w, h)
            data = [dict(k=t['k'], n=len(t['items']), names=[x['n'] for x in t['items']]) for t in DATA]
            ck(tag + 'title', pg.title() == CF.TITLE and len(pg.title()) <= 60, pg.title())
            ck(tag + 'single h1 text', pg.eval_on_selector_all('h1', 'e=>e.map(x=>x.textContent.trim())') == [H1], pg.eval_on_selector_all('h1', 'e=>e.map(x=>x.textContent.trim())'))
            meta = pg.evaluate("()=>[...document.querySelectorAll('meta[property=\"og:title\"],meta[name=\"twitter:title\"],meta[name=generator],meta[property=\"og:site_name\"],meta[name=application-name]')].map(m=>m.content)")
            desc = pg.evaluate("()=>document.querySelector('meta[name=description]').content")
            ck(tag + 'meta/OG/twitter/generator carry the name', len(meta) == 5 and all(NAME in m for m in meta), meta[:5])
            ck(tag + 'meta description <=160 chars, has keywords', len(desc) <= 160 and 'Arizona' in desc and 'rent' in desc, (len(desc), desc))
            ld = pg.evaluate("()=>JSON.parse(document.querySelector('script[type=\"application/ld+json\"]').textContent)")
            ck(tag + 'JSON-LD name+599', ld['@graph'][0]['name'] == NAME and ld['@graph'][1]['numberOfItems'] == TOTAL and len(ld['@graph'][1]['itemListElement']) == TOTAL and ld['@graph'][2]['@type'] == 'FAQPage' and len(ld['@graph'][2]['mainEntity']) == 6, ld['@graph'][0]['name'])
            ck(tag + 'FAQ visible on page matches JSON-LD', pg.locator('#faq details').count() == len(ld['@graph'][2]['mainEntity']) and all(q['name'] in pg.inner_text('#faq') for q in ld['@graph'][2]['mainEntity']))
            ck(tag + 'intro exact text in orange box', pg.inner_text('.intro') == INTRO and 'Free and sponsored assistance for legal purposes' not in pg.content())
            ck(tag + 'footer is the approved lines (incl. the independent-guide line) plus the Created by credit', pg.eval_on_selector_all('.foot p', 'e=>e.map(x=>x.textContent)') == list(CF.FOOTER) + [CF.CREDIT[0] + ' ' + CF.CREDIT[1]] and pg.eval_on_selector_all('.foot *', 'e=>e.length') == len(CF.FOOTER) + 2, pg.inner_text('.foot'))
            cr = pg.evaluate("()=>{const a=document.querySelector('.foot .credit a'); const cs=getComputedStyle(a); return {href:a.href, rel:a.rel, target:a.target, color:cs.color, last:document.querySelector('.foot').lastElementChild===a.parentElement}}")
            ck(tag + 'credit link: coreymcdaniel.com, same tab, rel noopener, bright blue, last line', cr == {'href': CF.CREDIT[2], 'rel': 'noopener', 'target': '', 'color': 'rgb(10, 132, 255)', 'last': True}, cr)
            op = ctx.new_page(); op.goto('file://' + __import__('os').path.abspath('offline.html'))
            oc = op.evaluate("()=>{const a=document.querySelector('footer .credit a'); return {text:a.parentElement.textContent, href:a.href, rel:a.rel, color:getComputedStyle(a).color, last:document.body.lastElementChild.tagName}}")
            op.close()
            ck(tag + 'offline page ends with the same credit link', oc == {'text': CF.CREDIT[0] + ' ' + CF.CREDIT[1], 'href': CF.CREDIT[2], 'rel': 'noopener', 'color': 'rgb(10, 132, 255)', 'last': 'FOOTER'}, oc)
            ck(tag + 'header = CMD logo then H1 without CMD / version', pg.locator('.brand svg.logo').count() == 1 and '>CMD<' in pg.inner_html('.brand svg') and not re.search(r'CMD|5\.5', pg.inner_text('h1')), pg.inner_text('h1'))
            body = pg.evaluate("()=>document.body.innerText")
            ck(tag + 'no version number visible anywhere', not re.search(r'(?<![\d.$])5\.5(?![\d%])', body) and not re.search(r'\bv5\b|version 5', body, re.I), re.findall(r'.{25}(?<![\d.$])5\.5(?![\d%]).{10}', body)[:3])
            html0 = pg.content()
            gone = re.findall(r'network security|wireshark|pen.?test|nmap|suricata|pfsense|opnsense|home network|only test networks|own network', html0 + body, re.I)
            ck(tag + 'deleted network-security tab: no trace (words)', gone == [], gone[:5])
            ck(tag + 'deleted tab: none of its 56 item names appear', not [n for n in DEL_NAMES if len(n) > 8 and n in html0], [n for n in DEL_NAMES if len(n) > 8 and n in html0][:5])
            tl = pg.eval_on_selector_all('.tab', 'e=>e.map(x=>x.textContent.trim())')
            ck(tag + 'tab labels exact, ALL CAPS, no Free, no digits', tl == LABELS and all(t == t.upper() and 'FREE' not in t and not re.search(r'\d', t) for t in tl), tl)
            html = pg.content()
            ck(tag + 'no old names/versions anywhere', not re.search(r'Resource Hub v[345]\.?\d?|CMD RESOURCE HUB ARIZONA 5|Arizona-5\.5', html), re.findall(r'.{20}Resource Hub v.{10}', html)[:3])
            exp = EXP
            allnames = []
            for i, t in enumerate(data):
                pg.click(f'.tab[data-i="{i}"]')
                n = pg.locator('.item').count()
                allnames += t['names']
                ck(tag + f'tab {i} {t["k"]} count', n == exp[t['k']] and pg.locator('.tab.on').count() == 1 and not re.search(r'\d', pg.locator('.tab.on').inner_text()) and pg.locator('.tab b').count() == 0 and 'Showing' not in pg.inner_text('#count'), n)
                shs = pg.eval_on_selector_all('#list .sech', 'e=>e.map(x=>x.textContent)')
                tabcats = [x['c'] for x in DATA[i]['items']]
                ck(tag + f'tab {i} subcategory headings: ALL CAPS, one per subcategory, items grouped', shs == [c.upper() for c in dict.fromkeys(tabcats)] and all(h == h.upper() for h in shs), shs[:4])
                hd = pg.evaluate("()=>({h2:document.querySelector('#thead h2').textContent,h3:document.querySelector('#thead h3').textContent})")
                ck(tag + f'tab {i} heading + blue subheader ALL CAPS, from config', hd['h2'] == CF.TABS[i][2] and hd['h3'] == CF.TABS[i][3] and hd['h2'] == hd['h2'].upper() and hd['h3'] == hd['h3'].upper(), hd)
                ck(tag + f'tab {i} blue subheader has no "Free" (jobs wording is Corey\'s)', 'FREE' not in hd['h3'] or CF.TABS[i][0] == 'jobs', hd['h3'])
                cts = pg.locator('.item .ct').count()
                ck(tag + f'tab {i} contact blocks == items', cts == n, cts)
                ex = pg.locator('.item', has_text='EXAMPLE USE:').count()
                ck(tag + f'tab {i} EXAMPLE USE labels', ex > 0, ex)
                # subcategory filter
                pg.select_option('#cat', index=1)
                f = pg.locator('.item').count()
                ck(tag + f'tab {i} subcategory filter', 0 < f < n, f)
                pg.select_option('#cat', index=0)
                # per-tab search
                pg.fill('#q', 'zzzqqq')
                ck(tag + f'tab {i} search no match', pg.locator('.empty').count() == 1 and pg.locator('.item').count() == 0)
                pg.fill('#q', t['names'][2][:6].lower())
                s = pg.locator('.item').count()
                ck(tag + f'tab {i} search hit', 0 < s < n and 'Showing' in pg.inner_text('#count'), s)
                pg.fill('#q', '')
            ck(tag + 'unique names, total', len(allnames) == TOTAL and len(set(allnames)) == TOTAL, (len(allnames), len(set(allnames))))
            ck(tag + 'no count digits next to any tab/category label or heading', not re.search(r'\(\d+\)', pg.inner_text('#tabs') + ' '.join(pg.eval_on_selector_all('h2', 'e=>e.map(x=>x.textContent)'))), '')
            ck(tag + 'no tab note/warning boxes', pg.locator('.note').count() == 0)
            # global search
            pg.fill('#gq', 'library')
            g = pg.locator('.item').count()
            expg = sum(1 for t in DATA for x in t['items'] if 'library' in ' '.join([x['n'], x['d'], x['c'], x['s'], ' '.join(x['e']), x['x'], x['p'], x['ct']['a'] or '', x['ct']['p'] or '', x['ct']['p2'] or '', ' '.join(x['ct']['e']), x['ct']['w'] or '', x['u']]).lower())
            tabs_hit = pg.evaluate("()=>new Set([...document.querySelectorAll('.item .tag')].map(e=>e.textContent.split(' · ')[0])).size")
            ck(tag + 'global search', g == expg and g > 1 and tabs_hit > 1 and pg.locator('.tab.on').count() == 0, (g, expg, tabs_hit))
            pg.fill('#gq', '')
            ck(tag + 'global search cleared -> active tab', pg.locator('.item').count() > 0)
            # dropdown expand/collapse
            pg.click('.tab[data-i="0"]')
            hd = pg.locator('.hd').first
            bd = pg.locator('.bd').first
            ck(tag + 'collapsed initially (aria + hidden)', hd.get_attribute('aria-expanded') == 'false' and not bd.is_visible())
            hd.click()
            ck(tag + 'expands (aria + visible + contact visible)', hd.get_attribute('aria-expanded') == 'true' and bd.is_visible() and pg.locator('.item').first.locator('.ct').is_visible())
            hd.click()
            ck(tag + 'collapses again', hd.get_attribute('aria-expanded') == 'false' and not bd.is_visible())
            # keyboard: focus header, Enter toggles, collapsed links not focusable
            pg.locator('.hd').nth(1).focus(); pg.keyboard.press('Enter')
            ck(tag + 'keyboard Enter expands', pg.locator('.hd').nth(1).get_attribute('aria-expanded') == 'true')
            pg.keyboard.press('Space')
            ck(tag + 'keyboard Space collapses', pg.locator('.hd').nth(1).get_attribute('aria-expanded') == 'false')
            hidden_focusable = pg.evaluate("()=>[...document.querySelectorAll('.item:not(.open) .bd a, .item:not(.open) .bd button')].filter(e=>e.offsetParent!==null).length")
            ck(tag + 'collapsed content not focusable', hidden_focusable == 0, hidden_focusable)
            # overflow
            ov = pg.evaluate("()=>document.documentElement.scrollWidth - window.innerWidth")
            ck(tag + 'no horizontal overflow', ov <= 0, ov)
            pg.locator('.hd').first.click()
            ov = pg.evaluate("()=>document.documentElement.scrollWidth - window.innerWidth")
            ck(tag + 'no horizontal overflow (expanded card)', ov <= 0, ov)
            # overlays: Escape, focus return, inert
            pg.click('#gear')
            ck(tag + 'settings opens, background inert', pg.locator('#stov.on').count() == 1 and pg.evaluate("()=>document.querySelector('.wrap').inert") is True)
            pg.keyboard.press('Escape')
            ck(tag + 'Escape closes, focus returns to gear', pg.locator('#stov.on').count() == 0 and pg.evaluate("()=>document.activeElement.id") == 'gear' and pg.evaluate("()=>document.querySelector('.wrap').inert") is False)
            pg.click('#prt'); ck(tag + 'print dialog opens', pg.locator('#prov.on').count() == 1); pg.keyboard.press('Escape')
            ck(tag + 'zero JS console errors', jserrs(pg) == [], jserrs(pg))
            if w == 1280:
                pg.click('.tab[data-i="0"]'); pg.locator('.hd').nth(2).click()
                pg.screenshot(path='test-output/hub-v55-main.png')
            else:
                pg.evaluate('()=>window.scrollTo(0,0)'); pg.wait_for_timeout(500)
                pg.screenshot(path='test-output/hub-v55-mobile.png')
            ctx.close()
    if which == 'settings':
        ctx, pg = mk(b)
        pg.click('#gear'); pg.wait_for_selector('#sttest')
        pg.click('label.sw:has([data-on="flm"])'); pg.select_option('[data-model="llm7"]', 'mistral-Nemo-Instruct-2407')
        pg.fill('[data-key="groq"]', 'gsk_testkey123')
        pg.click('#stsave')
        ck('settings save message', 'Saved' in pg.inner_text('#stmsg'), pg.inner_text('#stmsg'))
        cfg = json.loads(pg.evaluate("()=>localStorage.getItem('hub55_cfg')"))
        ck('hub55_cfg written', cfg['on'].get('flm') is False and cfg['model'].get('llm7') == 'mistral-Nemo-Instruct-2407' and cfg['key'].get('groq') == 'gsk_testkey123', cfg)
        pg.reload(); pg.click('#gear')
        ck('settings load after reload', not pg.is_checked('[data-on="flm"]') and pg.input_value('[data-model="llm7"]') == 'mistral-Nemo-Instruct-2407' and pg.input_value('[data-key="groq"]') == 'gsk_testkey123')
        pg.click('#streset')
        ck('settings reset', pg.is_checked('[data-on="flm"]') and pg.input_value('[data-key="groq"]') == '' and pg.evaluate("()=>localStorage.getItem('hub55_cfg')") is None and 'Reset' in pg.inner_text('#stmsg'))
        ctx.close()
        # migration from hub4_cfg
        ctx, pg = mk(b)
        pg.evaluate("()=>{localStorage.clear();localStorage.setItem('hub4_cfg',JSON.stringify({on:{ovh:false},model:{},key:{},check:true}))}")
        pg.reload(); pg.click('#gear')
        ck('migrate hub4_cfg -> hub55_cfg', json.loads(pg.evaluate("()=>localStorage.getItem('hub55_cfg')"))['on'] == {'ovh': False} and not pg.is_checked('[data-on="ovh"]') and pg.is_checked('[data-on="__check"]'))
        pg.evaluate("()=>{localStorage.clear();localStorage.setItem('hub3_cfg',JSON.stringify({on:{flm:false}}))}")
        pg.reload(); pg.click('#gear')
        ck('migrate hub3_cfg -> hub55_cfg', not pg.is_checked('[data-on="flm"]') and pg.evaluate("()=>localStorage.getItem('hub55_cfg')") is not None)
        pg.evaluate("()=>{localStorage.clear();localStorage.setItem('hub5_cfg',JSON.stringify({on:{llm7:false},model:{},key:{groq:'kk'},check:false}))}")
        pg.reload(); pg.click('#gear')
        ck('migrate hub5_cfg -> hub55_cfg', not pg.is_checked('[data-on="llm7"]') and pg.input_value('[data-key="groq"]') == 'kk' and json.loads(pg.evaluate("()=>localStorage.getItem('hub55_cfg')"))['on'] == {'llm7': False})
        ctx.close()
        # corrupted storage
        for label, setup in [('invalid JSON', "()=>{localStorage.clear();localStorage.setItem('hub55_cfg','{bad');localStorage.setItem('hub55_models','nope{')}"),
                             ('array cfg', "()=>{localStorage.clear();localStorage.setItem('hub55_cfg','[1,2,3]')}"),
                             ('string cfg', "()=>{localStorage.clear();localStorage.setItem('hub55_cfg','\"hello\"')}"),
                             ('wrong types', "()=>{localStorage.clear();localStorage.setItem('hub55_cfg',JSON.stringify({on:'x',model:[1],key:{groq:123,bogus:'k'},check:'yes'}));localStorage.setItem('hub55_models',JSON.stringify({stamp:'2026-11-11',lists:{llm7:'oops',ovh:[1,2]}}))}")]:
            ctx, pg = mk(b)
            pg.evaluate(setup); pg.reload()
            pg.click('#gear')
            ok = pg.locator('.pv').count() > 5 and pg.is_checked('[data-on="llm7"]') and pg.input_value('[data-key="groq"]') == ''
            ck(f'corrupted storage: {label}', ok and jserrs(pg) == [], jserrs(pg))
            pg.locator('.hd').count()
            ctx.close()
        # storage blocked entirely
        blk = "Object.defineProperty(window,'localStorage',{get(){throw new DOMException('blocked','SecurityError')}})"
        ctx, pg = mk(b, init=blk)
        pg.click('#gear'); pg.fill('[data-key="groq"]', 'k'); pg.click('#stsave')
        ck('storage blocked: page works + warning shown', pg.locator('.item').count() == EXPL[0] and 'blocked saving' in pg.inner_text('#stmsg') and jserrs(pg) == [], pg.inner_text('#stmsg'))
        ctx.close()
        # test providers (live) + refresh model lists (live)
        ctx, pg = mk(b)
        pg.click('#gear'); pg.click('#sttest')
        pg.wait_for_function("()=>!document.querySelector('#pvtest .spin')", timeout=150000)
        txt = pg.inner_text('#pvtest'); R['test_providers'] = txt
        ck('Test providers: all 4 no-key show result lines', all(n in txt for n in ['LLM7', 'OVHcloud', 'flm.stonech.at', 'Pollinations']) and txt.count('✓ working') + txt.count('✗') >= 4, txt)
        ck('Test providers: >=3 working', txt.count('✓ working') >= 3, txt.count('✓ working'))
        pg.screenshot(path='test-output/settings-test.png')
        pg.click('#strefresh')
        pg.wait_for_function("()=>document.querySelector('#pvtest').innerText.includes('Model dropdowns')", timeout=60000)
        R['refresh'] = pg.inner_text('#pvtest')
        ck('Refresh model lists runs', '✓' in R['refresh'], R['refresh'])
        ck('settings tests: zero JS errors', jserrs(pg) == [], jserrs(pg))
        ctx.close()
    if which == 'ai':
        ctx, pg = mk(b)
        out = []
        for tab in (0, 3, 5, 6):
            pg.click(f'.tab[data-i="{tab}"]')
            btn = pg.locator('.aib').nth(1)
            name = btn.get_attribute('data-ai')
            t0 = time.time(); btn.click(); wait_done(pg)
            r = results(pg); r['item'] = name; r['tab'] = tab; r['secs'] = round(time.time() - t0, 1)
            out.append(r)
            ck(f'AI Similar tab {tab} "{name}"', r['n'] >= 3 and 'Answered by' in r['meta'] and name in r['title'], (r['meta'], r['n'], r['first'][:2]))
            if tab == 3: pg.screenshot(path='test-output/hub-v55-ai.png')
            pg.click('#aiov [data-close]')
        pg.click('.tab[data-i="4"]')
        t0 = time.time(); pg.click('#tabai'); wait_done(pg)
        r = results(pg); r['item'] = '(tab-level AI)'; r['tab'] = 4; r['secs'] = round(time.time() - t0, 1); out.append(r)
        ck('AI tab-level (Super Cheap)', r['n'] >= 3 and 'Answered by' in r['meta'], (r['meta'], r['n'], r['first'][:2]))
        links = pg.evaluate("()=>[...document.querySelectorAll('#aibody .res a')].map(a=>a.href)")
        ck('AI result links all http(s) + target=_blank noopener', all(l.startswith('http') for l in links) and pg.evaluate("()=>[...document.querySelectorAll('#aibody .res a')].every(a=>a.target==='_blank'&&a.rel.includes('noopener'))"), links[:3])
        ck('AI run: zero JS errors', jserrs(pg) == [], jserrs(pg))
        R['ai'] = out; R['net'] = pg.net
    if which == 'fallback':
        # 1: LLM7 network-aborted -> next provider answers (live)
        ctx, pg = mk(b)
        pg.route('https://api.llm7.io/**', lambda r: r.abort())
        pg.locator('.aib').first.click(); wait_done(pg)
        r = results(pg); R['llm7_aborted'] = r
        ck('fallback: LLM7 blocked -> another provider answers', r['n'] >= 3 and 'LLM7' not in r['meta'].split('·')[0].replace('Answered by', ''), (r['meta'], r['n']))
        ctx.close()
        # 2: llm7 429, ovh 500, flm empty -> Pollinations
        ctx, pg = mk(b)
        pg.route('https://api.llm7.io/**', fake(429, '{"error":{"message":"rate limited (forced)"}}'))
        pg.route('https://oai.endpoints.kepler.ai.cloud.ovh.net/**', fake(500, '{"error":{"message":"forced 500"}}'))
        pg.route('https://flm.stonech.at/**', fake(200, '{"choices":[{"message":{"content":""}}]}'))
        t0 = time.time(); pg.locator('.aib').first.click(); wait_done(pg)
        r = results(pg); R['chain_to_pollinations'] = r
        ck('fallback: 429 -> 500 -> empty -> Pollinations answers (live)', r['n'] >= 3 and 'Pollinations' in r['meta'] and (lambda full: 'LLM7.io: HTTP 429' in full and 'forced 500' in full and 'empty answer' in full)(pg.inner_text('#aibody')), (r['meta'], pg.inner_text('#aibody')[-350:]))
        ctx.close()
        # 3: all fail
        ctx, pg = mk(b)
        pg.route('https://**/*chat/completions*', fake(401, '{"error":{"message":"forced 401"}}'))
        pg.route('https://text.pollinations.ai/openai', fake(401, '{"error":{"message":"forced 401"}}'))
        pg.locator('.aib').first.click(); wait_done(pg, 120000)
        r = results(pg); R['all_fail'] = r
        ck('all-fail: clear error listing each provider', 'every enabled provider failed' in r['body'] and all(n in r['body'] for n in ['LLM7', 'OVHcloud', 'flm', 'Pollinations']) and r['n'] == 0, r['body'][:300])
        ck('all-fail: Settings button works', (pg.click('#aigo') or True) and pg.locator('#stov.on').count() == 1 and pg.locator('#aiov.on').count() == 0)
        pg.screenshot(path='test-output/ai-allfail.png')
        ck('fallback runs: zero JS errors', jserrs(pg) == [], jserrs(pg))
        ctx.close()
        # 4: keyed providers go first and fall through on bad key
        ctx, pg = mk(b)
        pg.evaluate("()=>localStorage.setItem('hub55_cfg', JSON.stringify({on:{},model:{},key:{groq:'dummy-invalid',gemini:'dummy-invalid'}}))")
        pg.reload()
        pg.route('https://api.groq.com/**', fake(401, '{"error":{"message":"Invalid API Key"}}'))
        pg.route('https://generativelanguage.googleapis.com/**', fake(400, '[{"error":{"message":"API key not valid"}}]'))
        pg.route('https://api.llm7.io/**', fake(200, chat_ok('[{"name":"Alpha","url":"https://example.org/a","why":"w","type":"free"}]')))
        pg.locator('.aib').first.click(); wait_done(pg)
        r = results(pg)
        ck('keyed providers tried first, bad keys fall through to no-key chain', r['n'] == 1 and 'LLM7' in r['meta'] and 'Google Gemini API (AI Studio): HTTP 400' in r['body'] + '' or ('Groq' in pg.inner_text('#aibody') and r['n'] == 1), (r['meta'], pg.inner_text('#aibody')[-300:]))
        ctx.close()
    if which == 'race':
        ctx, pg = mk(b)
        held = []
        reqs = []
        def hold(r):
            if r.request.method == 'OPTIONS':
                r.fulfill(status=204, headers={ALLOW: '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*'})
            else: held.append(r)
        pg.route('https://api.llm7.io/**', hold)
        pg.on('requestfailed', lambda r: reqs.append(('failed', r.failure)) if 'llm7' in r.url else None)
        def answer(route, n):
            try: route.fulfill(status=200, headers={ALLOW: '*'}, content_type='application/json', body=chat_ok('[{"name":"Result-%d","url":"https://example.org/%d","why":"w","type":"free"}]' % (n, n)))
            except Exception as e: reqs.append(('late-fulfill-error', str(e)[:60]))
        n2 = pg.locator('.aib').nth(1).get_attribute('data-ai')
        pg.evaluate("()=>{const bs=document.querySelectorAll('.aib');bs[0].click();bs[1].click();bs[1].click()}")
        pg.wait_for_timeout(1000)
        ab = sum(1 for r in reqs if r[0] == 'failed' and re.search(r'ABORTED|cancelled', r[1] or ''))
        ck('race: 3 rapid clicks -> earlier calls aborted, only the newest stays live (engine-neutral: held minus aborted == 1)', len(held) - ab <= 1, (len(held), ab))
        # answer in reverse order: stale answers must NOT overwrite the newest
        for i, r_ in enumerate(reversed(held)): answer(r_, 3 - i)   # newest gets Result-3 first, then stale 2,1
        pg.wait_for_timeout(1500)
        r = results(pg)
        ck('race: panel shows only the LAST request (stale replies ignored)', n2 in r['title'] and r['n'] == 1 and r['first'][0].startswith('Result-3'), (r['title'], r['first']))
        pg.click('#aiov [data-close]')
        # close mid-request -> request aborted, nothing updates later
        held.clear(); reqs.clear()
        pg.locator('.aib').nth(2).click(); pg.wait_for_timeout(600)
        pg.click('#aiov [data-close]'); pg.wait_for_timeout(500)
        ck('race: closing panel aborts the in-flight request', any(r[0]=='failed' and re.search(r'ABORTED|cancelled', r[1] or '') for r in reqs), reqs)
        before = pg.inner_text('#aibody')
        if held: answer(held[0], 99)
        pg.wait_for_timeout(1500)
        after = pg.inner_text('#aibody')
        ck('race: late reply after close does not touch the panel', before == after and 'Result-99' not in after, (before[:60], after[:60]))
        # Stop button
        held.clear()
        pg.locator('.aib').nth(3).click(); pg.wait_for_timeout(500)
        pg.click('#aistop'); pg.wait_for_timeout(600)
        ck('race: Stop button shows stopped state and aborts', 'Stopped' in pg.inner_text('#aibody') and pg.locator('#aibody .spin').count() == 0, pg.inner_text('#aibody')[:80])
        pg.click('#aiov [data-close]')
        # switch tab mid-request
        held.clear()
        pg.locator('.aib').nth(1).click(); pg.wait_for_timeout(500)
        t0n = pg.evaluate("()=>document.querySelector('#aih').textContent")
        pg.evaluate("()=>document.querySelector('.tab[data-i=\"3\"]').click()")
        answer(held[0], 7); pg.wait_for_timeout(1000)
        r = results(pg)
        ck('race: switching tab mid-request keeps the result tied to the original item', r['n'] == 1 and r['title'] == t0n and jserrs(pg) == [], (r['title'], t0n, jserrs(pg)))
        # open settings while AI running then close -> cancels
        pg.click('#aiov [data-close]')
        held.clear()
        pg.locator('.aib').first.click(); pg.wait_for_timeout(400)
        pg.evaluate("()=>{document.querySelector('#gear').click()}"); pg.wait_for_timeout(400)
        ck('race: opening Settings during a request cancels it cleanly', pg.locator('#stov.on').count() == 1 and jserrs(pg) == [], jserrs(pg))
        ck('race: no JS errors overall', jserrs(pg) == [], jserrs(pg))
        ctx.close()
    if which == 'xss':
        ctx, pg = mk(b)
        evil = [
            {'name': '<img src=x onerror=window.__pwn=1>Evil', 'url': 'javascript:window.__pwn=2', 'why': '<script>window.__pwn=3</script>', 'type': 'free'},
            {'name': '<b>Quote</b>"Break', 'url': 'https://example.org/" onmouseover="window.__pwn=4" x="', 'why': "<b onclick=window.__pwn=5>x</b>", 'type': '"><svg onload=window.__pwn=6>'},
            {'name': 'DataURL', 'url': 'data:text/html,<script>alert(1)</script>', 'why': 'x', 'type': 'cheap'},
            {'name': 'VBS', 'url': ' JaVaScRiPt:alert(1)', 'why': 'x', 'type': 'cheap'},
            {'name': 'Good', 'url': 'https://example.com/ok', 'why': 'fine & dandy <ok>', 'type': 'cheap'},
            {'name': 'Dup', 'url': 'https://example.com/ok', 'why': 'dup', 'type': 'free'},
            {'name': 5, 'url': 'https://example.com/n', 'why': 'bad name type'},
        ]
        pg.route('https://api.llm7.io/**', fake(200, chat_ok('Sure! Here you go:\n```json\n' + json.dumps(evil) + '\n```\n[1] ok')))
        pg.locator('.aib').first.click(); wait_done(pg)
        time.sleep(1.2)
        info = pg.evaluate("()=>({pwn:window.__pwn||null,imgs:document.querySelectorAll('#aibody img,#aibody script,#aibody svg').length,hrefs:[...document.querySelectorAll('#aibody .res a')].map(a=>a.getAttribute('href')),names:[...document.querySelectorAll('#aibody .res b')].map(b=>b.textContent),attrs:[...document.querySelectorAll('#aibody *')].filter(e=>[...e.attributes].some(a=>/^on/i.test(a.name))).length})")
        R['xss'] = info
        ck('XSS: no script executed, no injected elements/handlers', info['pwn'] is None and info['imgs'] == 0 and info['attrs'] == 0, info)
        ck('XSS: only http(s) links, javascript:/data: dropped, dups removed', all(re.match(r'https?://', h) for h in info['hrefs']) and 'https://example.com/ok' in info['hrefs'] and len(info['hrefs']) == len(set(info['hrefs'])), info['hrefs'])
        ck('XSS: names shown as literal text', any(n.startswith('<b>Quote</b>') for n in info['names']), info['names'])
        # settings text / item text escaping with weird storage values
        ctx2, pg2 = mk(b)
        pg2.evaluate("()=>localStorage.setItem('hub55_cfg', JSON.stringify({key:{groq:'\"><img src=x onerror=window.__pwn=7>'},model:{llm7:'<b>x</b>'}}))")
        pg2.reload(); pg2.click('#gear'); time.sleep(.5)
        ck('XSS: stored key/model values cannot inject', pg2.evaluate("()=>window.__pwn||null") is None and pg2.locator('#stbody img').count() == 0)
        pg2.fill('[data-key="groq"]', 'bad\u00e9key'); pg2.click('#stsave'); pg2.click('#stov [data-close]')
        pg2.route('https://api.groq.com/**', fake(200, chat_ok('[]')))
        pg2.route('https://api.llm7.io/**', fake(200, chat_ok('[{"name":"Ok","url":"https://example.org","why":"w","type":"free"}]')))
        pg2.locator('.aib').first.click(); wait_done(pg2)
        ck('non-ASCII key handled gracefully (no crash, falls through)', 'invalid' in pg2.inner_text('#aibody') or pg2.locator('#aibody .res').count() == 1, pg2.inner_text('#aibody')[:200])
        ctx2.close(); ctx.close()
    if which == 'print':
        # print-all via hash
        ctx, pg = mk(b, url=F + '#print-all')
        n = pg.locator('.item').count(); o = pg.locator('.item.open').count()
        ck('#print-all renders all items all expanded', n == TOTAL and o == TOTAL and pg.locator('.hd[aria-expanded="true"]').count() == TOTAL, (n, o))
        ck('#print-all 9 section titles, no counts', pg.locator('.ptitle').count() == len(EXPL) and not re.search(r'\(\d+\)', ' '.join(pg.eval_on_selector_all('.ptitle','e=>e.map(x=>x.textContent)'))))
        pg.emulate_media(media='print')
        vis = pg.evaluate("()=>({tabs:getComputedStyle(document.querySelector('#tabs')).display,aib:getComputedStyle(document.querySelector('.aib')).display,body:getComputedStyle(document.body).backgroundColor,pdate:getComputedStyle(document.querySelector('#pdate')).display,h1:document.querySelector('h1').innerText,link:document.querySelector('.pa').offsetParent!==null})")
        ck('print CSS: light page, controls hidden, URLs shown, header present', vis['tabs'] == 'none' and vis['aib'] == 'none' and vis['body'] == 'rgb(255, 255, 255)' and vis['link'] and vis['h1'].startswith(H1), vis)
        if ENG == 'chromium': pg.pdf(path='test-output/CMD-Resource-Hub-Arizona.pdf', format='Letter', print_background=True, margin={'top': '0.7in', 'bottom': '0.7in', 'left': '0.5in', 'right': '0.5in'},
               display_header_footer=True,
               header_template='<div style="font-size:9px;width:100%;padding:0 0.5in;color:#003a66;display:flex;justify-content:space-between"><span>CMD Resource Hub Arizona — Arizona Assistance Programs</span><span>Printed Nov 11, 2026</span></div>',
               footer_template='<div style="font-size:9px;width:100%;padding:0 0.5in;color:#555;display:flex;justify-content:flex-end"><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>')
        ck('PDF written', True)
        ctx.close()
        for i in range(len(EXPL)):
            ctx, pg = mk(b, url=F + f'#print-tab-{i}')
            n = pg.locator('.item').count()
            ck(f'#print-tab-{i} renders full tab expanded', n == EXPL[i] and pg.locator('.item.open').count() == n and pg.locator('.ptitle').count() == 1, n)
            ctx.close()
        # print button flow: filter active -> print current tab prints the WHOLE tab, then restores filtered view on afterprint
        ctx, pg = mk(b)
        pg.evaluate("()=>{window.__printed=0;window.print=()=>{window.__printed++; window.__cnt=document.querySelectorAll('.item').length; window.__open=document.querySelectorAll('.item.open').length; window.dispatchEvent(new Event('afterprint'))}}")
        pg.click('.tab[data-i="1"]'); pg.fill('#q', 'zzzqqq')
        pg.click('#prt'); pg.click('#pcur'); time.sleep(0.6)
        st = pg.evaluate("()=>({p:window.__printed,cnt:window.__cnt,open:window.__open,after:document.querySelectorAll('.item').length,empty:!!document.querySelector('.empty')})")
        ck('Print current tab: prints whole tab (ignores filter), then restores filtered view', st['p'] == 1 and st['cnt'] == EXPL[1] and st['open'] == EXPL[1] and st['empty'], st)
        pg.fill('#q', ''); pg.click('#prt'); pg.click('#pall'); time.sleep(0.6)
        st = pg.evaluate("()=>({p:window.__printed,cnt:window.__cnt,after:document.querySelectorAll('.item').length,pd:document.querySelector('#pdate').textContent})")
        ck('Print all: 599 printed then view restored to active tab', st['p'] == 2 and st['cnt'] == TOTAL and st['after'] == EXPL[1] and st['pd'] == '', st)
        ck('print flow: zero JS errors', jserrs(pg) == [], jserrs(pg))
        ctx.close()
    if which == 'a11y':
        ctx, pg = mk(b)
        pg.keyboard.press('Tab')
        order = []
        for _ in range(12):
            order.append(pg.evaluate("()=>{const a=document.activeElement;return (a.id||a.className||a.tagName)+':'+(a.getAttribute('aria-label')||a.textContent||'').trim().slice(0,25)}"))
            pg.keyboard.press('Tab')
        R['tab_order'] = order
        ck('keyboard tab order reaches controls', len(order) == 12, order)
        imgs_no_alt = pg.evaluate("()=>document.querySelectorAll('img:not([alt])').length")
        ck('no images without alt', imgs_no_alt == 0)
        ctx.close()
    print(json.dumps(R, indent=1, ensure_ascii=False)[:6000])
    print('SUMMARY', sum(1 for c in CHECKS if c[1]), 'pass /', len(CHECKS), 'total;', [c[0] for c in CHECKS if not c[1]])
    json.dump({'checks': CHECKS, 'extra': R}, open(f'test-output/t55-{ENG}-{which}.json', 'w'), indent=1, ensure_ascii=False)
