# Máquina de Agentes — Projeto Tech (`ia-executa-agents`)

> **GPS do projeto tech.** Este arquivo orienta qualquer sessão de Claude Code que abrir esta pasta. Leitura obrigatória antes de escrever código.

---

## ⚠️ Nota importante sobre estrutura

**Este projeto NÃO usa o `estrutura-template` do Pedro.**

O `estrutura-template` é o principal entregável da mentoria — mas ele serve pra **projetos de gestão/negócio**, não pra desenvolvimento de software. Forçar ele num repo Python seria ignorar 20 anos de convenções da indústria de software (src/, tests/, docs/, pyproject.toml).

Este repo usa **layout Python padrão**. A pasta irmã `../01-negocio/` é onde o `estrutura-template` é aplicado — e é lá que fica o "case real" de uso do template pra um projeto de negócio.

**Princípio da mentoria que isso reforça:** *"O método é pra gestão. Se você vai programar, use as convenções de programação."*

---

## O que é este projeto

**Uma operação automatizada por agentes de IA** que cuida de marketing, criação de conteúdo e captação de leads pra empresa `@ia.executa` (Pedro Giorgis). Produto vendido: Mentoria IA com Claude Code.

Este repo contém o **código** dos agentes. A documentação de negócio (marca, ICP, ofertas, financeiro) vive na pasta irmã `../01-negocio/` e é **somente-leitura** pra este repo.

**Nome curto:** `ia-executa-agents`
**Stack inicial:** Python 3.11+ + Claude Agent SDK + SQLite + Gemini Flash Image + Meta Graph API
**Fase atual:** Fase 1 Light — operação via chat no Claude Code, rodando no PC do Pedro

---

## Fontes de verdade externas (ler ANTES de codar)

Todo agente, em runtime, precisa consultar estas fontes. Todo dev, ao começar uma sessão séria, precisa ler também.

| Fonte | O que tem | Quando consultar |
|---|---|---|
| [`docs/funcional/00-fontes-negocio.md`](docs/funcional/00-fontes-negocio.md) | **Ponte pros docs de negócio** — posicionamento, escada de valor, programa, copys. Comece por aqui. | **Sempre**, no início de qualquer sessão |
| [`docs/tecnica/00-arquitetura.md`](docs/tecnica/00-arquitetura.md) | Arquitetura interna do projeto: 5 agentes, stack, pipeline, guardrails | **Sempre**, antes de mexer em estrutura de agente |
| [`docs/funcional/01-visao-geral.md`](docs/funcional/01-visao-geral.md) | O que este projeto é em 2 páginas | Primeira vez que alguém abre o repo |
| [`docs/funcional/02-fase-atual.md`](docs/funcional/02-fase-atual.md) | Em que fase estamos, o que falta | Pra saber o próximo passo |
| [`../CLAUDE.md`](../CLAUDE.md) | GPS macro do projeto inteiro (negócio + tech) | Quando precisar de contexto amplo |

**Regra de ouro:** os arquivos em `../01-negocio/` são **somente-leitura** pra este repo. Código nunca edita lá. Se um agente precisa atualizar estratégia, ele avisa o Pedro via Telegram; o Pedro edita o doc de negócio manualmente.

---

## Estrutura do repo (layout Python padrão)

