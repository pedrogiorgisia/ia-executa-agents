"""Send the combined email via Resend.

Usage:
  python send_email_resend.py <html_path> <subject>
Reads env from .env in the current working directory.
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request
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


def main():
    html_path = sys.argv[1]
    subject = sys.argv[2]
    load_env()

    api_key = os.environ["RESEND_API_KEY"]
    from_email = os.environ["RESEND_FROM_EMAIL"]
    to_email = os.environ["NEWS_EMAIL_DESTINATARIO"]

    html_body = Path(html_path).read_text(encoding="utf-8")
    payload = {
        "from": f"Pedro Giorgis <{from_email}>",
        "to": [to_email],
        "subject": subject,
        "html": html_body,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "curl/8.4.0",
            "Accept": "*/*",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"HTTP {resp.status}")
            print(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}")
        print(e.read().decode("utf-8"))
        sys.exit(1)


if __name__ == "__main__":
    main()
