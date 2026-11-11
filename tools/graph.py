import os
D = os.path.dirname(os.path.abspath(__file__))
import gzip, shutil
_osm = os.path.join(D, 'data', 'map.osm')
if not os.path.exists(_osm) and os.path.exists(_osm + '.gz'):
    with gzip.open(_osm + '.gz', 'rb') as a, open(_osm, 'wb') as b: shutil.copyfileobj(a, b)
import xml.etree.ElementTree as ET, json, math
r=ET.parse(os.path.join(D,'data','map.osm')).getroot()
LAT0,LON0=49.597,11.005; KX=math.cos(math.radians(LAT0))*111320; KY=110540
nodes={e.get('id'):(float(e.get('lat')),float(e.get('lon'))) for e in r.iter('node')}
WALK={'footway','path','pedestrian','residential','service','living_street','tertiary','tertiary_link','secondary','secondary_link','unclassified','steps','cycleway','track','road','primary'}
idx={}; xy=[]; edges=set()
def nid(n):
    if n not in idx:
        lat,lon=nodes[n]; idx[n]=len(xy)//2; xy.extend([round((lon-LON0)*KX),round(-(lat-LAT0)*KY)])
    return idx[n]
for w in r.iter('way'):
    t={x.get('k'):x.get('v') for x in w.findall('tag')}
    if t.get('highway') in WALK and t.get('access') not in ('private','no') and t.get('foot') not in ('no','private') and t.get('area')!='yes':
        nds=[n.get('ref') for n in w.findall('nd') if n.get('ref') in nodes]
        for a,b in zip(nds,nds[1:]):
            i,j=nid(a),nid(b)
            if i!=j: edges.add((min(i,j),max(i,j)))
flat=[v for e in sorted(edges) for v in e]
raw=json.load(open(os.path.join(D,'data','raw.json'))); raw['graph']={'xy':xy,'e':flat}
json.dump(raw,open(os.path.join(D,'data','raw.json'),'w'),ensure_ascii=False)
print(len(xy)//2,len(edges))
