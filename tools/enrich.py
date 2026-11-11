import os
D = os.path.dirname(os.path.abspath(__file__))
import json, re, math, unicodedata
raw = json.load(open(os.path.join(D,'data','raw.json')))
LAT0, LON0 = 49.597, 11.005
KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
def P(lat, lon): return ((lon - LON0) * KX, -(lat - LAT0) * KY)

EXCLUDE = {
    'Hinterhaus': 'in OSM als geschlossen markiert',
    'Patio': 'nur tagsüber',
    'minibar': 'nur tagsüber',
}
CAFE_KEEP = {'Gambrinus','Aroma Lounge','Enoteca','vino','Zum weißen Lamm - Weinbar & Cafe','Sax','Beisl (Cafe und Bistro)','Theatercafe'}
CURATED = {
 'Delphi Bar': dict(cat='bar', food=False, styles=['Cocktails & Bar','Gemütlich & urig'], desc='Bar am Bohlenplatz, nur Freitag und Samstag geöffnet.', hours='Fr,Sa 18:00-02:00'),
 'Flaxa': dict(name='Flaxa – Vinothek & Event Café', cat='bar', food=True, cuisine='international', styles=['Wein & Genuss','Modern & locker'], desc='Vinothek und Bistro an der Östlichen Stadtmauerstraße, Do–Sa bis 23 Uhr.', hours='Tu,We 09:00-19:00; Th-Sa 13:00-23:00; Su,Mo off'),
 'Gambrinus': dict(cat='kneipe', food=True, cuisine='pizza', styles=['Gemütlich & urig','Studentenkneipe'], desc='Kneipe und Bistro mit Pizza, Baguettes und Crêpes, täglich bis 2 Uhr.'),
 'Aroma Lounge': dict(cat='bar', styles=['Cocktails & Bar'], desc='Shisha-Lounge mit Cocktails, lange geöffnet.', hours='Mo-Su 18:00-03:00'),
 'Enoteca': dict(name='Enoteca Erlangen', cat='bar', food=False, styles=['Wein & Genuss','Gemütlich & urig'], desc='Gemütliche Weinstube in der Schiffstraße.', hours='Tu-Su 11:00-22:00; Mo off'),
 'vino': dict(name='vino', cat='bar', styles=['Wein & Genuss'], desc='Weinbar am Neustädter Kirchenplatz.'),
 'Zum weißen Lamm - Weinbar & Cafe': dict(name='Zum weißen Lamm', cat='bar', styles=['Wein & Genuss','Gemütlich & urig'], desc='Weinbar in der Hauptstraße, täglich ab 17 Uhr.'),
 'Sax': dict(cat='bar', styles=['Cocktails & Bar','Modern & locker'], desc='Café-Bar am Schlossplatz, Fr/Sa bis 2 Uhr.'),
 'Beisl (Cafe und Bistro)': dict(name='Beisl', cat='kneipe', food=True, cuisine='international', styles=['Gemütlich & urig','Studentenkneipe'], desc='Café und Bistro in der Hauptstraße, täglich bis 2 Uhr.'),
 'Theatercafe': dict(cat='bar', styles=['Gemütlich & urig','Wein & Genuss'], desc='Theatercafé gegenüber dem Markgrafentheater, abends geöffnet.'),
 'Paisley Park': dict(name='Paisley', cat='club', styles=['DJ-Bar & Tanzen'], desc='Club mit DJs von Black und RnB bis House – Programm vorher checken.', hours='Fr,Sa 23:00-05:00'),
 'Jürgen Sigwarts Kulisse': dict(name='Kulisse', cuisine='regional', styles=['Fränkisch & Bier','Gemütlich & urig'], desc='Fränkisches Restaurant mit Freisitz in der Theaterstraße.', hours='Mo-Sa 18:00-23:30; Su off'),
 "Luitpoldstub'n": dict(cat='kneipe', food=True, cuisine='regional', styles=['Fränkisch & Bier','Gemütlich & urig','Sportsbar'], desc='Fränkische Wirtschaft mit Sportübertragungen und Freisitz, lange geöffnet.', hours='Mo-Fr 14:00-02:00; Sa 13:00-24:00; Su 00:00-24:00'),
 'No Name Bar': dict(cat='kneipe', styles=['Gemütlich & urig','Studentenkneipe'], desc='Kleine Kneipe mit Spielen und Freisitz – nur Barzahlung.', hours='Mo-Th 16:00-24:00; Fr,Sa 16:00-01:00; Su off'),
 'Alter Simpl': dict(styles=['Fränkisch & Bier', 'Gemütlich & urig'], desc='Erlanger Institution für fränkische Küche, rustikal und traditionell.'),
 'Steinbach-Bräu': dict(name='Steinbach Bräu', cat='restaurant', food=True, cuisine='regional', styles=['Fränkisch & Bier', 'Gemütlich & urig'], desc='Familienbrauerei mit eigenem Bier, Wirtshaus und kleinem Biermuseum.'),
 'Blaue Traube am Zollhaus': dict(styles=['Fränkisch & Bier'], desc='Gaststätte mit frischer fränkischer Küche.'),
 'Kitzmann BräuSchänke': dict(styles=['Fränkisch & Bier', 'Gemütlich & urig'], desc='Brauereiwirtschaft der traditionsreichen Kitzmann-Brauerei.'),
 'Altstädter Schießhaus': dict(styles=['Fränkisch & Bier', 'Gemütlich & urig'], desc='Traditionswirtshaus am Fuß des Burgbergs mit fränkischer Küche.'),
 'Hans im Glück': dict(styles=['Modern & locker'], desc='Burgergrill am Hugenottenplatz, viel Vegetarisches.'),
 'Glüxrausch': dict(cat='kneipe', food=True, styles=['Modern & locker', 'Cocktails & Bar'], desc='Bar-Restaurant mit Burgern in der Altstadt.'),
 'Mireo': dict(styles=['Modern & locker'], desc='Mediterranes Restaurant mit Bar, lange geöffnet.'),
 'Basilikum': dict(styles=['Modern & locker'], desc='Mediterranes Bistro mit Weinkarte an der Altstädter Kirche.'),
 'YiKou Asian Tapas Bar': dict(name='YiKou', styles=['Modern & locker', 'Cocktails & Bar'], desc='Asiatische Tapas-Bar mit hochwertiger Küche.'),
 'Zum Pleitegeier': dict(cat='restaurant', food=True, cuisine='pizza', styles=['Studentenkneipe', 'Gemütlich & urig'], desc='Kultkneipe – legendäre Bananenpizza, Selbstbedienung, überdachter Biergarten.'),
 'Tio': dict(cat='bar', food=True, cuisine='pizza', styles=['Studentenkneipe', 'Modern & locker'], desc='Café, Bar und Pizzeria – eine der bestbewerteten Bars der Stadt.'),
 'Bogarts': dict(cat='bar', food=True, cuisine='burger', styles=['Sportsbar', 'Modern & locker'], desc='Bar, Restaurant und Sportsbar am Bahnhof, Fr/Sa bis 3 Uhr.'),
 'Klimperkasten': dict(cat='kneipe', styles=['Studentenkneipe', 'Gemütlich & urig'], desc='Urige Kneipe mit lebhafter Stimmung, guter Musik und Events.'),
 "Granny Mac's": dict(name="Granny Mac's Irish Pub", food=True, cuisine='burger', styles=['Irish Pub'], desc='Irish Pub am Martin-Luther-Platz, montags Pub Quiz, Burger und Fish & Chips.'),
 "Murphy's Law": dict(food=True, cuisine='pub', styles=['Irish Pub'], desc='Irish Pub seit 1985, Live-Musik, Pies und Whiskey.'),
 'Goldener Mond': dict(styles=['Irish Pub', 'Gemütlich & urig'], desc='Gemütlicher Irish Pub südlich vom Bahnhof, Fr/Sa bis 4 Uhr.'),
 "Die Hex'": dict(styles=['Schlager & Oldies'], desc='Die Schlager- und Oldie-Kneipe der Stadt.'),
 'The Dartmoor Inn': dict(styles=['Irish Pub', 'Gemütlich & urig'], desc='Britischer Pub zum Wohlfühlen.'),
 'Wort und Klang': dict(name='Wort & Klang', cat='bar', styles=['Studentenkneipe', 'Modern & locker'], desc='Das „bunte Wohnzimmer“: Bar mit Großstadtflair und sehr gutem Kickertisch.', hours='Tu-Th 19:00-02:00, Fr,Sa 18:00-02:00'),
 'El Leon': dict(name='ELEON Bar', cat='bar', food=True, styles=['Cocktails & Bar'], desc='Cocktailbar mit Burgern und Pizza, gute Atmosphäre.'),
 'Transfer Bar und Club': dict(name='Transfer', cat='club', styles=['DJ-Bar & Tanzen'], desc='Szene-Bar seit 1983, eine der ersten DJ-Bars Bayerns – perfekt als letzter Stopp.'),
 'Zirkel': dict(styles=['DJ-Bar & Tanzen', 'Studentenkneipe'], desc='Studentenclub und Diskothek in der Altstadt.'),
 'Kulturzentrum E-Werk': dict(name='E-Werk', styles=['DJ-Bar & Tanzen'], desc='Kulturzentrum mit Partys und Konzerten – Programm vorher checken.'),
 'Kellerbühne im E-Werk': dict(styles=['Gemütlich & urig', 'Studentenkneipe'], desc='Kneipe im Kulturzentrum E-Werk.'),
 'Kanapee': dict(styles=['Studentenkneipe', 'Gemütlich & urig'], desc='Wohnzimmerkneipe in der Neuen Straße, lange offen.'),
 'Strohalm': dict(styles=['Studentenkneipe', 'Gemütlich & urig'], desc='Altstadtkneipe, Fr/Sa bis 3 Uhr.'),
 'La Sorbonne': dict(styles=['Studentenkneipe', 'Gemütlich & urig'], desc='Kneipe in der oberen Hauptstraße.'),
 'Backstage': dict(styles=['Studentenkneipe', 'DJ-Bar & Tanzen'], desc='Kneipe mit langen Nächten, Fr/Sa bis 5 Uhr.'),
 'Fanblock': dict(styles=['Sportsbar'], desc='Sportsbar in der Goethestraße.'),
 'Amnestia': dict(food=True, styles=['Gemütlich & urig'], desc='Kneipe mit griechischer Küche, täglich bis 2 Uhr.'),
 'Café Brazil': dict(food=True, styles=['Gemütlich & urig', 'Modern & locker'], desc='Café-Kneipe in der Bismarckstraße, täglich bis 1 Uhr.'),
 'Toledo': dict(cat='bar', styles=['Cocktails & Bar', 'Modern & locker'], desc='Tapas und Drinks am Martin-Luther-Platz, täglich bis 2 Uhr.'),
 "Anna's Café": dict(styles=['Cocktails & Bar', 'Modern & locker'], desc='Bistro-Bar, Do–Sa bis 4 Uhr.'),
 'Muskat': dict(styles=['Modern & locker'], desc='Bio-Restaurant und Café, Fr/Sa bis 3 Uhr.'),
 'O-sha': dict(styles=['Modern & locker'], desc='Thai-Restaurant am Theaterplatz, am Wochenende bis 2 Uhr.'),
 'Galileo': dict(styles=['Modern & locker', 'Cocktails & Bar'], desc='Bar-Restaurant in rustikal-elegantem Ambiente.'),
 'Spruz': dict(),
 'Traditionskneipe Spruz': dict(name='Spruz', styles=['Gemütlich & urig', 'Fränkisch & Bier'], desc='Traditionskneipe in der Weißen Herzstraße.'),
 'Society': dict(styles=['Cocktails & Bar'], desc='Bar in der Rückertstraße.'),
 'Mirage': dict(styles=['Cocktails & Bar'], desc='Bar in der Altstadt, täglich bis 2 Uhr.'),
 'Nachtcafe Smile': dict(styles=['Cocktails & Bar', 'Gemütlich & urig'], desc='Nachtcafé, am Wochenende bis 2 Uhr.'),
 'Wörner': dict(styles=['Cocktails & Bar', 'Gemütlich & urig'], desc='Bar am Martin-Luther-Platz.'),
 'La Casita': dict(styles=['Cocktails & Bar'], desc='Bar in der Hauptstraße.'),
 'StarClub': dict(styles=['Gemütlich & urig'], desc='Kneipe in der Stubenlohstraße.'),
 'Loco': dict(styles=['DJ-Bar & Tanzen']),
 'Gleis 1': dict(styles=['Gemütlich & urig'], desc='Kneipe am Bahnhof.'),
 'Rosmarin': dict(styles=['Modern & locker'], desc='Restaurant mit Bar, täglich bis 1:30 Uhr.'),
 'La Brasserie': dict(styles=['Modern & locker'], desc='Brasserie am Anfang der Nürnberger Straße, bis 1 Uhr.'),
 'Arizona': dict(styles=['Modern & locker'], desc='Amerikanisches Restaurant, Burger und Steaks.'),
}
EXTRA_OLD = [  # nicht in den OSM-Daten, aus Recherche
 dict(name='Gambrinus', addr='Vierzigmannstraße 7', cat='kneipe', food=False, styles=['Gemütlich & urig', 'Fränkisch & Bier'], desc='Kneipe und Bistro, gut bewertet.', hours='ab 17 Uhr', near='Steinbach-Bräu', dx=14, dy=-10),
 dict(name='Aroma Lounge', addr='Hauptstraße 106', cat='bar', food=False, styles=['Cocktails & Bar'], desc='Shisha-Lounge mit Cocktails, bis 3 Uhr.', hours='bis 03 Uhr', near='Glüxrausch', dx=10, dy=-14),
]

