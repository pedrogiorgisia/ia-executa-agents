"""Render carrossel multi-slide (Educacao + Prova Social).

Aceita content.json com schema:
  {
    "formato": "carousel_educational" | "carousel_storytelling",
    "slides": [
      {"kicker": "...", "headline_html": "...", "body": "...", "photo_prompt": "..."},
      {"headline_html": "...", "body": "..."},
      ...
    ]
  }

Cada slide vira 1 PNG 1080x1080. Saida: post-slide-N.png na pasta do dia.
"""
from __future__ import annotations
import asyncio
import base64
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).parent.parent

for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

OR_KEY = os.environ["OPENROUTER_API_KEY"]


def gen_photo(prompt: str, out: Path) -> Path:
    body = json.dumps({
        "model": "google/gemini-3.1-flash-image-preview",
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {OR_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ia.executa",
            "X-Title": "PP-Travel Carousel",
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Gemini {e.code}: {e.read().decode()[:300]}")
    msg = resp["choices"][0]["message"]
    for img in (msg.get("images") or []):
        url = img.get("image_url", {}).get("url", "")
        if url.startswith("data:image"):
            out.write_bytes(base64.b64decode(url.split(",", 1)[1]))
            print(f"  [photo] {out.name} ({out.stat().st_size:,} bytes, {time.time()-t0:.1f}s)")
            return out
    raise RuntimeError("sem imagem na resposta Gemini")


# Template do slide do carrossel
# - Slide 1 (capa): igual V2 single photo
# - Slides 2-N: foto top 50% + bloco navy bottom 50% com texto + indicador slide N/total
SLIDE_TPL = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Inter:ital,wght@0,400;0,500;0,700;0,800;0,900;1,400;1,500;1,700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1080px; height: 1080px; position: relative; overflow: hidden; font-family: 'Inter', sans-serif; background: #0a1a52; }
.bg { position: absolute; top: 0; left: 0; right: 0; height: 540px; background-image: url('data:image/__MIME__;base64,__B64__'); background-size: cover; background-position: center; }
.bg::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,10,30,0.10) 0%, rgba(10,26,82,0.40) 70%, rgba(10,26,82,1) 100%); }
.brand-top { position: absolute; top: 30px; left: 0; right: 0; text-align: center; font-family: 'Playfair Display', serif; font-weight: 500; font-size: 22px; letter-spacing: 0.32em; color: #fff; text-shadow: 0 2px 12px rgba(0,0,0,0.5); z-index: 2; }
.body-block { position: absolute; top: 540px; left: 0; right: 0; bottom: 0; padding: 60px 70px 100px; color: #fff; }
.kicker { display: inline-block; font-size: 13px; font-weight: 700; letter-spacing: 0.28em; text-transform: uppercase; color: #c9a961; margin-bottom: 24px; padding: 6px 14px; background: rgba(255,255,255,0.08); border-radius: 999px; }
.slide-headline { font-family: 'Playfair Display', serif; font-weight: 800; font-size: 48px; line-height: 1.1; letter-spacing: -0.01em; color: #c9a961; margin-bottom: 24px; }
.slide-headline strong { font-weight: 900; }
.slide-headline em { font-style: italic; font-weight: 700; }
.slide-body { font-family: 'Inter', sans-serif; font-size: 22px; line-height: 1.5; color: rgba(255,255,255,0.92); max-width: 920px; }
.slide-indicator { position: absolute; bottom: 30px; right: 70px; font-size: 14px; font-weight: 700; color: rgba(255,255,255,0.6); letter-spacing: 0.1em; }
.handle { position: absolute; bottom: 30px; left: 70px; font-size: 14px; font-weight: 700; color: rgba(255,255,255,0.65); letter-spacing: 0.08em; }
</style></head>
<body>
  <div class="bg"></div>
  <div class="brand-top">PP TRAVEL</div>
  <div class="body-block">
    __KICKER_BLOCK__
    <div class="slide-headline">__HEADLINE__</div>
    <div class="slide-body">__BODY__</div>
  </div>
  <div class="handle">@pptravelinfinite</div>
  <div class="slide-indicator">__INDICATOR__</div>
</body></html>
"""


async def render_slides(content: dict, out_dir: Path) -> list[Path]:
    slides = content["slides"]
    total = len(slides)
    print(f"[render] {total} slides")

    # 1. Gera/cacheia fotos
    photos: list[Path] = []
    for i, s in enumerate(slides, 1):
        photo_path = out_dir / f"foto-slide-{i}.png"
        if photo_path.exists():
            print(f"  [cache] slide {i}: usando {photo_path.name}")
        elif s.get("photo_prompt"):
            gen_photo(s["photo_prompt"], photo_path)
        else:
            # Reusa foto do slide anterior (carrossel pode ter 1 foto comum)
            if photos:
                photo_path = photos[-1]
                print(f"  [reuse] slide {i}: reusa foto do slide {i-1}")
            else:
                raise RuntimeError(f"slide {i} sem photo_prompt e sem fallback")
        photos.append(photo_path)

    # 2. Render cada slide
    out_pngs: list[Path] = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1080}, device_scale_factor=2)
        for i, (slide, photo) in enumerate(zip(slides, photos), 1):
            mime = "jpeg" if photo.suffix.lower() in (".jpg", ".jpeg") else "png"
            b64 = base64.b64encode(photo.read_bytes()).decode("ascii")
            kicker = slide.get("kicker", "")
            kicker_block = f'<div class="kicker">{kicker}</div>' if kicker else ""
            html = (SLIDE_TPL
                .replace("__MIME__", mime).replace("__B64__", b64)
                .replace("__KICKER_BLOCK__", kicker_block)
                .replace("__HEADLINE__", slide.get("headline_html", ""))
                .replace("__BODY__", slide.get("body", ""))
                .replace("__INDICATOR__", f"{i} / {total}"))

            page = await ctx.new_page()
            await page.set_content(html, wait_until="networkidle")
            out = out_dir / f"post-slide-{i}.png"
            await page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
            await page.close()
            print(f"  [slide {i}/{total}] {out.name}")
            out_pngs.append(out)
        await browser.close()
    return out_pngs


def main():
    if len(sys.argv) < 2:
        print("Uso: python render_carousel.py <content.json>")
        sys.exit(1)
    content_path = Path(sys.argv[1])
    content = json.loads(content_path.read_text(encoding="utf-8"))
    out_dir = content_path.parent
    out_pngs = asyncio.run(render_slides(content, out_dir))
    print(f"\n[done] {len(out_pngs)} slides em {out_dir}")


if __name__ == "__main__":
    main()
