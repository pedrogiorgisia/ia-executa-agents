# ia-executa-agents

Máquina de agentes de IA que cuida de marketing, criação de conteúdo e captação de leads pra empresa **Pedro Giorgis / `@ia.executa`**.

Produto vendido: Mentoria IA com Claude Code.

## O que este repo é

Este é o **projeto tech** da empresa. Contém:
- Código dos 5 agentes (Python + Claude Agent SDK)
- SQLite como fonte de verdade do Kanban
- Prompts versionados
- Skills customizadas
- Scripts de orquestração e agendamento

A documentação de **negócio** (marca, ICP, ofertas, financeiro) vive na pasta irmã `../01-negocio/` e é **somente-leitura** pra este repo.

## Fase atual

**Fase 1 Light** — operação via Claude Code no PC do Pedro. Zero custo adicional. Agentes são disparados manualmente via chat ou CLI enquanto a infraestrutura é validada.

## Setup

```bash
# 1. Clonar (futuro, quando o repo estiver no GitHub)
# git clone https://github.com/pedrogiorgisia/ia-executa-agents.git

# 2. Ambiente Python
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Variáveis de ambiente
cp .env.example .env
# Editar .env com as chaves reais

# 4. Inicializar banco
python 51-scripts/cli.py db init
```

## Como rodar

```bash
# Fase 1 Light — manual
python 51-scripts/cli.py agente_1 --action pauta-semanal
python 51-scripts/cli.py agente_2 --card-id c0001
python 51-scripts/cli.py agente_4 --publish c0001

# Futuro (Fase 2) — Task Scheduler do Windows chama schedule.py
python 51-scripts/schedule.py
```

## Stack

| Camada | Ferramenta |
|---|---|
| LLM texto | Claude (via Anthropic API) + prompt caching |
| LLM imagem | Gemini 3.1 Flash Image (free tier) |
| Publicação | Meta Graph API |
| Email | Resend (free tier) |
| Estado | SQLite |
| Orquestração | Claude Agent SDK + scripts Python |
| Observabilidade | (Fase 2) Langfuse self-hosted |
| Notificações | Bot Telegram |

## Documentação

- **GPS do projeto:** [`CLAUDE.md`](CLAUDE.md)
- **Visão em 2 páginas:** [`docs/funcional/01-visao-geral.md`](docs/funcional/01-visao-geral.md)
- **Fase atual:** [`docs/funcional/02-fase-atual.md`](docs/funcional/02-fase-atual.md)
- **Arquitetura completa:** [`docs/tecnica/00-arquitetura.md`](docs/tecnica/00-arquitetura.md)
- **Ponte pros docs de negócio:** [`docs/funcional/00-fontes-negocio.md`](docs/funcional/00-fontes-negocio.md)

## Licença

Privado — todos os direitos reservados. Não redistribuir.
