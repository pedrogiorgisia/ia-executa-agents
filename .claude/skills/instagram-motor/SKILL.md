---
name: instagram-motor
description: Orquestra a automação completa de posts de Instagram para PP-Travel e contas-irmãs. Use sempre que o usuário pedir para "rodar o motor", "post da PP-Travel", "gerar reel reflexivo", "gerar carrossel", "publicar no @pptravelinfinite", "publicar no @ia.executa", "fazer post da semana", "automatizar instagram", "gerar conteúdo PP-Travel", "test reel", "audit instagram" ou qualquer pedido relacionado a criação automatizada de mídia (foto + texto, vídeo Reel, single photo, story, carrossel) para Instagram seguindo a marca PP-Travel. Use também quando o usuário mencionar trabalhar nos pilares Educação, Inspiração, Engajamento, Prova Social, Conversão ou Inspiração Reflexiva. Use quando ele falar em sourcing via Grok, geração via Gemini Image 3.1 ou Veo Lite, ou publicação via Zernio para Instagram. Não use para outras redes (LinkedIn, TikTok, X) — só Instagram.
---

# Instagram Motor — PP-Travel

> Motor de geração + publicação automatizada de posts no Instagram, com foco inicial em
> 3 pilares (Inspiração, Engajamento, Inspiração Reflexiva) testando no `@ia.executa`
> antes de migrar pra `@pptravelinfinite`.

> 📐 **Antes de qualquer mudança estrutural, leia [ARQUITETURA.md](ARQUITETURA.md)** —
> mapa completo da skill com anatomia, subagentes, scripts, pastas de dados e fluxo end-to-end.

## O que o motor faz (passo a passo)

Quando você é invocado (seja por agendamento 10h BRT, seja por comando manual):

1. **Determinar dia/pilar** — lê hoje (`datetime.now()`) e mapeia pra pilar em [`pages/pp-travel/pilares.md`](../../../pages/pp-travel/pilares.md). Pilar pode ser sobrescrito por `--pilar` no comando.
2. **Ler configs da página** — sempre carregue *todos* esses arquivos antes de pensar em qualquer post.

   ⭐ **PRIMEIRO E MAIS IMPORTANTE** — fonte oficial da estratégia da PP-Travel:
   - [`pages/pp-travel/guia-objetivos.md`](../../../pages/pp-travel/guia-objetivos.md) — **GUIA OFICIAL** dos 5 pilares com: definição, elementos OBRIGATÓRIOS, estrutura ideal do conteúdo (passo a passo), o que evitar, gatilhos psicológicos, tipos de conteúdo, sugestões práticas, métricas de sucesso, **checklist de criação**, otimização para algoritmo IG 2025, estratégia de resposta a comentários, horários estratégicos. **Esse arquivo dita a estrutura de TODO candidato.** Antes de finalizar um candidato, rode mentalmente o **checklist** do pilar correspondente. Se algum item do checklist não tá atendido, refaça.

   Configs operacionais:
   - [`pages/pp-travel/page.yaml`](../../../pages/pp-travel/page.yaml) — contas Zernio, modelos, schedule, hashtags fixas
   - [`pages/pp-travel/voice.md`](../../../pages/pp-travel/voice.md) — tom, USPs, personas, frases-âncora, banco de frases reflexivas, **HARD BANS**
   - [`pages/pp-travel/pilares.md`](../../../pages/pp-travel/pilares.md) — resumo operacional dos 5 pilares + subgênero Inspiração Reflexiva + rotação semanal (versão curta — a versão **canonical** dos pilares é o `guia-objetivos.md`)
   - [`pages/pp-travel/formatos.md`](../../../pages/pp-travel/formatos.md) — 6 formatos com estrutura, prompts-template Gemini/Veo, regras de cada
   - [`pages/pp-travel/sourcing.md`](../../../pages/pp-travel/sourcing.md) — mapa dia→queries Grok, filtros HARD
   - [`pages/pp-travel/historico.md`](../../../pages/pp-travel/historico.md) — últimos 60 dias de posts (dedup)
   - `pages/pp-travel/promos-ativas.md` (se existir) — promos vigentes para pilar Conversão
   - `pages/pp-travel/casos-clientes.md` (se existir) — casos para pilar Prova Social

   ⭐ **Banco de ideias** ([`pages/pp-travel/ideias/`](../../../pages/pp-travel/ideias/)):
   - [`ideias/README.md`](../../../pages/pp-travel/ideias/README.md) — explica o fluxo
   - [`ideias/templates-engajamento.md`](../../../pages/pp-travel/ideias/templates-engajamento.md) — 13 fórmulas virais reutilizáveis (microdecisão, batalha, quiz, polêmica, etc). Não consomem.
   - [`ideias/disponiveis.md`](../../../pages/pp-travel/ideias/disponiveis.md) — banco de ideias específicas prontas pra postar. **MOTOR PEGA daqui** quando faz sentido pro pilar do dia.
   - [`ideias/usadas.md`](../../../pages/pp-travel/ideias/usadas.md) — histórico de ideias consumidas. **Motor lê antes de pegar de `disponiveis.md`** pra evitar repetir.
