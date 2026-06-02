# Templates de render — HTML + ffmpeg patterns validados

> Templates aprovados pelo Pedro em 2026-06-01.
> Reutilizar como base — não reinventar.

---

## Template V2 (Single Photo · Foto full-bleed + overlay)

**Aprovado pelo Pedro** nos 5 mocks PP-Travel (Inspiração, Educação, Engajamento, Prova Social, Conversão).

### Estrutura visual

```
┌────────────────────────┐
│       PP TRAVEL        │  ← Serifado branco topo central, fade-shadow
│                        │
│    [FOTO FULL-BLEED]   │
│    Gemini Image        │
│                        │
│    ╔═════════╗         │
│    ║ KICKER  ║         │  ← Pílula amarela #fcd34d com backdrop blur
│    ╚═════════╝         │
│    Headline grande     │  ← Montserrat, mix de regular/bold/italic, 70-90px
│    misturando pesos    │     em branco com text-shadow
│                        │
│    ┌──────────────┐    │
│    │ Pílula white │    │  ← Sub-headline com cor navy
│    └──────────────┘    │
│                        │
│ @pptravelinfinite ✈    │  ← Footer com handle + "arrasta →"
└────────────────────────┘
```

### Paleta aprovada

```python
NAVY = "#0a1a52"
NAVY_DARK = "#061238"
GOLD = "#c9a961"
GOLD_PILL = "#fcd34d"       # pílula amarela do kicker
TEXT = "#ffffff"
PROMO_YELLOW = "#fcd34d"
```

### HTML/CSS validado

Arquivo de referência:
[`scripts/render_pp_5_pilares.py`](../../../scripts/render_pp_5_pilares.py)

Núcleo do template (resumido):

```python
HTML_TPL = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,500;1,700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  width: 1080px; height: 1080px;
  position: relative; overflow: hidden;
  font-family: 'Montserrat', system-ui, sans-serif;
}
.bg {
  position: absolute; inset: 0;
  background-image: url('data:image/__MIME__;base64,__B64__');
  background-size: cover; background-position: center;
}
/* gradient escuro pro texto contrastar */
.bg::after {
  content: ""; position: absolute; inset: 0;
  background:
    linear-gradient(180deg, rgba(0,10,30,0.55) 0%, rgba(0,10,30,0.05) 30%, rgba(0,10,30,0.10) 50%, rgba(0,10,30,0.85) 100%),
    linear-gradient(90deg, rgba(0,10,30,0.35) 0%, rgba(0,10,30,0.05) 60%);
}
.brand-top {
  position: absolute; top: 50px; left: 0; right: 0;
  text-align: center;
  font-family: 'Montserrat', serif; font-weight: 500;
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
  font-family: 'Montserrat', sans-serif; font-weight: 500;
  font-size: 70px; line-height: 1.05;
  letter-spacing: -0.02em; color: #ffffff;
  text-shadow: 0 4px 18px rgba(0,0,0,0.5);
  margin-bottom: 32px;
}
.headline strong { font-weight: 900; }
.headline em { font-style: italic; font-weight: 500; }
.pill {
  display: inline-block; background: #ffffff;
  color: #0a1a52; padding: 16px 26px;
  border-radius: 12px; font-family: 'Montserrat', sans-serif;
  font-weight: 600; font-size: 22px; letter-spacing: 0.02em;
  box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}
.pill em { font-style: italic; color: #0a1a52; opacity: 0.85; }
.bottom {
  position: absolute; left: 70px; right: 70px; bottom: 60px;
  z-index: 2; display: flex; align-items: center; justify-content: space-between;
}
.handle {
  font-family: 'Montserrat', sans-serif; font-weight: 700;
  font-size: 18px; color: rgba(255,255,255,0.85);
  letter-spacing: 0.06em;
}
.swipe-hint {
  font-family: 'Montserrat', sans-serif; font-weight: 500;
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
```

### Render via Playwright (Python async)

```python
from playwright.async_api import async_playwright
import base64

async def render(photo_path: Path, html_tpl: str, ...) -> Path:
    # 1. Inline a foto como base64 data URL (NÃO usar file:// — bug com espaços em paths Windows)
    mime = "jpeg" if photo_path.suffix.lower() in (".jpg", ".jpeg") else "png"
    b64 = base64.b64encode(photo_path.read_bytes()).decode("ascii")

    # 2. Substituir placeholders
    html = (html_tpl
        .replace("__MIME__", mime)
        .replace("__B64__", b64)
        .replace("__KICKER__", kicker)
        .replace("__HEADLINE__", headline_html)  # pode ter <strong>, <em>
        .replace("__PILL__", sub_pill))

    # 3. Playwright renderiza
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1080}, device_scale_factor=2)
        page = await ctx.new_page()
        await page.set_content(html, wait_until="networkidle")
        out = OUT_DIR / "post.png"
        await page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
        await browser.close()
    return out
```

**Importante**: usar `device_scale_factor=2` pra gerar 2160×2160 (1080 @2x). Instagram aceita até 1080×1080 e o downscale fica nítido.

