"""Renderiza 5 slides do post manifesto pro Instagram do @ia.executa.

Saida: data/instagram/test-manifesto/slide-N.png (1080x1080)
"""
from __future__ import annotations
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

OUT_DIR = Path(__file__).parent.parent / "data" / "instagram" / "test-manifesto"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Paleta da landing (00-posicionamento + index.html da landing)
BG = "#0a0a0d"
SURFACE = "#14141a"
GOLD = "#e0b87a"
GOLD_DARK = "#c79d50"
TEXT = "#fdfcfb"
MUTED = "#a19fad"
GREEN = "#2dd4bf"

# Cada slide: (kicker opcional, main_html, footer_html opcional)
SLIDES = [
    {
        "kicker": "manifesto",
        "main": '<span class="line">IA não vai</span><span class="line">te <em>substituir</em>.</span>',
        "footer": '<div class="swipe">→ desliza</div>',
    },
    {
        "kicker": "",
        "main": '<span class="line">Vai substituir</span><span class="line">quem <em>não usa</em>.</span>',
        "footer": "",
    },
    {
        "kicker": "",
        "main": '<span class="line">Se você é</span><span class="line">gestor não-técnico,</span><span class="line gap">você já tá <em>atrasado</em>.</span>',
        "footer": "",
    },
    {
        "kicker": "",
        "main": '<span class="line muted">Mas não é pra correr.</span><span class="line gap">É pra parar de</span><span class="line">ficar <em>pra trás</em>.</span>',
        "footer": "",
    },
    {
        "kicker": "próxima turma",
        "main": '<span class="line cta-h">Mentoria IA</span><span class="line cta-h">com <em>Claude Code</em></span><span class="line cta-sub">Turma de 5 · 3 encontros</span>',
        "footer": '<div class="cta-bar">Link na bio →</div>',
    },
]

HTML_TPL = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  width: 1080px;
  height: 1080px;
  background: {bg};
  color: {text};
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 80px 96px;
  position: relative;
  overflow: hidden;
}}

/* Sutil radial pra dar profundidade */
body::before {{
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 35%, rgba(224,184,122,0.06) 0%, transparent 55%);
  pointer-events: none;
}}

/* Borda dourada na esquerda — assinatura visual */
body::after {{
  content: "";
  position: absolute;
  left: 0; top: 12%; bottom: 12%;
  width: 4px;
  background: linear-gradient(180deg, transparent 0%, {gold} 30%, {gold} 70%, transparent 100%);
}}

.kicker {{
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.32em;
  text-transform: uppercase;
  color: {gold};
  opacity: 0.9;
  z-index: 1;
}}

.main {{
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex: 1;
  margin-top: 40px;
  margin-bottom: 40px;
  z-index: 1;
}}

.line {{
  font-size: 96px;
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: {text};
  display: block;
}}

.line.muted {{ color: {muted}; font-weight: 500; font-size: 64px; }}
.line.gap {{ margin-top: 24px; }}

em {{
  font-style: normal;
  color: {gold};
}}

.cta-h {{ font-size: 80px; font-weight: 800; }}
.cta-sub {{
  font-size: 36px;
  font-weight: 500;
  color: {muted};
  margin-top: 32px;
  letter-spacing: 0.02em;
}}

.footer {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 1;
}}

.brand {{
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: {text};
}}
.brand .at {{ color: {gold}; }}

.swipe {{
  font-size: 20px;
  font-weight: 500;
  color: {muted};
  letter-spacing: 0.04em;
}}

.cta-bar {{
  background: {green};
  color: {bg};
  font-weight: 800;
  font-size: 22px;
  letter-spacing: 0.06em;
  padding: 14px 28px;
  border-radius: 999px;
}}

.dots {{
  display: flex;
  gap: 8px;
}}
.dot {{
  width: 8px; height: 8px;
  border-radius: 50%;
  background: {muted};
  opacity: 0.35;
}}
.dot.on {{ background: {gold}; opacity: 1; }}
</style>
</head>
<body>
  <div class="kicker">{kicker}</div>
  <div class="main">{main}</div>
  <div class="footer">
    <div class="brand"><span class="at">@</span>ia.executa</div>
    <div class="footer-right">{footer}</div>
  </div>
</body>
</html>
"""


async def render() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1080}, device_scale_factor=2)
        for i, s in enumerate(SLIDES, start=1):
            html = HTML_TPL.format(
                bg=BG, text=TEXT, gold=GOLD, muted=MUTED, green=GREEN,
                kicker=s["kicker"] or "&nbsp;",
                main=s["main"],
                footer=s["footer"],
            )
            page = await ctx.new_page()
            await page.set_content(html, wait_until="networkidle")
            out = OUT_DIR / f"slide-{i}.png"
            await page.screenshot(path=str(out), full_page=False, clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
            print(f"  [ok] {out.name}")
            await page.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(render())
    print(f"\nSlides em: {OUT_DIR}")