3. **Sourcing** — chame `scripts/run_pp_sourcing.py` (ele lê o dia da semana e roda 1-2 queries Grok direcionadas). Resultado em `data/instagram/pp-travel/YYYY-MM-DD/digest.md`.
4. **Gere candidatos VIA SUBAGENTS** — **NUNCA escreva copy ou prompts visuais de cabeça**. Sempre invoque:

   **4a. Copy Specialist** (`.claude/agents/copy-specialist.md`):
   - Você invoca via `Task` com `subagent_type: copy-specialist`
   - Brief: pilar, tema candidato, hook source do digest
   - Subagent: consulta banco-frases → pesquisa viral se vazio → invoca marketing-skills:copywriting + marketing-psychology + copy-editing → itera mínimo 2 ciclos → retorna JSON com headline_html, sub_pill, caption, first_comment, linhas_frase, `_audit_log`
   - **Custo runtime: zero** (todo loop é texto)

   **4b. Visual Specialist** (`.claude/agents/visual-specialist.md`):
   - Você invoca via `Task` com `subagent_type: visual-specialist`
   - Brief: pilar, formato (single/carousel/reel), texto já gerado pela copy-specialist
   - Subagent: consulta templates aprovados → escreve 3-5 variações de prompt → itera mínimo 2 ciclos NO TEXTO → retorna JSON com photo_prompt ou video_prompt + `_visual_audit`
   - **Custo runtime: zero** (NUNCA chama Gemini/Veo — só escreve o prompt)

5. **Escolha 1 candidato vencedor** entre os 5 da copy-specialist. Combine com o prompt visual. Salve `content.json` completo em `data/instagram/pp-travel/YYYY-MM-DD/content.json`.
6. **Gere mídia** — conforme `content.formato`:
   - **photo (single/carousel)** → OpenRouter `google/gemini-3.1-flash-image-preview`
   - **reel/reflexivo** → OpenRouter `google/veo-3.1-lite` (R$ 2,88/Reel — metade do Fast), 6s, 9:16
   - Veja [`references/midias.md`](references/midias.md) para chamadas exatas
