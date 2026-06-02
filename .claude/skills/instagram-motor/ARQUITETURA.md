# Arquitetura — instagram-motor

> Mapa completo da skill. Leia isto antes de qualquer manutenção estrutural.
> Atualizado 2026-06-02.

---

## 🗺️ Anatomia da skill

```
.claude/skills/instagram-motor/                      ← PASTA DA SKILL
├── SKILL.md                                         ← Entrypoint (Claude carrega quando trigger bate)
├── ARQUITETURA.md                                   ← Este arquivo
├── assets/                                          ← TEMPLATES estáticos (HTML)
│   ├── template-v2-single-photo.html
│   ├── template-carousel-slide.html
│   └── README.md
├── references/                                      ← DOCS lidos sob demanda
│   ├── viralizacao.md                               (anatomia retention + 5 hooks + algoritmo 2025)
│   ├── midias.md                                    (endpoints OpenRouter Gemini/Veo)
│   ├── templates.md                                 (decisões visuais aprovadas)
│   └── exemplos-aprovados.md                        (histórico de aprovados + rejeitados)
└── scripts/
    └── README.md                                    ← Documenta scripts (que ficam fora)
```

## 🌐 Anatomia do projeto (o que a skill ORQUESTRA)

```
02-maquina-agentes/                                  ← PROJECT ROOT
│
├── .claude/
│   ├── skills/instagram-motor/                      ← a skill (acima)
│   └── agents/                                      ← SUBAGENTES invocados pela skill
│       ├── copy-specialist.md                       (texto, zero custo)
│       └── visual-specialist.md                     (prompts visuais, zero custo)
│
├── scripts/                                         ← SCRIPTS chamados pela skill
│   ├── post.py                                      (orquestrador end-to-end)
│   ├── run_pp_sourcing.py                           (Grok daily)
│   ├── preview.py                                   (gera HTML review)
│   ├── render_carousel.py                           (multi-slide)
│   ├── cost_tracker.py                              (registro OpenRouter)
│   └── run-pp-instagram.cmd                         (Task Scheduler wrapper 10h BRT)
│
├── pages/pp-travel/                                 ← CONFIG DA MARCA (canonical)
│   ├── guia-objetivos.md       ⭐                   (fonte oficial dos 5 pilares — 870 linhas)
│   ├── voice.md                                     (tom + USPs + HARD BANS)
│   ├── pilares.md                                   (resumo operacional + rotação semanal)
│   ├── formatos.md                                  (6 formatos + prompts-template)
│   ├── sourcing.md                                  (mapa dia→queries Grok)
│   ├── page.yaml                                    (config técnica: contas, modelos)
│   ├── historico.md                                 (60 dias últimos posts — dedup)
│   ├── ideias/                                      ← BANCO DE IDEIAS
│   │   ├── disponiveis.md                           (temas prontos)
│   │   ├── usadas.md                                (consumidas, dedup)
│   │   ├── templates-engajamento.md                 (13 fórmulas virais)
│   │   └── README.md
│   └── banco-frases/                                ← BANCO DE FRASES REFLEXIVAS
│       ├── reflexivas-disponiveis.md                (frases curadas com fonte)
│       ├── reflexivas-usadas.md                     (consumidas)
│       └── README.md
│
└── data/                                            ← OUTPUT DO MOTOR (gitignored futuro)
    ├── instagram/pp-travel/                         ← posts gerados
    │   ├── _dashboard.html                          (índice navegável de todos os dias)
    │   └── YYYY-MM-DD/                              (1 pasta por dia)
    │       ├── digest.md                            (sourcing Grok)
    │       ├── q2_raw.md, q7_raw.md ...             (raw das queries)
    │       ├── content.json                         (candidato escolhido)
    │       ├── content-v2.json, v3.json             (re-gerações)
    │       ├── foto-<slug>.png OU video-<slug>-raw.mp4
    │       ├── post-final.png OU reel-final.mp4
    │       ├── visual-audit.json                    (output do visual-specialist)
    │       └── preview.html
    ├── instagram/_research/                         ← pesquisas web/Grok arquivadas
    │   ├── grok-viral-quotes.md
    │   └── grok-viral-italia.md
    └── _gastos/
        └── openrouter.csv                           ← LEDGER de custos (timestamp, script, model, purpose, cost)
```

---

## 🧠 Subagentes (dependências de execução)

A skill invoca **2 subagentes** especializados em fases diferentes:

| Subagente | Path | Quando | O que faz | Custo |
|---|---|---|---|---|
| **copy-specialist** | `.claude/agents/copy-specialist.md` | Antes de salvar `content.json` (passo 4a) | Lê banco-frases + ideias → pesquisa viral se vazio → invoca skills `marketing-skills:copywriting + copy-editing + marketing-psychology` → itera 2-3 ciclos com auto-crítica → retorna pacote completo (headline_html, caption, first_comment) + `_audit_log` | R$ 0 (só texto) |
| **visual-specialist** | `.claude/agents/visual-specialist.md` | Antes de chamar Gemini/Veo (passo 4b) | Lê templates aprovados + checklist retention → escreve 3-5 variações de prompt → audita timing (Reel: hook frame 1, retention 5s) → retorna `photo_prompt` ou `video_prompt` + `_visual_audit` | R$ 0 (NUNCA chama Gemini/Veo) |

