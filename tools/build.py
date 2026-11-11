import os
D = os.path.dirname(os.path.abspath(__file__))
import json
raw=json.load(open(os.path.join(D,'data','raw.json'))); raw.pop('venues')
raw['bounds']=[[round(a,1) for a in p] for p in raw['bounds']]
ven=json.load(open(os.path.join(D,'data','venues.json')))
t=open(os.path.join(D,'template.html')).read()
t=t.replace('/*__MAP__*/null',json.dumps(raw,ensure_ascii=False,separators=(',',':'))).replace('/*__VENUES__*/[]',json.dumps(ven,ensure_ascii=False,separators=(',',':')))
open(os.path.join(D,'..','public','index.html'),'w').write(t)
print(len(t))
