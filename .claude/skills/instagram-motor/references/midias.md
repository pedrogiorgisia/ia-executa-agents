# Geração de mídia — endpoints OpenRouter

> Tudo validado em 2026-06-01. Atualizar se OpenRouter mudar API.
> Chave: `OPENROUTER_API_KEY` no `.env` (já configurado).

---

## 1. Foto via Gemini 3.1 Flash Image Preview

**Modelo:** `google/gemini-3.1-flash-image-preview`
**Custo:** input $0.0000005/tok, output $0.000003/tok — ~R$ 0,01 por imagem
**Resolução:** ~1536×1536 (saída do modelo, depois ajustar)
**Tempo:** ~8s/imagem

### Chamada (Python via urllib)

```python
import base64, json, urllib.request, os

key = os.environ["OPENROUTER_API_KEY"]
body = json.dumps({
    "model": "google/gemini-3.1-flash-image-preview",
    "messages": [{"role": "user", "content": PROMPT}],
    "modalities": ["image", "text"],
}).encode()

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=body,
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ia.executa",
        "X-Title": "PP-Travel Motor",
    },
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
    resp = json.loads(r.read().decode())

msg = resp["choices"][0]["message"]
for img in (msg.get("images") or []):
    url = img.get("image_url", {}).get("url", "")
    if url.startswith("data:image"):
        png_bytes = base64.b64decode(url.split(",", 1)[1])
        # salvar PNG
```

### Prompt template (Inspiração / Single Photo)

```
Professional travel photography of [DESTINO/CENA].
[LIGHTING: golden hour / blue hour / overcast].
Cinematic atmosphere, shallow depth of field, shot on 35mm full-frame.
Aspect ratio: [1:1 para carrossel, 4:5 para single].
Composition: [SUBJECT] on the lower-right third, leaving large negative
space in the upper-left for text overlay.
No people facing camera. No text in the image. Editorial magazine quality.
```

### Por que esse modelo

- Aprovado pelo Pedro nos 5 mocks PP-Travel (2026-06-01)
- 1536×1536 melhor que 1024×1024 do 2.5 Flash
- $0.01/imagem é barato pra rodar diário
- Preview gratuito (pricing image="?" no docs, mas cobra só input/output tokens)

### Fallback

Se 3.1 falhar (500/timeout), tentar `google/gemini-2.5-flash-image` (custa $0.0000003/img, qualidade um pouco menor).

---

## 2. Vídeo via Veo 3.1 Lite

**Modelo:** `google/veo-3.1-lite`
**Custo:** ~R$ 2,88 (6s 720p com áudio) ou R$ 1,80 sem áudio
**Resolução máxima:** 720p (1280×720 ou 720×1280 pra 9:16)
**Durações suportadas:** 4, 6, 8 segundos
**Aspect ratios:** 9:16, 16:9
**Tempo:** ~70s

### Workflow (assíncrono - 3 etapas)

```
1. POST /api/v1/videos { model, prompt, duration, aspect_ratio } → { id, status: "pending" }
2. POLL GET /api/v1/videos/{id} a cada 5s até status = "completed"
3. GET /api/v1/videos/{id}/content?index=0 → bytes do MP4
```

### Chamada (Python)

```python
def call(method, path, body=None):
    url = path if path.startswith("http") else f"https://openrouter.ai/api/v1{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"Authorization": f"Bearer {KEY}"}
    if body:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
        if r.headers.get("Content-Type", "").startswith("application/json"):
            return json.loads(raw.decode())
        return raw  # bytes (download)

# 1. Submeter
job = call("POST", "/videos", {
    "model": "google/veo-3.1-lite",
    "prompt": VIDEO_PROMPT,
    "duration": 6,
    "aspect_ratio": "9:16",
})
job_id = job["id"]

# 2. Poll
while True:
    time.sleep(5)
    res = call("GET", f"/videos/{job_id}")
    status = res["status"]
    if status == "completed":
        break
    if status in ("failed", "error"):
        raise RuntimeError(res)

# 3. Download
mp4_bytes = call("GET", f"/videos/{job_id}/content?index=0")
Path("output.mp4").write_bytes(mp4_bytes)
```