**Princípio comum**: subagentes iteram em TEXTO. Quem chama Gemini/Veo é apenas o `post.py`, **1 vez por post**, com o prompt já travado.

---

## 🪖 Skills externas que os subagentes invocam

Plugin `marketing-skills` instalado em `C:\Users\pedro\.claude\plugins\cache\marketingskills\`.

| Skill | Quem invoca | Pra quê |
|---|---|---|
| `marketing-skills:copywriting` | copy-specialist | Drafts de headline + caption |
| `marketing-skills:copy-editing` | copy-specialist | Polimento (ritmo, concordância, fluidez) |
| `marketing-skills:marketing-psychology` | copy-specialist | Identificar gatilho de cada candidato |
| `marketing-skills:social-content` | copy-specialist (opcional) | Formato específico pra IG |

A `dev-browser` skill **não** é usada pelo instagram-motor (usada em outros pipelines).

---

## 🔁 Fluxo end-to-end

### Fase 1 — Sourcing (10h BRT automático)

```
[Task Scheduler] → run-pp-instagram.cmd
                         ↓
                  python scripts/run_pp_sourcing.py
                         ├── lê page.yaml + sourcing.md
                         ├── determina pilar do dia (rotação semanal)
                         ├── chama 1-2 queries Grok via OpenRouter (+ plugin web)
                         ├── registra custo via cost_tracker
                         └── salva digest.md em data/instagram/pp-travel/YYYY-MM-DD/
```

### Fase 2 — Geração via subagentes (custo zero)

```
claude.cmd headless
       ├── carrega SKILL.md (instagram-motor)
       ├── lê configs: voice.md, guia-objetivos.md, pilares.md, formatos.md,
       │              historico.md, ideias/, banco-frases/
       ├── lê digest.md do dia
       ├── decide pilar do dia
       │
       ├── INVOCA copy-specialist
       │     ├── consulta banco-frases/ideias
       │     ├── pesquisa viral (Grok/web) se necessário
       │     ├── invoca marketing-skills
       │     ├── itera 2-3 ciclos
       │     └── retorna: headline, sub_pill, caption, first_comment + _audit_log
       │
       ├── INVOCA visual-specialist
       │     ├── lê templates + exemplos aprovados
       │     ├── checklist retention (frame 1 hook, etc)
       │     ├── itera 2-3 ciclos NO TEXTO
       │     └── retorna: photo_prompt OU video_prompt + _visual_audit
       │
       └── salva content.json em data/instagram/pp-travel/YYYY-MM-DD/
```

### Fase 3 — Geração de mídia + render (custo R$ 0,01 ou R$ 2,88)

```
python scripts/post.py (modo generate default)
       ├── lê content.json
       ├── usa cache se foto/vídeo já existem
       │   senão: chama Gemini Image OU Veo Lite
       │         (registra custo via cost_tracker)
       ├── render overlay
       │   ├── Single Photo: Playwright + assets/template-v2-single-photo.html
       │   ├── Carrossel: Playwright + assets/template-carousel-slide.html × N
       │   └── Reel: ffmpeg drawtext (timing retention: T=0 hook)
       ├── chama scripts/preview.py
       │   ├── gera preview.html no diretório do dia
       │   └── regenera _dashboard.html global
       └── PARA AQUI (não posta)
```

### Fase 4 — Aprovação humana (Pedro)

```
Pedro abre _dashboard.html
       ↓
Vê todos os dias com: thumb + caption + first_comment + status DRAFT
       ↓
Clica numa data → vê preview.html detalhado
       ↓
Fala no chat: "posta o de DD/MM"
       ↓
Claude interativo (esta sessão) executa:
       python scripts/post.py --date YYYY-MM-DD --publish
```

### Fase 5 — Publicação + state update

```
python scripts/post.py --publish
       ├── upload mídia → Zernio /v1/media/presign + PUT
       ├── create post → Zernio /v1/posts (publishNow: true)
       ├── update historico.md (linha do post)
       ├── move ideia disponiveis.md → usadas.md
       └── (se Reel) move frase disponiveis → usadas
