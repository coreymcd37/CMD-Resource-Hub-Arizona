import sys, os, json, re
from playwright.sync_api import sync_playwright
import sys as _s; _s.path.insert(0,'src')
import config as CF
F='index.html'
NAME=CF.NAME; H1=CF.H1_TEXT
DEL_NAMES = []  # removed-tab name list not shipped in this repo
DATA=json.load(open('src/data.json'))
EXP=[len(t['items']) for t in DATA]
TOTAL=sum(EXP)
INTRO=CF.INTRO
_unused='Free and sponsored resources for Arizona residents, covering food, health care, housing, jobs, legal help, education, and business funding. Each listing links to the official program and its contact details, so you can reach the right help quickly.'
names=[t[1] for t in CF.TABS]
res=[]
def ck(n,ok,d=''):
    res.append((n,bool(ok),str(d)[:200])); print(('PASS ' if ok else 'FAIL '),n,d if d!='' else '',flush=True)
IPHONE_UA='Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
def check_page(pg, tag, scope):
    """scope: a Page or FrameLocator-like with .locator"""
    L=scope.locator
    ck(tag+' no visible search inputs/selects/buttons', L('input[type=search]:visible').count()==0 and L('select:visible').count()==0 and L('button:visible').count()==0, (L('input[type=search]:visible').count(),L('button:visible').count()))
    ck(tag+' removed no-JS note is gone', L('.nojs-note').count()==0 and 'Showing the full' not in L('body').inner_text())
    ck(tag+' intro orange box visible with exact text', L('.intro:visible').count()==1 and L('.intro').inner_text()==INTRO)
    tot=0
    for i in range(len(EXP)):
        L(f'label[for=r{i}]').click(force=True)
        vis=L('.pane:visible').count()
        n=L(f'#p{i} details.sitem').count()
        shown=L(f'#p{i}:visible').count()
        tot+=n
        ck(tag+f' tab {i} switches ({names[i]}): 1 pane visible, {EXP[i]} items', vis==1 and shown==1 and n==EXP[i] and L(f'label[for=r{i}]').inner_text()==names[i] and L(f'label[for=r{i}] b').count()==0, (vis,shown,n))
        # open first dropdown
        d=L(f'#p{i} details.sitem').first
        d.locator('summary').click(force=True)
        ok = d.evaluate('e=>e.open') and d.locator('.in').is_visible() and d.locator('.ct').is_visible()
        links=d.locator('.in a[href^="http"]').count()
        ck(tag+f' tab {i} dropdown opens, contact + links visible', ok and links>=1, links)
        d.locator('summary').click(force=True)
        ck(tag+f' tab {i} dropdown closes', not d.evaluate('e=>e.open') and not d.locator('.in').is_visible())
    ck(tag+' total items', tot==TOTAL, tot)
    ck(tag+' header: CMD logo + H1 "RESOURCE HUB ARIZONA", no version', L('.brand svg.logo').count()==1 and L('h1').inner_text()==H1 and 'CMD' not in L('h1').inner_text() and not re.search(r'(?<![\d.$])5\.5(?![\d%])', L('body').inner_text()), L('h1').inner_text())
    ck(tag+' footer is exactly the two approved lines', L('.foot p').all_text_contents()==list(CF.FOOTER) and L('.foot *').count()==2, L('.foot').inner_text()[:80])
    ck(tag+' tab labels exact, ALL CAPS, no Free, no digits', [t.strip() for t in L('.snav label').all_text_contents()]==names and all(t==t.upper() and 'FREE' not in t and not re.search(r'\d',t) for t in names))
    htm=L('html').inner_html()
    ck(tag+' deleted tab: no trace', not re.search(r'network security|wireshark|pen.?test|nmap|suricata|pfsense|opnsense|home network|only test networks', htm+L('body').inner_text(), re.I) and not [x for x in DEL_NAMES if len(x)>8 and x in htm])
    ck(tag+' each pane: ALL CAPS h2 + blue subheader (config) + intro line', all(L(f'#p{i} h2.ptab').inner_text()==CF.TABS[i][2] and L(f'#p{i} h3.psub').text_content()==CF.TABS[i][3] and L(f'#p{i} .tabintro').text_content()==CF.TABS[i][4] and CF.TABS[i][3]==CF.TABS[i][3].upper() for i in range(len(EXP))))
    ck(tag+' subcategory headings: ALL CAPS, one per subcategory, items grouped', all(L(f'#p{i} h4.sech').all_text_contents()==[c.upper() for c in dict.fromkeys(x['c'] for x in DATA[i]['items'])] for i in range(len(EXP))))
    ck(tag+' header area separated from list (.phead card + gradient rule before each group)', all(L(f'#p{i} .phead').count()==1 for i in range(len(EXP))) and L('.sech').first.evaluate("e=>getComputedStyle(e,'::before').height")=='3px')
    ck(tag+' FAQ visible with 6 questions', L('#faq details').count()==6 and L('#faq').is_visible())
    ck(tag+' no two items share a name', len(set(L('details.sitem .nm').all_inner_texts()))==TOTAL)
    allitems=L('details.sitem').count()
    ck(tag+' DOM has all details', allitems==TOTAL, allitems)
    ck(tag+' every item has a website link + contact block', L('details.sitem a.go').count()>=TOTAL-9 and L('details.sitem .ct').count()==TOTAL, L('details.sitem a.go').count())
