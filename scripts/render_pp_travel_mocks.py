"""Renderiza 5 mocks da PP-Travel (1 por pilar) pro Pedro validar o visual.

Saida: data/instagram/pp-travel-mocks/<pilar>.png  (1080x1080)

Paleta da PP-Travel:
- Azul-marinho: #0a1a52
- Azul-marinho escuro (rodape): #061238
- Dourado: #c9a961
- Branco off: #fafaf2

Templates:
- card  (educacao/inspiracao/engajamento/prova_social): foto top 35% / navy center 50% / logo 15%
- promo (conversao): foto top 70% / cta branco 30% + badge OFF
"""
from __future__ import annotations
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

OUT_DIR = Path(__file__).parent.parent / "data" / "instagram" / "pp-travel-mocks"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand
NAVY = "#0a1a52"
NAVY_DARK = "#061238"
GOLD = "#c9a961"
GOLD_LIGHT = "#e0c98a"
TEXT = "#fafaf2"
TEXT_MUTED = "#c2c0b6"
PROMO_YELLOW = "#fcd34d"

# 5 mocks — uma por pilar
MOCKS = [
    {
        "pilar": "educacao",
        "template": "card",
        "kicker": "Duvidas frequentes",
        "title": "Como conseguem um preco mais barato que a propria companhia aerea?",
        "body": "Nos intermediamos a compra e venda de milhas. Voce voa pela mesma cia, mesma poltrona, mas paga ate 47% menos.",
        "destino_emoji": "✈️",
        "destino_nome": "Lisboa · Portugal",
        "photo_gradient": "linear-gradient(135deg, #ff9a56 0%, #ff6a88 50%, #6a4c93 100%)",
    },
    {
        "pilar": "inspiracao",
        "template": "card",
        "kicker": "Inspiracao do dia",
        "title": "Maldivas em outubro: 7 dias em bangalo sobre a agua",
        "body": "Janela perfeita: baixa temporada, mar 28C, ceu limpo. Saindo de Sao Paulo via Doha por 95k milhas Smiles.",
        "destino_emoji": "🏝️",
        "destino_nome": "Maldivas",
        "photo_gradient": "linear-gradient(135deg, #00c9ff 0%, #92fe9d 50%, #38bdf8 100%)",
    },
    {
        "pilar": "engajamento",
        "template": "card",
        "kicker": "Comenta ai",
        "title": "Praia ou montanha?",
        "body": "Vota no comentario: 🏖️ pra praia · 🏔️ pra montanha. A opcao mais votada vira nosso proximo roteiro de promo.",
        "destino_emoji": "🤔",
        "destino_nome": "Voce decide",
        "photo_gradient": "linear-gradient(135deg, #fbbf24 0%, #38bdf8 50%, #a78bfa 100%)",
    },
    {
        "pilar": "prova_social",
        "template": "card",
        "kicker": "Cliente da PP",
        "title": "\"Economizei R$ 4.200 voando pra Lisboa em junho\"",
        "body": "Ana, cliente desde 2024. Comprou no balcao da Latam por R$ 8.700. Atraves da PP, mesma poltrona, mesmo voo: R$ 4.500.",
        "destino_emoji": "💬",
        "destino_nome": "Depoimento real",
        "photo_gradient": "linear-gradient(135deg, #f59e0b 0%, #ec4899 50%, #8b5cf6 100%)",
    },
    {
        "pilar": "conversao",
        "template": "promo",
        "destino_titulo": "Miami",
        "destino_sub": "Rio de Janeiro · ida e volta",
        "preco_label": "A partir de",
        "preco_principal": "R$ 1.998",
        "preco_parc": "ou 6x de R$ 333",
        "badge_off": "42% OFF",
        "data_badge": "JAN 2026",
        "cta": "RESERVE JA!",
        "photo_gradient": "linear-gradient(135deg, #06b6d4 0%, #f472b6 50%, #fbbf24 100%)",
        "destino_emoji": "🌴",
    },
]


# =========== TEMPLATES HTML ===========

