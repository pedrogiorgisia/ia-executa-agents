"""Test rapido: OpenRouter consegue gerar imagem boa pra IG?

Testa 3 modelos populares e mede qualidade + custo + velocidade.
"""
from __future__ import annotations
import base64
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "data" / "instagram" / "_openrouter-test"
OUT.mkdir(parents=True, exist_ok=True)

# Load .env
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ["OPENROUTER_API_KEY"]

PROMPT = (
    "Professional travel photography of Lisbon Portugal at golden hour. "
    "Famous yellow Tram 28 climbing a steep cobblestone street in Alfama neighborhood. "
    "Warm sunset light bathing pastel buildings in amber and pink tones. "
    "Cinematic atmosphere, shallow depth of field, shot on 35mm full-frame camera. "
    "Square 1:1 aspect ratio. Composition: tram on the lower-right third, leaving "
    "large negative space in the upper-left for text overlay. "
    "No people facing camera. No text in the image. High-end editorial quality."
)

# Modelos a testar - so os que fazem imagem
MODELS = [
    "google/gemini-2.5-flash-image",
]


def call_chat(model: str, prompt: str) -> tuple[float, dict]:
    """Chat completions com modalities=image - padrao da OpenRouter pra image models."""
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ia.executa",
            "X-Title": "PP-Travel Image Test",
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            elapsed = time.time() - t0
            return elapsed, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        elapsed = time.time() - t0
        return elapsed, {"error": e.read().decode()[:500]}


def extract_image(resp: dict, out_path: Path) -> bool:
    """OpenRouter retorna images em assistant message.images[].image_url.url (base64 data uri)."""
    if "error" in resp:
        print(f"  [ERROR resposta]: {resp['error'][:300]}")
        return False
    try:
        msg = resp["choices"][0]["message"]
        imgs = msg.get("images") or []
        for img in imgs:
            url = img.get("image_url", {}).get("url", "")
            if url.startswith("data:image"):
                b64 = url.split(",", 1)[1]
                out_path.write_bytes(base64.b64decode(b64))
                return True
        # Fallback: as vezes vem como content tipo list com image
        content = msg.get("content")
        if isinstance(content, list):
            for c in content:
                if c.get("type") == "image_url":
                    url = c.get("image_url", {}).get("url", "")
                    if url.startswith("data:image"):
                        out_path.write_bytes(base64.b64decode(url.split(",", 1)[1]))
                        return True
        print(f"  [FAIL] resposta sem imagem")
        print(f"  shape: keys={list(msg.keys())}, content type={type(content).__name__}")
        if isinstance(content, str):
            print(f"  content[:200]={content[:200]}")
        return False
    except (KeyError, IndexError) as e:
        print(f"  [FAIL parse] {e}")
        print(f"  resp keys: {list(resp.keys())}")
        return False


def main() -> None:
    for model in MODELS:
        print(f"\n=== {model} ===")
        elapsed, resp = call_chat(model, PROMPT)
        slug = model.replace("/", "_").replace(":", "_")
        out = OUT / f"{slug}.png"
        ok = extract_image(resp, out)
        if ok:
            print(f"  [ok] {out.name} ({out.stat().st_size:,} bytes, {elapsed:.1f}s)")
        else:
            print(f"  tempo: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
