"""Test rapido: o Gemini Image gera foto de qualidade pra Instagram?"""
from __future__ import annotations
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "data" / "instagram" / "_gemini-test"
OUT.mkdir(parents=True, exist_ok=True)

# Load .env
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
model = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image-preview")

# Prompt cinematic style, com espaco pro texto
prompt = (
    "Professional travel photography of Lisbon, Portugal at golden hour: "
    "view of the colorful tram 28 climbing a steep cobblestone street in Alfama, "
    "warm sunset light on pastel buildings, atmospheric, cinematic, moody, "
    "shot on full-frame camera with 35mm lens, shallow depth of field. "
    "Composition: subject on the right third, leaving negative space on the upper-left "
    "for text overlay. Color palette: warm ambers, deep blues, golden highlights. "
    "Aspect ratio 1:1 square format. No people facing the camera, no text in the image."
)

print(f"[gemini] modelo: {model}")
print(f"[gemini] gerando 1 imagem (Lisbon)...")

try:
    resp = client.models.generate_content(
        model=model,
        contents=[prompt],
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )
    n_imgs = 0
    for part in resp.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            n_imgs += 1
            out = OUT / f"lisbon-{n_imgs}.png"
            out.write_bytes(part.inline_data.data)
            print(f"  [ok] {out}")
    if n_imgs == 0:
        print("  [FAIL] resposta sem imagem")
        print(f"  resp: {resp}")
except Exception as e:
    print(f"  [ERROR] {type(e).__name__}: {e}")
