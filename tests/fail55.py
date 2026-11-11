from playwright.sync_api import sync_playwright
src=open('index.html',encoding='utf8').read()
i=src.index('<script>\ntry {')
def variant(name, repl):
    open(f'/tmp/f_{name}.html','w',encoding='utf8').write(repl)
variant('runtime', src.replace('<script>\ntry {','<script>\ntry {\nnull.boom;',1))
variant('late', src.replace("document.documentElement.classList.add('js');","throw new Error('late failure');",1))
variant('syntax', src.replace('<script>\ntry {','<script>\ntry { @@@ ',1))
with sync_playwright() as p:
    for en in ['chromium','webkit','firefox']:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']) if en=='chromium' else getattr(p,en).launch()
        for v in ['runtime','late','syntax']:
            pg=b.new_page(viewport={'width':390,'height':844}); pg.goto(f'file:///tmp/f_{v}.html')
            r=pg.evaluate("()=>({items:document.querySelectorAll('details.sitem').length,vis:!!document.querySelector('.pane').offsetParent||[...document.querySelectorAll('.pane')].some(e=>e.offsetParent),search:!!document.querySelector('#q').offsetParent,btn:[...document.querySelectorAll('button')].some(b=>b.offsetParent),err:(document.getElementById('jserr').hidden?'':document.getElementById('jserr').textContent.slice(0,90))})")
            print(en,v,r,flush=True); pg.close()
        b.close()