---

## Template Reel Reflexivo (vídeo overlay ffmpeg)

**Validado pelo Pedro** com Veo 3.1 Lite + frase do banco (2026-06-01).

### Estrutura do overlay

```
[Veo MP4 720×1280]
   +
[Linhas da frase reflexiva centralizadas, fade-in 1.2-2.3s, fade-out 4.5-5.7s]
   +
[Handle @pptravelinfinite no rodapé, alpha 0.85 sempre visível]
```

### ffmpeg drawtext pattern

Arquivo de referência:
[`scripts/gen_reel_reflexivo.py`](../../../scripts/gen_reel_reflexivo.py)

```python
# Timeline alpha (fade in/out)
T_IN_START = 1.2
T_IN_END = 2.3
T_OUT_START = 4.4
T_OUT_END = 5.7
ALPHA_EXPR = (
    f"if(lt(t,{T_IN_START}),0,"
    f"if(lt(t,{T_IN_END}),(t-{T_IN_START})/({T_IN_END}-{T_IN_START}),"
    f"if(lt(t,{T_OUT_START}),1,"
    f"if(lt(t,{T_OUT_END}),({T_OUT_END}-t)/({T_OUT_END}-{T_OUT_START}),0))))"
)

def drawtext(text: str, fontsize: int, y_expr: str, alpha_expr: str = "1.0", shadow: bool = True) -> str:
    # Escape pra ffmpeg filter (cuidado com aspas, dois pontos, backslash)
    safe = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\\\\\'")
    parts = [
        f"fontfile='C\\:/Windows/Fonts/arial.ttf'",
        f"text='{safe}'",
        "x=(w-text_w)/2",
        f"y={y_expr}",
        f"fontsize={fontsize}",
        "fontcolor=white",
        f"alpha='{alpha_expr}'",
    ]
    if shadow:
        parts += ["shadowcolor=black@0.7", "shadowx=3", "shadowy=3", "box=0"]
    return "drawtext=" + ":".join(parts)

# Construir filtergraph
LH = 75  # line-height
base_y = "h*0.32"
filters = []
for i, linha in enumerate(linhas_da_frase):
    y = f"{base_y}+{i*LH}" if i > 0 else base_y
    filters.append(drawtext(linha, fontsize=56, y_expr=y, alpha_expr=ALPHA_EXPR))
# Handle rodapé sempre visível
filters.append(drawtext("@pptravelinfinite", fontsize=28, y_expr="h-80", alpha_expr="0.85"))

# Rodar ffmpeg
cmd = [
    "ffmpeg", "-y",
    "-i", str(raw_mp4),
    "-vf", ",".join(filters),
    "-c:a", "copy",     # mantém áudio do Veo
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    str(out_mp4),
]
subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8")
```

### Como quebrar uma frase longa em linhas

A frase do banco vai pro overlay como N linhas centralizadas verticalmente.
Regras:
- Cada linha máx ~22 chars (fonte 56px em 720px de largura)
- Quebra natural (pontuação, "e", "que", etc.)
- 3-4 linhas no máximo (mais que isso polui a imagem)

**Exemplos validados:**

```
"Coisas não te seguem na lembrança. Lugares sim."
→
Coisas não te seguem
na lembrança.
Lugares sim.

"Tem viagem que muda o que você lê, o que come, e quem você é."
→
Tem viagem que muda
o que você lê,
o que come,
e quem você é.
```

---

## Gotchas comuns

### 1. Path file:// com espaços (Windows)
Não usar `background-image: url('file:///path with spaces/...')` — bugs no Chromium do Playwright.
**Solução:** sempre base64-inline a imagem como data URL.

### 2. Encoding Windows cp1252
Scripts Python no Windows às vezes falham em chars Unicode (✓, →, etc.) no print:
**Solução:** rodar com `python -X utf8 script.py` ou trocar caracteres especiais por ASCII no print.

### 3. ffmpeg fontfile escaping
No Windows, path do Arial precisa de escape duplo do `:`:
`fontfile='C\:/Windows/Fonts/arial.ttf'`

### 4. Acentos no drawtext
ffmpeg drawtext aceita UTF-8 — só garantir que o arquivo Python esteja salvo em UTF-8.

### 5. Aspas dentro do texto
Escape de aspas simples no drawtext é triplo: `\\\\\\'`.
Se o texto tem aspas, considere substituir por outra pontuação ou usar `textfile=...` em vez de `text=...`.

---

## Como decidir qual template usar

| Pilar | Formato | Template |
|---|---|---|
| Inspiração | Single Photo | **V2** (full-bleed + overlay) |
| Inspiração Reflexiva | Reel | **Reel Reflexivo** (Veo + ffmpeg overlay) |
| Engajamento | Single Photo | **V2** com headline-pergunta grande |
| Educação | Carrossel | V2 estendido pra N slides (a desenvolver) |
| Prova Social | Carrossel | V2 estendido (a desenvolver) |
| Conversão | Single Photo | V2 (com badge OFF nos extras) |