```

---

## 💾 Onde tudo é salvo

| Tipo de dado | Caminho | Quem escreve | Quem lê |
|---|---|---|---|
| Config canonical | `pages/pp-travel/*.md`, `page.yaml` | Pedro/Claude (raro) | SKILL.md, subagentes, scripts |
| Banco de ideias (estoque) | `pages/pp-travel/ideias/disponiveis.md` | copy-specialist (research), Pedro (manual) | copy-specialist |
| Ideias usadas (dedup) | `pages/pp-travel/ideias/usadas.md` | post.py (no --publish) | copy-specialist |
| Banco de frases (estoque) | `pages/pp-travel/banco-frases/reflexivas-disponiveis.md` | copy-specialist (research), Pedro | copy-specialist |
| Frases usadas | `pages/pp-travel/banco-frases/reflexivas-usadas.md` | post.py | copy-specialist |
| Histórico de posts | `pages/pp-travel/historico.md` | post.py (--publish) | copy-specialist (dedup 60d) |
| Sourcing diário | `data/instagram/pp-travel/YYYY-MM-DD/digest.md` | run_pp_sourcing.py | claude headless |
| Content escolhido | `data/instagram/pp-travel/YYYY-MM-DD/content.json` | claude headless | post.py |
| Auditoria visual | `data/instagram/pp-travel/YYYY-MM-DD/visual-audit.json` | visual-specialist | Pedro (review) |
| Mídia gerada | `data/instagram/pp-travel/YYYY-MM-DD/foto-*.png` ou `video-*.mp4` | post.py | post.py, preview.py |
| Render final | `data/instagram/pp-travel/YYYY-MM-DD/post-final.png` ou `reel-final.mp4` | post.py | Zernio, preview.py |
| Preview de revisão | `data/instagram/pp-travel/YYYY-MM-DD/preview.html` | preview.py | Pedro (browser) |
| **Dashboard global** | `data/instagram/pp-travel/_dashboard.html` | preview.py | Pedro (browser) ⭐ |
| Pesquisas arquivadas | `data/instagram/_research/*.md` | scripts de pesquisa | copy-specialist (próximas) |
| Ledger custos | `data/_gastos/openrouter.csv` | cost_tracker.py | Pedro (auditoria) |

---

## 🔌 Integrações externas

| Serviço | Uso | Auth |
|---|---|---|
| **OpenRouter** | Grok 4.3 (sourcing + research), Gemini 3.1 Flash Image (fotos), Veo 3.1 Lite (Reels) | `OPENROUTER_API_KEY` no `.env` |
| **Zernio** | Posting + media upload no Instagram | `ZERNIO_API_KEY` no `.env`, conta `@ia.executa` connected |
| **Google Drive** (MCP) | Read `Ideias de posts futuros.gdoc` 1× pra seeding | claude.ai connector |

---

## ✅ Checklist de saúde da skill

Pra verificar que tudo tá funcionando:

```bash
# 1. Skill carrega corretamente
ls .claude/skills/instagram-motor/SKILL.md          # existe

# 2. Subagentes referenciados existem
ls .claude/agents/copy-specialist.md                # existe
ls .claude/agents/visual-specialist.md              # existe

# 3. Scripts importam cost_tracker sem erro
python -c "import sys; sys.path.insert(0,'scripts'); from cost_tracker import register_cost; print('ok')"

# 4. Configs canonical presentes
ls pages/pp-travel/{guia-objetivos,voice,pilares,formatos,sourcing,historico}.md
ls pages/pp-travel/page.yaml

# 5. Bancos presentes
ls pages/pp-travel/ideias/disponiveis.md
ls pages/pp-travel/banco-frases/reflexivas-disponiveis.md

# 6. Templates HTML presentes
ls .claude/skills/instagram-motor/assets/template-v2-single-photo.html
ls .claude/skills/instagram-motor/assets/template-carousel-slide.html

# 7. Task Scheduler registrado
schtasks /Query /TN "ia-executa\pp-travel-instagram"

# 8. Ledger ativo
python scripts/cost_tracker.py 2026-06                # mostra resumo
```

---

## 🚨 Pontos críticos

1. **Aprovação humana obrigatória**: `post.py` default NÃO posta. Só `--publish` posta. NUNCA pular esse gate.
2. **Subagentes iteram em texto**: nem copy-specialist nem visual-specialist chamam OpenRouter pra mídia. Sempre texto.
3. **Cost tracking obrigatório**: todo script que chama OpenRouter PRECISA importar `cost_tracker` e registrar.
4. **HARD BANS**: voice.md tem 5 categorias proibidas (política, religião, tragédia, concorrentes, futebol-opinião). Filtro nas queries Grok + checklist nos subagentes.
5. **Acentuação pt-BR**: TODA copy precisa de acentos corretos. "Inspiração", não "Inspiracao".

---

## 📚 Onde encontrar mais detalhes

- **Workflow operacional passo a passo**: `SKILL.md` (na mesma pasta)
- **Princípios de viralização IG 2025**: `references/viralizacao.md`
- **Endpoints OpenRouter exatos**: `references/midias.md`
- **Histórico de decisões + aprovados/rejeitados**: `references/exemplos-aprovados.md`
- **Decisões de templates HTML/ffmpeg**: `references/templates.md`
- **Guia canonical PP-Travel (5 pilares completos)**: `pages/pp-travel/guia-objetivos.md`
