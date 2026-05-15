# News Curator — Output

Esta pasta recebe a saída diária do **news-curator**, um pipeline que coleta notícias de IA das últimas 48h e produz uma mensagem pronta pra WhatsApp.

## Estrutura

```
data/news/
├── README.md              ← este arquivo
├── historico.md           ← títulos já enviados (anti-duplicação)
└── AAAAMMDD/              ← uma pasta por dia (gitignored)
    ├── raw/
    │   ├── github-releases.md
    │   ├── labs-blogs.md
    │   ├── tech-press.md
    │   └── hn-communities.md
    ├── consolidado.md
    ├── top-5.md
    └── whatsapp.md        ← ★ msg pronta pra copiar
```

As pastas datadas (`AAAAMMDD/`) são **gitignored** — não vamos versionar o conteúdo coletado. Apenas o `historico.md` (índice) e este README são commitados.

## Como rodar

### Manual (Fase 1 — calibragem)

Abra uma sessão do Claude Code nesta pasta e cole:

```
Execute o pipeline do prompts/news/news-master.md
```

O master vai disparar os 4 subagentes em paralelo, consolidar e gerar a mensagem final em `data/news/AAAA-MM-DD/whatsapp.md`.

### Agendado (Fase 2 — após calibragem)

Use a skill `/schedule` do Claude Code:

```
/schedule
```

Configure pra rodar todo dia às 08:00 BRT com o prompt apontando pra `prompts/news/news-master.md`.

**Importante:** `/schedule` roda na cloud da Anthropic, então os subagentes em `.claude/agents/news/` precisam estar **commitados no GitHub** (já estão).

## Fontes monitoradas

Total de fontes: ~20, distribuídas em 4 subagentes:

- **`news-github-releases`** — 9 repos via `.atom` (Claude Code, Gemini CLI, Aider, Continue, ElevenLabs, llama.cpp, vLLM, Codex)
- **`news-labs-blogs`** — 8 labs (Anthropic, OpenAI, DeepMind, Mistral, xAI, Perplexity, Cohere, Meta AI)
- **`news-tech-press`** — 5 veículos (TechCrunch, The Verge, Ars Technica, MIT Tech Review, VentureBeat)
- **`news-hn-communities`** — Hacker News + r/LocalLLaMA

## ICP da mensagem

Executivos, gestores e profissionais de produto interessados em IA. **Não devs hardcore.**
- Critério de inclusão: muda decisão prática de uso/compra de IA
- Critério de exclusão: detalhe técnico denso, opinião sem ação, hype sem produto
