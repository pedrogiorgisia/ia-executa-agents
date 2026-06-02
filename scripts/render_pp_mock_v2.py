"""V2 - mock no estilo @pptravelinfinite real: foto full-bleed + texto overlay.

Saida: data/instagram/pp-travel-mocks-v2/<pilar>.png

Diferencas vs V1:
- Foto ocupa o quadrado INTEIRO (nao mais 35%/50%/15% em camadas)
- Texto overlay com tipografia Inter pesada (nao mais Playfair Display)
- Misturando peso normal + bold + italico nas mesmas palavras (estilo Editorial)
- Pílula branca com sub-headline (estilo "TOP 5 DESTINOS")
- "PP TRAVEL" pequeno no topo central, serifado
- Sem rodape navy - tudo overlaid sobre a foto

Photo fetch: Picsum (sem auth) ou path local pra placeholder. Quando Pexels/Gemini
estiver configurado, substitui em 1 linha.
"""
from __future__ import annotations
import asyncio
import base64
import urllib.request
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).parent.parent
OUT = ROOT / "data" / "instagram" / "pp-travel-mocks-v2"
PHOTOS = ROOT / "data" / "instagram" / "_placeholder-photos"
OUT.mkdir(parents=True, exist_ok=True)
PHOTOS.mkdir(parents=True, exist_ok=True)


def fetch_placeholder(seed: str) -> Path:
    """Baixa uma foto qualquer do Picsum (real, mas aleatoria) usando seed."""
    p = PHOTOS / f"{seed}.jpg"
    if p.exists():
        return p
    url = f"https://picsum.photos/seed/{seed}/1080/1080"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        p.write_bytes(r.read())
    return p


# 1 mock so pra validar o estilo - pilar Inspiração
MOCK = {
    "pilar": "inspiracao",
    "kicker": "Inspiração do dia",
    # Headline com 3 estilos no mesmo bloco (normal / bold / italico)
    "headline_html": (
        'Por que <strong>Lisboa</strong> em <em>outubro</em>'
        '<br>é a janela <strong>perfeita</strong>?'
    ),
    "sub_pill": "Spoiler: temperatura, preço e lotação",
    "photo_seed": "lisboa-outubro",
}


HTML_TPL = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Inter:ital,wght@0,400;0,500;0,700;0,800;0,900;1,400;1,500;1,700&display=swap');
* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  width: 1080px; height: 1080px;
  position: relative;
  overflow: hidden;
  font-family: 'Inter', system-ui, sans-serif;
}}

.bg {{
  position: absolute; inset: 0;
  background-image: url('data:image/{photo_mime};base64,{photo_b64}');
  background-size: cover;
  background-position: center;
}}

/* gradient escuro de baixo pra cima pro texto contrastar */
.bg::after {{
  content: "";
  position: absolute; inset: 0;
  background:
    linear-gradient(180deg, rgba(0,10,30,0.55) 0%, rgba(0,10,30,0.05) 30%, rgba(0,10,30,0.10) 50%, rgba(0,10,30,0.85) 100%),
    linear-gradient(90deg, rgba(0,10,30,0.35) 0%, rgba(0,10,30,0.05) 60%);
}}

/* Topo: PP TRAVEL pequeno centralizado */
.brand-top {{
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
}}

/* Centro: headline gigantesco */
.content {{
  position: absolute;
  left: 70px; right: 70px; bottom: 230px;
  z-index: 2;
  color: #ffffff;
}}

.kicker {{
  display: inline-block;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.32em;
  text-transform: uppercase;
  color: #fcd34d;
  margin-bottom: 24px;
  padding: 8px 16px;
  background: rgba(0,10,30,0.45);
  border-radius: 999px;
  backdrop-filter: blur(6px);
}}

.headline {{
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 74px;
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: #ffffff;
  text-shadow: 0 4px 18px rgba(0,0,0,0.5);
  margin-bottom: 32px;
}}
.headline strong {{ font-weight: 900; }}
.headline em {{ font-style: italic; font-weight: 500; }}

.pill {{
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
}}
.pill em {{ font-style: italic; color: #0a1a52; opacity: 0.85; }}

/* rodape micro: handle + hashtags */
.bottom {{
  position: absolute;
  left: 70px; right: 70px; bottom: 60px;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
}}
.handle {{
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 18px;
  color: rgba(255,255,255,0.85);
  letter-spacing: 0.06em;
}}
.swipe-hint {{
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 16px;
  color: rgba(255,255,255,0.6);
  letter-spacing: 0.08em;
}}
</style></head>
<body>
  <div class="bg"></div>
  <div class="brand-top">PP TRAVEL</div>
  <div class="content">
    <div class="kicker">{kicker}</div>
    <div class="headline">{headline_html}</div>
    <div class="pill">{sub_pill}</div>
  </div>
  <div class="bottom">
    <div class="handle">@pptravelinfinite</div>
    <div class="swipe-hint">arrasta &rarr;</div>
  </div>
</body></html>
"""


async def render() -> None:
    # Se a foto Gemini ja existe, usa ela em vez do Picsum placeholder
    gemini_photo = ROOT / "data" / "instagram" / "_openrouter-test" / "google_gemini-2.5-flash-image.png"
    if gemini_photo.exists():
        print(f"[1/3] usando foto Gemini existente: {gemini_photo.name}")
        photo = gemini_photo
    else:
        print(f"[1/3] baixando foto placeholder (Picsum, seed={MOCK['photo_seed']})...")
        photo = fetch_placeholder(MOCK["photo_seed"])
        print(f"  [ok] {photo.name}")

    photo_mime = "jpeg" if photo.suffix.lower() in (".jpg", ".jpeg") else "png"
    photo_b64 = base64.b64encode(photo.read_bytes()).decode("ascii")
    print(f"  [info] foto inline {len(photo_b64):,} chars base64 (mime: {photo_mime})")
    html = HTML_TPL.format(
        photo_mime=photo_mime,
        photo_b64=photo_b64,
        kicker=MOCK["kicker"],
        headline_html=MOCK["headline_html"],
        sub_pill=MOCK["sub_pill"],
    )

    print(f"[2/3] renderizando layout...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1080}, device_scale_factor=2)
        page = await ctx.new_page()
        await page.set_content(html, wait_until="networkidle")
        out = OUT / f"{MOCK['pilar']}-v2.png"
        await page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
        print(f"  [ok] {out}")
        await page.close()
        await browser.close()

    print(f"[3/3] pronto. Abre {out} pra ver")


if __name__ == "__main__":
    asyncio.run(render())