### Prompts template (Reel Reflexivo — ver formatos.md §6)

**Tipo A — Janela de avião:**
```
A 6-second cinematic vertical 9:16 video. View from an airplane window
looking out over a sea of clouds at golden hour. The wing of the plane is
visible at the bottom-left of the frame. Camera: very subtle gentle pan,
extremely smooth, no jumps or cuts. Lighting: warm sunset light streaming
through the window casting orange and pink hues. Mood: contemplative,
aspirational, peaceful, dreamlike. Color palette: warm ambers, deep blues,
soft pinks. No on-screen text. No people visible. Editorial cinema quality.
1080x1920, 30fps.
```

**Tipo B — Pessoa de costas em paisagem:**
```
A 6-second cinematic vertical 9:16 video. Wide shot of a young woman seen
from behind, sitting on a rocky cliff edge overlooking a vast dramatic
landscape — a deep Norwegian-style fjord with steep mountains rising from
dark blue water. She wears a warm beige sweater, her hair gently moves
with the wind. Camera: very slow push-in toward the horizon, smooth,
no jumps. Lighting: blue hour just before sunset, dramatic dusky sky with
hints of deep pink and amber. Mood: contemplative, introspective,
awe-inspiring, vast. Color palette: deep blues, slate grays, warm dusk pinks.
No on-screen text. Face not visible. Editorial cinema quality.
1080x1920, 30fps.
```

**Tipo C — Idoso contemplando:**
```
A 6-second cinematic vertical 9:16 video. Older person (60-70s) sitting
on a bench overlooking a beautiful landscape — Mediterranean coast, mountains,
sunset over water. Seen from behind or 3/4, face not recognizable. They look
peaceful, reflective. Camera: subtle slow zoom out revealing more of the
landscape. Mood: wisdom, calm, "experiences over things". No on-screen text.
1080x1920, 30fps.
```

---

## 3. Comparação rápida de modelos (decididos)

| Tipo | Modelo escolhido | Custo | Por quê |
|---|---|---|---|
| Foto | `google/gemini-3.1-flash-image-preview` | R$ 0,01 | Qualidade aprovada Pedro 2026-06-01 |
| Vídeo Reel | `google/veo-3.1-lite` | R$ 2,88 | 50% mais barato que Fast com mesma resolução 720p |
| Texto (caption/headline/decision) | EU (Claude Code rodando) | R$ 0 | Decisão Pedro: "vc mesmo, nao chame llm" |
| Sourcing X | `x-ai/grok-4.3` + plugin web | R$ 0,15-0,35 | Único LLM com acesso real-time a X |

### Alternativas (caso o padrão falhe)

| Quando | Fallback |
|---|---|
| Gemini Image 500 | `google/gemini-2.5-flash-image` (mais barato, qualidade menor) |
| Veo Lite 500 | `google/veo-3.1-fast` (R$ 2,88 vs R$ 1,80 — 60% mais caro) |
| Veo demora >10min | Cancelar job, usar foto Gemini estática como fallback |

---

## 4. Sobre áudio do Veo

Veo Lite gera áudio ambient automaticamente (não dá pra desligar — `duration_seconds_without_audio` existe no schema mas modelo sempre gera som).

**Opções:**
1. **Manter** (default atual) — som ambiente do Veo é razoável (vento, ondas)
2. **Substituir** via ffmpeg com trilha livre de royalties:
   ```bash
   ffmpeg -i input.mp4 -i trilha.mp3 -c:v copy -map 0:v -map 1:a -shortest output.mp4
   ```

Padrão: manter áudio do Veo até descobrir que alguma trilha funciona melhor pra retention.

---

## 5. Limites e guardrails

- **Custo cap diário:** R$ 5 (definido em `page.yaml`). Se motor passar disso, parar e notificar Telegram.
- **Rate limits OpenRouter:** ~60 reqs/min. Não atinge em uso normal (1 post/dia).
- **Veo timeout:** se job ficar pending >10min, cancelar e logar erro.
- **Gemini Image regen:** se imagem voltar com texto AI dentro, regerar com `negative_prompt: "text, captions, watermark"` adicionado.
