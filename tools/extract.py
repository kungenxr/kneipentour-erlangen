import os
D = os.path.dirname(os.path.abspath(__file__))
import gzip, shutil
_osm = os.path.join(D, 'data', 'map.osm')
if not os.path.exists(_osm) and os.path.exists(_osm + '.gz'):
    with gzip.open(_osm + '.gz', 'rb') as a, open(_osm, 'wb') as b: shutil.copyfileobj(a, b)
import xml.etree.ElementTree as ET, json, math, re, collections, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else _osm
r = ET.parse(SRC).getroot()
LAT0, LON0 = 49.597, 11.005
KX = math.cos(math.radians(LAT0)) * 111320
KY = 110540
def P(lat, lon): return ((lon - LON0) * KX, -(lat - LAT0) * KY)

nodes = {}
ways = {}
wtags = {}
rels = []
pois = []
for e in r:
    if e.tag == 'node':
        nodes[e.get('id')] = (float(e.get('lat')), float(e.get('lon')))
        t = {x.get('k'): x.get('v') for x in e.findall('tag')}
        if t: pois.append(('node', e.get('id'), t))
    elif e.tag == 'way':
        ways[e.get('id')] = [n.get('ref') for n in e.findall('nd')]
        t = {x.get('k'): x.get('v') for x in e.findall('tag')}
        wtags[e.get('id')] = t
        if t: pois.append(('way', e.get('id'), t))
    elif e.tag == 'relation':
        t = {x.get('k'): x.get('v') for x in e.findall('tag')}
        mem = [(m.get('type'), m.get('ref'), m.get('role')) for m in e.findall('member')]
        rels.append((t, mem))

def coords(wid):
    return [P(*nodes[n]) for n in ways.get(wid, []) if n in nodes]

# Douglas-Peucker
def dp(pts, eps):
    if len(pts) < 3: return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1e-9
    imax, dmax = 0, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / L if L > 1e-6 else math.hypot(x - x1, y - y1)
        if d > dmax: imax, dmax = i, d
    if dmax > eps:
        return dp(pts[:imax + 1], eps)[:-1] + dp(pts[imax:], eps)
    return [pts[0], pts[-1]]

def path(pts, closed, eps=0.8):
    pts = dp(pts, eps)
    if len(pts) < 2: return ''
    s = 'M' + ' '.join(f'{round(x)} {round(y)}' for x, y in pts)
    return s + ('Z' if closed else '')

layers = collections.defaultdict(list)
GREEN = {('leisure', 'park'), ('leisure', 'garden'), ('landuse', 'grass'), ('landuse', 'meadow'), ('natural', 'scrub'),
         ('natural', 'wood'), ('landuse', 'forest'), ('landuse', 'cemetery'), ('leisure', 'playground'), ('landuse', 'allotments'),
         ('leisure', 'pitch'), ('landuse', 'village_green'), ('natural', 'grassland'), ('landuse', 'recreation_ground')}
def area_class(t):
    if 'building' in t or 'building:part' in t: return 'building'
    if t.get('natural') == 'water' or 'water' in t or t.get('waterway') == 'riverbank' or t.get('landuse') == 'basin': return 'water'
    for k, v in GREEN:
        if t.get(k) == v: return 'green'
    if t.get('highway') == 'pedestrian' and t.get('area') == 'yes': return 'plaza'
    if t.get('place') == 'square': return 'plaza'
    if t.get('amenity') == 'parking': return 'parking'
    return None

ROAD_W = {'secondary': 14, 'tertiary': 12, 'tertiary_link': 10, 'primary': 15, 'residential': 9, 'unclassified': 9,
          'living_street': 8, 'pedestrian': 10, 'service': 5, 'road': 7, 'footway': 2.4, 'path': 2.4, 'cycleway': 2.4,
          'steps': 2.4, 'track': 3}
roads = collections.defaultdict(list)
street_geo = collections.defaultdict(list)  # name -> list of point lists
railways = []
waterways = []

for wid, t in wtags.items():
    pts = coords(wid)
    if len(pts) < 2: continue
    closed = ways[wid][0] == ways[wid][-1]
    hw = t.get('highway')
    if hw in ROAD_W and t.get('area') != 'yes':
        roads[hw].append(path(pts, False, 0.6))
        if t.get('name') and hw not in ('footway', 'path', 'cycleway', 'steps', 'service'):
            street_geo[t['name']].append(pts)
        continue
    if t.get('railway') == 'rail' and t.get('service') is None:
        railways.append(path(pts, False, 1))
        continue
    if t.get('waterway') in ('river', 'stream', 'canal'):
        waterways.append(path(pts, False, 1))
        continue
    if closed:
        c = area_class(t)
        if c: layers[c].append(path(pts, True, 0.6 if c == 'building' else 1))

