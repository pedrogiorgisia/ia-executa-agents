"""Teste da skill instagram-motor: gera + posta 1 Single Photo de Inspiracao.

Segue os passos 6-9 do SKILL.md:
  6. Gera foto Gemini 3.1
  7. Render overlay V2 (Playwright HTML)
  8. Posta via Zernio em @ia.executa
  9. Append em historico.md

Candidato escolhido: Lencois Maranhenses em junho.
"""
from __future__ import annotations
import asyncio, base64, json, mimetypes, os, time, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).parent.parent
TODAY = datetime.now().strftime("%Y-%m-%d")
OUT = ROOT / "data" / "instagram" / "pp-travel" / TODAY
OUT.mkdir(parents=True, exist_ok=True)

for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

OR_KEY = os.environ["OPENROUTER_API_KEY"]
ZERNIO_KEY = os.environ["ZERNIO_API_KEY"]
ZERNIO_BASE = "https://zernio.com/api/v1"
IG_ACCOUNT = "6a1df37a2b2567671a8f620e"  # @ia.executa (test - phase=testing)

# =============== CANDIDATO ESCOLHIDO ===============
CONTENT = {
    "pilar": "inspiracao",
    "formato": "single_photo",
    "destino": "Lencois Maranhenses",
    "kicker": "Inspiração do dia",
    "headline_html": (
        'Junho é a <strong>única janela</strong>'
        '<br>pros Lençóis com <em>lagoas cheias</em>.'
    ),
    "sub_pill": "Depois disso, seca até fevereiro.",
    "photo_prompt": (
        "Professional aerial drone travel photography of Lençóis Maranhenses in Brazil "
        "at golden hour. Vast white sand dunes stretching to the horizon, with "
        "stunning crystal-clear turquoise blue lagoons nestled between the dunes. "
        "Warm late-afternoon sunlight casting long shadows across the white sand. "
        "Cinematic atmosphere, editorial quality, shot from a slightly elevated angle. "
        "Composition: dunes and lagoons fill the lower-right two thirds of the frame, "
        "leaving generous negative space in the upper-left for text overlay. "
        "Color palette: pristine white sand, deep turquoise water, warm amber sky. "
        "No people visible, no text, no logos in the image. "
        "High-end editorial National Geographic style. Aspect ratio 4:5 portrait."
    ),
    "caption": (
        "Junho é a única janela do ano pros Lençóis com as lagoas cheias.\n\n"
        "Depois disso, seca até fevereiro.\n\n"
        "Você já foi pra esse pedaço do Brasil que parece outro planeta? 👇\n\n"
        "#PPTravelInfinite #PassagensAéreas #DicasDeViagem "
        "#ViajarÉPreciso #DestinoCerto #MilhasComSegurança "
        "#LençóisMaranhenses #Maranhão #BrasilDeNorteASul"
    ),
    "first_comment": (
        "Quer cotar passagem pro Maranhão com milhas? "
        "Manda 'LENÇÓIS' no direct que a gente faz a conta pra você."
    ),
}
# ====================================================


# ====== Util HTTP ======

def http(method: str, url: str, headers: dict, body: bytes | None = None) -> tuple[int, bytes]:
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


# ====== Passo 6: Foto Gemini 3.1 ======

def gen_photo() -> Path:
    print(f"\n[6/9] Gerando foto Gemini 3.1 - {CONTENT['destino']}")
    body = json.dumps({
        "model": "google/gemini-3.1-flash-image-preview",
        "messages": [{"role": "user", "content": CONTENT["photo_prompt"]}],
        "modalities": ["image", "text"],
    }).encode()
    t0 = time.time()
    status, raw = http("POST", "https://openrouter.ai/api/v1/chat/completions", {
        "Authorization": f"Bearer {OR_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ia.executa",
        "X-Title": "PP-Travel Motor Test",
    }, body)
    if status >= 300:
        raise RuntimeError(f"Gemini failed {status}: {raw.decode()[:500]}")
    resp = json.loads(raw.decode())
    msg = resp["choices"][0]["message"]
    for img in (msg.get("images") or []):
        url = img.get("image_url", {}).get("url", "")
        if url.startswith("data:image"):
            png_bytes = base64.b64decode(url.split(",", 1)[1])
            out = OUT / f"foto-{CONTENT['destino'].lower().replace(' ', '-')}.png"
            out.write_bytes(png_bytes)
            elapsed = time.time() - t0
            print(f"  [ok] {out.name} ({len(png_bytes):,} bytes, {elapsed:.1f}s)")
            return out
    raise RuntimeError(f"sem imagem na resposta Gemini")


