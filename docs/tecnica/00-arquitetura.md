# Arquitetura da Máquina de Agentes — Pedro Giorgis

> **Documento de design.** Define como a operação automatizada por agentes de IA vai ser construída: quais agentes existem, como se comunicam, qual stack usar, como observar, onde colocar humano no loop e quais são as regras não-negociáveis.
>
> **Baseado em pesquisa do estado da arte em abr/2026** — fontes linkadas ao final. Este é um doc vivo; revisar conforme a construção avançar.
>
> **Dependências:**
> - [01-negocio/.../00-posicionamento.md](../../../01-negocio/01-arquivos-projeto/01-marca-posicionamento/00-posicionamento.md) — TODO agente lê isto antes de gerar qualquer conteúdo
> - [01-negocio/.../00-escada-de-valor.md](../../../01-negocio/01-arquivos-projeto/02-ofertas/00-escada-de-valor.md) — define pra onde empurrar o lead

---

## 1. Resumo executivo — as 7 decisões-chave

1. **Framework de orquestração:** começar com **Claude Agent SDK + Claude Code** como orquestrador principal, usando MCPs pra integrações externas. Evoluir pra **LangGraph** se/quando precisar de grafos estaduais complexos. **Não usar CrewAI ou AutoGen** — não compensam pro nosso caso.
2. **Padrão arquitetural:** **Supervisor/Worker** com 5 workers especializados (o padrão mais usado em 2026 e o que mais combina com o caso).
3. **Observabilidade:** **Langfuse self-hosted** no Railway (MIT, free, dados ficam com a gente). Não-negociável: sem observabilidade, não entra em produção.
4. **Estado/Kanban:** **SQLite + tabela única de tarefas + eventos** orquestrado pelo Claude Agent SDK. Simples. Evoluir pra Prefect/Temporal só se crescer muito.
5. **Nível de autonomia:** **"Bounded agent com human-in-the-loop em gates críticos"** — NÃO buscar autonomia total. Pedro aprova conteúdo antes de publicar (gate via Telegram — já está configurado no Claude Code dele).
6. **Stack de conteúdo Fase 1 (zero-custo):** posts de **texto + carrossel de imagens**, sem vídeo. **Gemini 3.1 Flash Image (Nano Banana 2)** pra imagens (500/dia grátis) + Claude pra texto. Publicação via **Meta Graph API oficial** (grátis, 200 calls/hora). Vídeo/avatar ficam pra Fase 2 — quando já tiver receita das turmas 1-2 pra pagar HeyGen.
7. **Limite de cadeia:** nenhum workflow autônomo pode ter **mais de 5 passos sem aprovação humana**. Motivo: 85% de acurácia por passo = ~20% de sucesso em 10 passos. Matemática fatal.

### 1.1 Regra de ouro da Fase 1: custo zero adicional

Tudo na Fase 1 roda em cima do que o Pedro **já paga**:
- **Claude** — assinatura Claude Pro existente (via Claude Code)
- **Hospedagem** — Railway que já tem projeto rodando
- **Ferramentas grátis** — Gemini Flash Image, Meta Graph API, Resend, Langfuse, Telegram bot, Brave Search MCP (free tier)

Custo adicional da Fase 1: **R$ 0/mês**. Só sobe pra Fase 2 quando houver receita pra justificar.

---

## 2. Princípios — o que aprendemos com 2025 (e não vamos repetir)

Estes princípios vêm de post-mortems reais de sistemas de agentes em produção. Cada um é uma dor que alguém sentiu.

### 2.1 Autonomia total é o alvo errado
*"Os vencedores não serão as empresas perseguindo IA totalmente autônoma. Serão as que encontram workflows de alto valor onde um agente limitado pode gerar impacto mensurável, com avaliação adequada e salvaguardas human-in-the-loop."*

Nossa abordagem: autônomo onde for barato errar (pesquisa, rascunho), humano no gate onde for caro errar (publicação, compra, DM pra cliente).

### 2.2 A matemática dos passos
Se um agente tem 85% de acurácia por ação, um workflow de 10 passos só funciona em ~20% dos casos. **Corolário:** workflows devem ser curtos OU ter checkpoints entre passos.

### 2.3 Black box é inaceitável
*"Sem ferramentas de observabilidade, problemas passam despercebidos até causarem dano real."*

Corolário: observabilidade **antes** de qualquer agente rodar em produção.

### 2.4 Identidade dos agentes
Agentes precisam de **suas próprias credenciais**, não piggyback no login do usuário. Caso real: o Google Antigravity deletou o drive inteiro de um usuário em vez de uma pasta específica. Permissões por agente, sandbox, tokens próprios.

### 2.5 Anti-padrões de plataforma
Instagram e afins punem pesado "AI-slop" e over-automation. Mais de 2 posts/dia via API = shadowban. Conteúdo genérico = penalizado. **Qualidade > volume.**

### 2.6 Modelo não é mais o gargalo
Os frontier models já são "bons o suficiente". O gargalo virou **engenharia de agentes**: observabilidade, orquestração, avaliação. É onde o trabalho de verdade mora.

---

## 3. Os 5 agentes — papéis refinados

Mesma estrutura da proposta original, mas com escopos redefinidos pra respeitar o princípio dos 5 passos máximos sem gate.