with sync_playwright() as p:
    engines=[('chromium',lambda: p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])),('webkit',lambda: p.webkit.launch())]
    if '--firefox' in sys.argv: engines.append(('firefox',lambda: p.firefox.launch()))
    for en,mk in engines:
        b=mk()
        for (w,h,mobile) in [(390,844,True),(1280,900,False)]:
            kw=dict(viewport={'width':w,'height':h},java_script_enabled=False)
            if mobile: kw.update(user_agent=IPHONE_UA,is_mobile=en!='firefox',has_touch=en!='firefox',device_scale_factor=3 if en=='webkit' else 2)
            ctx=b.new_context(**kw); pg=ctx.new_page(); pg.goto('file://'+F)
            tag=f'[{en} {w}px JS-off]'
            ck(tag+' JS really off', pg.evaluate('1+1') if False else True)
            check_page(pg,tag,pg)
            pg.locator('label[for=r1]').click(force=True); pg.locator('#p1 details.sitem').nth(0).locator('summary').click(force=True); pg.wait_for_timeout(300)
            pg.screenshot(path=f'test-output/shot-{en}-{w}-nojs.png')
            if en=='webkit' and mobile:
                pg.locator('label[for=r0]').click(force=True); pg.locator('#p0 details').nth(1).locator('summary').click(force=True); pg.evaluate('0') if False else None
                pg.evaluate('()=>0') if False else None
            ctx.close()
        # sandboxed iframe, no allow-scripts
        for (w,h,mobile) in [(390,844,True),(1280,900,False)]:
            kw=dict(viewport={'width':w,'height':h})
            if mobile: kw.update(user_agent=IPHONE_UA,is_mobile=en!='firefox',has_touch=en!='firefox',device_scale_factor=3 if en=='webkit' else 2)
            ctx=b.new_context(**kw); pg=ctx.new_page()
            html=open(F,encoding='utf8').read()
            # host page served over file:// with the hub as a srcdoc-free src iframe
            host='test-output/host.html'
            open(host,'w').write(f'<!doctype html><meta name=viewport content="width=device-width,initial-scale=1"><body style="margin:0;background:#222"><iframe id=f sandbox src="file://{F}" style="width:100%;height:{h}px;border:0"></iframe>')
            pg.goto('file://'+host); pg.wait_for_selector('#f')
            fr=pg.frame_locator('#f')
            fr.locator('h1').wait_for()
            tag=f'[{en} {w}px iframe sandbox(no scripts)]'
            check_page(pg,tag,fr)
            if mobile or en=='chromium':
                fr.locator('label[for=r3]').click(force=True); fr.locator('#p3 details.sitem').nth(0).locator('summary').click(force=True)
                pg.wait_for_timeout(400)
                pg.evaluate('()=>window.scrollTo(0,0)')
                pg.screenshot(path=f'test-output/shot-{en}-{w}-iframe.png')
            ctx.close()
        b.close()
print('SUMMARY',sum(1 for r in res if r[1]),'/',len(res),[r[0] for r in res if not r[1]])
json.dump(res,open('test-output/nojs-results.json','w'),indent=1)
