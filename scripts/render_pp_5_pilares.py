"""Gera os 5 mocks finais da PP-Travel (1 por pilar) com foto Gemini + texto overlay.

Para cada pilar:
1. Se a foto Gemini ainda nao existe, gera via OpenRouter (~6s)
2. Renderiza o mock V2 (foto full-bleed + texto overlay) -> PNG 1080x1080

Saida: data/instagram/pp-travel-mocks-v2/<pilar>.png
"""
from __future__ import annotations
import asyncio
import base64
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).parent.parent
OUT = ROOT / "data" / "instagram" / "pp-travel-mocks-v2"
PHOTOS = ROOT / "data" / "instagram" / "_gemini-photos"
OUT.mkdir(parents=True, exist_ok=True)
PHOTOS.mkdir(parents=True, exist_ok=True)

# Load .env
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

OPENROUTER_KEY = os.environ["OPENROUTER_API_KEY"]
IMAGE_MODEL = "google/gemini-2.5-flash-image"


# Os 5 mocks - 1 por pilar
PILARES = [
    {
        "pilar": "educacao",
        "kicker": "Dúvida frequente",
        "headline_html": (
            'Como a gente <strong>consegue</strong> um preço '
            '<em>menor</em> que o da <strong>cia aérea</strong>?'
        ),
        "sub_pill": "Resposta: intermediamos compra e venda de milhas",
        "gemini_prompt": (
            "Professional travel photography: interior of a commercial aircraft cabin, "
            "view from a window seat looking outside at clouds and sunset sky. "
            "Warm golden hour light coming through the airplane window, soft reflections. "
            "Cinematic mood, shallow depth of field, shot on full-frame camera with 35mm lens. "
            "Square 1:1 aspect ratio. Composition: window on the right two-thirds, "
            "leaving large negative space on the left for text overlay. "
            "No people visible. No text in the image. High-end editorial quality, "
            "subtle atmospheric haze for premium feel."
        ),
    },
    {
        "pilar": "inspiracao",
        "kicker": "Inspiração do dia",
        "headline_html": (
            'Por que <strong>Lisboa</strong> em <em>outubro</em>'
            '<br>é a janela <strong>perfeita</strong>?'
        ),
        "sub_pill": "Spoiler: temperatura, preço e lotação",
        "gemini_prompt": (
            "Professional travel photography of Lisbon Portugal at golden hour. "
            "Famous yellow Tram 28 climbing a steep cobblestone street in Alfama. "
            "Warm sunset light bathing pastel buildings in amber and pink tones. "
            "Cinematic atmosphere, shallow depth of field. Square 1:1 aspect ratio. "
            "Composition: tram on the lower-right third, leaving large negative space "
            "in the upper-left for text overlay. No people facing camera. "
            "No text in the image. High-end editorial quality."
        ),
    },
    {
        "pilar": "engajamento",
        "kicker": "Comenta aí",
        "headline_html": (
            '<strong>Praia</strong> ou <em>montanha</em>?'
            '<br>O <strong>próximo destino</strong> sai daqui.'
        ),
        "sub_pill": "🏖️ pra praia · 🏔️ pra montanha (a mais votada vira promo)",
        "gemini_prompt": (
            "Professional travel photography: split-composition image showing on one side "
            "a tropical paradise beach with turquoise water and palm trees at sunset, "
            "and on the other side snow-capped mountain peaks at dawn with golden alpenglow. "
            "Subtle vertical seam in the middle, both halves equally beautiful and dramatic. "
            "Cinematic, editorial style. Square 1:1 aspect ratio. "
            "Composition: scene fills the lower 60% of the frame, leaving generous negative "
            "space at the top for text overlay. No people visible. No text in the image."
        ),
    },
    {
        "pilar": "prova_social",
        "kicker": "Cliente real",
        "headline_html": (
            '<em>"Economizei</em> <strong>R$ 4.200</strong>'
            '<br>voando pra Lisboa em <strong>junho</strong><em>"</em>'
        ),
        "sub_pill": "Ana, cliente desde 2024 — mesmo voo, metade do preço",
        "gemini_prompt": (
            "Professional travel photography: a happy couple at an international airport "
            "departure hall, hugging or smiling together, with travel suitcases visible. "
            "They are facing slightly away from camera (3/4 view from behind), looking at "
            "a large window with airplanes outside or a departures board. Warm cinematic "
            "lighting, natural and authentic moment. Shot on 35mm lens, shallow depth of field. "
            "Square 1:1 aspect ratio. Composition: subjects on the lower-right third, "
            "large negative space upper-left for text overlay. No faces directly visible. "
            "No text in the image. Editorial quality."
        ),
    },
    {
        "pilar": "conversao",
        "kicker": "Promo · Janela curta",
        "headline_html": (
            '<strong>Miami</strong> ida e volta'
            '<br>a partir de <strong>R$ 1.998</strong> <em>(42% off)</em>'
        ),
        "sub_pill": "Saindo do Rio · janeiro · só até domingo",
        "gemini_prompt": (
            "Professional travel photography of Miami Florida at twilight blue hour. "
            "Iconic South Beach skyline with art-deco neon-lit pastel buildings, "
            "palm tree silhouettes in the foreground, atmospheric pink-purple sky. "
            "Cinematic, vibrant but not overdone, premium editorial style. "
            "Square 1:1 aspect ratio. Composition: skyline fills the lower 50%, "
            "leaving large negative space at the top for text overlay. "
            "No people visible. No text or logos in the image. High-end quality."
        ),
    },
]