```
                    ┌─────────────────────────┐
                    │     SUPERVISOR          │
                    │  (Claude Code +         │
                    │   Agent SDK loop)       │
                    │                         │
                    │  - lê posicionamento    │
                    │  - lê escada de valor   │
                    │  - orquestra o Kanban   │
                    │  - dispara workers      │
                    │  - escala pro humano    │
                    └────────────┬────────────┘
                                 │
        ┌────────────┬───────────┼───────────┬────────────┐
        ▼            ▼           ▼           ▼            ▼
  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
  │ Agente 1 │ │ Agente 2 │ │ Agente 3│ │ Agente 4 │ │ Agente 5 │
  │ Estratégia│ │ Produção │ │ Captação│ │ Publicação│ │ Analytics│
  │   de     │ │     de   │ │   de    │ │    e     │ │    e     │
  │ Conteúdo │ │ Conteúdo │ │  Leads  │ │ Distribuição│Otimização│
  └──────────┘ └──────────┘ └─────────┘ └──────────┘ └──────────┘
```

### Agente 1 — Estratégia de Conteúdo
**Missão:** decidir **o que** publicar na próxima semana.

**Input:** posicionamento + escada de valor + tendências da semana (via Brave Search MCP) + analytics da semana anterior (do Agente 5).

**Output:** pauta semanal com N cards no Kanban (coluna "Backlog"), cada card contendo: hook, ângulo, perfil-alvo (um dos 19 perfis do ICP), call-to-action, objetivo do post (topo/meio/fundo de funil).

**Guardrails:**
- Sempre referencia o posicionamento (não inventa ângulos novos sem revisão)
- Usa um dos perfis do ICP, nunca genérico
- Nunca usa palavra do "território inimigo" (prompt mágico, hack, guru)

**Gate humano:** Pedro aprova a pauta semanal de uma vez (dentro do Telegram) antes de virar produção.

---

### Agente 2 — Produção de Conteúdo

#### Fase 1 (zero-custo): posts de texto + carrossel de imagens

**Missão:** transformar cada card aprovado em **um asset publicável em formato texto + imagem**.

**Input:** 1 card da coluna "Em Produção".

**Output:** pacote com: legenda final (hook + corpo + CTA), carrossel de 3-7 imagens (cada slide com 1 ideia), thumbnail do slide 1, hashtags.

