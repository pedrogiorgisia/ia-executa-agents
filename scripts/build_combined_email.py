"""Build email-combinado.html from top.md + podcast link.

Usage:
  python build_combined_email.py <top_md> <template_html> <podcast_link> <data_humana> <timestamp> <output_html>
"""
from __future__ import annotations
import html
import re
import sys
from pathlib import Path


def parse_top_md(md_text: str) -> list[dict]:
    blocks = re.split(r"\n---\n", md_text)
    items = []
    for block in blocks:
        block = block.strip()
        m_title = re.search(r"^###\s+(.+)$", block, re.MULTILINE)
        if not m_title:
            continue
        title = m_title.group(1).strip()

        def grab(label: str) -> str:
            pat = rf"\*\*{re.escape(label)}:\*\*\s*(.+?)(?=\n\n|\Z)"
            mm = re.search(pat, block, re.DOTALL)
            return mm.group(1).strip().replace("\n", " ") if mm else ""

        items.append({
            "title": title,
            "aconteceu": grab("O que aconteceu"),
            "significa": grab("O que isso significa pra você"),
            "quem": grab("Pra quem importa mais"),
            "fonte": grab("Fonte"),
        })
    return items


def render_item(item: dict) -> str:
    t = html.escape(item["title"], quote=True)
    a = html.escape(item["aconteceu"], quote=True)
    s = html.escape(item["significa"], quote=True)
    q = html.escape(item["quem"], quote=True)
    link = html.escape(item["fonte"], quote=True)
    return f"""<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin:20px 0; border-bottom:1px solid #e4e4e7; padding-bottom:20px;">
  <tr><td>
    <h2 style="margin:0 0 12px 0; font-size:17px; font-weight:600; color:#18181b; line-height:1.35;">{t}</h2>
    <p style="margin:0 0 10px 0; font-size:14px; color:#3f3f46;"><strong style="color:#18181b;">O que aconteceu:</strong> {a}</p>
    <p style="margin:0 0 10px 0; font-size:14px; color:#3f3f46;"><strong style="color:#18181b;">O que isso significa pra você:</strong> {s}</p>
    <p style="margin:0 0 14px 0; font-size:13px; color:#71717a;"><strong style="color:#52525b;">Pra quem importa mais:</strong> {q}</p>
    <a href="{link}" style="display:inline-block; padding:8px 14px; background-color:#18181b; color:#fafafa; text-decoration:none; border-radius:6px; font-size:13px; font-weight:500;">Ver fonte →</a>
  </td></tr>
</table>"""


def main():
    top_md_path, template_path, podcast_link, data_humana, timestamp_gen, out_path = sys.argv[1:7]
    md_text = Path(top_md_path).read_text(encoding="utf-8")
    template = Path(template_path).read_text(encoding="utf-8")
    items = parse_top_md(md_text)
    items_html = "\n".join(render_item(it) for it in items)
    out = (template
           .replace("{{DATA_HUMANA}}", data_humana)
           .replace("{{PODCAST_LINK}}", podcast_link)
           .replace("{{ITENS_HTML}}", items_html)
           .replace("{{TIMESTAMP_GERACAO}}", timestamp_gen)
           .replace("{{TOTAL_ITENS}}", str(len(items))))
    Path(out_path).write_text(out, encoding="utf-8")
    print(f"Wrote {out_path} with {len(items)} items")


if __name__ == "__main__":
    main()