# multipolygons
for t, mem in rels:
    if t.get('type') != 'multipolygon': continue
    c = area_class(t)
    if not c: continue
    # join member ways into rings (simple: rings that are already closed; else chain)
    segs = [ways[ref] for typ, ref, role in mem if typ == 'way' and ref in ways]
    rings = []
    segs = [s[:] for s in segs if s]
    while segs:
        ring = segs.pop(0)
        changed = True
        while ring[0] != ring[-1] and changed:
            changed = False
            for i, s in enumerate(segs):
                if s[0] == ring[-1]: ring += s[1:]; segs.pop(i); changed = True; break
                if s[-1] == ring[-1]: ring += s[::-1][1:]; segs.pop(i); changed = True; break
        rings.append(ring)
    for ring in rings:
        pts = [P(*nodes[n]) for n in ring if n in nodes]
        if len(pts) > 2: layers[c].append(path(pts, True, 0.8))

# street labels: per name the longest single way segment, oriented left->right
labels = []
for name, segs in street_geo.items():
    total = sum(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(s, s[1:])) for s in segs)
    if total < 90: continue
    best = max(segs, key=lambda s: sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(s, s[1:])))
    blen = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(best, best[1:]))
    if blen < 60: continue
    pts = dp(best, 2)
    if pts[-1][0] < pts[0][0]: pts = pts[::-1]
    labels.append({'n': name, 'd': 'M' + ' '.join(f'{round(x)} {round(y)}' for x, y in pts), 'len': round(blen)})

# squares / places
places = []
for kind, oid, t in pois:
    if t.get('place') in ('square',) and t.get('name'):
        if kind == 'node': lat, lon = nodes[oid]
        else:
            ns = [nodes[n] for n in ways[oid] if n in nodes]
            lat = sum(a for a, b in ns) / len(ns); lon = sum(b for a, b in ns) / len(ns)
        x, y = P(lat, lon); places.append({'n': t['name'], 'x': round(x), 'y': round(y)})
    if kind == 'way' and t.get('name') and ((t.get('highway') == 'pedestrian' and t.get('area') == 'yes') or t.get('place') == 'square' or t.get('leisure') in ('park',) ):
        ns = [nodes[n] for n in ways[oid] if n in nodes]
        if len(ns) > 2:
            lat = sum(a for a, b in ns) / len(ns); lon = sum(b for a, b in ns) / len(ns)
            x, y = P(lat, lon); places.append({'n': t['name'], 'x': round(x), 'y': round(y), 'park': t.get('leisure') == 'park'})
    if t.get('railway') == 'station' and t.get('name') and kind == 'node':
        x, y = P(*nodes[oid]); places.append({'n': t['name'], 'x': round(x), 'y': round(y), 'station': True})

# --- venues ---
def centroid(kind, oid):
    if kind == 'node': return nodes[oid]
    ns = [nodes[n] for n in ways[oid] if n in nodes]
    return (sum(a for a, b in ns) / len(ns), sum(b for a, b in ns) / len(ns))

# nearest street name for missing addresses
street_pts = []
for name, segs in street_geo.items():
    for s in segs:
        for p in s: street_pts.append((p, name))
def nearest_street(x, y):
    best = min(street_pts, key=lambda q: (q[0][0] - x) ** 2 + (q[0][1] - y) ** 2)
    return best[1]

venues = []
for kind, oid, t in pois:
    am = next((x for x in (t.get('amenity') or '').split(';') if x in ('restaurant','pub','bar','nightclub','cafe','hookah_lounge')), None)
    if am not in ('restaurant', 'pub', 'bar', 'nightclub', 'cafe', 'hookah_lounge'): continue
    if not t.get('name'): continue
    lat, lon = centroid(kind, oid)
    x, y = P(lat, lon)
    addr = (t.get('addr:street', '') + ' ' + t.get('addr:housenumber', '')).strip()
    venues.append({'osm': f'{kind}/{oid}', 'name': t['name'], 'amenity': am, 'cuisine': t.get('cuisine'),
                   'addr': addr or ('nahe ' + nearest_street(x, y)), 'hours': t.get('opening_hours'),
                   'lat': round(lat, 6), 'lon': round(lon, 6), 'web': t.get('website') or t.get('contact:website'),
                   'outdoor': t.get('outdoor_seating'), 'beer': t.get('brewery')})

json.dump({'layers': {k: v for k, v in layers.items()}, 'roads': roads, 'rail': railways, 'water': waterways,
           'labels': labels, 'places': places, 'venues': venues,
           'bounds': [P(float(r.find('bounds').get('maxlat')), float(r.find('bounds').get('minlon'))),
                      P(float(r.find('bounds').get('minlat')), float(r.find('bounds').get('maxlon')))]},
          open(os.path.join(D,'data','raw.json'), 'w'), ensure_ascii=False)
print({k: len(v) for k, v in layers.items()}, {k: len(v) for k, v in roads.items()}, len(labels), len(places), len(venues))
print(places)