CARD_TPL = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  width: 1080px; height: 1080px;
  background: {navy};
  color: {text};
  font-family: 'Inter', system-ui, sans-serif;
  display: flex; flex-direction: column;
  overflow: hidden;
}}
/* TOPO 35% = foto (placeholder gradient) */
.photo {{
  height: 378px;
  background: {photo_gradient};
  position: relative;
  display: flex; align-items: center; justify-content: center;
}}
.photo::after {{
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 60%, {navy} 100%);
}}
.dest-overlay {{
  position: absolute;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 18px;
  background: rgba(6,18,56,0.7);
  padding: 14px 24px;
  border-radius: 999px;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(201,169,97,0.4);
}}
.dest-overlay .emoji {{ font-size: 32px; }}
.dest-overlay .name {{
  font-family: 'Playfair Display', serif;
  font-size: 22px;
  font-weight: 600;
  color: {text};
  letter-spacing: 0.02em;
}}
/* CENTRO 50% = bloco navy com texto */
.card {{
  flex: 1;
  padding: 70px 88px 50px 88px;
  display: flex; flex-direction: column;
  justify-content: center;
}}
.kicker {{
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.32em;
  text-transform: uppercase;
  color: {gold};
  margin-bottom: 28px;
}}
.title {{
  font-family: 'Playfair Display', serif;
  font-weight: 800;
  font-size: 56px;
  line-height: 1.08;
  color: {gold};
  letter-spacing: -0.01em;
  margin-bottom: 28px;
}}
.body {{
  font-family: 'Inter', sans-serif;
  font-size: 26px;
  font-weight: 400;
  line-height: 1.5;
  color: {text};
  max-width: 880px;
}}
/* BASE 15% = rodape com logo */
.footer {{
  background: {navy_dark};
  height: 150px;
  display: flex; align-items: center; justify-content: center;
  gap: 14px;
  border-top: 1px solid rgba(201,169,97,0.15);
}}
.logo-icon {{ font-size: 38px; }}
.logo-text {{
  font-family: 'Playfair Display', serif;
  font-size: 30px;
  font-weight: 700;
  color: {gold};
  letter-spacing: 0.18em;
}}
.logo-sub {{
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: {text_muted};
  letter-spacing: 0.4em;
  margin-top: 4px;
}}
.logo-block {{ display: flex; flex-direction: column; align-items: center; }}
</style></head>
<body>
  <div class="photo">
    <div class="dest-overlay">
      <span class="emoji">{destino_emoji}</span>
      <span class="name">{destino_nome}</span>
    </div>
  </div>
  <div class="card">
    <div class="kicker">{kicker}</div>
    <div class="title">{title}</div>
    <div class="body">{body}</div>
  </div>
  <div class="footer">
    <span class="logo-icon">🧳</span>
    <div class="logo-block">
      <span class="logo-text">PP TRAVEL</span>
      <span class="logo-sub">INFINITE</span>
    </div>
  </div>