# ====== Passo 7: Render overlay V2 ======

HTML_TPL = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Inter:ital,wght@0,400;0,500;0,700;0,800;0,900;1,400;1,500;1,700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  width: 1080px; height: 1080px;
  position: relative; overflow: hidden;
  font-family: 'Inter', system-ui, sans-serif;
}
.bg {
  position: absolute; inset: 0;
  background-image: url('data:image/__MIME__;base64,__B64__');
  background-size: cover; background-position: center;
}
.bg::after {
  content: ""; position: absolute; inset: 0;
  background:
    linear-gradient(180deg, rgba(0,10,30,0.55) 0%, rgba(0,10,30,0.05) 30%, rgba(0,10,30,0.10) 50%, rgba(0,10,30,0.85) 100%),
    linear-gradient(90deg, rgba(0,10,30,0.35) 0%, rgba(0,10,30,0.05) 60%);
}
.brand-top {
  position: absolute; top: 50px; left: 0; right: 0;
  text-align: center;
  font-family: 'Playfair Display', serif; font-weight: 500;
  font-size: 26px; letter-spacing: 0.32em;
  color: #ffffff; text-shadow: 0 2px 12px rgba(0,0,0,0.5); z-index: 2;
}
.content {
  position: absolute; left: 70px; right: 70px; bottom: 230px;
  z-index: 2; color: #ffffff;
}
.kicker {
  display: inline-block; font-size: 14px; font-weight: 700;
  letter-spacing: 0.28em; text-transform: uppercase;
  color: #fcd34d; margin-bottom: 24px;
  padding: 8px 16px; background: rgba(0,10,30,0.45);
  border-radius: 999px; backdrop-filter: blur(6px);
}
.headline {
  font-family: 'Inter', sans-serif; font-weight: 500;
  font-size: 68px; line-height: 1.05;
  letter-spacing: -0.02em; color: #ffffff;
  text-shadow: 0 4px 18px rgba(0,0,0,0.5);
  margin-bottom: 32px;
}
.headline strong { font-weight: 900; }
.headline em { font-style: italic; font-weight: 500; }
.pill {
  display: inline-block; background: #ffffff;
  color: #0a1a52; padding: 16px 26px;
  border-radius: 12px; font-family: 'Inter', sans-serif;
  font-weight: 600; font-size: 22px; letter-spacing: 0.02em;
  box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}
.bottom {
  position: absolute; left: 70px; right: 70px; bottom: 60px;
  z-index: 2; display: flex; align-items: center; justify-content: space-between;
}
.handle {
  font-family: 'Inter', sans-serif; font-weight: 700;
  font-size: 18px; color: rgba(255,255,255,0.85);
  letter-spacing: 0.06em;
}
.swipe-hint {
  font-family: 'Inter', sans-serif; font-weight: 500;
  font-size: 16px; color: rgba(255,255,255,0.6);
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


async def render_overlay(photo: Path) -> Path:
    print(f"\n[7/9] Render overlay V2 com Playwright")
    mime = "jpeg" if photo.suffix.lower() in (".jpg", ".jpeg") else "png"
    b64 = base64.b64encode(photo.read_bytes()).decode("ascii")
    html = (HTML_TPL
        .replace("__MIME__", mime)
        .replace("__B64__", b64)
        .replace("__KICKER__", CONTENT["kicker"])
        .replace("__HEADLINE__", CONTENT["headline_html"])
        .replace("__PILL__", CONTENT["sub_pill"]))

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1080}, device_scale_factor=2)
        page = await ctx.new_page()
        await page.set_content(html, wait_until="networkidle")
        out = OUT / "post-final.png"
        await page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
        await browser.close()
    print(f"  [ok] {out.name} ({out.stat().st_size:,} bytes)")
    return out