7. **Render overlay** — use Playwright (foto) ou ffmpeg (vídeo) pra adicionar texto + logo. Templates HTML em [`references/templates.md`](references/templates.md). Para Reels, ler [`references/viralizacao.md`](references/viralizacao.md) antes de definir overlay.
8. **Publique via Zernio** — `POST /v1/posts` com `publishNow: true`. Para Reels: `platformSpecificData.contentType: "reels"`. Use `accountId` do `page.yaml.phase` (testing → `@ia.executa`, production → `@pptravelinfinite`).
9. **Registre no `historico.md`** — append da linha do post (data, pilar, formato, headline, hook source, url_post).
10. **Mova a ideia consumida** de `pages/pp-travel/ideias/disponiveis.md` para `usadas.md` (se veio de lá). Se foi ideia gerada na hora, ainda assim registra em `usadas.md` pra dedup futuro.
11. **Adicione ideias bônus** ao `disponiveis.md` — todo digest do sourcing traz N temas; só 1 vira post hoje. Os outros (>=2 quando o digest é rico) viram entradas novas em `disponiveis.md` pra dias futuros.
12. **Gere `preview.html`** do dia (via `scripts/preview.py`) — vai pra `data/instagram/pp-travel/YYYY-MM-DD/preview.html`. Pedro abre quando quiser revisar.

## Comandos suportados

| Comando | O que faz |
|---|---|
| `/post-instagram pp-travel` | Roda o pipeline completo, end-to-end, postando direto |
| `/post-instagram pp-travel --dry-run` | Para no passo 5 (mostra os 5 candidatos + o escolhido, sem postar) |
| `/post-instagram pp-travel --pilar inspiracao` | Force um pilar específico (override do dia da semana) |
| `/test-reel-reflexivo` | Gera 1 Reel Reflexivo de teste (Veo Lite + frase do banco), NÃO posta |
| `/audit-instagram pp-travel` | Auditoria mensal: lê últimos 30 posts do histórico, gera relatório de mix, identifica gaps |
| `/post-instagram pp-travel --conta ia-executa` | Override de conta (default = `page.yaml.phase`) |

## Foco atual (Fase 1)

Apenas 3 pilares são suportados em produção. Os outros 2 ainda não:

| Pilar | Dia padrão | Status | Por quê |
|---|---|---|---|
| **Inspiração** | Terça | ✅ Em produção | Stack validada (Gemini 3.1 + overlay V2) |
| **Inspiração Reflexiva** | Sábado | ✅ Em produção | Veo 3.1 Lite + overlay ffmpeg validados |
| **Engajamento** | Quarta + Domingo | 🟡 Pendente templates virais | Ler `Ideias de posts futuros.gdoc` no Drive em `20-empresas/projetos-paralelos/01-ativas/04-pp-travel/` (Google Doc — abrir via MCP Google Drive) |
| **Educação** | Segunda | 🔴 Fora de foco | Decisão Pedro 2026-06-01 |
| **Prova Social** | Quinta | 🔴 Fora de foco | Depende de `casos-clientes.md` alimentado |
| **Conversão** | Sexta | 🔴 Fora de foco | Depende de `promos-ativas.md` alimentado |

Se o dia da semana cair em pilar fora de foco, o motor pula a execução ou (override) gera Engajamento como fallback.

## ⛔ COPY: SEMPRE via skills + banco + pesquisa (NUNCA inventar)

**Lição 2026-06-01**: gerar texto de cabeça produziu copy ruim (metáforas quebradas
tipo "acumular janela de avião", frases incompletas tipo "pagar menos ainda dá").

### Fluxo OBRIGATÓRIO antes de salvar qualquer texto em `content.json`:

1. **Para Reels Reflexivos (sábado)**:
   - Consultar [`pages/pp-travel/banco-frases/reflexivas-disponiveis.md`](../../../pages/pp-travel/banco-frases/reflexivas-disponiveis.md) primeiro
   - Cruzar com [`reflexivas-usadas.md`](../../../pages/pp-travel/banco-frases/reflexivas-usadas.md) (dedup)
   - Se o banco estiver vazio OU todas já foram usadas, **fazer web search + Grok** pra novas (ver §"Pesquisa de viral content")
   - Adicionar achados ao banco com FONTE (autor + link)
   - Pegar 1, usar, MOVER pra `usadas.md`

