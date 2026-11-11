# Kneipentour Erlangen

Interaktive Karte der Erlanger Innenstadt mit KI-Routenplanung für Kneipentouren.
Live über Cloudflare Workers; jeder Push auf `main` wird automatisch veröffentlicht.

## Aufbau
- `public/index.html` – die fertige Seite (wird generiert, nicht von Hand bearbeiten)
- `src/worker.js` – Worker: liefert die Seite aus, `/api/plan` leitet an die Claude API weiter
  (Secrets `ANTHROPIC_API_KEY`, `FRIEND_CODE` liegen bei Cloudflare)
- `tools/template.html` – Quelltext der Seite (HTML/CSS/JS), Platzhalter für Karten- und Lokaldaten
- `tools/enrich.py` – Lokalliste: Ausschlüsse (`EXCLUDE`), eigene Angaben (`CURATED`: Name, Art,
  Stil, Beschreibung, Öffnungszeiten im OSM-Format), Cafés mit Abendbetrieb (`CAFE_KEEP`)
- `tools/extract.py`, `tools/graph.py` – lesen den OSM-Export (`tools/data/map.osm.gz`)

## Änderungen
- Lokal-Daten ändern: `tools/enrich.py` anpassen, dann `python3 tools/enrich.py && python3 tools/build.py`
- Seite/Design ändern: `tools/template.html` anpassen, dann `python3 tools/build.py`
- Neuer OSM-Export: nach `tools/data/map.osm` entpacken bzw. ablegen, dann
  `python3 tools/extract.py && python3 tools/graph.py && python3 tools/enrich.py && python3 tools/build.py`
- Danach committen und auf `main` pushen.

Kartendaten © OpenStreetMap-Mitwirkende (ODbL) – Hinweis auf der Karte muss bleiben.