def gen_gemini_photo(prompt: str, out_path: Path) -> bool:
    """Gera uma foto via OpenRouter -> Gemini 2.5 Flash Image. Cacheado por arquivo."""
    if out_path.exists():
        print(f"  [cache] {out_path.name} ja existe ({out_path.stat().st_size:,} bytes)")
        return True
    body = json.dumps({
        "model": IMAGE_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ia.executa",
            "X-Title": "PP-Travel mocks",
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  [ERROR] {e.code}: {e.read().decode()[:300]}")
        return False
    elapsed = time.time() - t0
    msg = resp["choices"][0]["message"]
    imgs = msg.get("images") or []
    for img in imgs:
        url = img.get("image_url", {}).get("url", "")
        if url.startswith("data:image"):
            out_path.write_bytes(base64.b64decode(url.split(",", 1)[1]))
            print(f"  [ok] {out_path.name} ({out_path.stat().st_size:,} bytes, {elapsed:.1f}s)")
            return True
    print(f"  [FAIL] sem imagem na resposta")
    return False


HTML_TPL = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Inter:ital,wght@0,400;0,500;0,700;0,800;0,900;1,400;1,500;1,700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  width: 1080px; height: 1080px;
  position: relative;
  overflow: hidden;
  font-family: 'Inter', system-ui, sans-serif;
}

.bg {
  position: absolute; inset: 0;
  background-image: url('data:image/__MIME__;base64,__B64__');
  background-size: cover;
  background-position: center;
}

.bg::after {
  content: "";
  position: absolute; inset: 0;
  background:
    linear-gradient(180deg, rgba(0,10,30,0.55) 0%, rgba(0,10,30,0.05) 30%, rgba(0,10,30,0.10) 50%, rgba(0,10,30,0.85) 100%),
    linear-gradient(90deg, rgba(0,10,30,0.35) 0%, rgba(0,10,30,0.05) 60%);
}

.brand-top {
  position: absolute;
  top: 50px; left: 0; right: 0;
  text-align: center;
  font-family: 'Playfair Display', serif;
  font-weight: 500;
  font-size: 26px;
  letter-spacing: 0.32em;
  color: #ffffff;
  text-shadow: 0 2px 12px rgba(0,0,0,0.5);
  z-index: 2;
}

.content {
  position: absolute;
  left: 70px; right: 70px; bottom: 230px;
  z-index: 2;
  color: #ffffff;
}

.kicker {
  display: inline-block;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: #fcd34d;
  margin-bottom: 24px;
  padding: 8px 16px;
  background: rgba(0,10,30,0.45);
  border-radius: 999px;
  backdrop-filter: blur(6px);
}

.headline {
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 70px;
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: #ffffff;
  text-shadow: 0 4px 18px rgba(0,0,0,0.5);
  margin-bottom: 32px;
}
.headline strong { font-weight: 900; }
.headline em { font-style: italic; font-weight: 500; }

.pill {
  display: inline-block;
  background: #ffffff;
  color: #0a1a52;
  padding: 16px 26px;
  border-radius: 12px;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 22px;
  letter-spacing: 0.02em;
  box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}
.pill em { font-style: italic; color: #0a1a52; opacity: 0.85; }

.bottom {
  position: absolute;
  left: 70px; right: 70px; bottom: 60px;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.handle {
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 18px;
  color: rgba(255,255,255,0.85);
  letter-spacing: 0.06em;
}
.swipe-hint {
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 16px;
  color: rgba(255,255,255,0.6);
  letter-spacing: 0.08em;
}
</style></head>
<body>
  <div class="bg"></div>
  <div class="brand-top">PP TRAVEL</div>
  <div class="content">
    <div class="kicker">__KICKER__</div>
    <div class="headline">__HEADLINE__</div>
    <div class="pill">__PILL__</div>
  </div>
  <div class="bottom">
    <div class="handle">@pptravelinfinite</div>
    <div class="swipe-hint">arrasta &rarr;</div>
  </div>
</body></html>
"""


def build_html(photo: Path, kicker: str, headline_html: str, sub_pill: str) -> str:
    mime = "jpeg" if photo.suffix.lower() in (".jpg", ".jpeg") else "png"
    b64 = base64.b64encode(photo.read_bytes()).decode("ascii")
    return (
        HTML_TPL
        .replace("__MIME__", mime)
        .replace("__B64__", b64)
        .replace("__KICKER__", kicker)
        .replace("__HEADLINE__", headline_html)
        .replace("__PILL__", sub_pill)
    )


async def render_all() -> None:
    print(f"[fase 1] gerando {len(PILARES)} fotos Gemini\n")
    photos: dict[str, Path] = {}
    for p in PILARES:
        print(f"--- {p['pilar']} ---")
        path = PHOTOS / f"{p['pilar']}.png"
        ok = gen_gemini_photo(p["gemini_prompt"], path)
        if ok:
            photos[p["pilar"]] = path
        else:
            print(f"  pulando render de {p['pilar']}")
        print()

    print(f"\n[fase 2] renderizando {len(photos)} mocks\n")
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1080}, device_scale_factor=2)
        for p in PILARES:
            if p["pilar"] not in photos:
                continue
            html = build_html(photos[p["pilar"]], p["kicker"], p["headline_html"], p["sub_pill"])
            page = await ctx.new_page()
            await page.set_content(html, wait_until="networkidle")
            out = OUT / f"{p['pilar']}.png"
            await page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
            print(f"  [ok] {out.name}")
            await page.close()
        await browser.close()

    print(f"\n[fim] mocks em {OUT}")


if __name__ == "__main__":
    asyncio.run(render_all())
