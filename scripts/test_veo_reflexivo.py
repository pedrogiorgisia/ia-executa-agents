"""Teste Veo 3.1 Fast — gera 1 reel reflexivo de 7s.

Workflow:
  1. POST /api/v1/videos {model, prompt, duration, aspect_ratio} -> {id, polling_url}
  2. Poll GET /api/v1/videos/{id} ate status=completed
  3. GET /api/v1/videos/{id}/content?index=0 -> baixa MP4

Custo: $0.10/segundo * 7s = $0.70 = ~R$ 4,20
"""
from __future__ import annotations
import json, os, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "data" / "instagram" / "_veo-test"
OUT.mkdir(parents=True, exist_ok=True)

for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = "google/veo-3.1-fast"
BASE = "https://openrouter.ai/api/v1"

# Prompt reflexivo classico (template A do formatos.md - janela de aviao)
PROMPT = (
    "A 6-second cinematic vertical 9:16 video. View from an airplane window "
    "looking out over a sea of clouds at golden hour. The wing of the plane is "
    "visible at the bottom-left of the frame. Camera: very subtle gentle pan, "
    "extremely smooth, no jumps or cuts. Lighting: warm sunset light streaming "
    "through the window casting orange and pink hues. Mood: contemplative, "
    "aspirational, peaceful, dreamlike. Color palette: warm ambers, deep blues, "
    "soft pinks. No on-screen text. No people visible. Editorial cinema quality. "
    "1080x1920, 30fps."
)


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


def main() -> None:
    print(f"[1/3] POST /api/v1/videos (model={MODEL}, 7s, 9:16)")
    t0 = time.time()
    res = http("POST", "/videos", {
        "model": MODEL,
        "prompt": PROMPT,
        "duration": 6,
        "aspect_ratio": "9:16",
    })
    if res.get("error"):
        print(f"  [ERROR] {res['error']}")
        return
    job = res["json"]
    job_id = job.get("id")
    status = job.get("status")
    print(f"  [ok] job_id={job_id} status={status}")
    print(f"       full response: {json.dumps(job, indent=2)[:400]}")

    # 2) Poll
    print(f"\n[2/3] Polling status...")
    poll_count = 0
    last_status = status
    while True:
        time.sleep(5)
        poll_count += 1
        elapsed = time.time() - t0
        res = http("GET", f"/videos/{job_id}")
        if res.get("error"):
            print(f"  [ERROR poll {poll_count}] {res['error']}")
            return
        status = res["json"].get("status")
        if status != last_status:
            print(f"  [poll {poll_count} @ {elapsed:.0f}s] status: {last_status} -> {status}")
            last_status = status
        else:
            print(f"  [poll {poll_count} @ {elapsed:.0f}s] still {status}")
        if status in ("completed", "succeeded", "success"):
            print(f"  [ok] completed em {elapsed:.0f}s")
            print(f"       full: {json.dumps(res['json'], indent=2)[:800]}")
            break
        if status in ("failed", "error"):
            print(f"  [FAIL] {json.dumps(res['json'], indent=2)[:500]}")
            return
        if elapsed > 600:
            print(f"  [timeout] >10min sem terminar")
            return

    # 3) Download
    print(f"\n[3/3] Baixando video...")
    res = http("GET", f"/videos/{job_id}/content?index=0")
    if res.get("error"):
        # Tenta achar URL no payload anterior
        urls = res.get("json", {}).get("unsigned_urls") or []
        if urls:
            print(f"  fallback: usando unsigned_urls[0]={urls[0][:80]}...")
            res = http("GET", urls[0])
        else:
            print(f"  [ERROR] {res['error']}")
            return
    out_path = OUT / "reflexivo-janela.mp4"
    out_path.write_bytes(res["raw"])
    elapsed = time.time() - t0
    print(f"  [ok] {out_path.name} ({len(res['raw']):,} bytes) · total {elapsed:.0f}s")


if __name__ == "__main__":
    main()
