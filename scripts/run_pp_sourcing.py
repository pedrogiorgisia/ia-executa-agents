"""Sourcing PP-Travel — 1-2 queries Grok por dia, direcionadas ao pilar do dia.

Mapeamento (definido em pages/pp-travel/sourcing.md):
  Seg → Educação    → Q2 (milhas) + Q7 (news BR)
  Ter → Inspiração  → Q4 (destinos viral)
  Qua → Engajamento → Q6 (trending geral)
  Qui → Prova Soc   → Q3 (achei passagem)
  Sex → Conversão   → Q1 (cias)
  Sáb → Inspiração Reflexiva → nenhuma query (evergreen)
  Dom → Engajamento → Q6 (trending geral)

Saida: data/instagram/pp-travel/YYYY-MM-DD/
  - q{N}_raw.md   (1 por query)
  - digest.md     (consolidado)

Filtros HARD aplicados (politica, tragedia, concorrentes) - ver sourcing.md.
"""
from __future__ import annotations
import json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

# UTC-3 -> dia da semana BRT
NOW = datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")
WEEKDAY = NOW.strftime("%A").lower()  # monday, tuesday, etc

OUT = ROOT / "data" / "instagram" / "pp-travel" / TODAY
OUT.mkdir(parents=True, exist_ok=True)

for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = "x-ai/grok-4.3"

# ---- FILTROS HARD em TODA query ----
GLOBAL_FILTERS = """
FILTROS HARD (CRITICOS - aplicar sempre):
- EXCLUIR politica: tweets de politicos, presidentes, ministros, governos. Se a info
  e relevante (recorde turismo, etc.), pegar de fonte INSTITUCIONAL/neutra (PANROTAS,
  Ministerio Turismo institucional, NAO de pessoa publica governante).
- EXCLUIR tragedias: mortes, acidentes, falencias, demissoes.
- EXCLUIR concorrentes: CVC, Decolar, 123Milhas, MaxMilhas, Vai de Promo, Submarino Viagens.
- EXCLUIR polemicas com cias aereas (relato de cliente brigando).
- EXCLUIR futebol-opiniao (Copa OK como CONTEXTO de viagem, mas nao comentar desempenho).

PARA CADA TWEET retornar EXATAMENTE:
(a) @autor, (b) texto (max 200 chars), (c) likes ou views,
(d) link, (e) por que importa pra PP-Travel.

CROSS-REFERENCE: se MESMO tema aparece em 2+ contas diferentes, marcar [CROSS-VALIDATED].
""".strip()


# ---- DEFINICOES das 7 queries ----
QUERIES = {
    "Q1": {
        "label": "Cias aereas BR",
        "prompt": (
            "Busque em X.com tweets em PORTUGUES das ULTIMAS 24H sobre LATAM, GOL, AZUL, "
            "AVIANCA, TAP ou IBERIA no contexto brasileiro. Foque em: promocoes, mudancas "
            "de regra, novas rotas, novos voos.\n\n"
            "Liste os 8 tweets mais relevantes. Priorize likes>200.\n\n"
            + GLOBAL_FILTERS
        ),
    },
    "Q2": {
        "label": "Programas de milhas",
        "prompt": (
            "Busque em X.com tweets em PORTUGUES das ULTIMAS 48H sobre programas de milhas: "
            "LATAM PASS, SMILES, TUDOAZUL, LIVELO, ESFERA, MULTIPLUS. Foque em: vencimento, "
            "bonus de transferencia, bugs/oportunidades, mudancas de regra.\n\n"
            "Liste 8 tweets relevantes. Priorize likes>100.\n\n"
            + GLOBAL_FILTERS
        ),
    },
    "Q3": {
        "label": "Achei passagem barata (viral)",
        "prompt": (
            "Busque em X.com tweets em PORTUGUES das ULTIMAS 72H com padroes 'achei "
            "passagem', 'passagem por R$', 'voo barato', 'consegui passagem'. Foco em "
            "PESSOAS REAIS (nao bots de promo). Quais destinos estao bombando em "
            "'consegui barato'?\n\n"
            "Liste 8 tweets com engagement visivel (>50 likes ou >100 reposts).\n\n"
            + GLOBAL_FILTERS
        ),
    },
    "Q4": {
        "label": "Destinos virais com foto/video",
        "prompt": (
            "Busque em X.com tweets em PORTUGUES dos ULTIMOS 7 DIAS sobre destinos turisticos "
            "com fotos ou videos que VIRALIZARAM. Foque em tweets com likes>500. "
            "Quais destinos brasileiros e internacionais estao bombando visualmente esta "
            "semana?\n\n"
            "Liste 10 tweets. Indique tipo de midia (foto/video) e destino.\n\n"
            + GLOBAL_FILTERS
        ),
    },
    "Q5": {
        "label": "Hashtags travel trending",
        "prompt": (
            "Busque em X.com tweets em PORTUGUES das ULTIMAS 24H com hashtags do nicho "
            "travel: #turismo, #viagem, #milhas, #dicasdeviagem, #passagensaereas. "
            "Liste os 8 tweets que mais geraram interacao. Identifique 3 temas dominantes.\n\n"
            + GLOBAL_FILTERS
        ),
    },
    "Q6": {
        "label": "Trending geral (cross-pollinate)",
        "prompt": (
            "Quais sao os 5 assuntos MAIS COMENTADOS no X Brasil HOJE (ultimas 12h)? "
            "Para cada um:\n"
            "(1) descreva em 1 linha,\n"
            "(2) cite 1 tweet (autor + link),\n"
            "(3) avalie se tem ANGULO criativo possivel para PP-Travel. Se nao tem "
            "angulo, escreva 'sem angulo'.\n\n"
            + GLOBAL_FILTERS
        ),
    },
    "Q7": {
        "label": "News travel BR (jornalistico)",
        "prompt": (
            "Busque noticias jornalisticas brasileiras das ULTIMAS 48H sobre setor de viagens, "
            "turismo, companhias aereas, programas de milhas. Fontes preferidas: PANROTAS, "
            "Mercado e Eventos, Melhores Destinos, Passageiro de Primeira, Mundo do Marketing, "
            "Valor Investe.\n\n"
            "Liste 5-7 noticias com: titulo, fonte, link, 1 frase resumo, por que importa pra PP.\n\n"
            + GLOBAL_FILTERS
        ),
    },
}