</body></html>
"""

PROMO_TPL = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  width: 1080px; height: 1080px;
  font-family: 'Inter', sans-serif;
  display: flex; flex-direction: column;
  overflow: hidden;
}}
/* TOPO 70% = foto + badges */
.photo {{
  height: 756px;
  background: {photo_gradient};
  position: relative;
  display: flex; align-items: center; justify-content: center;
  font-size: 220px;
}}
.photo::after {{
  content: "";
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.15) 0%, transparent 30%, transparent 70%, rgba(0,0,0,0.25) 100%);
}}
.badge-off {{
  position: absolute;
  top: 50px; left: 50px;
  background: {navy_dark};
  color: {text};
  border-radius: 50%;
  width: 130px; height: 130px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  font-family: 'Inter', sans-serif;
  font-weight: 800;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  border: 2px solid {gold};
}}
.badge-off .num {{ font-size: 32px; line-height: 1; }}
.badge-off .lbl {{ font-size: 14px; letter-spacing: 0.1em; margin-top: 4px; color: {gold}; }}
.badge-date {{
  position: absolute;
  top: 50px; right: 50px;
  background: rgba(255,255,255,0.92);
  color: {navy};
  padding: 14px 20px;
  border-radius: 10px;
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 18px;
  letter-spacing: 0.12em;
  box-shadow: 0 4px 14px rgba(0,0,0,0.2);
}}
/* BASE 30% = CTA branco */
.cta-block {{
  flex: 1;
  background: {text};
  padding: 36px 60px;
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 36px;
  align-items: center;
}}
.dest {{ display: flex; flex-direction: column; }}
.dest-titulo {{
  font-family: 'Playfair Display', serif;
  font-size: 64px;
  font-weight: 800;
  color: {navy};
  line-height: 1;
}}
.dest-sub {{
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  color: {navy};
  opacity: 0.65;
  font-weight: 500;
  margin-top: 8px;
  letter-spacing: 0.04em;
}}
.preco-block {{ text-align: center; padding: 0 24px; border-left: 1px solid rgba(10,26,82,0.15); border-right: 1px solid rgba(10,26,82,0.15); }}
.preco-label {{
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: {navy};
  opacity: 0.65;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}}
.preco-principal {{
  font-family: 'Playfair Display', serif;
  font-size: 44px;
  font-weight: 800;
  color: {navy};
  line-height: 1.1;
  margin-top: 4px;
}}
.preco-parc {{
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: {navy};
  opacity: 0.7;
  margin-top: 4px;
}}
.cta-button {{
  background: {promo_yellow};
  color: {navy};
  padding: 22px 36px;
  border-radius: 999px;
  font-family: 'Inter', sans-serif;
  font-weight: 800;
  font-size: 22px;
  letter-spacing: 0.06em;
  white-space: nowrap;
  box-shadow: 0 6px 20px rgba(252,211,77,0.45);
}}
.brand-strip {{
  background: {navy_dark};
  color: {text};
  height: 56px;
  display: flex; align-items: center; justify-content: center;
  gap: 12px;
  font-family: 'Playfair Display', serif;
  font-weight: 700;
  font-size: 18px;
  letter-spacing: 0.16em;
  color: {gold};
}}
.brand-strip .sub {{ font-family: 'Inter', sans-serif; font-size: 12px; color: {text_muted}; letter-spacing: 0.35em; margin-left: 8px; }}
</style></head>
<body>
  <div class="photo">
    <span style="opacity:0.85; filter: drop-shadow(0 8px 24px rgba(0,0,0,0.3));">{destino_emoji}</span>
    <div class="badge-off">
      <span class="num">{badge_off}</span>
    </div>
    <div class="badge-date">{data_badge}</div>
  </div>
  <div class="cta-block">
    <div class="dest">
      <span class="dest-titulo">{destino_titulo}</span>
      <span class="dest-sub">{destino_sub}</span>
    </div>
    <div class="preco-block">
      <div class="preco-label">{preco_label}</div>
      <div class="preco-principal">{preco_principal}</div>
      <div class="preco-parc">{preco_parc}</div>
    </div>
    <div class="cta-button">{cta}</div>
  </div>
  <div class="brand-strip">🧳 PP TRAVEL <span class="sub">INFINITE</span></div>
</body></html>
"""


def render_card_html(m: dict) -> str:
    return CARD_TPL.format(
        navy=NAVY, navy_dark=NAVY_DARK, gold=GOLD, text=TEXT, text_muted=TEXT_MUTED,
        photo_gradient=m["photo_gradient"],
        destino_emoji=m["destino_emoji"],
        destino_nome=m["destino_nome"],
        kicker=m["kicker"],
        title=m["title"],
        body=m["body"],
    )


def render_promo_html(m: dict) -> str:
    return PROMO_TPL.format(
        navy=NAVY, navy_dark=NAVY_DARK, gold=GOLD, text=TEXT, text_muted=TEXT_MUTED,
        promo_yellow=PROMO_YELLOW,
        photo_gradient=m["photo_gradient"],
        destino_emoji=m["destino_emoji"],
        badge_off=m["badge_off"],
        data_badge=m["data_badge"],
        destino_titulo=m["destino_titulo"],
        destino_sub=m["destino_sub"],
        preco_label=m["preco_label"],
        preco_principal=m["preco_principal"],
        preco_parc=m["preco_parc"],
        cta=m["cta"],
    )


async def render() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1080}, device_scale_factor=2)
        for m in MOCKS:
            html = render_card_html(m) if m["template"] == "card" else render_promo_html(m)
            page = await ctx.new_page()
            await page.set_content(html, wait_until="networkidle")
            out = OUT_DIR / f"{m['pilar']}.png"
            await page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
            print(f"  [ok] {out.name}")
            await page.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(render())
    print(f"\nMocks em: {OUT_DIR}")
