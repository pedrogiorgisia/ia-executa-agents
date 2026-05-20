"""Cron job do Railway — roda a cada hora, envia o próximo item da fila.

Lê queue e state do GitHub, manda no Telegram, atualiza state.
Env vars necessárias no Railway:
  GITHUB_PAT, GITHUB_REPO
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID_NEWS_CANAL
"""
from __future__ import annotations
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

# BRT = UTC-3
BRT = timezone(timedelta(hours=-3))
HORA_INICIO = 7   # 07:00 BRT
HORA_FIM = 22     # 22:00 BRT


def gh_get_json(token: str, repo: str, path: str) -> tuple[dict | None, str | None]:
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "User-Agent": "ia-executa-agents",
        "Accept": "application/vnd.github.v3+json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            content = json.loads(base64.b64decode(data["content"]).decode("utf-8"))
            return content, data["sha"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, None
        raise


def gh_put(token: str, repo: str, path: str, content: dict, message: str, sha: str | None) -> None:
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    body = {
        "message": message,
        "content": base64.b64encode(json.dumps(content, ensure_ascii=False).encode()).decode(),
    }
    if sha:
        body["sha"] = sha
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
        "Authorization": f"token {token}",
        "User-Agent": "ia-executa-agents",
        "Content-Type": "application/json",
    }, method="PUT")
    with urllib.request.urlopen(req, timeout=15):
        pass


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_message(item: dict) -> str:
    parts = [
        f"📰 <b>{esc(item['titulo'])}</b>",
        "──────────────────",
        "",
        esc(item["aconteceu"]),
    ]
    if item.get("significa"):
        parts += ["", "💡 <b>O que isso significa pra você:</b>", f"<b>{esc(item['significa'])}</b>"]
    if item.get("fonte"):
        parts += ["", f"🔗 {item['fonte']}"]
    return "\n".join(parts)


def send_telegram(token: str, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "User-Agent": "curl/8.4.0",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except Exception as e:
        print(f"Erro Telegram: {e}")
        return False


def main() -> None:
    token_gh = os.environ["GITHUB_PAT"]
    repo = os.environ["GITHUB_REPO"]
    token_tg = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID_NEWS_CANAL"]

    agora_brt = datetime.now(BRT)
    hoje = agora_brt.date().isoformat()
    hora = agora_brt.hour

    print(f"[{agora_brt.strftime('%Y-%m-%d %H:%M')} BRT] Iniciando...")

    if hora < HORA_INICIO or hora > HORA_FIM:
        print(f"Fora do horário de envio ({HORA_INICIO}h-{HORA_FIM}h BRT). Saindo.")
        return

    # Ler state
    state, state_sha = gh_get_json(token_gh, repo, "data/telegram-state.json")
    if not state:
        print("State nao encontrado. News-master ainda nao rodou hoje?")
        return
    if state.get("date") != hoje:
        print(f"State é de {state.get('date')}, nao de hoje ({hoje}). Saindo.")
        return

    sent = state.get("sent", 0)

    # Ler queue
    queue, _ = gh_get_json(token_gh, repo, f"data/news/{hoje}/telegram-queue.json")
    if not queue:
        print(f"Queue de {hoje} nao encontrada. Saindo.")
        return

    items = queue.get("items", [])
    total = len(items)

    if sent >= total:
        print(f"Todos os {total} itens ja foram enviados hoje.")
        return

    item = items[sent]
    msg = format_message(item)
    ok = send_telegram(token_tg, chat_id, msg)

    if ok:
        novo_sent = sent + 1
        print(f"Enviado [{novo_sent}/{total}]: {item['titulo'][:60]}")
        gh_put(token_gh, repo, "data/telegram-state.json",
               {"date": hoje, "sent": novo_sent},
               f"state: {novo_sent}/{total} - {hoje}", state_sha)
    else:
        print("Falha ao enviar. Saindo com erro.")
        sys.exit(1)


if __name__ == "__main__":
    main()
