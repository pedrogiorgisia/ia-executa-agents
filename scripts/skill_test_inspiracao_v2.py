"""V2 do test inspiracao - seguindo o guia-objetivos.md.

Diferencas vs v1:
- Hook emocional (nao factual): "Imagine acordar com essa vista."
- Gatilho aspiracional + equilibrio sonho/realidade
- Link sutil com PP Travel no caption
- CTA emocional/social ("Marca a pessoa que voce levaria")
- Hashtags reduzidas pra 7 (era 9)

Reusa foto Gemini ja gerada (cache).
"""
from __future__ import annotations
import asyncio, base64, json, os, time, urllib.request, urllib.error
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

ZERNIO_KEY = os.environ["ZERNIO_API_KEY"]
ZERNIO_BASE = "https://zernio.com/api/v1"
IG_ACCOUNT = "6a1df37a2b2567671a8f620e"  # @ia.executa

# =============== CANDIDATO V2 (corrigido vs guia) ===============
CONTENT = {
    "pilar": "inspiracao",
    "formato": "single_photo",
    "destino": "Lençóis Maranhenses",
    "version": "v2-corrigida-vs-guia",

    # Hook emocional + gatilho aspiracional (vs antes que era factual)
    "kicker": "Inspiração do dia",
    "headline_html": (
        'Imagine acordar<br>'
        'com essa <em>vista</em>.<br>'
        'E pagar <strong>metade</strong> do<br>'
        'que você imagina.'
    ),
    # Sub-pill com elemento de urgência sazonal
    "sub_pill": "Lagoas cheias só de junho a setembro.",

    # Caption seguindo estrutura ideal do guia (Pilar 2):
    # 1. Frase de conexão emocional
    # 2. Contexto do sonho acessível (sensorial)
    # 3. Link sutil com PP Travel
    # 4. CTA emocional/social (marca a pessoa)
    "caption": (
        "Tem lugares no Brasil que parecem outro planeta.\n\n"
        "Os Lençóis Maranhenses em junho — água turquesa entre dunas brancas, "
        "até o céu vira reflexo. Existe só uma janela do ano com as lagoas "
        "cheias assim: junho a setembro.\n\n"
        "E sim — com as milhas certas, dá pra ir pagando muito menos do que "
        "parece. Esse é o tipo de viagem que a gente vive estruturando.\n\n"
        "Com quem você viveria isso? Marca aqui 👇\n\n"
        "#PPTravelInfinite #ViajarÉPreciso #LençóisMaranhenses "
        "#Maranhão #DicasDeViagem #BrasilDeNorteASul #ExperienciasQueValem"
    ),

    # First comment com gatilho de autoridade (do guia)
    "first_comment": (
        "A gente já levou famílias pros Lençóis com milhas Smiles e Latam Pass — "
        "é uma das viagens que mais marca nossos clientes. "
        "Manda LENÇÓIS no direct que faço a conta pra você."
    ),
}
# ================================================================


def http(method: str, url: str, headers: dict, body: bytes | None = None) -> tuple[int, bytes]:
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


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
  font-size: 58px; line-height: 1.08;
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
    print(f"\n[render] V2 overlay com headline emocional")
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
        out = OUT / "post-final-v2.png"
        await page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
        await browser.close()
    print(f"  [ok] {out.name} ({out.stat().st_size:,} bytes)")
    return out


def post_zernio(final_png: Path) -> dict:
    print(f"\n[post] Zernio @ia.executa")
    body = json.dumps({"filename": final_png.name, "contentType": "image/png"}).encode()
    status, raw = http("POST", f"{ZERNIO_BASE}/media/presign", {
        "Authorization": f"Bearer {ZERNIO_KEY}",
        "Content-Type": "application/json",
    }, body)
    if status >= 300:
        raise RuntimeError(f"presign failed {status}: {raw.decode()[:500]}")
    presign = json.loads(raw.decode())

    status, raw = http("PUT", presign["uploadUrl"], {"Content-Type": "image/png"}, final_png.read_bytes())
    if status >= 300:
        raise RuntimeError(f"upload failed {status}")
    print(f"  [ok] upload -> {presign['publicUrl'][:60]}...")

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


def update_historico(zernio_post_id: str) -> None:
    print(f"\n[historico] Atualizando + marcando v1 como despublicado")
    historico = ROOT / "pages" / "pp-travel" / "historico.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = (
        f"| {now} | inspiracao | single_photo (v2-corrigida) | "
        f"\"Imagine acordar com essa vista. E pagar metade do que você imagina.\" | "
        f"grok_x:Q5+sazonal_junho+guia_pilar2 | "
        f"https://instagram.com/p/{zernio_post_id} |"
    )
    content = historico.read_text(encoding="utf-8")
    # Marca a linha v1 como despublicada
    content = content.replace(
        "| 2026-06-01 20:04 | inspiracao | single_photo |",
        "| 2026-06-01 20:04 | inspiracao | single_photo ❌ DESPUBLICADO (nao seguia guia) |"
    )
    if "## Auditoria mensal" in content:
        content = content.replace("## Auditoria mensal", f"{line}\n\n## Auditoria mensal")
    else:
        content += f"\n{line}\n"
    historico.write_text(content, encoding="utf-8")
    print(f"  [ok] historico.md atualizado")


async def main():
    print(f"=" * 60)
    print(f"V2 - Inspiracao Lencois Maranhenses (vs guia-objetivos.md)")
    print(f"Mudancas: hook emocional + gatilho aspiracional + link PP + CTA social")
    print(f"=" * 60)

    # Reusa foto Gemini do post v1
    photo_v1 = OUT / "foto-lencois-maranhenses.png"
    if not photo_v1.exists():
        raise RuntimeError(f"Foto base nao encontrada: {photo_v1}")
    print(f"\n[1] Reusando foto Gemini do v1 ({photo_v1.stat().st_size:,} bytes)")

    # Salva content.json v2
    content_json = OUT / "content-v2.json"
    content_json.write_text(json.dumps(CONTENT, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[2] content-v2.json salvo")

    final = await render_overlay(photo_v1)
    result = post_zernio(final)
    post_id = (result.get("post") or result).get("_id", "?")
    update_historico(post_id)

    print(f"\n{'=' * 60}")
    print(f"[done] V2 publicado: https://www.instagram.com/ia.executa/")
    print(f"       post_id v2: {post_id}")


if __name__ == "__main__":
    asyncio.run(main())