2. **Para qualquer outra peça de texto (headline/caption/first_comment)**:
   - INVOCAR as skills:
     - `marketing-skills:copywriting` (pra escrever)
     - `marketing-skills:marketing-psychology` (pra escolher gatilho)
     - `marketing-skills:copy-editing` (pra polir)
     - `marketing-skills:social-content` (pra formato IG)
   - Auto-review contra checklist do pilar (§`guia-objetivos.md`)
   - Se falhar qualquer item OBRIGATÓRIO, RE-ESCREVER

3. **NUNCA escrever texto direto** sem passar por uma das vias acima.

### Pesquisa de viral content (quando banco esvaziar)

Fontes a consultar (rodízio):

| Tipo | Fonte | Como |
|---|---|---|
| Sites curados pt-BR | Carpe Mundi, Ligado em Viagem, Pinterest | WebFetch |
| Autores brasileiros | Quintana, Klink, Medeiros, Manoel de Barros | WebSearch + Goodreads |
| X virais pt-BR | Grok 4.3 + plugin web, query "min_likes:2000 frases viagem últimos 6m" | OpenRouter Grok |
| Reddit | r/TravelBR, r/wanderlust | WebFetch |

Adicione achados ao `banco-frases/reflexivas-disponiveis.md` com fonte rastreável.

---

## 💰 REGISTRO DE GASTOS — toda chamada OpenRouter

**Lição 2026-06-01**: Pedro pediu visibilidade total dos custos pra refinar depois.

### Como funciona

Todo script que chama OpenRouter (Grok, Gemini Image, Veo) **DEVE chamar**:

```python
from cost_tracker import register_cost
register_cost(
    script="nome_do_script.py",
    model="provider/model-name",
    purpose="descricao curta do que era pra fazer",
    cost_usd=valor,
    tokens_in=N, tokens_out=N,  # se aplicavel
)
```

Ledger: `data/_gastos/openrouter.csv`

### Resumo a qualquer hora

```bash
python scripts/cost_tracker.py            # total
python scripts/cost_tracker.py 2026-06    # do mes
```

Mostra por modelo, por script, total USD/BRL.

### Scripts JÁ instrumentados (2026-06-01)

- `post.py` — registra Gemini Image + Veo
- `run_pp_sourcing.py` — registra cada query Grok separada

### Quando criar um script novo que chama OpenRouter

**Sempre** importe e use `register_cost()`. Sem exceção. Auditoria depende disso.

---

## ⛔ APROVAÇÃO HUMANA OBRIGATÓRIA

**O motor NUNCA posta automaticamente.** Decisão do Pedro 2026-06-01.

### Fluxo correto

```
10h BRT (Task Scheduler):
  scripts/run-pp-instagram.cmd
    ├── roda sourcing (digest.md)
    ├── invoca `claude.cmd -p "..."` headless → gera content.json
    └── roda `python scripts/post.py` (modo generate)
        ├── gera foto/vídeo (Gemini/Veo)
        ├── renderiza overlay (Playwright/ffmpeg)
        └── gera preview.html (sem postar)

Pedro abre quando quiser → vê dashboard → revisa caption + 1º comentário

Pedro fala aqui no chat: "posta o do dia X"
  ↓
Eu (Claude interativo) executo:
  python scripts/post.py --date YYYY-MM-DD --publish

  Só AGORA o post vai pro Instagram, historico/ideias são atualizados.
```

### Modos do `scripts/post.py`

| Comando | O que faz | Quando |
|---|---|---|
| `python scripts/post.py` (default) | Gera tudo (mídia + render + preview) mas **NÃO posta** | 10h auto + manual |
| `python scripts/post.py --date X --publish` | Lê tudo gerado, posta no Zernio, atualiza historico/ideias | **APENAS após aprovação humana** |
| `python scripts/post.py --dry-run` | Simula tudo, nada persiste | Teste |

### Quando NÃO posso usar `--publish`

