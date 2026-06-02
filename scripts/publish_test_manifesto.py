"""Publica o carrossel manifesto no @ia.executa via Zernio.

Fluxo:
1. Lê os 5 PNGs em data/instagram/test-manifesto/
2. POST /v1/media/presign pra cada arquivo -> recebe uploadUrl + publicUrl
3. PUT cada arquivo no uploadUrl
4. POST /v1/posts com os 5 publicUrls + caption + firstComment

Antes de rodar:
- ZERNIO_API_KEY já deve estar no .env
- Account ID do @ia.executa: 6a1df37a2b2567671a8f620e (hardcoded por enquanto)
"""
from __future__ import annotations
import json
import mimetypes
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent
SLIDES_DIR = ROOT / "data" / "instagram" / "test-manifesto"

ZERNIO_BASE = "https://zernio.com/api/v1"
IG_ACCOUNT_ID = "6a1df37a2b2567671a8f620e"

CAPTION = (
    "O risco da IA nao e ela te substituir.\n"
    "E voce ficar parado enquanto outros aprendem a usar.\n\n"
    "A Mentoria IA com Claude Code e pra gestores nao-tecnicos que "
    "querem virar essa chave em 3 encontros, com turma de no maximo 5 pessoas.\n\n"
    "Link na bio para conhecer a proxima turma.\n\n"
    "#IA #ClaudeCode #Produtividade #Gestao #Mentoria "
    "#InteligenciaArtificial #FuturoDoTrabalho #Lideranca #AutomacaoIA"
)

FIRST_COMMENT = (
    "Detalhes da proxima turma e formulario de inscricao:\n"
    "https://mentoria-pedro-giorgis.netlify.app/"
)


def load_env() -> None:
    if os.environ.get("ZERNIO_API_KEY"):
        return
    env_file = ROOT / ".env"
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def http(method: str, url: str, headers: dict, body: bytes | None = None) -> tuple[int, bytes]:
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def presign(api_key: str, file_name: str, content_type: str) -> dict:
    body = json.dumps({"filename": file_name, "contentType": content_type}).encode()
    status, raw = http("POST", f"{ZERNIO_BASE}/media/presign", {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }, body)
    if status >= 300:
        raise RuntimeError(f"presign failed {status}: {raw.decode(errors='replace')[:500]}")
    return json.loads(raw.decode())


def upload(upload_url: str, file_path: Path, content_type: str) -> None:
    data = file_path.read_bytes()
    status, raw = http("PUT", upload_url, {"Content-Type": content_type}, data)
    if status >= 300:
        raise RuntimeError(f"upload failed {status}: {raw.decode(errors='replace')[:500]}")


def create_post(api_key: str, media_urls: list[str]) -> dict:
    body = json.dumps({
        "content": CAPTION,
        "mediaItems": [{"type": "image", "url": u} for u in media_urls],
        "platforms": [{
            "platform": "instagram",
            "accountId": IG_ACCOUNT_ID,
            "platformSpecificData": {"firstComment": FIRST_COMMENT},
        }],
        "publishNow": True,
    }).encode()
    status, raw = http("POST", f"{ZERNIO_BASE}/posts", {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }, body)
    if status >= 300:
        raise RuntimeError(f"create_post failed {status}: {raw.decode(errors='replace')[:1000]}")
    return json.loads(raw.decode())


def main() -> None:
    load_env()
    api_key = os.environ["ZERNIO_API_KEY"]

    pngs = sorted(SLIDES_DIR.glob("slide-*.png"))
    if len(pngs) != 5:
        print(f"Esperava 5 slides em {SLIDES_DIR}, encontrei {len(pngs)}")
        sys.exit(1)

    print(f"[1/3] Presign + upload de {len(pngs)} arquivos")
    public_urls: list[str] = []
    for png in pngs:
        ctype = mimetypes.guess_type(str(png))[0] or "image/png"
        signed = presign(api_key, png.name, ctype)
        upload(signed["uploadUrl"], png, ctype)
        public_urls.append(signed["publicUrl"])
        print(f"  [ok] {png.name} -> {signed['publicUrl'][:80]}...")

    print(f"\n[2/3] Criando post no Instagram (@ia.executa)")
    result = create_post(api_key, public_urls)

    print(f"\n[3/3] Resposta da Zernio:")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])

    post = result.get("post") or result
    pid = post.get("_id") or post.get("id") or "?"
    print(f"\n[done] Post ID: {pid}")


if __name__ == "__main__":
    main()
