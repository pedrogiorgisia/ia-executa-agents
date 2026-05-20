"""Gera telegram-queue.json a partir do top.md e faz push pro GitHub.

Roda localmente após o news-master (07:00).
Usage: python scripts/generate_telegram_queue.py data/news/YYYY-MM-DD/top.md
"""
from __future__ import annotations
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from send_telegram_news import load_env, parse_items

MAX_ITEMS = 15


_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}


def url_ok(url: str) -> bool:
    """Retorna True se a URL existe. Tenta HEAD; se bloqueado, tenta GET."""
    # Tenta HEAD primeiro (rápido)
    try:
        req = urllib.request.Request(url, method="HEAD", headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=8) as r:
            if r.status == 404:
                return False
            if r.status < 400:
                return True
            # 4xx/5xx que não seja 404: cai no fallback GET
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        # 403, 405, 429, etc. — muitos sites bloqueiam HEAD, tenta GET
    except Exception:
        pass  # timeout, SSL, connection error — tenta GET

    # Fallback: GET (lê só o início da resposta para não baixar a página inteira)
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read(512)  # lê só 512 bytes pra confirmar que existe
            return r.status < 400
    except urllib.error.HTTPError as e:
        return e.code not in (404, 410)
    except Exception:
        return False


def gh_get(token: str, repo: str, path: str) -> tuple[dict | None, str | None]:
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "User-Agent": "ia-executa-agents",
        "Accept": "application/vnd.github.v3+json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            return data, data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, None
        raise


def gh_put(token: str, repo: str, path: str, content: str, message: str, sha: str | None = None) -> None:
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    body: dict = {"message": message, "content": base64.b64encode(content.encode()).decode()}
    if sha:
        body["sha"] = sha
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
        "Authorization": f"token {token}",
        "User-Agent": "ia-executa-agents",
        "Content-Type": "application/json",
    }, method="PUT")
    with urllib.request.urlopen(req, timeout=15):
        pass


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python generate_telegram_queue.py <top_md_path>")
        sys.exit(1)

    load_env()
    token = os.environ.get("GITHUB_PAT", "")
    repo = os.environ.get("GITHUB_REPO", "")
    if not token or not repo:
        print("GITHUB_PAT ou GITHUB_REPO nao configurados")
        sys.exit(1)

    top_md = Path(sys.argv[1]).read_text(encoding="utf-8")
    todos = parse_items(top_md)
    hoje = date.today().isoformat()

    # Validar URLs — descartar itens com 404 ou sem fonte
    items = []
    descartados = []
    for item in todos:
        if not item.get("fonte"):
            descartados.append((item["titulo"][:50], "sem fonte"))
            continue
        if url_ok(item["fonte"]):
            items.append(item)
            if len(items) == MAX_ITEMS:
                break
        else:
            descartados.append((item["titulo"][:50], "URL inválida"))

    for titulo, motivo in descartados:
        print(f"  [descartado] {motivo}: {titulo}")
    print(f"  {len(items)} itens válidos de {len(todos)} coletados")

    queue = {"date": hoje, "items": items}
    queue_json = json.dumps(queue, ensure_ascii=False, indent=2)

    state = {"date": hoje, "sent": 0}
    state_json = json.dumps(state, ensure_ascii=False)

    # Push queue do dia
    queue_path = f"data/news/{hoje}/telegram-queue.json"
    _, sha_q = gh_get(token, repo, queue_path)
    gh_put(token, repo, queue_path, queue_json, f"feat: telegram queue {hoje}", sha_q)
    print(f"Queue: {len(items)} itens -> {queue_path}")

    # Resetar state
    state_path = "data/telegram-state.json"
    _, sha_s = gh_get(token, repo, state_path)
    gh_put(token, repo, state_path, state_json, f"reset: telegram state {hoje}", sha_s)
    print(f"State resetado: sent=0")


if __name__ == "__main__":
    main()