CUIS = [
 ('Fränkisch & Deutsch', ['regional', 'german', 'bohemian', 'schnitzel', 'bavarian']),
 ('Burger & Steak', ['burger', 'american', 'steak_house', 'pub']),
 ('Italienisch & Pizza', ['italian', 'pizza']),
 ('Mediterran & Griechisch', ['mediterranean', 'greek', 'tapas', 'spanish', 'latin_american']),
 ('Asiatisch', ['asian', 'vietnamese', 'thai', 'japanese', 'sushi', 'ramen', 'chinese', 'korean']),
 ('Indisch & Orientalisch', ['indian', 'arab', 'turkish', 'kebab']),
 ('Mexikanisch', ['mexican', 'tex-mex']),
]
NAME_CUIS = {'Holzgarten': 'regional', 'Muskat': 'international', 'Rosmarin': 'mediterranean', 'Jürgen Sigwarts Kulisse': 'regional',
             'Lesecafé Erlangen': 'international', 'Rizellis': 'italian', 'Mi Xiang Dim Sum': 'chinese', 'PapaKocht!': 'international',
             "Luitpoldstub'n": 'regional', "Altmann's Stube": 'regional', 'AVA Restaurant & Lounge': 'international', 'Rahmen Ippin': 'ramen',
             'Seoulicious': 'korean', 'Tio': 'pizza', 'Amnestia': 'greek', 'Café Brazil': 'international'}