```
02-maquina-agentes/                       ← raiz do repo git
├── CLAUDE.md                             ← este arquivo
├── README.md                             ← setup, como rodar
├── .gitignore
├── .env.example                          ← template das credenciais
├── requirements.txt                      ← dependências Python
├── pyproject.toml                        ← (futuro) config do projeto
│
├── docs/                                 ← documentação do projeto tech
│   ├── funcional/                        ← o QUE o projeto faz (lê docs do negócio)
│   │   ├── 00-fontes-negocio.md          ← ponte pros docs de ../01-negocio/
│   │   ├── 01-visao-geral.md             ← o que este projeto é em 2 páginas
│   │   └── 02-fase-atual.md              ← em que fase estamos, o que falta
│   └── tecnica/                          ← COMO o projeto é construído
│       ├── 00-arquitetura.md             ← documento de design completo (33KB)
│       └── adr/                          ← Architecture Decision Records (futuro)
│
├── src/                                  ← ★ CÓDIGO
│   ├── __init__.py
│   ├── supervisor.py                     ← orquestrador dos agentes
│   ├── agents/                           ← os 5 agentes especializados
│   │   ├── __init__.py
│   │   ├── agente_1_estrategia.py
│   │   ├── agente_2_producao.py
│   │   ├── agente_3_captacao.py
│   │   ├── agente_4_publicacao.py
│   │   └── agente_5_analytics.py
│   ├── shared/                           ← libs compartilhadas entre agentes
│   │   ├── __init__.py
│   │   ├── db.py                         ← SQLite helpers
│   │   ├── drive_reader.py               ← lê docs de ../01-negocio/
│   │   ├── claude_client.py              ← Claude com prompt caching
│   │   ├── gemini_client.py              ← Gemini Flash Image
│   │   ├── instagram_client.py           ← Meta Graph API
│   │   └── telegram_client.py            ← bot do Telegram
│   ├── prompts/                          ← prompts versionados (markdown, não código)
│   │   ├── agente_1_pauta.md
│   │   └── ...
│   └── skills/                           ← skills customizadas (markdown Claude skills)
│       ├── hook-writer-shortform/
│       ├── carousel-designer/
│       └── preparador-1on1/
│
├── scripts/                              ← entrypoints executáveis
│   ├── cli.py                            ← CLI pra rodar 1 agente manualmente
│   └── schedule.py                       ← jobs agendados (Task Scheduler do Windows)
│
├── tests/                                ← testes unitários/integração
│   └── __init__.py
│
└── data/                                 ← SQLite e artefatos locais (gitignored)
    └── agents.db                         ← ★ FONTE DE VERDADE do Kanban
```

**O que NÃO tem (intencional):**
- `01-arquivos-projeto/`, `02-tarefas-e-cronograma/`, `50-base-conhecimento/`, `51-scripts/`, `97-workspace/`, `98-backups/`, `99-temp/` — essas são pastas do estrutura-template do Pedro, que serve pra **projetos de gestão**, não pra projetos de código. Este repo usa padrão Python.

---

## Convenções de código

### Python
- **Python 3.11+** (use type hints sempre)
- **Formatação:** black (ou ruff format)
- **Linting:** ruff
- **Nomes:** snake_case pra variáveis/funções, PascalCase pra classes
- **Strings:** aspas duplas por padrão
- **Imports:** `from src.shared.db import ...` (paths absolutos a partir de src/)

### Estrutura de um agente

Todo agente vive em `src/agents/agente_N_nome.py` e expõe uma função `run()`:

```python
def run(card_id: str | None = None, dry_run: bool = True) -> dict:
    """Entrypoint do agente. Chamado pelo supervisor ou via scripts/cli.py."""
```

**Default de `dry_run` é `True`.** Agente só executa efeitos externos (publicar, enviar email) se for chamado explicitamente com `dry_run=False`.

### Chamadas ao Claude — SEMPRE com prompt caching

Nunca chamar `anthropic.messages.create()` diretamente. Sempre via `src/shared/claude_client.py`, que já injeta as fontes de verdade (posicionamento, escada, arquitetura) no system prompt com cache markers. Isso derruba o custo em ~90% a partir da 2ª chamada.

### Segredos

- **`.env`** contém todas as chaves (Anthropic, Gemini, Meta, Telegram, Resend)
- **`.env` é gitignored** — NUNCA commitar
- **`.env.example`** tem os nomes das variáveis sem valores, commitado
- Ao usar uma chave no código, ler via `os.environ` só

### SQLite

