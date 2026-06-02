"""Envia as noticias do top.md para o Telegram, uma mensagem por item.

Usage:
  python send_telegram_news.py <top_md_path>
Reads env from .env in the current working directory.
"""
from __future__ import annotations
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import json
from pathlib import Path


def load_env(env_path: Path = Path(".env")) -> None:
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k.strip(), v)


def parse_items(top_md: str) -> list[dict]:
    """Parse top.md into list of items with titulo, aconteceu, significa, fonte."""
    items = []
    # Split by --- separator
    blocks = re.split(r'\n---\n', top_md)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # Extract title (### heading)
        title_match = re.search(r'###\s+(.+)', block)
        if not title_match:
            continue
        title = title_match.group(1).strip()

        # Extract "O que aconteceu"
        aconteceu_match = re.search(r'\*\*O que aconteceu:\*\*\s*(.+?)(?=\n\n|\*\*|$)', block, re.DOTALL)
        aconteceu = aconteceu_match.group(1).strip() if aconteceu_match else ""

        # Extract "O que isso significa"
        significa_match = re.search(r'\*\*O que isso significa.*?:\*\*\s*(.+?)(?=\n\n|\*\*|$)', block, re.DOTALL)
        significa = significa_match.group(1).strip() if significa_match else ""

        # Extract fonte (first URL)
        fonte_match = re.search(r'\*\*Fonte:\*\*\s*(https?://\S+)', block)
        fonte = fonte_match.group(1).strip() if fonte_match else ""
        # Remove trailing pipe and second URL if present
        fonte = fonte.split(' |')[0].strip()

        if title and aconteceu:
            items.append({
                "titulo": title,
                "aconteceu": aconteceu,
                "significa": significa,
                "fonte": fonte,
            })
    return items


def esc(text: str) -> str:
    """Escape HTML special characters in plain text content."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_message(item: dict) -> str:
    """Format one item as HTML for Telegram."""
    parts = [
        f"📰 <b>{esc(item['titulo'])}</b>",
        "──────────────────",
        "",
        esc(item["aconteceu"]),
    ]
    if item["significa"]:
        parts += [
            "",
            f"💡 <b>O que isso significa pra você:</b>",
            f"<b>{esc(item['significa'])}</b>",
        ]
    if item["fonte"]:
        parts += ["", f'🔗 {item["fonte"]}']
    return "\n".join(parts)


def send_message(token: str, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "curl/8.4.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Erro ao enviar: {e}")
        return False


def main():
    top_md_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not top_md_path:
        print("Uso: python send_telegram_news.py <top_md_path>")
        sys.exit(1)

    load_env()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID_NEWS_CANAL", os.environ.get("TELEGRAM_CHAT_ID_PEDRO", ""))
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID_PEDRO nao configurados")
        sys.exit(1)

    top_md = Path(top_md_path).read_text(encoding="utf-8")
    items = parse_items(top_md)
    if not items:
        print("Nenhum item encontrado no top.md")
        sys.exit(1)

    # Header message
    from datetime import date
    hoje = date.today().strftime("%d/%m")
    header = f"🤖 <b>News IA — {hoje}</b>\n{len(items)} notícias de hoje:"
    send_message(token, chat_id, header)
    time.sleep(0.5)

    ok = 0
    for i, item in enumerate(items, 1):
        msg = format_message(item)
        success = send_message(token, chat_id, msg)
        if success:
            ok += 1
            print(f"[{i}/{len(items)}] OK — {item['titulo'][:50]}")
        else:
            print(f"[{i}/{len(items)}] ERRO — {item['titulo'][:50]}")
        time.sleep(0.8)  # evitar rate limit

    print(f"\n{ok}/{len(items)} mensagens enviadas.")
    if ok == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