def cgroup(c):
    if not c: return 'International'
    toks = [x.strip().lower() for x in c.split(';')]
    for g, keys in CUIS:
        if any(t in keys for t in toks): return g
    return 'International'

DAYS = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
def tmin(s):
    h, m = s.split(':'); return int(h) * 60 + int(m)
def parse_hours(h):
    """-> list of 7 entries: list of [start,end] or None (unbekannt)"""
    if not h: return None
    if '"' in h or 'easter' in h or re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b', h): return None
    if h.strip() in ('closed', 'off'): return [[] for _ in DAYS]
    res = [None] * 7
    rules = [x.strip() for x in h.split(';') if x.strip()]
    parts = []
    for ru in rules:
        parts += [x.strip() for x in re.split(r',\s*(?=(?:Mo|Tu|We|Th|Fr|Sa|Su|PH)\b)', ru) if x.strip()]
    pend = []
    for p in parts:
        m = re.match(r'^((?:(?:Mo|Tu|We|Th|Fr|Sa|Su|PH)(?:\[\d\])?(?:-(?:Mo|Tu|We|Th|Fr|Sa|Su))?\s*,?\s*)+)?(.*)$', p)
        dpart, tpart = (m.group(1) or '').strip(), m.group(2).strip()
        days = set()
        for tok in re.split(r'[,\s]+', dpart):
            if not tok or tok.startswith('PH') or '[' in tok: continue
            if '-' in tok:
                a, b = tok.split('-'); i, j = DAYS.index(a), DAYS.index(b)
                k = i
                while True:
                    days.add(k)
                    if k == j: break
                    k = (k + 1) % 7
            else: days.add(DAYS.index(tok))
        if not dpart: days = set(range(7))
        if dpart and all(t.startswith('PH') or '[' in t for t in re.split(r'[,\s]+', dpart) if t):
            if not pend: continue
            days = set()
        if not tpart:
            pend += list(days); continue
        days |= set(pend); pend = []
        if tpart in ('off', 'closed'):
            for d in days: res[d] = []
            continue
        iv = []
        ok = True
        for rng in tpart.split(','):
            rng = rng.strip()
            mm = re.match(r'^(\d{1,2}:\d\d)-(\d{1,2}:\d\d)\+?$', rng)
            mo = re.match(r'^(\d{1,2}:\d\d)\+$', rng)
            if mm:
                a, b = tmin(mm.group(1)), tmin(mm.group(2))
                if b <= a: b += 1440
                iv.append([a, b])
            elif mo:
                a = tmin(mo.group(1)); iv.append([a, max(a + 300, 24 * 60 + 60)])
            else: ok = False
        if not ok: return None
        for d in days:
            # Regeln für denselben Tag in einer Zeile ergänzen sich (z. B. "Tu-Su 11-14, Tu-Su 17-22")
            res[d] = iv if res[d] is None or p in rules else (res[d] + iv)
    if all(x is None for x in res): return None
    return [x if x is not None else [] for x in res]

