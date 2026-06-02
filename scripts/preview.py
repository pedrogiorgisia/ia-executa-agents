"""Gera HTML estático de revisão pro Pedro.

Estrutura:
  data/instagram/pp-travel/_dashboard.html   ← índice de todos os dias
  data/instagram/pp-travel/{YYYY-MM-DD}/preview.html   ← detalhe do dia

Uso:
  python scripts/preview.py                # gera dashboard de todos + preview do dia atual
  python scripts/preview.py 2026-06-01     # preview de uma data específica
"""
from __future__ import annotations
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
BASE = ROOT / "data" / "instagram" / "pp-travel"


# ====== CSS comum ======

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: #0a0a0d; color: #fdfcfb; line-height: 1.5; padding: 40px 20px; }
.container { max-width: 1100px; margin: 0 auto; }
h1, h2, h3 { font-weight: 700; }
h1 { font-size: 32px; margin-bottom: 8px; }
h2 { font-size: 22px; margin: 32px 0 16px; color: #e0b87a; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; }
h3 { font-size: 18px; margin-bottom: 12px; }
a { color: #2dd4bf; text-decoration: none; }
a:hover { text-decoration: underline; }
.subtitle { color: #a19fad; margin-bottom: 32px; }
.card { background: #14141a; border-radius: 12px; padding: 24px; margin-bottom: 24px; border: 1px solid rgba(255,255,255,0.05); }
.media-wrap { background: #000; border-radius: 8px; overflow: hidden; margin-bottom: 16px; max-width: 600px; }
.media-wrap img, .media-wrap video { width: 100%; display: block; }
.meta-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 16px; }
.meta { background: rgba(224,184,122,0.06); border-radius: 8px; padding: 10px 14px; }
.meta-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: #a19fad; margin-bottom: 4px; }
.meta-value { font-size: 14px; color: #fdfcfb; font-weight: 600; }
.tag { display: inline-block; background: rgba(45,212,191,0.12); color: #2dd4bf; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; margin-right: 6px; }
.tag.pilar { background: rgba(224,184,122,0.15); color: #e0b87a; }
.tag.format { background: rgba(168,85,247,0.12); color: #c084fc; }
pre.caption { background: rgba(255,255,255,0.04); padding: 16px; border-radius: 8px; font-family: 'Segoe UI', sans-serif; white-space: pre-wrap; font-size: 14px; line-height: 1.6; color: #fdfcfb; border-left: 3px solid #e0b87a; }
.hashtags { color: #2dd4bf; font-weight: 600; }
.first-comment { background: rgba(45,212,191,0.06); border-left: 3px solid #2dd4bf; padding: 16px; border-radius: 8px; font-size: 14px; margin-top: 12px; }
.empty { color: #a19fad; font-style: italic; }
.row { display: flex; gap: 24px; flex-wrap: wrap; }
.col-img { flex: 0 0 auto; }
.col-txt { flex: 1; min-width: 300px; }
.day-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 20px; }
.day-card { background: #14141a; border-radius: 10px; padding: 20px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; gap: 14px; }
.day-card:hover { border-color: rgba(224,184,122,0.4); }
.day-card-head { display: flex; gap: 16px; align-items: flex-start; }
.day-card a.date-link { color: #fdfcfb; font-weight: 700; font-size: 18px; }
.day-card a.date-link:hover { color: #e0b87a; }
.day-thumb { width: 160px; height: 160px; flex: 0 0 160px; background: #000; border-radius: 6px; overflow: hidden; }
.day-thumb img, .day-thumb video { width: 100%; height: 100%; object-fit: cover; }
.day-meta { flex: 1; min-width: 0; }
.day-section-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: #a19fad; margin: 4px 0 6px; font-weight: 600; }
.day-caption { background: rgba(255,255,255,0.03); border-left: 3px solid #e0b87a; padding: 12px 14px; border-radius: 6px; font-size: 13px; line-height: 1.55; max-height: 220px; overflow: hidden; position: relative; }
.day-caption.expanded { max-height: none; }
.day-caption::after { content: ""; position: absolute; bottom: 0; left: 0; right: 0; height: 32px; background: linear-gradient(transparent, #14141a); pointer-events: none; }
.day-caption.expanded::after { display: none; }
.day-firstcomment { background: rgba(45,212,191,0.06); border-left: 3px solid #2dd4bf; padding: 12px 14px; border-radius: 6px; font-size: 13px; line-height: 1.55; }
.day-status { display: inline-block; font-size: 11px; padding: 3px 10px; border-radius: 999px; font-weight: 700; letter-spacing: 0.05em; }
.day-status.draft { background: rgba(252,211,77,0.15); color: #fcd34d; }
.day-status.published { background: rgba(45,212,191,0.15); color: #2dd4bf; }
.cost-bar { display: flex; gap: 16px; font-size: 13px; color: #a19fad; padding: 12px 16px; background: rgba(255,255,255,0.02); border-radius: 6px; margin-bottom: 16px; }
.cost-bar strong { color: #fdfcfb; }
"""


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def highlight_hashtags(caption: str) -> str:
    """Marca hashtags em verde."""
    import re
    return re.sub(r"(#\w+)", r'<span class="hashtags">\1</span>', esc(caption))


def find_media(day_dir: Path) -> Path | None:
    """Procura o arquivo final pra exibir."""
    for name in ("post-final.png", "reel-final.mp4", "post-final-v2.png"):
        p = day_dir / name
        if p.exists():
            return p
    # fallback: qualquer png/mp4
    pngs = list(day_dir.glob("*.png"))
    if pngs:
        return pngs[0]
    return None


def gen_day_preview(day_dir: Path) -> Path:
    """Gera preview.html pra 1 dia."""
    date = day_dir.name
    content_paths = list(day_dir.glob("content*.json"))
    media = find_media(day_dir)

    if not content_paths:
        # Sem content.json — dia incompleto
        html = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Preview {date}</title><style>{CSS}</style></head><body><div class="container">
<a href="../_dashboard.html">← dashboard</a>
<h1>{date}</h1>
<p class="subtitle">⚠️ Nenhum content.json encontrado neste dia.</p>
</div></body></html>"""
        out = day_dir / "preview.html"
        out.write_text(html, encoding="utf-8")
        return out

    # Pega o content.json mais recente (v2 > v1)
    content_paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    content = json.loads(content_paths[0].read_text(encoding="utf-8"))

    pilar = content.get("pilar", "?")
    formato = content.get("formato", "?")
    tema = content.get("tema", "?")
    kicker = content.get("kicker", "")
    headline_html = content.get("headline_html", "")
    sub_pill = content.get("sub_pill", "")
    caption = content.get("caption", "")
    first_comment = content.get("first_comment", "")
    hook_source = content.get("hook_source", "n/a")

    # Render do media
    if media:
        ext = media.suffix.lower()
        if ext == ".mp4":
            media_html = f'<video controls loop muted playsinline><source src="{media.name}" type="video/mp4"></video>'
        else:
            media_html = f'<img src="{media.name}" alt="post">'
        media_block = f'<div class="media-wrap">{media_html}</div>'
    else:
        media_block = '<p class="empty">⚠️ Mídia final não encontrada.</p>'

    html = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Preview {date} — {tema}</title><style>{CSS}</style></head><body>
<div class="container">
<a href="../_dashboard.html">← dashboard</a>
<h1>{date}</h1>
<p class="subtitle">
  <span class="tag pilar">{pilar}</span>
  <span class="tag format">{formato}</span>
  <span class="tag">fonte: {esc(hook_source)}</span>
</p>

<div class="card">
  <div class="row">
    <div class="col-img">{media_block}</div>
    <div class="col-txt">
      <h3>Texto sobreposto no post</h3>
      <div class="meta-grid">
        <div class="meta"><div class="meta-label">Kicker</div><div class="meta-value">{esc(kicker)}</div></div>
        <div class="meta"><div class="meta-label">Tema</div><div class="meta-value">{esc(tema)}</div></div>
      </div>
      <h3>Headline (HTML)</h3>
      <pre class="caption">{esc(headline_html)}</pre>
      <h3>Sub-pílula</h3>
      <pre class="caption">{esc(sub_pill)}</pre>
    </div>
  </div>
</div>

<div class="card">
  <h2>Caption</h2>
  <pre class="caption">{highlight_hashtags(caption)}</pre>
  {('<h2>Primeiro comentário</h2><div class="first-comment">' + esc(first_comment) + '</div>') if first_comment else ''}
</div>

<div class="card">
  <h2>Detalhes técnicos</h2>
  <div class="meta-grid">
    <div class="meta"><div class="meta-label">Formato</div><div class="meta-value">{formato}</div></div>
    <div class="meta"><div class="meta-label">Pilar</div><div class="meta-value">{pilar}</div></div>
    <div class="meta"><div class="meta-label">Fonte (sourcing)</div><div class="meta-value">{esc(hook_source)}</div></div>
    <div class="meta"><div class="meta-label">content.json</div><div class="meta-value">{content_paths[0].name}</div></div>
  </div>
</div>

</div></body></html>"""

    out = day_dir / "preview.html"
    out.write_text(html, encoding="utf-8")
    return out


def gen_dashboard() -> Path:
    """Gera _dashboard.html com índice de todos os dias.

    Cada card mostra: thumb + caption truncada + first comment + metadados.
    """
    days = sorted([d for d in BASE.iterdir() if d.is_dir() and not d.name.startswith("_")], reverse=True)

    cards: list[str] = []
    for d in days:
        media = find_media(d)
        content_paths = list(d.glob("content*.json"))
        if not content_paths:
            continue
        # Prefere content-v2.json > content.json (mais novo)
        content_paths.sort(key=lambda p: (p.name == "content.json", p.name), reverse=True)
        c = json.loads(content_paths[0].read_text(encoding="utf-8"))

        # Tema com fallback: tema > destino > strip(headline)
        import re as _re
        tema = c.get("tema") or c.get("destino") or _re.sub(r"<[^>]+>", "", c.get("headline_html", "?"))[:60]

        # Determina status (published se tem URL no historico, caso contrario draft)
        # Simplificacao: se existe post_final, ja foi gerado mas pode nao ter sido postado ainda
        status_label = "DRAFT (aguarda aprovação)"
        status_class = "draft"

        media_html = ""
        if media:
            ext = media.suffix.lower()
            if ext == ".mp4":
                media_html = f'<video src="{d.name}/{media.name}" muted loop playsinline autoplay></video>'
            else:
                media_html = f'<img src="{d.name}/{media.name}" alt="">'

        caption = c.get("caption", "")
        first_comment = c.get("first_comment", "")

        first_comment_block = ""
        if first_comment:
            first_comment_block = f"""
  <div class="day-section-label">1º comentário (auto)</div>
  <div class="day-firstcomment">{esc(first_comment)}</div>"""

        cards.append(f"""<div class="day-card">
  <div class="day-card-head">
    <div class="day-thumb">{media_html}</div>
    <div class="day-meta">
      <a href="{d.name}/preview.html" class="date-link">{d.name}</a>
      <p style="margin:4px 0 8px;font-size:14px;color:#fdfcfb;font-weight:500;">{esc(tema)}</p>
      <p style="margin-bottom:8px;">
        <span class="tag pilar">{c.get('pilar', '?')}</span>
        <span class="tag format">{c.get('formato', '?')}</span>
      </p>
      <span class="day-status {status_class}">{status_label}</span>
    </div>
  </div>
  <div>
    <div class="day-section-label">Caption</div>
    <div class="day-caption">{highlight_hashtags(caption) if caption else '<span class="empty">sem caption</span>'}</div>
  </div>{first_comment_block}
</div>""")

    html = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Dashboard PP-Travel Instagram</title><style>{CSS}</style></head><body>
<div class="container">
<h1>PP-Travel · Instagram Motor</h1>
<p class="subtitle">{len(days)} dias com conteúdo gerado · gerado em {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

<h2>Posts</h2>
<div class="day-list">
{''.join(cards) if cards else '<p class="empty">Nenhum dia com content.json ainda.</p>'}
</div>

</div></body></html>"""

    out = BASE / "_dashboard.html"
    out.write_text(html, encoding="utf-8")
    return out


def main() -> None:
    args = sys.argv[1:]
    if args:
        date = args[0]
        day_dir = BASE / date
        if not day_dir.exists():
            print(f"Diretorio nao existe: {day_dir}")
            sys.exit(1)
        out = gen_day_preview(day_dir)
        print(f"[ok] {out.relative_to(ROOT)}")

    # Sempre regenera o dashboard
    dashboard = gen_dashboard()
    print(f"[ok] {dashboard.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
