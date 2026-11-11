import sys
from playwright.sync_api import sync_playwright
F='index.html'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1280,'height':900}); errs=[]
    pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file://'+F)
    print('items',pg.locator('.item').count(),'tabs',pg.locator('#tabs .tab').count(),'static',pg.locator('#static').count(),'errs',errs)
    print(pg.inner_text('#tabs')); print(pg.inner_text('#thead')); print(repr(pg.inner_text('#count')))
    pg.fill('#q','food'); print(pg.inner_text('#count'), pg.locator('.item').count())
    pg.locator('.item .hd').first.click(); print(pg.locator('.item.open .in').inner_text()[:300])
    pg.screenshot(path='/tmp/smoke.png'); b.close()
