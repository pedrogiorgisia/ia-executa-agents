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
| `news-github-releases` | Releases de repos do ecossistema IA | haiku |
| `news-labs-blogs` | Blogs oficiais (Anthropic, OpenAI, DeepMind etc.) | haiku |
| `news-tech-press` | Imprensa especializada (TechCrunch, Verge etc.) | haiku |
| `news-hn-communities` | Hacker News + Reddit | haiku |

Todos usam `haiku` por padrão pra baratear coleta. O ranking final no master pode usar `sonnet`.

## Limitação importante

Subagentes do Claude Code **não podem chamar outros subagentes**. Por isso o "master" não é um subagente — é o prompt em `prompts/news/news-master.md` executado como sessão principal (manual ou via `/schedule`).
