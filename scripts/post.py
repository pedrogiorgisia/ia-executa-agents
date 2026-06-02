"""Orquestrador do motor Instagram PP-Travel.

⚠️ APROVACAO HUMANA OBRIGATORIA — o motor NAO posta sem comando explicito.

Modos de execucao:

  GENERATE (default) — gera tudo mas NAO posta:
    python scripts/post.py
      1. Garante sourcing (run_pp_sourcing.py)
      2. Le content.json (provido por Claude interativo ou headless)
      3. Gera midia (Gemini/Veo)
      4. Renderiza overlay
      5. Gera preview.html pro Pedro revisar
      [STOP. Aguarda aprovacao humana]

  PUBLISH — apos aprovacao do Pedro, Claude roda isso:
    python scripts/post.py --date YYYY-MM-DD --publish
      6. Posta via Zernio (publishNow=true)
      7. Atualiza historico.md + ideias/usadas.md + remove de disponiveis.md
      8. Regenera preview.html (com URL final do post)

  DRY-RUN — testa pipeline sem postar nem atualizar estado:
    python scripts/post.py --dry-run

Outros flags:
  --pilar inspiracao        Override pilar do dia
  --date 2026-06-02         Data especifica
  --content path.json       content.json especifico
  --account <zernio_id>     Conta Zernio override
"""
from __future__ import annotations
import argparse
import asyncio
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from cost_tracker import register_cost, log_call

# Carrega .env
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

OR_KEY = os.environ["OPENROUTER_API_KEY"]
ZERNIO_KEY = os.environ["ZERNIO_API_KEY"]
ZERNIO_BASE = "https://zernio.com/api/v1"

# Conta de teste atual (page.yaml.phase=testing)
IG_ACCOUNT_TEST = "6a1df37a2b2567671a8f620e"  # @ia.executa

# Mapa pilar -> dia (rotacao alinhada com guia-objetivos.md)
WEEKDAY_TO_PILAR = {
    "monday":    "educacao",
    "tuesday":   "conversao",
    "wednesday": "inspiracao",
    "thursday":  "conversao",  # alt: inspiracao
    "friday":    "engajamento",
    "saturday":  "inspiracao_reflexiva",
    "sunday":    "prova_social",
}


# ======== HTTP helpers ========

def http_or(method: str, path: str, body: dict | None = None) -> tuple[int, bytes]:
    """OpenRouter HTTP."""
    url = path if path.startswith("http") else f"https://openrouter.ai/api/v1{path}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": f"Bearer {OR_KEY}",
        "HTTP-Referer": "https://ia.executa",
        "X-Title": "PP-Travel Motor",
    }
    if body:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def http_zernio(method: str, url: str, headers: dict, body: bytes | None = None) -> tuple[int, bytes]:
    """Zernio HTTP."""
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


# ======== Step 2: Sourcing ========

