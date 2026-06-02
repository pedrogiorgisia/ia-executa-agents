"""Registra gastos OpenRouter (Grok/Gemini/Veo) em CSV pra auditoria.

Uso (em qualquer script que chame OpenRouter):

    from cost_tracker import register_cost
    register_cost(
        script="post.py",
        model="google/veo-3.1-lite",
        purpose="reel reflexivo - frase Mark Twain",
        cost_usd=0.48,
        tokens_in=None,    # opcional pra modelos de imagem/video
        tokens_out=None,
        extra={"duration_s": 6},  # opcional
    )

Saida: data/_gastos/openrouter.csv
Estrutura: timestamp,script,model,purpose,tokens_in,tokens_out,cost_usd,cost_brl,extra

Cotacao USD->BRL fixa em 6.0 pra calculos (atualizar se mudar muito).
"""
from __future__ import annotations
import csv
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
LEDGER = ROOT / "data" / "_gastos" / "openrouter.csv"
USD_TO_BRL = 6.0  # cotacao aprox

# Custos acumulados nesta execução (em memória). A plataforma (worker) drena isto
# após cada geração pra registrar no banco com job_id/brand_id. NÃO substitui o CSV.
SESSION_COSTS: list[dict] = []

HEADERS = [
    "timestamp",
    "script",
    "model",
    "purpose",
    "tokens_in",
    "tokens_out",
    "cost_usd",
    "cost_brl",
    "extra_json",
]


def register_cost(
    script: str,
    model: str,
    purpose: str,
    cost_usd: float,
    tokens_in: int | None = None,
    tokens_out: int | None = None,
    extra: dict | None = None,
) -> None:
    """Append uma linha ao ledger. Cria header se primeira chamada."""
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    new_file = not LEDGER.exists()

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "script": script,
        "model": model,
        "purpose": purpose,
        "tokens_in": tokens_in if tokens_in is not None else "",
        "tokens_out": tokens_out if tokens_out is not None else "",
        "cost_usd": f"{cost_usd:.6f}",
        "cost_brl": f"{cost_usd * USD_TO_BRL:.4f}",
        "extra_json": json.dumps(extra, ensure_ascii=False) if extra else "",
    }

    with LEDGER.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)

    # acumula pra plataforma drenar
    SESSION_COSTS.append({
        "script": script,
        "model": model,
        "purpose": purpose,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": round(cost_usd, 6),
        "cost_brl": round(cost_usd * USD_TO_BRL, 4),
    })


def summary(month: str | None = None) -> dict:
    """Retorna resumo de gastos (total, por modelo, por purpose).

    month: 'YYYY-MM' pra filtrar. None = todos os meses.
    """
    if not LEDGER.exists():
        return {"total_usd": 0, "total_brl": 0, "count": 0, "by_model": {}, "by_script": {}}

    total_usd = 0.0
    by_model: dict[str, float] = {}
    by_script: dict[str, float] = {}
    count = 0

    with LEDGER.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if month and not row["timestamp"].startswith(month):
                continue
            cost = float(row["cost_usd"])
            total_usd += cost
            by_model[row["model"]] = by_model.get(row["model"], 0) + cost
            by_script[row["script"]] = by_script.get(row["script"], 0) + cost
            count += 1

    return {
        "total_usd": round(total_usd, 4),
        "total_brl": round(total_usd * USD_TO_BRL, 2),
        "count": count,
        "by_model": {k: round(v, 4) for k, v in sorted(by_model.items(), key=lambda x: -x[1])},
        "by_script": {k: round(v, 4) for k, v in sorted(by_script.items(), key=lambda x: -x[1])},
    }


def main_cli() -> None:
    """CLI rapido pra ver gastos: python cost_tracker.py [YYYY-MM]"""
    import sys
    month = sys.argv[1] if len(sys.argv) > 1 else None

    s = summary(month)
    label = f"mes {month}" if month else "total"
    print(f"\n=== Gastos OpenRouter ({label}) ===")
    print(f"Total: ${s['total_usd']:.4f} (R$ {s['total_brl']:.2f}) em {s['count']} chamadas\n")

    if s["by_model"]:
        print("Por modelo:")
        for model, cost in s["by_model"].items():
            print(f"  {model:50}  ${cost:.4f}  (R$ {cost * USD_TO_BRL:.2f})")
        print()

    if s["by_script"]:
        print("Por script:")
        for script, cost in s["by_script"].items():
            print(f"  {script:30}  ${cost:.4f}  (R$ {cost * USD_TO_BRL:.2f})")


if __name__ == "__main__":
    main_cli()
