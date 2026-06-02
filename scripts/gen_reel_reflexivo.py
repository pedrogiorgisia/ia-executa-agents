"""Gera 1 Reel Reflexivo completo: Veo video + overlay frase + handle.

Aceita config inline: model, duracao, prompt video, frase reflexiva.
Saida: data/instagram/_reels-reflexivos/{slug}.mp4
"""
from __future__ import annotations
import base64, json, os, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT_DIR = ROOT / "data" / "instagram" / "_reels-reflexivos"
OUT_DIR.mkdir(parents=True, exist_ok=True)

for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

KEY = os.environ["OPENROUTER_API_KEY"]
BASE = "https://openrouter.ai/api/v1"

# ============== CONFIG ==============
SLUG = "pessoa-fjord-lite"
MODEL = "google/veo-3.1-lite"  # METADE do preco do Fast
DURATION = 6  # segundos (4/6/8 suportados)
ASPECT = "9:16"

VIDEO_PROMPT = (
    "A 6-second cinematic vertical 9:16 video. Wide shot of a young woman seen from "
    "behind, sitting on a rocky cliff edge overlooking a vast dramatic landscape — "
    "a deep Norwegian-style fjord with steep mountains rising from dark blue water. "
    "She wears a warm beige sweater, her hair gently moves with the wind. "
    "Camera: very slow push-in toward the horizon, smooth, no jumps. "
    "Lighting: blue hour just before sunset, dramatic dusky sky with hints of "
    "deep pink and amber on the horizon. Mood: contemplative, introspective, "
    "awe-inspiring, vast. Color palette: deep blues, slate grays, warm dusk pinks. "
    "No on-screen text. Face not visible. Editorial cinema quality, 35mm lens, "
    "shallow depth of field on the wind in her hair. 1080x1920, 30fps."
)

# Frase reflexiva (do banco em voice.md)
FRASE = "Tem viagem que muda o que você lê, o que come, e quem você é."

# Quebra em linhas pra overlay
LINHAS = [
    "Tem viagem que muda",
    "o que você lê,",
    "o que come,",
    "e quem você é.",
]
# ====================================


def http(method: str, path: str, body: dict | None = None) -> dict:
    url = path if path.startswith("http") else f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"Authorization": f"Bearer {KEY}"}
    if body:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            if r.headers.get("Content-Type", "").startswith("application/json"):
                return {"status": r.status, "json": json.loads(raw.decode())}
            return {"status": r.status, "raw": raw}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": e.read().decode()[:500]}


def gen_veo() -> Path:
    print(f"[1/3] POST /api/v1/videos (model={MODEL}, {DURATION}s, {ASPECT})")
    t0 = time.time()
    res = http("POST", "/videos", {
        "model": MODEL,
        "prompt": VIDEO_PROMPT,
        "duration": DURATION,
        "aspect_ratio": ASPECT,
    })
    if res.get("error"):
        raise RuntimeError(f"POST falhou: {res['error']}")
    job = res["json"]
    job_id = job["id"]
    print(f"  [ok] job_id={job_id} status={job.get('status')}")

    print(f"\n[2/3] Polling...")
    last_status = job.get("status")
    while True:
        time.sleep(5)
        elapsed = time.time() - t0
        res = http("GET", f"/videos/{job_id}")
        if res.get("error"):
            raise RuntimeError(f"poll falhou: {res['error']}")
        status = res["json"].get("status")
        if status != last_status:
            print(f"  [@ {elapsed:.0f}s] {last_status} -> {status}")
            last_status = status
        else:
            print(f"  [@ {elapsed:.0f}s] still {status}")
        if status in ("completed", "succeeded", "success"):
            cost = res["json"].get("usage", {}).get("cost")
            print(f"  [ok] completed em {elapsed:.0f}s · custo: ${cost}")
            break
        if status in ("failed", "error"):
            raise RuntimeError(f"job falhou: {json.dumps(res['json'])[:500]}")
        if elapsed > 600:
            raise RuntimeError("timeout >10min")

    res = http("GET", f"/videos/{job_id}/content?index=0")
    if "raw" not in res:
        raise RuntimeError(f"download falhou: {res}")
    raw_path = OUT_DIR / f"{SLUG}-raw.mp4"
    raw_path.write_bytes(res["raw"])
    print(f"  [ok] raw video salvo: {raw_path.name} ({len(res['raw']):,} bytes)")
    return raw_path


def overlay(raw_path: Path) -> Path:
    """Adiciona linhas + handle via ffmpeg drawtext."""
    print(f"\n[3/3] Overlay via ffmpeg drawtext")

    FONT = r"C\:/Windows/Fonts/arial.ttf"

    # Timeline alpha
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

    def drawtext(text: str, fontsize: int, y_expr: str, alpha_expr: str = "1.0",
                 shadow: bool = True) -> str:
        safe = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\\\\\'")
        p = [
            f"fontfile='{FONT}'",
            f"text='{safe}'",
            "x=(w-text_w)/2",
            f"y={y_expr}",
            f"fontsize={fontsize}",
            "fontcolor=white",
            f"alpha='{alpha_expr}'",
        ]
        if shadow:
            p += ["shadowcolor=black@0.7", "shadowx=3", "shadowy=3", "box=0"]
        return "drawtext=" + ":".join(p)

    # Posicionamento vertical: comeca em 32% da altura, line-height ~70px
    LH = 75
    base_y = "h*0.32"
    filters = []
    for i, linha in enumerate(LINHAS):
        y = f"{base_y}+{i*LH}" if i > 0 else base_y
        filters.append(drawtext(linha, fontsize=56, y_expr=y, alpha_expr=ALPHA_EXPR))
    # Handle no rodape
    filters.append(drawtext("@pptravelinfinite", fontsize=28, y_expr="h-80", alpha_expr="0.85"))

    out_path = OUT_DIR / f"{SLUG}-FINAL.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_path),
        "-vf", ",".join(filters),
        "-c:a", "copy",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"  [FAIL] {r.stderr[-1500:]}")
        sys.exit(1)
    print(f"  [ok] {out_path.name} ({out_path.stat().st_size:,} bytes)")
    return out_path


if __name__ == "__main__":
    raw = gen_veo()
    final = overlay(raw)
    print(f"\n[done] reel pronto: {final}")
    print(f"[frase] \"{FRASE}\"")
