# Kneipentour Erlangen – auf Cloudflare veröffentlichen

Die Seite läuft als Cloudflare Worker: Er liefert die Karte aus und leitet die KI-Planung an die
Claude API weiter. Dein API-Schlüssel liegt nur als Secret bei Cloudflare, nie im Browser.

## Einmalig einrichten (ca. 5 Minuten)

Voraussetzung: [Node.js](https://nodejs.org) ab Version 18.

```bash
cd kneipentour-cf
npm install
npx wrangler login                          # öffnet den Browser, mit deinem Cloudflare-Konto anmelden
npx wrangler secret put ANTHROPIC_API_KEY   # API-Schlüssel aus platform.claude.com einfügen
npx wrangler secret put FRIEND_CODE         # selbst ausgedachter Code für deine Freunde, z. B. "bergkirchweih"
npx wrangler deploy
```

Am Ende zeigt Wrangler die Adresse an, z. B. `https://kneipentour-erlangen.<dein-name>.workers.dev`.
Diesen Link schickst du deinen Freunden zusammen mit dem Freundes-Code.

## Gut zu wissen

- **Kosten:** Eine Routenplanung kostet mit `claude-sonnet-5-5` grob ein paar Cent. Für noch weniger
  in `wrangler.jsonc` `MODEL` auf `claude-haiku-5-5` stellen und neu deployen.
  Setz dir in der Claude Console ein Ausgabenlimit für den Schlüssel.
- **Schutz:** Ohne richtigen Freundes-Code geht nur die Schnellroute (ohne KI). Pro IP sind
  12 KI-Anfragen in 10 Minuten erlaubt.
- **Code ändern:** `npx wrangler secret put FRIEND_CODE` erneut ausführen, gilt sofort.
- **Eigene Domain:** im Cloudflare-Dashboard unter Workers → kneipentour-erlangen → Settings → Domains.
- **Lokal testen:** `npx wrangler dev` (Secrets dafür in eine Datei `.dev.vars` schreiben:
  `ANTHROPIC_API_KEY=...` und `FRIEND_CODE=...`).
- **Neue Version:** `public/index.html` austauschen und `npx wrangler deploy`.
- Ausblenden oder Hinzufügen von Lokalen gilt auf der gehosteten Seite nur für den jeweiligen Besuch.
- Kartendaten © OpenStreetMap-Mitwirkende (ODbL) – der Hinweis steht auf der Karte und muss bleiben.
