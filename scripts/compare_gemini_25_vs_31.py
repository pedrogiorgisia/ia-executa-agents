"""Compara Gemini 2.5 Flash Image vs 3.1 Flash Image Preview - mesma prompt, lado a lado."""
from __future__ import annotations
import base64, json, os, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "data" / "instagram" / "_compare-25-vs-31"
OUT.mkdir(parents=True, exist_ok=True)

for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

KEY = os.environ["OPENROUTER_API_KEY"]

# Mesmo prompt nos 2 — destino que testa: detalhe, cor, atmosfera
PROMPT = (
    "Professional travel photography of Rio de Janeiro at golden hour: "
    "view of Sugarloaf Mountain (Pão de Açúcar) from Copacabana beach, "
    "warm sunset light, cinematic atmosphere, shallow depth of field, "
    "shot on full-frame camera with 35mm lens. Square 1:1 aspect ratio. "
    "Composition: mountain on the right third, leaving large negative space "
    "on the upper-left for text overlay. No people facing camera. No text "
    "in the image. High-end editorial travel magazine quality."
)


def call(model: str) -> tuple[float, bytes | None, str | None]:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "modalities": ["image", "text"],
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ia.executa",
            "X-Title": "Gemini Compare",
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return time.time() - t0, None, f"{e.code}: {e.read().decode()[:300]}"
    elapsed = time.time() - t0
    try:
        msg = resp["choices"][0]["message"]
        for img in (msg.get("images") or []):
            url = img.get("image_url", {}).get("url", "")
            if url.startswith("data:image"):
                return elapsed, base64.b64decode(url.split(",", 1)[1]), None
        return elapsed, None, f"no image in response: keys={list(msg.keys())}"
    except Exception as e:
        return elapsed, None, f"parse error: {e}"


for model, slug in [
    ("google/gemini-2.5-flash-image", "25"),
    ("google/gemini-3.1-flash-image-preview", "31"),
]:
    print(f"\n=== {model} ===")
    elapsed, img, err = call(model)
    if img:
        out = OUT / f"rio-{slug}.png"
        out.write_bytes(img)
        print(f"  [ok] {out.name} ({len(img):,} bytes, {elapsed:.1f}s)")
    else:
        print(f"  [FAIL {elapsed:.1f}s] {err}")