- Sem aprovação explícita do Pedro nesta sessão
- Se o `preview.html` ainda nem foi aberto pelo Pedro
- Se houver dúvida sobre o conteúdo (caption sensível, foto questionável, hashtags duvidosas)

### Quando POSSO usar `--publish`

- Pedro disse claramente: "posta o do dia X" / "publica esse" / "manda no IG"
- Ele especificou data ou contexto que identifica o post

**Em dúvida, perguntar antes de publicar.** Custo de não publicar = 0. Custo de publicar errado = retrabalho + risco de marca.

---

## Princípios não-negociáveis

Antes de gerar QUALQUER post, garanta que:

1. **HARD BANS aplicados** ([`pages/pp-travel/voice.md`](../../../pages/pp-travel/voice.md) §⛔):
   - 🚫 Política (incluindo dados factuais vindos de pessoa pública governante)
   - 🚫 Religião opinativa
   - 🚫 Tragédias (mortes, acidentes, falências)
   - 🚫 Concorrentes (CVC, Decolar, 123Milhas, MaxMilhas, Submarino, Vai de Promo)
   - 🚫 Polêmicas com cias (relatos negativos)
   - 🚫 Futebol-opinião (Copa OK como contexto de viagem, mas não comentar)
2. **Acentos pt-BR sempre presentes** — "Inspiração", não "Inspiracao"; "preço", não "preco"
3. **Dedup contra histórico de 60d** — não repetir headline idêntica, mesmo gancho dentro de 7d, mesmo destino dentro de 5d, mesma estrutura de hook dentro de 14d
4. **LGPD** — nunca rosto reconhecível sem autorização (use 3/4 de costas ou silhueta)
5. **Caption: primeiros 125 chars cabem o hook** — IG trunca em "...ver mais"
6. **Posts diretos, sem aprovação humana** — decisão Pedro 2026-06-01. Telegram só notifica.

## Referências (leia conforme o caso)

| Arquivo | Quando ler |
|---|---|
| [`references/viralizacao.md`](references/viralizacao.md) | Sempre que gerar Reel (princípios de hook, retention, caption, hashtags) |
| [`references/midias.md`](references/midias.md) | Sempre que for chamar Gemini Image ou Veo Lite (endpoints + curl exatos) |
| [`references/templates.md`](references/templates.md) | Sempre que for renderizar overlay (HTML + ffmpeg validados) |
| [`references/exemplos-aprovados.md`](references/exemplos-aprovados.md) | Antes de definir um candidato (referência dos mocks que o Pedro aprovou) |

## Custo médio por execução

| Item | Custo |
|---|---|
| Sourcing Grok (1-2 queries) | R$ 0,15 – R$ 0,35 |
| Texto (Claude headless via subscription) | R$ 0 |
| Foto Gemini 3.1 Image | R$ 0,01 |
| Vídeo Veo 3.1 Lite (6s 720p com áudio) | R$ 2,88 |
| Posting Zernio | R$ 0 |
| **Custo médio dia normal (foto)** | **~R$ 0,30** |
| **Custo dia com Reel** | **~R$ 3,20** |

Mês com 7 dias úteis × 4 semanas + 4 Reels reflexivos: **~R$ 20/mês**.

## Estado da arte (2026-06-01)

- Gemini Image 3.1 Flash Preview testado e aprovado pelo Pedro (5 mocks PP-Travel)
- Veo 3.1 Fast testado → trocado por Lite (50% mais barato, mesma resolução 720p)
- Zernio @ia.executa conectada, accountId `6a1df37a2b2567671a8f620e`
- Zernio @pptravelinfinite ainda não conectada (Pedro vai conectar)
- Template visual aprovado: V2 (foto full-bleed + PP TRAVEL topo + headline misturando pesos + pílula branca)
- Sourcing daily mode roda em 23-30s, custo R$ 0,15-0,35