# ---- MAPA: dia da semana -> queries a rodar ----
DAILY_PLAN = {
    "monday":    ["Q2", "Q7"],  # Educacao
    "tuesday":   ["Q4"],         # Inspiracao
    "wednesday": ["Q6"],         # Engajamento
    "thursday":  ["Q3"],         # Prova Social
    "friday":    ["Q1"],         # Conversao
    "saturday":  [],             # Inspiracao Reflexiva (sem Grok)
    "sunday":    ["Q6"],         # Engajamento
}

# Pilar do dia (apenas pra log/header — motor real lê do page.yaml)
PILAR_DO_DIA = {
    "monday": "Educação",
    "tuesday": "Inspiração",
    "wednesday": "Engajamento",
    "thursday": "Prova Social",
    "friday": "Conversão",
    "saturday": "Inspiração Reflexiva",
    "sunday": "Engajamento",
}


def call_grok(qid: str, q: dict) -> dict:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": q["prompt"]}],
        "plugins": [{"id": "web", "max_results": 12}],
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ia.executa",
            "X-Title": "PP-Travel Sourcing",
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"id": qid, **q, "error": f"HTTP {e.code}: {e.read().decode()[:300]}", "elapsed": time.time() - t0}
    elapsed = time.time() - t0
    msg = resp["choices"][0]["message"]
    return {
        "id": qid,
        **q,
        "elapsed": elapsed,
        "content": msg.get("content") or "",
        "annotations": msg.get("annotations") or [],
        "tokens_in": resp.get("usage", {}).get("prompt_tokens"),
        "tokens_out": resp.get("usage", {}).get("completion_tokens"),
        "error": None,
    }


