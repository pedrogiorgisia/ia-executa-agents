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

# (keywords_em_minúsculo, hashtag) — ordem importa: mais específico primeiro
_TAG_RULES: list[tuple[list[str], str]] = [
    (["openai", "chatgpt", "gpt-4", "gpt-5", "o1", "o3", "o4", "sora"], "#OpenAI"),
    (["anthropic", "claude"], "#Anthropic"),
    (["google", "gemini", "deepmind", "notebooklm", "bard"], "#Google"),
    (["microsoft", "copilot", "azure"], "#Microsoft"),
    (["meta", "llama", "whatsapp ia"], "#Meta"),
    (["apple", "siri"], "#Apple"),
    (["amazon", "aws", "alexa"], "#Amazon"),
    (["nvidia", "gpu", "chip", "semicondutor"], "#Hardware"),
    (["agente", "agent", "multi-agent", "multiagente"], "#Agentes"),
    (["open source", "código aberto", "hugging face", "ollama", "mistral"], "#OpenSource"),
    (["llm", "modelo de linguagem", "foundation model", "fine-tun", "treinamento"], "#LLM"),
    (["demiss", "layoff", "corte de funcionário", "redução de quadro"], "#Mercado"),
    (["invest", "funding", "capta", "rodada", "bilhão", "milhão", "valuation", "ipo"], "#Investimento"),
    (["regulaç", "regulament", "lei ", "governo", "congresso", "gdpr", "ai act", "política pública"], "#Regulação"),
    (["segurança", "security", "hack", "vazamento", "privacidade", "deepfake", "desinform"], "#Segurança"),
    (["produtividade", "workflow", "automação", "automate", "eficiência"], "#Produtividade"),
    (["código", "developer", "programaç", "engenharia de software", "copilot"], "#Desenvolvimento"),
    (["imagem", "vídeo", "áudio", "geração de conteúdo", "midjourney", "stable diffusion"], "#IAGenerativa"),
    (["saúde", "médico", "hospital", "medicina", "diagnóstico"], "#Saúde"),
    (["educaç", "escola", "universidade", "ensino", "aprendizado"], "#Educação"),
    (["robô", "robótica", "física", "hardware"], "#Robótica"),
    (["startup", "empreendedor"], "#Startups"),
    (["pesquisa", "research", "estudo", "paper", "benchmark"], "#Pesquisa"),
]


def generate_tags(item: dict, min_tags: int = 5, max_tags: int = 8) -> list[str]:
    text = " ".join([
        item.get("titulo", ""),
        item.get("aconteceu", ""),
        item.get("significa", ""),
    ]).lower()

    tags: list[str] = ["#IA"]  # sempre presente
    for keywords, tag in _TAG_RULES:
        if tag in tags:
            continue
        if any(kw in text for kw in keywords):
            tags.append(tag)
        if len(tags) == max_tags:
            break

    # Completa até min_tags com tags genéricas de fallback
    fallbacks = ["#Tecnologia", "#Inovação", "#FuturoDoTrabalho", "#TransformaçãoDigital", "#MachineLearning"]
    for fb in fallbacks:
        if len(tags) >= min_tags:
            break
        if fb not in tags:
            tags.append(fb)

    return tags


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
    load_env()
    token = os.environ.get("GITHUB_PAT", "")
    repo = os.environ.get("GITHUB_REPO", "")
    if not token or not repo:
        print("GITHUB_PAT ou GITHUB_REPO nao configurados")
        sys.exit(1)

    # Aceita caminho explícito ou auto-detecta o top.md de hoje
    if len(sys.argv) >= 2:
        top_md_path = Path(sys.argv[1])
    else:
        hoje = date.today().isoformat()
        top_md_path = Path(__file__).parent.parent / "data" / "news" / hoje / "top.md"

    if not top_md_path.exists():
        print(f"top.md nao encontrado: {top_md_path}")
        sys.exit(1)

    top_md = top_md_path.read_text(encoding="utf-8")
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
            item["tags"] = generate_tags(item)
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