**Stack Fase 1:**
- **Claude (via Claude Code + Agent SDK)** — gera copy completa a partir do posicionamento + hook do card. Já pago.
- **Gemini 3.1 Flash Image (Nano Banana 2)** — gera os slides do carrossel. **500 imagens/dia grátis**, 4K, sem cartão de crédito. Fonte: [Google AI](https://ai.google.dev/gemini-api/docs/image-generation).
- **Pollinations.ai** — fallback gratuito sem signup pra imagens (Flux, GPT Image Large, Seedream). Se o Gemini estourar quota ou der problema.
- **Templates de carrossel em HTML + Playwright** — pra slides de texto puro (quando não precisa gerar imagem do zero, tipo quote cards, frameworks, listas). HTML renderizado → screenshot PNG. Zero custo.

**Guardrails:**
- Formato quadrado (1080x1080) pra posts, vertical (1080x1350) pra carrossel
- Carrossel: 3-7 slides, cada slide com 1 ideia só
- Hook na legenda nos primeiros 3 segundos de leitura (= ~10 palavras)
- Nunca gerar se o card não tem perfil-alvo definido
- Imagens sempre respeitam identidade visual (a definir em `00-marca-posicionamento/`)

**Gate humano:** Pedro aprova o pacote finalizado antes de ir pra publicação. Revisão no Telegram (preview das imagens + legenda). Aprovar/rejeitar com reação.

#### Fase 2 (futuro, quando houver receita): vídeo com avatar

Quando a máquina já tiver validado funil com texto+imagem e houver caixa das turmas pra cobrir custos, migrar pra vídeo:

- **HeyGen Video Agent** — hub único: prompt → avatar Pedro + voz clonada (ElevenLabs embutido) → B-roll (Sora 2, Veo 3.1) → legendas → vídeo em ~4 min.
- **Dependências:** gravar amostra de voz do Pedro (~2 min) e vídeo de referência (~1 min) pra treinar o avatar.
- **Trigger pra ativar:** turma 1 rodada + receita entrando.

---

### Agente 3 — Captação de Leads
**Missão:** gerenciar **3 funis de lead magnet em paralelo**, cada um mirando um bucket do ICP, todos afunilando pra mesma turma.

**Os 3 lead magnets:**

| # | Nome | ICP-alvo | Fonte |
|---|---|---|---|
| 1 | **Analisador de Voz** | Universal (todos os 19 perfis) | `brand-voice-analyzer` adaptado PT-BR |
| 2 | **Preparador de 1-on-1** | PMs, gerentes, coordenadores (ICP #1) | Criar do zero |
| 3 | **Review Estratégico** | C-level, founders (ICP #2) | `product-strategist` adaptado PT-BR |

Cada um com **seu próprio hook, landing, vídeo de 5 min e sequência de nurture** — mas todos com a mesma mentoria no final.

**Input:** visitor que baixa qualquer um dos 3 → email capturado com flag de qual magnet.

**Output:** sequência de 5 emails de nurture específica do magnet, que leva o lead à turma.

**Responsabilidades:**
- Receber opt-in, enviar ZIP do magnet + vídeo de 5 min
- Disparar 5 emails específicos do funil daquele magnet:
  - Email 1: welcome + confirmação
  - Email 2: caso real de alguém usando esse magnet específico
  - Email 3: objeção típica do perfil-alvo do magnet
  - Email 4: prova social / depoimento
  - Email 5: convite pra turma com ancoragem de preço (usa `customer-success-manager`)
- Se lead responder qualquer email → escala pro Pedro (`sales-engineer` ajuda Pedro a preparar resposta técnica)

**Stack:**
- **Resend** free tier (3k/mês, 100/dia) pra envio
- **SQLite** pra estado do funil por lead (coluna `magnet_source` indica qual funil)
- **15 templates pré-aprovados** (5 por magnet × 3 magnets)
- Skills consultadas: `customer-success-manager`, `sales-engineer`, `email-sequence`, `copywriting`

**Guardrails:**
- Emails NUNCA saem sem aprovação em lote do Pedro (15 templates aprovados uma vez)
- Respeitar opt-out sempre
- Nunca enviar antes do horário local razoável
- Max 5 emails por lead, daí stop
- Lead que baixa 2 magnets diferentes → trata como 1 lead com maior intenção

**Gate humano:** Pedro aprova os 15 templates **uma vez**. Depois roda sozinho. Resposta de lead vira notificação imediata.

---

### Agente 4 — Publicação e Distribuição
**Missão:** publicar o asset aprovado nos canais certos, no horário certo.

**Input:** card da coluna "Agendado" com asset + legenda + janela de publicação.

**Output:** post publicado + link + registro no Kanban (coluna "Publicado").

**Stack Fase 1 (zero-custo):**
- **Meta Graph API oficial** — 100% gratuita, sem mensalidade, sem per-call. Limite de 200 calls/hora por conta (muito acima do nosso uso de 2 posts/dia). Fonte: [Instagram Graph API Guide 2026](https://elfsight.com/blog/instagram-graph-api-complete-developer-guide-for-2026/).
- **Requisito:** conta **Business ou Creator** (gratuita, só converter a conta). Conta pessoal não tem acesso à API.
- **LinkedIn Posts API** — também gratuita via OAuth.
- **Scheduling:** tabela no SQLite — nunca publicar 2x no mesmo dia
- **Cross-posting opcional:** LinkedIn quando o conteúdo casar

**Guardrails:**
- Nunca > 2 posts/dia (anti-shadowban — limite mais restrito que o da API, por segurança)
- Nunca republicar o mesmo conteúdo em < 30 dias
- Publicação só acontece se o card tem flag "Pedro aprovou" = true
- Respeitar janela de horário (ex.: nunca postar entre 00h-06h)

**Gate humano:** implícito no card (só publica o que Pedro aprovou na saída do Agente 2).

**Nota histórica:** a primeira versão deste doc recomendava Late (GetLate) pra evitar shadowban. Revisando a documentação de 2026, a Meta Graph API oficial é segura e gratuita — o risco de shadowban é de API não-oficial (scraping), não da oficial. Late fica como opção futura SE o Pedro quiser unificar IG + TikTok + YouTube num só provedor.

---

### Agente 5 — Analytics e Otimização
**Missão:** medir o que funciona, realimentar o Agente 1.

**Input:** métricas puxadas do Instagram/LinkedIn/email (via Late MCP ou Graph API oficial de analytics).

**Output:** relatório semanal + insights acionáveis pro Agente 1 na próxima rodada de pauta.

**Métricas core (da escada):**
- Impressões, engajamento, saves, shares por post
- Conversão post → clique no link do lead magnet
- Conversão email nurture → clique → turma
- NPS das turmas
- Receita por canal

**Guardrails:**
- Relatório é só dado, não decide sozinho mudar de rumo
- Recomendações vão pro Pedro em relatório semanal (Telegram digest toda segunda 08h)
- Nunca muda pesos de perfil-alvo sem aprovação do Pedro

**Gate humano:** relatório semanal com recomendações → Pedro confirma → Agente 1 aplica na próxima pauta.

---

## 4. Stack recomendada (ponta a ponta)

### 4.1 Fase 1 — zero-custo adicional

Tudo roda em cima do que o Pedro já paga (Claude Pro + Railway). **Custo adicional: R$ 0/mês.**

| Camada | Tool | Custo | Por quê |
|---|---|---|---|
| **Orquestrador** | Claude Code + Claude Agent SDK | Já pago (Claude Pro) | Já é o ambiente do Pedro. Agent SDK é *tool-use-first*, simples, MCP nativo. |
| **Framework multi-agente** | Agent SDK como base | Já pago | LangGraph é melhor pra grafos estaduais complexos — começar leve, migrar depois se precisar. |
| **Estado / Kanban** | SQLite + FastAPI | Grátis (rodando no Railway) | Baixa fricção. Tabelas: `cards`, `events`, `leads`. |
| **Hospedagem** | **Railway** | Já pago | Todos os serviços num projeto só: FastAPI, Langfuse, workers, bot Telegram. |
| **Observabilidade** | **Langfuse self-hosted** (Docker no Railway) | Grátis (MIT) | Traces, prompts, tokens, custos por agente. Dados nunca saem do Pedro. |
| **Texto** | Claude (via Agent SDK) | Já pago | Copy, roteiros, legendas, respostas. |
| **Geração de imagens** | **Gemini 3.1 Flash Image (Nano Banana 2)** | **500/dia grátis** | 4K, sem cartão. Fonte: [Google AI docs](https://ai.google.dev/gemini-api/docs/image-generation). |
| **Fallback de imagens** | Pollinations.ai | Grátis sem signup | Flux, GPT Image Large, Seedream. Backup se Gemini falhar/estourar quota. |
| **Templates de slide** | HTML + Playwright (screenshot) | Grátis | Pra quote cards, frameworks, listas — HTML renderizado vira PNG. |
| **Publicação** | **Meta Graph API oficial** (Instagram + Facebook) | **Grátis** | 200 calls/hora. Exige conta Business/Creator (gratuita). |
| **Publicação LinkedIn** | LinkedIn Posts API | Grátis | Via OAuth. |
| **Pesquisa de tendências** | Brave Search MCP | Free tier (2k queries/mês) | Padrão do Stormy playbook. Suficiente pra começar. |
| **Email** | Resend | Free tier (3k/mês, 100/dia) | Nurture do lead magnet. |
| **Gate humano** | Telegram bot (MCP) | Grátis | Já configurado no Claude Code do Pedro. Aprovação via reação. |
| **Scheduling** | cron do sistema ou Claude Code `/loop` | Grátis | Rodadas periódicas (pauta segunda, publicação diária). |

### 4.2 Fase 2 — quando houver receita

Upgrades previstos quando as turmas 1-2 gerarem receita:

| Upgrade | Custo estimado/mês | Quando |
|---|---|---|
| HeyGen Video Agent (vídeo+avatar+voz) | USD 49-99 (Creator/Business) | Depois da turma 1 rodada |
| Langfuse Cloud (se não quiser mais self-host) | USD 0-29 (tem free tier) | Só se o Pedro não quiser manter o Docker |
| Late (GetLate) — se quiser unificar IG+TikTok+YouTube | USD 14/mês | Só se expandir pra TikTok e YouTube |
| Brave Search API tier pago | USD 5-10/mês | Se esturar as 2k queries/mês grátis |

### 4.3 Skills consumidas pelos agentes

Skills de marketing/produto que ficam instaladas em `~/.claude/skills/` e são consultadas pelos agentes durante o workflow. **Fontes de origem abaixo — algumas são adaptações pro PT-BR e o tom de voz do Pedro.**

#### Do pack `coreyhaines31/marketingskills` (já instalado como plugin)

Usadas pelos agentes como slash commands quando relevante:
- `copywriting`, `copy-editing` — Agente 2 (geração de legenda, revisão)
- `content-strategy`, `social-content`, `marketing-psychology`, `marketing-ideas` — Agente 1 (pauta)
- `community-marketing` — Agente 3 (WhatsApp pós-turma)
- `lead-magnets`, `cold-email`, `email-sequence` — Agente 3 (nurture)
- `customer-research` — Pedro mesmo (validação de ICP, não automatizada)
- `ab-test-setup`, `analytics-tracking` — Agente 5
- `launch-strategy`, `pricing-strategy`, `referral-program` — Pedro (decisões estratégicas)

#### Do pack `alirezarezvani/claude-skills` (selecionadas cirurgicamente — NÃO instalar o plugin completo)

Copiadas manualmente e **adaptadas pro PT-BR + tom do Pedro**. 6 skills apenas:

| Skill | Função | Usado por |
|---|---|---|
| `brand-voice-analyzer` | Analisa amostras e devolve perfil de voz estruturado | Agente 1 + **Lead Magnet #1** |
| `content-creator` | Gerador estruturado com hooks/ângulos | Agente 1 |
| `customer-success-manager` | Nurture + retenção + upsell pós-turma | Agente 3 |
| `sales-engineer` | Qualificação de lead + resposta técnica | Agente 3 |
| `revenue-operations` | Métricas de funil, ARR/MRR por canal | Agente 5 |
| `product-strategist` | Review estratégico de decisão de produto | Pedro + **Lead Magnet #3** |

#### Skills criadas do zero (não existem em nenhum pack)

Gaps reais que nenhum pack cobre. Escrever do zero, em PT-BR, com o tom do Pedro:

| Skill | Função | Prioridade |
|---|---|---|
| `hook-writer-shortform` | Hooks de 3s pra Reels/LinkedIn posts curtos | Alta — Agente 1 |
| `carousel-designer` | Estrutura de slide (hook → 3-5 content → CTA) | Alta — Agente 2 |
| `preparador-1on1` | Prepara pra 1-on-1 lendo histórico + projetos + pendências | Alta — **Lead Magnet #2** |
| `algoritmo-instagram` | Otimização por plataforma (timing, hashtags, formato) | Média — Agente 4 |
| `algoritmo-linkedin` | Idem pra LinkedIn | Média — Agente 4 |

---

## 5. Orquestração — como o Kanban funciona

### 5.1 Colunas do Kanban

```
Backlog  →  Aprovado  →  Em Produção  →  Revisão  →  Agendado  →  Publicado
            (gate 1)                      (gate 2)                  ↓
                                                                 Analytics
                                                                    ↓
                                                                 Feedback →
                                                                 Backlog (semana+1)
```

### 5.2 Modelo de estado (SQLite)

```sql
-- Tabela única de cards
cards (
  id TEXT PRIMARY KEY,
  column TEXT NOT NULL,              -- 'backlog' | 'aprovado' | 'em_producao' | ...
  perfil_alvo TEXT NOT NULL,         -- um dos 19 perfis do ICP
  angulo TEXT NOT NULL,
  hook TEXT,
  roteiro TEXT,
  asset_path TEXT,                   -- caminho do MP4 final
  legenda TEXT,
  hashtags TEXT,
  cta TEXT,
  objetivo TEXT,                     -- 'topo' | 'meio' | 'fundo'
  agente_responsavel TEXT,           -- agente atual
  pedro_aprovou INTEGER DEFAULT 0,   -- 0 ou 1
  publicado_em TEXT,                 -- ISO datetime
  metricas JSON,                     -- preenchido pelo Agente 5
  created_at TEXT,
  updated_at TEXT
)

-- Tabela de eventos (event sourcing leve pra auditoria)
events (
  id INTEGER PRIMARY KEY,
  card_id TEXT,
  event_type TEXT,                   -- 'criado' | 'aprovado' | 'produzido' | ...
  actor TEXT,                        -- 'agente_1' | 'pedro' | 'agente_2' | ...
  payload JSON,
  created_at TEXT
)

-- Tabela de leads (Agente 3)
leads (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE,
  source TEXT,                       -- 'instagram' | 'linkedin' | ...
  magnet_downloaded_at TEXT,
  nurture_stage INTEGER DEFAULT 0,   -- 0 a 5
  unsubscribed INTEGER DEFAULT 0,
  converted INTEGER DEFAULT 0        -- virou aluno?
)
```

### 5.3 Por que SQLite e não Postgres/Redis?

- **Escala suficiente:** max ~15 cards/semana. SQLite aguenta milhões.
- **Sem servidor:** 1 arquivo, zero ops.
- **Backup trivial:** `cp agents.db backup.db`.
- **Concorrência:** WAL mode resolve a maioria dos casos. Se o Pedro um dia precisar de mais, migra pra Postgres sem drama — a API do FastAPI fica igual.

---

## 6. Observabilidade — como "ver os agentes trabalhando"

A pergunta do Pedro: *"como conseguem ver os agentes trabalhando totalmente de forma autônoma"*. Resposta técnica:

### 6.1 Três planos de visibilidade

| Plano | O quê | Onde |
|---|---|---|
| **Macro — painel do Kanban** | Quantos cards em cada coluna, o que está onde, quanto tempo cada um leva | UI simples (Streamlit ou Next) lendo o SQLite |
| **Médio — timeline de eventos** | O que cada agente fez, quando, em qual card | Mesma UI, filtro por card |
| **Micro — traces do LLM** | Cada chamada de LLM, prompt exato, resposta, tokens, custo, latência | **Langfuse** |

### 6.2 Por que Langfuse

- **Open source MIT** — self-host, dados nunca saem do seu servidor
- **Step-level tracing** — vê cada passo do agente, não só o final
- **Cost tracking** — por agente, por task, por dia. Previne cost blowup.
- **Prompt management** — versiona prompts, A/B testa
- **Evals** — pode avaliar se o output respeitou os guardrails do posicionamento
- **Funciona com qualquer stack** — não prende a LangChain

### 6.3 Alerts que salvam a vida

Configurar estes alertas **antes** de subir qualquer agente em produção:

- **Cost spike:** qualquer agente gastar > R$X/dia → pausa automática + notifica Pedro
- **Loop detection:** mesmo agente rodando > N vezes na mesma tarefa → pausa
- **Tool failure:** qualquer tool call falhar 3x seguidas → pausa + notifica
- **Approval SLA:** card parado em "Revisão" > 48h → lembra Pedro
- **Publication failure:** erro na API do Late → notifica imediato

---

## 7. Níveis de autonomia e guardrails

Regra: autônomo onde é barato errar, humano no gate onde é caro.

| Operação | Autonomia | Gate humano |
|---|---|---|
| Pesquisar tendências | **Total** | — |
| Rascunhar hook / ângulo | **Total** | — |
| Escolher perfil-alvo | **Total** | — |
| **Aprovar a pauta semanal** | — | **Pedro aprova em lote (seg 09h)** |
| Gerar roteiro | **Total** | — |
| Gerar vídeo/avatar/voz | **Total** | — |
| **Aprovar o vídeo final** | — | **Pedro aprova no Telegram** |
| Agendar publicação | **Total** | — |
| Publicar no horário | **Total** | — |
| Enviar email nurture (template pré-aprovado) | **Total** | — |
| **Responder email de lead** | — | **Pedro sempre responde** |
| **Conversar no DM do Instagram** | — | **Pedro sempre responde** |
| Relatório semanal | **Total** | — |
| **Mudar de estratégia** | — | **Pedro decide** |

### Guardrails não-negociáveis

1. **Budget cap diário:** R$X/dia (a definir) — passou disso, pausa tudo.
2. **Rate limit:** máximo 2 publicações/dia, 1 por canal.
3. **Voice lock:** nenhum agente pode publicar em nome do Pedro sem gate de aprovação.
4. **Credentials isolation:** cada agente tem suas próprias API keys, loggadas em Langfuse, nunca no código.
5. **Sandbox:** se o código do agente rodar algo além de LLM calls, é em container isolado com filesystem efêmero.
6. **Observabilidade obrigatória:** agente sem tracing = agente desligado.
7. **Kill switch:** Pedro tem comando `/kill` no Telegram que para tudo imediatamente.

---

## 8. Pipeline ponta-a-ponta — exemplo concreto

Vamos seguir 1 Reel do começo ao fim:

```
SEGUNDA 08:00
└─ [cron] Agente 5 envia relatório da semana anterior pro Telegram do Pedro
   (impressões, engajamento, top 3 posts, insights)
   Pedro lê durante o café.

SEGUNDA 09:00
└─ [cron] Agente 1 cria pauta da semana:
   1. Lê 00-posicionamento.md + 00-escada-de-valor.md + relatório do Agente 5
   2. Roda Brave Search MCP pra pegar tendências (PMs, IA, produtividade)
   3. Cruza com 19 perfis do ICP
   4. Gera 5 cards na coluna "Backlog" (um por dia útil)
   5. Envia prévia pro Telegram do Pedro:
      "Pauta da semana: (1) Hook X pro perfil PM, (2) Hook Y pro advogado, ..."

SEGUNDA 09:15
└─ Pedro reage ✅ no Telegram → todos os cards vão pra "Aprovado"
   (ou reage ❌ num card específico → volta pra backlog pra reprocessar)

SEGUNDA 10:00
└─ Agente 2 pega o card 1 de "Aprovado":
   1. Gera roteiro de 30s com hook + corpo + CTA
   2. Chama HeyGen Video Agent com roteiro + avatar do Pedro + voz clonada
   3. HeyGen retorna MP4 em ~4 min
   4. Gera legenda + hashtags baseado no posicionamento
   5. Move card pra "Revisão"
   6. Envia preview pro Telegram:
      "Card 1 pronto: [MP4] + legenda. Aprovar?"

SEGUNDA 10:10
└─ Pedro assiste o vídeo no Telegram, reage ✅
   → Card vai pra "Agendado" com horário (definido pelo Agente 4)

SEGUNDA 14:00
└─ Agente 4 publica via Late no Instagram
   Move card pra "Publicado"
   Registra o link + ID do post

PROXIMA SEGUNDA
└─ Agente 5 puxa métricas do post: impressões, saves, comentários
   Alimenta o relatório da próxima semana
   Se gerou leads: Agente 3 assume o funil

QUALQUER HORA DO DIA
└─ Pedro pode abrir o painel Streamlit em localhost e ver:
   - Todos os cards em cada coluna
   - Linha do tempo de cada card (quem fez o quê, quando)
   - Traces Langfuse de cada chamada de LLM
   - Custos acumulados do dia
```

**Tempo de trabalho humano do Pedro nesse pipeline: ~15 min/dia** (aprovar pauta segunda, aprovar 1-2 vídeos/dia, responder leads que chegarem).

---

## 9. Anti-padrões — o que NÃO fazer

| ❌ Anti-padrão | Por quê | O que fazer em vez |
|---|---|---|
| **Agentes conversando entre si sem limite** | Gera loops, custo explode, alucinação acumula | Supervisor orquestra. Workers só falam quando chamados. |
| **Buscar autonomia total** | 85%^10 = 20% de sucesso. Impossível sem checkpoints | Human-in-the-loop em gates críticos |
| **Instagram Graph API direto pra postar** | Shadowban pra conta nova | Late (GetLate) |
| **Mais de 2 posts/dia** | Shadowban | Max 2/dia, qualidade > volume |
| **Conteúdo genérico AI-slop** | Plataformas penalizam | Lê posicionamento SEMPRE. Usa 1 dos 19 perfis. |
| **Sem observabilidade** | Black box = dano silencioso | Langfuse desde o dia 1 |
| **Credenciais compartilhadas entre agentes** | Explosão de dano quando um agente erra | API key por agente, logada, revogável |
| **CrewAI pra começar** | Prototype-friendly mas migra pra LangGraph depois | Claude Agent SDK direto, evita rewrite |
| **Postgres + Redis + RabbitMQ no dia 1** | Ops prematuro | SQLite + FastAPI até 10x do volume atual |
| **Prompts hardcoded no código** | Vira manutenção infernal | Prompts em Langfuse, versionados |
| **Publicar sem humano ver** | Risco de marca | Pedro aprova no Telegram, sempre |
| **Ignorar resposta de lead** | Mata a conversão | Resposta de lead = notificação imediata pro Pedro |

---

## 10. Cases estudados

Referências reais de 2025-2026 que informaram este documento:

- **[Stormy AI — Claude Code Playbook pra Instagram autônomo](https://stormy.ai/blog/autonomous-instagram-content-engine-claude-code-playbook)** — case mais próximo do nosso. Usa Claude Code + MCPs + Late. Citado ao longo do doc.
- **[State of AI Agents 2026 — Prosus](https://www.prosus.com/news-insights/2026/state-of-ai-agents-2026-autonomy-is-here)** — panorama do ecossistema.
- **[Google Cloud — Lessons from 2025 on agents and trust](https://cloud.google.com/transform/ai-grew-up-and-got-a-job-lessons-from-2025-on-agents-and-trust)** — lições de produção.
- **[Amazon — Evaluating AI agents: real-world lessons](https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon/)** — avaliação de agentes em produção.
- **[Databricks — Supervisor Agent Architecture](https://www.databricks.com/blog/multi-agent-supervisor-architecture-orchestrating-enterprise-ai-scale)** — padrão supervisor/worker em escala.
- **[WSO2 — Why AI Agents Need Their Own Identity](https://wso2.com/library/blogs/why-ai-agents-need-their-own-identity-lessons-from-2025-and-resolutions-for-2026/)** — gestão de identidade de agentes.
- **[The First Production AI Agents Study — Yi Zhou / Medium](https://medium.com/generative-ai-revolution-ai-native-transformation/the-first-production-ai-agents-study-reveals-why-agentic-engineering-becomes-mandatory-in-2026-ec5e00514e5e)** — origem da frase "85% → 20% em 10 passos".
- **[o-mega — LangGraph vs CrewAI vs AutoGen 2026](https://o-mega.ai/articles/langgraph-vs-crewai-vs-autogen-top-10-agent-frameworks-2026)** — comparativo dos frameworks.
- **[DataCamp — CrewAI vs LangGraph vs AutoGen](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen)** — comparativo técnico.
- **[AI Multiple — 15 AI Agent Observability Tools in 2026](https://research.aimultiple.com/agentic-monitoring/)** — levantamento de ferramentas.
- **[Softcery — 8 AI Observability Platforms Compared](https://softcery.com/lab/top-8-observability-platforms-for-ai-agents-in-2025)** — Langfuse vs LangSmith vs Phoenix lado a lado.
- **[ElevenLabs — HeyGen integration](https://elevenlabs.io/blog/how-heygen-uses-elevenlabs-to-deliver-lifelike-voice-for-ai-video)** — como HeyGen integra voz realista.

---

## 11. Roadmap de implementação (fases)

Não construir tudo de uma vez. Fases curtas, cada uma entregando valor. **Toda a Fase 1 é zero-custo adicional.**

### Fase 0 — Fundação de infra (antes de qualquer agente)
- [ ] Criar projeto novo no Railway (ou pasta dentro do projeto existente): `empresa-ia-pedro-agents`
- [ ] Setup **Langfuse** self-hosted via Docker no Railway
- [ ] Criar schema SQLite (cards, events, leads) + migrations
- [ ] Criar **FastAPI** com endpoints básicos: `GET /cards`, `POST /cards`, `PATCH /cards/{id}/move`, `POST /events`
- [ ] Criar UI mínima (Streamlit ou HTMX) que lê o SQLite e mostra o Kanban
- [ ] Setup bot Telegram dedicado pros gates + conectar no Claude Code do Pedro
- [ ] Criar os 3 prompts-base (pauta, legenda, email) versionados no Langfuse
- [ ] Configurar conta Instagram **Business/Creator** + app Meta Developer (gratuito)
- [ ] Obter token OAuth do Instagram Graph API + testar POST de 1 imagem manualmente
- [ ] Obter API key do Google AI Studio (Gemini grátis)

### Fase 1A — 1 post manual, fim-a-fim (validar o pipeline)
- [ ] Pedro cria 1 card à mão no SQLite (com perfil-alvo, hook, ângulo)
- [ ] Script Python lê o card, chama Claude pra gerar legenda + copy dos 3 slides
- [ ] Script chama Gemini Flash Image 3x pros slides
- [ ] Script chama Meta Graph API pra publicar como carrossel
- [ ] Langfuse captura tudo
- [ ] **Gate:** se qualquer dessas etapas não passar, não avança. Meta: 1 post publicado de verdade na conta nova.

### Fase 1B — Agente 2 (Produção) automatizado
- [ ] Supervisor (Claude Agent SDK loop) pega card do Backlog e dispara Agente 2
- [ ] Agente 2 roda pipeline de produção (Claude + Gemini), envia preview pra Telegram
- [ ] Pedro aprova com reação ✅ → card vai pra "Agendado"
- [ ] Agente 4 publica no horário
- [ ] Se Pedro rejeita com ❌ → retry 1x, depois escala
- [ ] **Meta:** Pedro escreve o card no SQLite, agente produz e publica sozinho (com gate de aprovação)

### Fase 1C — Agente 1 (Estratégia) automatizado
- [ ] Agente 1 roda toda segunda 09h
- [ ] Lê posicionamento + escada de valor + relatório da semana anterior (quando Agente 5 existir)
- [ ] Roda Brave Search MCP pra trends
- [ ] Gera pauta de 5 cards usando 5 perfis diferentes do ICP
- [ ] Envia prévia pro Pedro no Telegram
- [ ] Pedro aprova tudo com ✅ → cards vão pro Backlog
- [ ] **Meta:** Pedro não escreve mais cards, só aprova pauta semanal e posts individuais

### Fase 1D — Agente 3 (Captação) + 3 Lead Magnets em paralelo

**Estratégia:** 3 magnets diferentes, 3 funis paralelos, 1 mentoria no final. Cada magnet preserva 100% do `estrutura-template` completo (o entregável principal NÃO é entregue no magnet).

#### Criar as skills-base (adaptar/criar)

- [ ] **Analisador de Voz (Lead Magnet #1)** — adaptar `alirezarezvani/brand-voice-analyzer` pro PT-BR + tom do Pedro
  - [ ] Fazer fork local da skill
  - [ ] Traduzir prompts pro PT-BR
  - [ ] Adaptar output pra ser compatível com o que o Agente 1 consome
  - [ ] Testar com amostras reais do Pedro (validar que detecta o tom dele)

- [ ] **Preparador de 1-on-1 (Lead Magnet #2)** — criar do zero
  - [ ] Definir contrato de input (arquivos markdown/texto de reuniões passadas + pendências)
  - [ ] Definir contrato de output (tópicos abertos, preocupações detectadas, 3 perguntas, o que NÃO tocar, email de follow-up)
  - [ ] Escrever SKILL.md
  - [ ] Testar com 2-3 casos reais do Pedro

- [ ] **Review Estratégico (Lead Magnet #3)** — adaptar `alirezarezvani/product-strategist`
  - [ ] Fazer fork local da skill
  - [ ] Traduzir e adaptar ao formato que o ICP C-level espera
  - [ ] Testar com 1 documento estratégico real

#### Empacotamento + distribuição de cada magnet

Pra cada um dos 3:
- [ ] Criar pasta com SKILL.md + guia de instalação em 1 página + exemplo de uso
- [ ] Gravar vídeo de 5 min mostrando o antes/depois
- [ ] Empacotar como ZIP
- [ ] Hospedar no Railway (rota `/download/<magnet>`)
- [ ] Criar landing específica pra cada magnet (hook próprio, copy própria)

#### Funis de nurture (Agente 3)

- [ ] Integrar Resend
- [ ] Escrever 15 templates de email (5 por magnet × 3 magnets)
- [ ] Pedro aprova os 15 templates em bloco
- [ ] Agente 3 dispara sequência baseada em `magnet_source` no SQLite
- [ ] Resposta de qualquer lead → notificação imediata pro Pedro
- [ ] Skills consultadas: `customer-success-manager`, `sales-engineer`, `email-sequence`

#### Instalar skills do alirezarezvani (seleção cirúrgica)

- [ ] Clonar o repo `alirezarezvani/claude-skills` temporariamente
- [ ] Copiar 6 skills específicas pra `~/.claude/skills/`:
  - `brand-voice-analyzer`, `content-creator`, `customer-success-manager`, `sales-engineer`, `revenue-operations`, `product-strategist`
- [ ] Traduzir SKILL.md dessas pro PT-BR e adaptar ao tom do Pedro
- [ ] Deletar a pasta clonada (só queremos as 6, não o pack completo)
- [ ] Criar `02-maquina-agentes/skills-adaptadas/` no Drive como backup versionado

- [ ] **Meta:** 3 funis rodando em paralelo, leads entrando no SQLite, Pedro aprovando com ✅ no Telegram.

### Fase 1E — Agente 5 (Analytics) + feedback loop
- [ ] Agente 5 puxa métricas de cada post publicado via Graph API (impressões, engajamento, saves, comentários, profile visits)
- [ ] Agente 5 puxa métricas de nurture do Resend (open rate, click rate)
- [ ] Agente 5 cruza com a tabela de conversão (quem virou aluno)
- [ ] Relatório semanal automático no Telegram toda segunda 08h
- [ ] Feedback alimenta Agente 1 na rodada de pauta das 09h
- [ ] **Meta:** máquina fechada — dados alimentam pauta sem Pedro tocar

### Fase 2 — Upgrades (só quando houver receita das turmas)
- [ ] HeyGen Video Agent pra posts em vídeo (avatar + voz do Pedro)
- [ ] Gravar amostra de voz (~2 min) e vídeo de referência (~1 min)
- [ ] Migrar Agente 2 pra gerar vídeo em vez de carrossel (ou os dois formatos)
- [ ] Expandir pra TikTok/YouTube via Late (se justificar)
- [ ] **Trigger:** turma 1 rodada, receita entrando.

---

## 12. Decisões pendentes

Pra Pedro bater o martelo antes de começar a Fase 0:

1. **Budget mensal de tools** pra calibrar Claude API, HeyGen, Late, Resend, servidor. Faixa estimada: R$500-1500/mês pra começar.
2. **Qual skill vira o lead magnet?** Recomendação: atas de reunião (decisão já aberta na escada).
3. **Onde hospedar o Langfuse + FastAPI?** Opções: VPS barata (~R$30/mês DigitalOcean/Hetzner), ou localhost no PC do Pedro (só quando ligado). Recomendação: VPS barata, 24/7.
4. **Nome do Telegram bot** dedicado pros gates da máquina (separado do bot que o Pedro já usa).
5. **Conta Instagram** — usa a pessoal do Pedro ou cria uma nova da empresa? Implica posicionamento da marca também.
6. **Amostra de voz e vídeo do Pedro** pra treinar avatar/voz no HeyGen — precisa gravar.

---

*Última atualização: 2026-04-13. Este doc é vivo — atualizar sempre que mudar arquitetura, stack ou guardrail.*