def main() -> None:
    queries_to_run = DAILY_PLAN.get(WEEKDAY, [])
    pilar = PILAR_DO_DIA.get(WEEKDAY, "?")

    print(f"[run] {NOW.strftime('%Y-%m-%d %H:%M:%S')} {WEEKDAY.title()}")
    print(f"[pilar] {pilar}")
    print(f"[queries] {', '.join(queries_to_run) if queries_to_run else 'NENHUMA (Inspiracao Reflexiva e evergreen)'}\n")

    if not queries_to_run:
        digest = (
            f"# Digest PP-Travel — {TODAY} ({WEEKDAY.title()})\n\n"
            f"**Pilar do dia:** {pilar}\n\n"
            f"**Nenhuma query Grok executada** — sabado e dedicado a Inspiracao Reflexiva,\n"
            f"que usa evergreen (calendar + frases-ancora de voice.md).\n\n"
            f"O motor deve consultar:\n"
            f"- `pages/pp-travel/voice.md` (banco de frases reflexivas)\n"
            f"- `pages/pp-travel/formatos.md` §6 (Reel Reflexivo)\n"
            f"- `pages/pp-travel/pilares.md` (Inspiracao Reflexiva)\n"
            f"- `pages/pp-travel/historico.md` (dedup)\n"
        )
        (OUT / "digest.md").write_text(digest, encoding="utf-8")
        print(f"[saved] {OUT/'digest.md'}")
        return

    print(f"[run] disparando {len(queries_to_run)} query(s) em paralelo (Grok 4.3 + plugin web)\n")
    t0 = time.time()
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=len(queries_to_run)) as pool:
        future_to_qid = {pool.submit(call_grok, qid, QUERIES[qid]): qid for qid in queries_to_run}
        for fut in as_completed(future_to_qid):
            res = fut.result()
            results.append(res)
            status = "ERR" if res.get("error") else "OK "
            tok = f"in={res.get('tokens_in', '?')} out={res.get('tokens_out', '?')}" if not res.get("error") else ""
            ann = f"{len(res.get('annotations', []))}srcs" if not res.get("error") else ""
            print(f"  [{status}] {res['id']} {res['label']:32} {res['elapsed']:.1f}s {tok} {ann}")
            if res.get("error"):
                print(f"        {res['error'][:200]}")

    elapsed_total = time.time() - t0
    # Ordena pela ordem do plano (Q2, Q7) ao inves de ordem de chegada
    results.sort(key=lambda r: queries_to_run.index(r["id"]))

    print(f"\n[done] total {elapsed_total:.1f}s")

    # Custo estimado + registro por query
    from cost_tracker import register_cost
    tot_in = sum((r.get("tokens_in") or 0) for r in results)
    tot_out = sum((r.get("tokens_out") or 0) for r in results)
    # Grok 4.3: $1.25/MTok input, $2.50/MTok output
    cost_usd = (tot_in * 1.25 / 1_000_000) + (tot_out * 2.50 / 1_000_000)
    cost_brl = cost_usd * 6
    print(f"[cost]  ~${cost_usd:.4f} (~R$ {cost_brl:.2f}) | tokens in/out: {tot_in:,}/{tot_out:,}")
    # Registro um por query (granular)
    for r in results:
        if r.get("error"):
            continue
        r_in = r.get("tokens_in") or 0
        r_out = r.get("tokens_out") or 0
        r_cost = (r_in * 1.25 / 1_000_000) + (r_out * 2.50 / 1_000_000)
        register_cost(
            script="run_pp_sourcing.py",
            model=MODEL,
            purpose=f"{r['id']} {r['label']} ({pilar})",
            cost_usd=r_cost,
            tokens_in=r_in,
            tokens_out=r_out,
        )

    # Salva raw de cada query
    for r in results:
        if r.get("content"):
            (OUT / f"{r['id'].lower()}_raw.md").write_text(
                f"# {r['id']} — {r['label']}\n\n"
                f"**Elapsed:** {r['elapsed']:.1f}s · Tokens in/out: {r.get('tokens_in')}/{r.get('tokens_out')} · Sources: {len(r['annotations'])}\n\n"
                f"---\n\n{r['content']}\n\n"
                f"---\n\n## Sources (X.com annotations)\n\n"
                + "\n".join(
                    f"- {a.get('url_citation', {}).get('url', '')}" for a in r["annotations"]
                ),
                encoding="utf-8",
            )

    # Digest consolidado
    lines = [
        f"# Digest PP-Travel — {TODAY} ({WEEKDAY.title()})",
        f"",
        f"**Pilar do dia:** {pilar}",
        f"**Queries executadas:** {', '.join(queries_to_run)}",
        f"**Tempo total:** {elapsed_total:.1f}s · Custo: ~R$ {cost_brl:.2f}",
        f"",
        f"---",
        f"",
    ]
    for r in results:
        lines.append(f"## {r['id']} — {r['label']}")
        lines.append("")
        if r.get("error"):
            lines.append(f"_ERRO: {r['error']}_")
        else:
            lines.append(r["content"])
            lines.append("")
            lines.append(f"_{len(r['annotations'])} sources · {r['elapsed']:.1f}s · in={r['tokens_in']} out={r['tokens_out']}_")
        lines.append("")
        lines.append("---")
        lines.append("")

    (OUT / "digest.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[saved] {OUT/'digest.md'}")
    print(f"[saved] {len(results)} raw files em {OUT}")


if __name__ == "__main__":
    main()