- Único banco: `data/agents.db`
- Rollback journal mode (não WAL) — menos arquivos temporários, melhor pra Drive sync
- Schema em `src/shared/db.py` — migrations via scripts idempotentes
- Backups manuais via `scripts/cli.py db backup`

---

## Como rodar (Fase 1 Light)

Por enquanto nada roda sozinho. Você dispara os agentes via Claude Code aqui no chat:

```
"Claude, bora rodar a pauta da semana"
→ eu invoco o Agente 1 via script Python, mostro resultado, você aprova
```

Ou via CLI manual:

```bash
python scripts/cli.py agente_1 --action pauta-semanal
python scripts/cli.py agente_2 --card-id c0001
python scripts/cli.py agente_4 --publish c0001
```

Na Fase 2, esses mesmos comandos vão ser disparados pelo Task Scheduler do Windows automaticamente.

---

## Pipelines em produção (Claude Code subagents)

Além dos 5 agentes Python planejados, este repo tem **pipelines leves rodando com Claude Code subagents** (zero infra, zero custo):

| Pipeline | Pasta de subagentes | Prompt orquestrador | Output |
|---|---|---|---|
| **news-curator** — curadoria diária de IA via email | [`.claude/agents/news/`](.claude/agents/news/) | [`prompts/news/news-master.md`](prompts/news/news-master.md) | Email (HTML) via Resend + `data/news/AAAA-MM-DD/top.md` |

Esses pipelines rodam via `/schedule` (Claude Code cloud) ou manualmente. Não precisam dos agentes Python, do SQLite ou do supervisor.

**Secrets necessários** (no painel `/schedule` da Anthropic, OU no `.env` local pra execução manual):
- `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `NEWS_EMAIL_DESTINATARIO` (pra envio do email)
- `GITHUB_PAT`, `GITHUB_REPO` (pra rotina commitar `historico.md` de volta)

Setup completo: [`data/news/README.md`](data/news/README.md).

---

## Skills consultadas durante o DESENVOLVIMENTO

Quando você (Claude Code) tá escrevendo código neste repo, pode invocar estas skills quando relevante:

- `claude-api` — pra garantir que as chamadas usam prompt caching corretamente
- `skill-creator` — pra criar as skills customizadas em `src/skills/`
- `copywriting`, `copy-editing` — pros prompts dos agentes de conteúdo
- `marketing-psychology` — validação dos gatilhos nos prompts
- `simplify` — revisão de código, remover over-engineering

---

## Regras de ouro

1. **Ler fontes de verdade antes de codar.** Nunca assumir o que a marca vende ou como o Pedro fala — consultar os docs em `../01-negocio/`.
2. **Prompt caching sempre.** Claude API sem caching é cara. Já escrevemos o helper — usar ele.
3. **SQLite é a única fonte de verdade do Kanban.** Nada de arquivos paralelos. Se precisa persistir estado, vai no banco.
4. **Nunca publicar/enviar sem gate humano** (Fase 1). Todo agente que causa efeito externo tem `dry_run=True` como default.
5. **Drive é somente-leitura.** Os agentes leem `../01-negocio/` mas não escrevem lá.
6. **Guardrails não-negociáveis** (ver `docs/tecnica/00-arquitetura.md §7`): budget cap, rate limit, voice lock, credentials isolation, observabilidade, kill switch.
7. **Fase 1 é zero-custo adicional.** Não adicionar serviços pagos sem confirmar antes.
8. **Código em PT-BR no nível de domínio** (`agente_1_estrategia.py`, `pauta_semanal`, etc). Código em EN no nível técnico (`db.py`, `run`, `dry_run`).
9. **Este repo NÃO usa o estrutura-template do Pedro** — é projeto de código, usa layout Python padrão. O template fica em `../01-negocio/` onde FAZ sentido.

---

*Última atualização: 2026-04-13. Documento vivo — atualizar sempre que mudar estrutura, convenção ou regra de ouro.*
