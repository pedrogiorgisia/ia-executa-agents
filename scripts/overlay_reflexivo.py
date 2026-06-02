"""Adiciona overlay no MP4 Veo: frase reflexiva centralizada + handle @pptravelinfinite.

Usa ffmpeg drawtext com fade-in 1.2-2.5s e fade-out 4.5-5.7s.
Mantem o audio do Veo.

Saida: data/instagram/_veo-test/reflexivo-janela-FINAL.mp4
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "data" / "instagram" / "_veo-test" / "reflexivo-janela.mp4"
OUT = ROOT / "data" / "instagram" / "_veo-test" / "reflexivo-janela-FINAL.mp4"

# Configurar
LINHA1 = "Coisas não te seguem"
LINHA2 = "na lembrança."
LINHA3 = "Lugares sim."
HANDLE = "@pptravelinfinite"

FONT = r"C\:/Windows/Fonts/arial.ttf"  # escapar : pra ffmpeg
# Cores em formato 0xRRGGBB
WHITE = "white"
SHADOW = "black"

# Tempos (em segundos)
T_IN_START = 1.2     # comeca aparecer
T_IN_END = 2.3       # totalmente visivel
T_OUT_START = 4.5    # comeca sumir
T_OUT_END = 5.7      # totalmente sumido

# Curva de alpha por tempo (linear in/out)
ALPHA_EXPR = (
    f"if(lt(t,{T_IN_START}),0,"
    f"if(lt(t,{T_IN_END}),(t-{T_IN_START})/({T_IN_END}-{T_IN_START}),"
    f"if(lt(t,{T_OUT_START}),1,"
    f"if(lt(t,{T_OUT_END}),({T_OUT_END}-t)/({T_OUT_END}-{T_OUT_START}),0))))"
)


def drawtext_filter(text: str, fontsize: int, y_expr: str, alpha_expr: str = "1.0",
                    x_expr: str = "(w-text_w)/2", shadow: bool = True) -> str:
    """Constroi um filtro drawtext com escape correto."""
    # ffmpeg drawtext escape: : -> \: , ' -> '\\\'\'
    safe_text = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\\\\\'")
    parts = [
        f"fontfile='{FONT}'",
        f"text='{safe_text}'",
        f"x={x_expr}",
        f"y={y_expr}",
        f"fontsize={fontsize}",
        f"fontcolor={WHITE}",
        f"alpha='{alpha_expr}'",
    ]
    if shadow:
        parts += [f"shadowcolor={SHADOW}@0.7", "shadowx=3", "shadowy=3", "box=0"]
    return "drawtext=" + ":".join(parts)


# Construir filtergraph
# Posicionamento vertical: frase comeca em ~40% da altura, com line-height
filters = [
    drawtext_filter(LINHA1, fontsize=60, y_expr="h*0.36", alpha_expr=ALPHA_EXPR),
    drawtext_filter(LINHA2, fontsize=60, y_expr="h*0.36+74", alpha_expr=ALPHA_EXPR),
    drawtext_filter(LINHA3, fontsize=60, y_expr="h*0.36+170", alpha_expr=ALPHA_EXPR),
    # Handle no rodape - sempre visivel
    drawtext_filter(HANDLE, fontsize=28, y_expr="h-80", alpha_expr="0.85", shadow=True),
]

filter_complex = ",".join(filters)

cmd = [
    "ffmpeg", "-y",
    "-i", str(SRC),
    "-vf", filter_complex,
    "-c:a", "copy",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "20",
    str(OUT),
]

print(f"[render] gerando {OUT.name}...")
print(f"[filter] {filter_complex[:300]}...")
print()

result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
if result.returncode != 0:
    print(f"[FAIL] ffmpeg returncode={result.returncode}")
    print(f"--- stderr ---")
    print(result.stderr[-2000:])
    sys.exit(1)

size = OUT.stat().st_size
print(f"[ok] {OUT} ({size:,} bytes)")
