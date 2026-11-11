// Kneipentour Erlangen – Cloudflare Worker
// Liefert die Seite aus /public aus und leitet KI-Anfragen sicher an die Claude API weiter.
// Der API-Schlüssel bleibt als Secret auf dem Server und erreicht nie den Browser.

const SYSTEM = `Du bist ein ortskundiger Erlanger Nachtleben-Guide. Du planst ausschließlich Kneipentouren
für die Seite „Kneipentour Erlangen“ und antwortest nur mit dem angeforderten JSON. Anfragen, die nichts
mit der Tourplanung zu tun haben, beantwortest du mit {"error":"nur Tourplanung"}.`;

const MAX_PROMPT = 60000;       // Zeichen
const LIMIT = 12;               // Anfragen …
const WINDOW_MS = 10 * 60e3;    // … pro 10 Minuten und IP (pro Worker-Instanz)
const hits = new Map();

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

function rateLimited(ip) {
  const now = Date.now();
  const list = (hits.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  list.push(now);
  hits.set(ip, list);
  if (hits.size > 5000) hits.clear();
  return list.length > LIMIT;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/health") {
      return json({ ok: Boolean(env.ANTHROPIC_API_KEY), code: Boolean(env.FRIEND_CODE) });
    }

    if (url.pathname === "/api/plan") {
      if (request.method !== "POST") return json({ error: "method" }, 405);
      if (!env.ANTHROPIC_API_KEY) return json({ error: "Kein API-Schlüssel hinterlegt" }, 503);
      if (env.FRIEND_CODE && request.headers.get("x-friend-code") !== env.FRIEND_CODE) {
        return json({ error: "code" }, 401);
      }
      const ip = request.headers.get("cf-connecting-ip") || "unknown";
      if (rateLimited(ip)) return json({ error: "Zu viele Anfragen" }, 429);

      let prompt;
      try {
        ({ prompt } = await request.json());
      } catch {
        return json({ error: "bad request" }, 400);
      }
      if (typeof prompt !== "string" || !prompt.includes("Kneipentour") || prompt.length > MAX_PROMPT) {
        return json({ error: "bad request" }, 400);
      }

      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": env.ANTHROPIC_API_KEY,
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model: env.MODEL || "claude-sonnet-5-5",
          // Sonnet/Haiku 5.5 denken standardmäßig nach; das zählt zu max_tokens.
          // Genug Platz für Nachdenken + Antwort lassen, Aufwand auf "medium" begrenzen.
          max_tokens: Number(env.MAX_TOKENS) || 12000,
          output_config: { effort: env.EFFORT || "medium" },
          system: SYSTEM,
          messages: [{ role: "user", content: prompt }],
        }),
      });
      if (!res.ok) {
        const detail = await res.text();
        console.log("Claude API error", res.status, detail.slice(0, 500));
        return json({ error: "Claude API " + res.status }, 502);
      }
      const data = await res.json();
      const text = (data.content || []).filter((b) => b.type === "text").map((b) => b.text).join("");
      if (data.stop_reason === "max_tokens") console.log("Antwort abgeschnitten (max_tokens)", data.usage);
      return json({ text, stop_reason: data.stop_reason });
    }

    // alles andere: statische Seite
    return env.ASSETS.fetch(request);
  },
};
