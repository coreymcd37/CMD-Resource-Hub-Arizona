import json,subprocess,concurrent.futures as cf,re
D=json.load(open('data.json'))
urls={}
for t in D:
    for x in t['items']:
        urls.setdefault(x['u'],set()).add('listing:'+x['n'])
        for k in ([x['ct'].get('w')] if x['ct'].get('w') else [])+x['ct'].get('srcs',[]):
            urls.setdefault(k,set()).add('contact:'+x['n'])
html=open('index.html',encoding='utf8').read()
for h in re.findall(r'href="(https?://[^"]+)"',html):
    urls.setdefault(h.replace('&amp;','&'),set()).add('page')
print(len(urls),'unique urls')
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
def c(u):
    r=subprocess.run(['curl','-s','-L','-o','/dev/null','-w','%{http_code} %{url_effective}','--max-time','30','-A',UA,'-H','Accept: text/html,*/*',u],capture_output=True,text=True).stdout.strip()
    code,_,fin=r.partition(' ')
    return u,code,fin
res={}
with cf.ThreadPoolExecutor(24) as e:
    for u,code,fin in e.map(c,list(urls)): res[u]=dict(code=code,final=fin,for_=sorted(urls[u])[:2])
json.dump(res,open('test/curl-results.json','w'),indent=1)
from collections import Counter
print(Counter(r['code'] for r in res.values()))
bad=[u for u,r in res.items() if not r['code'].startswith('2')]
open('test/browser-urls.txt','w').write('\n'.join(bad))
for u in bad: print(res[u]['code'],u,res[u]['for_'])