def ensure_sourcing(date: str) -> Path:
    """Garante que digest.md existe pra o dia."""
    digest = ROOT / "data" / "instagram" / "pp-travel" / date / "digest.md"
    if digest.exists() and digest.stat().st_size > 200:
        print(f"  [skip] digest ja existe: {digest.name}")
        return digest
    print(f"  [run] rodando run_pp_sourcing.py")
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(ROOT / "scripts" / "run_pp_sourcing.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        print(f"  [FAIL] sourcing: {result.stderr[-1000:]}")
        sys.exit(1)
    return digest


# ======== Step 3: Geração de mídia ========

def gen_photo_gemini(prompt: str, out_dir: Path, slug: str) -> Path:
    """Gera foto via Gemini 3.1 Flash Image Preview."""
    print(f"  [media] Gemini Image — {slug}")
    t0 = time.time()
    status, raw = http_or("POST", "/chat/completions", {
        "model": "google/gemini-3.1-flash-image-preview",
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
        "usage": {"include": True},  # pede o custo REAL cobrado pelo OpenRouter
    })
    if status >= 300:
        raise RuntimeError(f"Gemini failed {status}: {raw.decode()[:400]}")
    resp = json.loads(raw.decode())
    msg = resp["choices"][0]["message"]
    usage = resp.get("usage", {}) or {}
    tokens_in = usage.get("prompt_tokens", 0)
    tokens_out = usage.get("completion_tokens", 0)
    # Custo REAL do OpenRouter (usage.cost em USD). Só cai na estimativa por token se faltar.
    real_cost = usage.get("cost")
    if isinstance(real_cost, (int, float)) and real_cost > 0:
        cost_usd = float(real_cost)
    else:
        cost_usd = (tokens_in * 0.0000005) + (tokens_out * 0.000003)
    register_cost(
        script="post.py",
        model="google/gemini-3.1-flash-image-preview",
        purpose=f"foto pro post: {slug}",
        cost_usd=cost_usd,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
    )
    log_call(
        kind="gemini_photo",
        model="google/gemini-3.1-flash-image-preview",
        prompt=prompt,
        result=json.dumps({"usage": usage, "has_image": bool(msg.get("images"))}, ensure_ascii=False),
        cost_usd=cost_usd, tokens_in=tokens_in, tokens_out=tokens_out,
        duration_ms=int((time.time() - t0) * 1000),
    )
    for img in (msg.get("images") or []):
        url = img.get("image_url", {}).get("url", "")
        if url.startswith("data:image"):
            png = base64.b64decode(url.split(",", 1)[1])
            out = out_dir / f"foto-{slug}.png"
            out.write_bytes(png)
            print(f"    [ok] {out.name} ({len(png):,} bytes, {time.time()-t0:.1f}s, ~R$ {cost_usd*6:.3f})")
            return out
    raise RuntimeError(f"sem imagem na resposta Gemini")


def gen_video_veo(prompt: str, out_dir: Path, slug: str, duration: int = 6) -> Path:
    """Gera vídeo via Veo 3.1 Lite (assíncrono)."""
    print(f"  [media] Veo 3.1 Lite — {slug} ({duration}s 9:16)")
    t0 = time.time()
    status, raw = http_or("POST", "/videos", {
        "model": "google/veo-3.1-lite",
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": "9:16",
    })
    if status >= 300:
        raise RuntimeError(f"Veo POST failed {status}: {raw.decode()[:400]}")
    job = json.loads(raw.decode())
    job_id = job["id"]
    print(f"    [poll] job_id={job_id}")

    last_status = job.get("status")
    while True:
        time.sleep(5)
        status, raw = http_or("GET", f"/videos/{job_id}")
        if status >= 300:
            raise RuntimeError(f"poll failed {status}")
        info = json.loads(raw.decode())
        cur = info.get("status")
        elapsed = time.time() - t0
        if cur != last_status:
            print(f"    [@ {elapsed:.0f}s] {last_status} -> {cur}")
            last_status = cur
        if cur in ("completed", "succeeded", "success"):
            cost = info.get("usage", {}).get("cost", 0)
            cost_usd = float(cost) if isinstance(cost, (int, float, str)) and str(cost) != "?" else 0
            print(f"    [ok] completed em {elapsed:.0f}s · custo: ${cost_usd:.2f} (R$ {cost_usd*6:.2f})")
            register_cost(
                script="post.py",
                model="google/veo-3.1-lite",
                purpose=f"reel reflexivo: {slug}",
                cost_usd=cost_usd,
                extra={"duration_s": duration, "aspect": "9:16"},
            )
            log_call(
                kind="veo_video",
                model="google/veo-3.1-lite",
                prompt=prompt,
                result=json.dumps(info, ensure_ascii=False),
                cost_usd=cost_usd, duration_ms=int(elapsed * 1000),
            )
            break
        if cur in ("failed", "error"):
            raise RuntimeError(f"Veo falhou: {json.dumps(info)[:400]}")
        if elapsed > 600:
            raise RuntimeError("Veo timeout >10min")

    # Download
    status, raw = http_or("GET", f"/videos/{job_id}/content?index=0")
    if status >= 300:
        raise RuntimeError(f"download failed {status}")
    out = out_dir / f"video-{slug}-raw.mp4"
    out.write_bytes(raw)
    print(f"    [ok] {out.name} ({len(raw):,} bytes)")
    return out


# ======== Step 4: Render ========

HTML_V2_TPL = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,500;1,700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1080px; height: 1080px; position: relative; overflow: hidden; font-family: 'Montserrat', sans-serif; }
.bg { position: absolute; inset: 0; background-image: url('data:image/__MIME__;base64,__B64__'); background-size: cover; background-position: center; }
.bg::after {
  content: ""; position: absolute; inset: 0;
  background:
    linear-gradient(180deg, rgba(0,10,30,0.55) 0%, rgba(0,10,30,0.05) 30%, rgba(0,10,30,0.10) 50%, rgba(0,10,30,0.85) 100%),
    linear-gradient(90deg, rgba(0,10,30,0.35) 0%, rgba(0,10,30,0.05) 60%);
}
.brand-top { position: absolute; top: 50px; left: 0; right: 0; text-align: center; font-family: 'Montserrat', sans-serif; font-weight: 500; font-size: 26px; letter-spacing: 0.32em; color: #fff; text-shadow: 0 2px 12px rgba(0,0,0,0.5); z-index: 2; }
.content { position: absolute; left: 70px; right: 70px; bottom: 230px; z-index: 2; color: #fff; }
.kicker { display: inline-block; font-size: 14px; font-weight: 700; letter-spacing: 0.28em; text-transform: uppercase; color: #fcd34d; margin-bottom: 24px; padding: 8px 16px; background: rgba(0,10,30,0.45); border-radius: 999px; backdrop-filter: blur(6px); }
.headline { font-family: 'Montserrat', sans-serif; font-weight: 500; font-size: 64px; line-height: 1.08; letter-spacing: -0.02em; color: #fff; text-shadow: 0 4px 18px rgba(0,0,0,0.5); margin-bottom: 32px; }
.headline strong { font-weight: 900; }
.headline em { font-style: italic; font-weight: 500; }
.pill { display: inline-block; background: #fff; color: #0a1a52; padding: 16px 26px; border-radius: 12px; font-family: 'Montserrat', sans-serif; font-weight: 600; font-size: 22px; letter-spacing: 0.02em; box-shadow: 0 8px 24px rgba(0,0,0,0.35); }
.bottom { position: absolute; left: 70px; right: 70px; bottom: 60px; z-index: 2; display: flex; align-items: center; justify-content: space-between; }
.handle { font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 18px; color: rgba(255,255,255,0.85); letter-spacing: 0.06em; }
.swipe-hint { font-family: 'Montserrat', sans-serif; font-weight: 500; font-size: 16px; color: rgba(255,255,255,0.6); letter-spacing: 0.08em; }
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
    <div class="swipe-hint">__SWIPE__</div>
  </div>
</body></html>
"""


async def render_single_photo(photo: Path, content: dict, out_dir: Path) -> Path:
    """Render V2 single photo. Le template de assets/ da skill."""
    from playwright.async_api import async_playwright
    print(f"  [render] V2 single photo overlay")
    mime = "jpeg" if photo.suffix.lower() in (".jpg", ".jpeg") else "png"
    b64 = base64.b64encode(photo.read_bytes()).decode("ascii")
    swipe = "" if content["formato"] == "single_photo" else "arrasta →"
    # Le template do assets/ da skill (canonical) — fallback pra HTML_V2_TPL inline se nao existir
    tpl_path = ROOT / ".claude" / "skills" / "instagram-motor" / "assets" / "template-v2-single-photo.html"
    html_tpl = tpl_path.read_text(encoding="utf-8") if tpl_path.exists() else HTML_V2_TPL
    html = (html_tpl
        .replace("__MIME__", mime).replace("__B64__", b64)
        .replace("__KICKER__", content["kicker"])
        .replace("__HEADLINE__", content["headline_html"])
        .replace("__PILL__", content.get("sub_pill", ""))
        .replace("__SWIPE__", swipe))

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1080}, device_scale_factor=2)
        page = await ctx.new_page()
        await page.set_content(html, wait_until="networkidle")
        out = out_dir / "post-final.png"
        await page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
        await browser.close()
    print(f"    [ok] {out.name} ({out.stat().st_size:,} bytes)")
    return out


def render_reel_reflexivo(raw_video: Path, content: dict, out_dir: Path) -> Path:
    """Render Reel Reflexivo via ffmpeg drawtext."""
    print(f"  [render] Reel Reflexivo overlay ffmpeg")
    # Montserrat SemiBold (alternativa Proxima Nova) — consistente com posts de foto.
    # ffmpeg drawtext exige escapar o ':' do drive no Windows.
    _font_path = ROOT / ".claude" / "skills" / "instagram-motor" / "assets" / "fonts" / "Montserrat-SemiBold.ttf"
    FONT = str(_font_path).replace("\\", "/").replace(":", "\\:") if _font_path.exists() else r"C\:/Windows/Fonts/arial.ttf"

    linhas = content["linhas_frase"]  # lista de strings (3-4 linhas)
    handle = "@pptravelinfinite"

    # Timeline alpha (fade in/out) — RETENTION 2025
    # Texto visivel desde frame 1 (T=0) ate 5s, fade discreto no fim
    # Antes: 1.2s -> 2.3s era anti-pattern (50% drop antes do hook chegar)
    T_IN_START, T_IN_END = 0.0, 0.3
    T_OUT_START, T_OUT_END = 5.0, 5.9
    ALPHA = (
        f"if(lt(t,{T_IN_START}),0,"
        f"if(lt(t,{T_IN_END}),(t-{T_IN_START})/({T_IN_END}-{T_IN_START}),"
        f"if(lt(t,{T_OUT_START}),1,"
        f"if(lt(t,{T_OUT_END}),({T_OUT_END}-t)/({T_OUT_END}-{T_OUT_START}),0))))"
    )

    def drawtext(text: str, fontsize: int, y: str, alpha: str = "1.0", shadow: bool = True) -> str:
        safe = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\\\\\'")
        parts = [
            f"fontfile='{FONT}'",
            f"text='{safe}'",
            "x=(w-text_w)/2",
            f"y={y}",
            f"fontsize={fontsize}",
            "fontcolor=white",
            f"alpha='{alpha}'",
        ]
        if shadow:
            parts += ["shadowcolor=black@0.7", "shadowx=3", "shadowy=3", "box=0"]
        return "drawtext=" + ":".join(parts)

    LH = 75
    base_y = "h*0.32"
    filters = []
    for i, linha in enumerate(linhas):
        y = f"{base_y}+{i*LH}" if i > 0 else base_y
        filters.append(drawtext(linha, fontsize=56, y=y, alpha=ALPHA))
    filters.append(drawtext(handle, fontsize=28, y="h-80", alpha="0.85"))

    out = out_dir / "reel-final.mp4"
    cmd = [
        "ffmpeg", "-y", "-i", str(raw_video),
        "-vf", ",".join(filters),
        "-c:a", "copy",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"    [FAIL] ffmpeg: {r.stderr[-800:]}")
        sys.exit(1)
    print(f"    [ok] {out.name} ({out.stat().st_size:,} bytes)")
    return out


# ======== Step 5: Post Zernio ========

def post_to_zernio(media: Path, content: dict, account_id: str, dry_run: bool = False) -> dict:
    """Posta no Zernio (single photo OR reel)."""
    if dry_run:
        print(f"  [dry-run] PULA post no Zernio")
        return {"post": {"_id": "dry-run-fake-id"}}

    is_reel = content["formato"] in ("reel", "reel_reflexivo")
    media_type = "video" if is_reel else "image"
    content_type = "video/mp4" if is_reel else "image/png"
    print(f"  [post] Zernio account={account_id} type={media_type}")

    # 1. Presign
    body = json.dumps({"filename": media.name, "contentType": content_type}).encode()
    status, raw = http_zernio("POST", f"{ZERNIO_BASE}/media/presign", {
        "Authorization": f"Bearer {ZERNIO_KEY}",
        "Content-Type": "application/json",
    }, body)
    if status >= 300:
        raise RuntimeError(f"presign failed {status}: {raw.decode()[:400]}")
    presign = json.loads(raw.decode())

    # 2. Upload PUT
    status, raw = http_zernio("PUT", presign["uploadUrl"], {"Content-Type": content_type}, media.read_bytes())
    if status >= 300:
        raise RuntimeError(f"upload failed {status}")
    print(f"    [ok] upload -> {presign['publicUrl'][:60]}...")

    # 3. Create post
    platform_data: dict = {}
    if content.get("first_comment"):
        platform_data["firstComment"] = content["first_comment"]
    if is_reel:
        platform_data["contentType"] = "reels"
        platform_data["shareToFeed"] = True

    body = json.dumps({
        "content": content["caption"],
        "mediaItems": [{"type": media_type, "url": presign["publicUrl"]}],
        "platforms": [{
            "platform": "instagram",
            "accountId": account_id,
            "platformSpecificData": platform_data,
        }],
        "publishNow": True,
    }).encode()
    status, raw = http_zernio("POST", f"{ZERNIO_BASE}/posts", {
        "Authorization": f"Bearer {ZERNIO_KEY}",
        "Content-Type": "application/json",
    }, body)
    if status >= 300:
        raise RuntimeError(f"create_post failed {status}: {raw.decode()[:600]}")
    res = json.loads(raw.decode())
    post_id = (res.get("post") or res).get("_id", "?")
    print(f"    [ok] post_id={post_id}")
    return res


# ======== Step 6-7: Update historico + ideias ========

def strip_html(s: str) -> str:
    """Remove tags <strong>, <em>, <br> de uma headline_html."""
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"</?(strong|em|b|i)>", "", s)
    return s.strip()


def update_historico(content: dict, post_id: str, date: str) -> None:
    print(f"  [historico] append linha")
    historico = ROOT / "pages" / "pp-travel" / "historico.md"
    now = datetime.now().strftime("%H:%M")
    # Reels usam 'frase_completa' ao inves de 'headline_html'
    headline_raw = content.get("headline_html") or content.get("frase_completa") or content.get("tema", "?")
    headline_plain = strip_html(headline_raw)
    hook_source = content.get("hook_source", "n/a")
    line = (
        f"| {date} {now} | {content['pilar']} | {content['formato']} | "
        f"\"{headline_plain}\" | {hook_source} | "
        f"https://instagram.com/p/{post_id} |"
    )
    h = historico.read_text(encoding="utf-8")
    if "## Auditoria mensal" in h:
        h = h.replace("## Auditoria mensal", f"{line}\n\n## Auditoria mensal")
    else:
        h += f"\n{line}\n"
    historico.write_text(h, encoding="utf-8")


def append_to_usadas(content: dict, post_id: str, date: str) -> None:
    print(f"  [ideias] append em usadas.md")
    usadas = ROOT / "pages" / "pp-travel" / "ideias" / "usadas.md"
    now = datetime.now().strftime("%H:%M")
    tema = content.get("tema") or strip_html(content["headline_html"])[:80]
    line = (
        f"- [{content['pilar']}] **{tema}**. Usado em {date} {now}. "
        f"post_id: {post_id}. URL: https://instagram.com/p/{post_id}."
    )
    u = usadas.read_text(encoding="utf-8")
    # insere antes do comentario "motor adiciona linhas abaixo"
    if "<!-- motor adiciona linhas abaixo -->" in u:
        u = u.replace("<!-- motor adiciona linhas abaixo -->", f"{line}\n\n<!-- motor adiciona linhas abaixo -->")
    else:
        u += f"\n{line}\n"
    usadas.write_text(u, encoding="utf-8")


def remove_from_disponiveis(content: dict) -> None:
    """Se o tema escolhido vem do banco, remove dele."""
    tema = content.get("tema")
    if not tema:
        return
    disp = ROOT / "pages" / "pp-travel" / "ideias" / "disponiveis.md"
    text = disp.read_text(encoding="utf-8")
    lines = text.split("\n")
    new_lines = [l for l in lines if tema not in l or not l.strip().startswith("-")]
    if len(new_lines) < len(lines):
        print(f"  [ideias] removida do banco: {tema[:60]}")
        disp.write_text("\n".join(new_lines), encoding="utf-8")


# ======== Step 8: Preview HTML ========

def gen_preview(date: str) -> Path:
    """Chama scripts/preview.py pra gerar preview HTML."""
    print(f"  [preview] gerando HTML")
    preview_script = ROOT / "scripts" / "preview.py"
    if not preview_script.exists():
        print(f"    [skip] preview.py nao existe ainda")
        return ROOT
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(preview_script), date],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        print(f"    [WARN] preview falhou: {result.stderr[-400:]}")
    else:
        print(f"    [ok] preview gerado")
    return ROOT / "data" / "instagram" / "pp-travel" / date / "preview.html"


# ======== MAIN ========

async def main_async(args: argparse.Namespace) -> None:
    date = args.date or datetime.now().strftime("%Y-%m-%d")
    out_dir = ROOT / "data" / "instagram" / "pp-travel" / date
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"{'='*70}")
    print(f"MOTOR Instagram PP-Travel — {date}")
    print(f"{'='*70}")

    # Step 1: Sourcing
    print(f"\n[1/8] Sourcing")
    ensure_sourcing(date)

    # Step 2: Carrega content.json
    print(f"\n[2/8] Carrega content.json")
    if args.content:
        content_path = Path(args.content)
    else:
        content_path = out_dir / "content.json"
    if not content_path.exists():
        print(f"  [FAIL] content.json nao encontrado: {content_path}")
        print(f"         Gere primeiro via Claude interativo OU rode `claude -p` headless")
        sys.exit(1)
    content = json.loads(content_path.read_text(encoding="utf-8"))
    print(f"  [ok] pilar={content['pilar']} formato={content['formato']}")

    # Step 3: Gera mídia (cache: reusa foto/video existente se ja tem)
    print(f"\n[3/8] Gera mídia")
    formato = content["formato"]
    slug = re.sub(r"[^a-z0-9-]+", "-", content.get("tema", "post").lower())[:40]

    if formato in ("single_photo", "carousel_educational", "carousel_storytelling"):
        # Procura foto existente
        existing_photos = list(out_dir.glob("foto-*.png"))
        if existing_photos and not args.regen_media:
            media = existing_photos[0]
            print(f"  [cache] usando foto existente: {media.name}")
        elif "photo_prompt" in content:
            media = gen_photo_gemini(content["photo_prompt"], out_dir, slug)
        else:
            raise RuntimeError("foto nao encontrada e content.json nao tem photo_prompt")
    elif formato in ("reel", "reel_reflexivo"):
        existing_videos = list(out_dir.glob("video-*-raw.mp4"))
        if existing_videos and not args.regen_media:
            media = existing_videos[0]
            print(f"  [cache] usando video existente: {media.name}")
        elif "video_prompt" in content:
            duration = content.get("video_duration", 6)
            media = gen_video_veo(content["video_prompt"], out_dir, slug, duration=duration)
        else:
            raise RuntimeError("video nao encontrado e content.json nao tem video_prompt")
    else:
        raise RuntimeError(f"formato nao suportado: {formato}")

    # Step 4: Render
    print(f"\n[4/8] Render overlay")
    if formato == "single_photo":
        final = await render_single_photo(media, content, out_dir)
    elif formato == "reel_reflexivo":
        final = render_reel_reflexivo(media, content, out_dir)
    elif formato in ("carousel_educational", "carousel_storytelling"):
        print(f"  [TODO] carrossel render — usando V2 single como fallback")
        final = await render_single_photo(media, content, out_dir)
    else:
        raise RuntimeError(f"render nao implementado: {formato}")

    # Step 5: Post Zernio (so com --publish)
    print(f"\n[5/8] Post Zernio")
    if not args.publish:
        if args.dry_run:
            print(f"  [dry-run] skipping post")
        else:
            print(f"  [generate-mode] APROVACAO HUMANA pendente. Para postar:")
            print(f"     python scripts/post.py --date {date} --publish")
        post_id = "(nao-postado)"
    else:
        account_id = args.account or IG_ACCOUNT_TEST
        result = post_to_zernio(final, content, account_id, dry_run=False)
        post_id = (result.get("post") or result).get("_id", "?")

    # Step 6-7: Update files (so com --publish bem-sucedido)
    print(f"\n[6/8] Update historico.md")
    if args.publish and post_id and post_id != "(nao-postado)":
        update_historico(content, post_id, date)
    else:
        print(f"  [skip] pula update historico.md (so atualiza apos --publish)")

    print(f"\n[7/8] Update ideias")
    if args.publish and post_id and post_id != "(nao-postado)":
        append_to_usadas(content, post_id, date)
        remove_from_disponiveis(content)
    else:
        print(f"  [skip] pula update ideias (so atualiza apos --publish)")

    # Step 8: Preview HTML
    print(f"\n[8/8] Preview HTML")
    gen_preview(date)

    print(f"\n{'='*70}")
    if args.dry_run:
        mode_label = "DRY-RUN (nada persistido)"
    elif args.publish:
        mode_label = f"PUBLICADO no Instagram · post_id={post_id}"
    else:
        mode_label = "GENERATE (gerado, NAO postado — aguarda aprovacao humana)"
    print(f"[done] {mode_label}")
    print(f"        diretorio: {out_dir}")
    print(f"        preview:   {out_dir / 'preview.html'}")
    print(f"{'='*70}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Orquestrador Instagram PP-Travel")
    parser.add_argument("--date", type=str, default=None, help="Data YYYY-MM-DD (default: hoje)")
    parser.add_argument("--content", type=str, default=None, help="Path do content.json (default: data/.../{date}/content.json)")
    parser.add_argument("--pilar", type=str, default=None, help="Override pilar do dia")
    parser.add_argument("--account", type=str, default=None, help="Zernio accountId override")
    parser.add_argument("--dry-run", action="store_true", help="Gera tudo mas nao posta")
    parser.add_argument("--publish", action="store_true", help="Posta no Zernio (aprovacao manual)")
    parser.add_argument("--regen-media", action="store_true", help="Regera midia mesmo se existir cache")
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