def de_hours(h):
    if not h: return ''
    s = h
    for a, b in [('Mo', 'Mo'), ('Tu', 'Di'), ('We', 'Mi'), ('Th', 'Do'), ('Fr', 'Fr'), ('Sa', 'Sa'), ('Su', 'So'), ('PH', 'Feiertag')]:
        s = re.sub(r'\b' + a + r'\b', b, s)
    s = s.replace('off', 'zu').replace('closed', 'geschlossen').replace(';', ' ·').replace('"', '')
    return s

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40]

out = []; seen = set(); excluded = []
byname = {v['name']: v for v in raw['venues']}
for v in raw['venues']:
    n = v['name']
    if n in EXCLUDE: excluded.append((n, EXCLUDE[n])); continue
    if n == "Altmann's Stube Hotel und Restaurant": continue
    if v['amenity'] in ('cafe','hookah_lounge') and n not in CAFE_KEEP: continue
    c = CURATED.get(n, {})
    am = v['amenity']
    cat = c.get('cat') or {'restaurant': 'restaurant', 'pub': 'kneipe', 'bar': 'bar', 'nightclub': 'club', 'cafe': 'bar', 'hookah_lounge': 'bar'}[am]
    cuisine_raw = c.get('cuisine') or v['cuisine'] or NAME_CUIS.get(n)
    food = c.get('food', cat == 'restaurant' or bool(v['cuisine']))
    styles = c.get('styles')
    if styles is None:
        styles = {'kneipe': ['Gemütlich & urig'], 'bar': ['Cocktails & Bar'], 'club': ['DJ-Bar & Tanzen']}.get(cat, [])
        if cat == 'restaurant' and cgroup(cuisine_raw) == 'Fränkisch & Deutsch': styles = ['Fränkisch & Bier']
    hours = c.get('hours') or v['hours']
    name = c.get('name', n)
    vid = slug(name)
    while vid in seen: vid += '-2'
    seen.add(vid)
    x, y = P(v['lat'], v['lon'])
    out.append(dict(id=vid, name=name, addr=v['addr'], cat=cat, food=bool(food), cuisine=cgroup(cuisine_raw) if food else None,
                    styles=styles, desc=c.get('desc', ''), hours=de_hours(hours), oh=parse_hours(hours),
                    lat=v['lat'], lon=v['lon'], web=v.get('web')))
for e in []:
    base = byname[e['near']]
    x, y = P(base['lat'], base['lon']); x += e['dx']; y += e['dy']
    lat = -y / KY + LAT0; lon = x / KX + LON0
    out.append(dict(id=slug(e['name']), name=e['name'], addr=e['addr'], cat=e['cat'], food=e['food'], cuisine=None, styles=e['styles'],
                    desc=e['desc'], hours=e['hours'], oh=None, lat=round(lat, 6), lon=round(lon, 6), web=None))

json.dump(out, open(os.path.join(D,'data','venues.json'), 'w'), ensure_ascii=False)
import collections
print(len(out), collections.Counter(v['cat'] for v in out), collections.Counter(v['cuisine'] for v in out if v['food']))
print('excluded', excluded)
unk = [v['name'] for v in out if v['oh'] is None]
print('hours unknown/unparsed:', len(unk), unk)
for v in out:
    if v['name'] in ('Transfer', 'Goldener Mond', 'Blaue Traube am Zollhaus', "Granny Mac's Irish Pub", 'Gionti', 'Herzstück', 'Basilikum', 'Veganoven'):
        print(v['name'], v['hours'], v['oh'])
