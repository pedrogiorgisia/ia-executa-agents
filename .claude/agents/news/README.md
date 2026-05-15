# News Curator — Subagentes

Esta pasta contém os 4 subagentes que compõem o pipeline de curadoria diária de notícias de IA.

## Arquitetura

```
   prompts/news/news-master.md  (orquestrador — disparado por /schedule)
              │
              │ dispara 4 subagentes em paralelo
              ▼
   ┌──────────┬──────────────┬───────────┬──────────────┐
   │ github-  │  labs-blogs  │ tech-     │ hn-          │
   │ releases │              │ press     │ communities  │
   └──────────┴──────────────┴───────────┴──────────────┘
              │
              ▼
   data/news/AAAA-MM-DD/raw/*.md
              │
              ▼
   master consolida → rankeia top 5 → gera whatsapp.md
```

## Subagentes

| Nome | O que coleta | Modelo |
|---|---|---|
| `news-github-releases` | Releases de repos do ecossistema IA | sonnet |
| `news-labs-blogs` | Blogs oficiais (Anthropic, OpenAI, DeepMind etc.) | sonnet |
| `news-tech-press` | Imprensa especializada (TechCrunch, Verge etc.) | sonnet |
| `news-hn-communities` | Hacker News + Reddit | sonnet |

Todos usam `sonnet` — qualidade da curadoria > custo. Subagente com Haiku tende a ser literal demais ("transcrevo o que vi") e perde o juízo de relevância.

## Limitação importante

Subagentes do Claude Code **não podem chamar outros subagentes**. Por isso o "master" não é um subagente — é o prompt em `prompts/news/news-master.md` executado como sessão principal (manual ou via `/schedule`).
