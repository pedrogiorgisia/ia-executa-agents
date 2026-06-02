"""Teste: Grok 4.3 via OpenRouter consegue fazer Live Search em X (Twitter)?

3 variantes:
  A) sem search          (baseline — Grok responde do que sabe)
  B) +plugin web         (search generico do OpenRouter)
  C) +search_parameters  (xAI nativo, fonte X — o que queremos)
"""
from __future__ import annotations
import json, os, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = "x-ai/grok-4.3"

QUERY = (
    "Liste 5 tweets recentes (últimas 24h) em português sobre LATAM, GOL, AZUL "
    "ou programas de milhas (Smiles, Latam Pass, TudoAzul). Foque em: promoções, "
    "polêmicas, mudanças de regra, viagens virais. Para cada tweet: "
    "(1) autor/username, (2) texto resumido, (3) engagement aprox, (4) link do tweet. "
    "Resposta em markdown lista."
)


def call(label: str, payload_extra: dict) -> None:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": QUERY}],
        **payload_extra,
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ia.executa",
            "X-Title": "Grok Live Search",
        },
        method="POST",
    )
    print(f"\n========== {label} ==========")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {e.read().decode()[:400]}")
        return
    elapsed = time.time() - t0
    msg = resp["choices"][0]["message"]
    content = msg.get("content") or ""
    usage = resp.get("usage", {})
    print(f"[{elapsed:.1f}s] tokens in={usage.get('prompt_tokens')} out={usage.get('completion_tokens')} cost={usage.get('cost_usd', usage.get('total_cost', 'n/a'))}")
    annotations = msg.get("annotations") or []
    print(f"annotations: {len(annotations)} sources")
    for a in annotations[:5]:
        print(f"  - {a.get('type', '?')}: {str(a)[:160]}")
    print(f"\n--- content (primeiros 2200 chars) ---")
    print(content[:2200])
    print(f"\n--- fim ({len(content)} chars total) ---")


# A — sem search
call("A) Sem search (baseline)", {})

# B — plugin web do OpenRouter
call("B) +plugin web OpenRouter", {"plugins": [{"id": "web", "max_results": 10}]})

# C — search_parameters nativo xAI (X source)
call("C) +search_parameters xAI (X source)", {
    "search_parameters": {
        "mode": "on",
        "sources": [{"type": "x"}],
        "max_search_results": 10,
        "return_citations": True,
    }
})