# ====== Passo 8: Post Zernio ======

def post_zernio(final_png: Path) -> dict:
    print(f"\n[8/9] Posta no Zernio (@ia.executa)")

    # 1. Presign
    body = json.dumps({"filename": final_png.name, "contentType": "image/png"}).encode()
    status, raw = http("POST", f"{ZERNIO_BASE}/media/presign", {
        "Authorization": f"Bearer {ZERNIO_KEY}",
        "Content-Type": "application/json",
    }, body)
    if status >= 300:
        raise RuntimeError(f"presign failed {status}: {raw.decode()[:500]}")
    presign = json.loads(raw.decode())

    # 2. Upload PUT
    status, raw = http("PUT", presign["uploadUrl"], {"Content-Type": "image/png"}, final_png.read_bytes())
    if status >= 300:
        raise RuntimeError(f"upload failed {status}")
    print(f"  [ok] upload {len(final_png.read_bytes()):,} bytes -> {presign['publicUrl'][:60]}...")

    # 3. Create post
    body = json.dumps({
        "content": CONTENT["caption"],
        "mediaItems": [{"type": "image", "url": presign["publicUrl"]}],
        "platforms": [{
            "platform": "instagram",
            "accountId": IG_ACCOUNT,
            "platformSpecificData": {"firstComment": CONTENT["first_comment"]},
        }],
        "publishNow": True,
    }).encode()
    status, raw = http("POST", f"{ZERNIO_BASE}/posts", {
        "Authorization": f"Bearer {ZERNIO_KEY}",
        "Content-Type": "application/json",
    }, body)
    if status >= 300:
        raise RuntimeError(f"create_post failed {status}: {raw.decode()[:500]}")
    res = json.loads(raw.decode())
    post_id = (res.get("post") or res).get("_id", "?")
    print(f"  [ok] post_id={post_id}")
    return res


# ====== Passo 9: Atualiza historico ======

def update_historico(zernio_post_id: str) -> None:
    print(f"\n[9/9] Append em historico.md")
    historico = ROOT / "pages" / "pp-travel" / "historico.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    headline_plain = CONTENT["headline_html"].replace("<strong>", "").replace("</strong>", "")\
        .replace("<em>", "").replace("</em>", "").replace("<br>", " ").replace("</br>", "").strip()
    line = (
        f"| {now} | {CONTENT['pilar']} | {CONTENT['formato']} | "
        f"\"{headline_plain}\" | grok_x:Q5+sazonal_junho | "
        f"https://instagram.com/p/{zernio_post_id} |"
    )
    content = historico.read_text(encoding="utf-8")
    # Append antes da seccao "Auditoria"
    if "## Auditoria mensal" in content:
        content = content.replace("## Auditoria mensal", f"{line}\n\n## Auditoria mensal")
    else:
        content += f"\n{line}\n"
    historico.write_text(content, encoding="utf-8")
    print(f"  [ok] adicionado")


# ============== MAIN ==============

async def main():
    print(f"=" * 60)
    print(f"Skill instagram-motor test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Candidato: {CONTENT['destino']} | Pilar: {CONTENT['pilar']} | Formato: {CONTENT['formato']}")
    print(f"=" * 60)

    # Salva content.json (passo 5 ja foi feito - escolhi candidato 1)
    content_json = OUT / "content.json"
    content_json.write_text(json.dumps(CONTENT, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[5/9] content.json salvo em {content_json.name}")

    photo = gen_photo()                # passo 6
    final = await render_overlay(photo)# passo 7
    result = post_zernio(final)        # passo 8
    post_id = (result.get("post") or result).get("_id", "?")
    update_historico(post_id)          # passo 9

    print(f"\n{'=' * 60}")
    print(f"[done] Post publicado no @ia.executa")
    print(f"       post_id Zernio: {post_id}")
    print(f"       Confere em: https://www.instagram.com/ia.executa/")


if __name__ == "__main__":
    asyncio.run(main())
