# News Curator — Output

Esta pasta recebe a saída diária do **news-curator**, um pipeline que coleta notícias de IA das últimas 48h, produz um arquivo `top.md` com 15-20 itens ordenados por relevância e **envia tudo por email** com layout HTML.

## Estrutura

```
data/news/
├── README.md              ← este arquivo
├── historico.md           ← títulos já enviados (anti-duplicação, versionado)
└── AAAAMMDD/              ← uma pasta por dia (gitignored)
    ├── raw/
    │   ├── github-releases.md
    │   ├── labs-blogs.md
    │   ├── tech-press.md
    │   └── hn-communities.md
    ├── consolidado.md
    ├── top.md             ← ★ 15-20 itens ordenados
    ├── whatsapp.md        ← sugestão de mensagem usando os 5 primeiros
    └── email.html         ← versão enviada por email
```

As pastas datadas são **gitignored**. Apenas `historico.md` e este README ficam versionados.

---

## Setup (uma vez)

### 1. Resend (envio de email)

1. Cria conta em [resend.com](https://resend.com) (gratuita, 3k emails/mês).
2. Em **API Keys**, gera uma nova key e copia.
3. (Opcional, recomendado) **Verifica um domínio próprio** em **Domains** pra que o email venha de `news@ia-executa.com` ao invés de `onboarding@resend.dev`. Se pular, funciona igual, só fica com remetente genérico no começo.

### 2. GitHub PAT (pra rotina commitar histórico)

1. Vai em [github.com/settings/tokens?type=beta](https://github.com/settings/tokens?type=beta) — **fine-grained personal access token**
2. **Repository access:** Only select repositories → escolhe `ia-executa-agents`
3. **Permissions:** Repository permissions → Contents → **Read and write**
4. Expira em 1 ano (ou no máximo permitido). Anota na agenda pra rotacionar.

### 3. `.env` local (pra rodar manual no seu PC)

Edita `02-maquina-agentes/.env` (já existe, copiado de `.env.example`):

```
RESEND_API_KEY=re_SUA_KEY_AQUI
RESEND_FROM_EMAIL=onboarding@resend.dev    # ou seu domínio verificado
NEWS_EMAIL_DESTINATARIO=pedro.giorgis@gmail.com
GITHUB_PAT=ghp_SEU_PAT_AQUI
GITHUB_REPO=pedrogiorgisia/ia-executa-agents
```

`.env` é gitignored — **nunca sobe pro GitHub**.

### 4. Painel `/schedule` da Anthropic (pra rotina agendada)

Quando você configurar a rotina via skill `/schedule`, cola os mesmos secrets no painel da rotina (a skill pergunta). Anthropic guarda criptografado.

Os 5 secrets que a rotina precisa:
- `RESEND_API_KEY`
- `RESEND_FROM_EMAIL`
- `NEWS_EMAIL_DESTINATARIO`
- `GITHUB_PAT`
- `GITHUB_REPO`

---

## Como rodar

### Manual (Fase 1 — calibragem)

Abre Claude Code na raiz do repo (`02-maquina-agentes/`) e cola:

```
Execute o pipeline em prompts/news/news-master.md
```

O pipeline:
1. Cria pasta do dia
2. Dispara os 4 subagentes em paralelo
3. Consolida, deduplicacia, rankeia
4. Gera `top.md`, `whatsapp.md`, `email.html`
5. Envia o email
6. Atualiza `historico.md` (em manual, não commita)

### Agendado (Fase 2 — após calibragem)

Configura via skill `/schedule` (Claude Code):

```
/schedule
```

- **Horário sugerido:** todo dia às 07:00 BRT (10:00 UTC)
- **Prompt:** `Execute o pipeline em prompts/news/news-master.md`
- **Secrets:** os 5 listados acima
- **Repo:** `pedrogiorgisia/ia-executa-agents` (branch `main`)

Em modo agendado, o passo 11 também executa: commit + push do `historico.md` de volta no GitHub.

---

## Fontes monitoradas

~20 fontes em 4 subagentes:

- **`news-github-releases`** — 9 repos via `.atom` (Claude Code, Gemini CLI, Aider, Continue, ElevenLabs, llama.cpp, vLLM, Codex)
- **`news-labs-blogs`** — 8 labs (Anthropic, OpenAI, DeepMind, Mistral, xAI, Perplexity, Cohere, Meta AI)
- **`news-tech-press`** — 5 veículos (TechCrunch, The Verge, Ars Technica, MIT Tech Review, VentureBeat)
- **`news-hn-communities`** — Hacker News + r/LocalLLaMA

## ICP da curadoria

Executivos, gestores, profissionais de produto interessados em IA. **Não devs hardcore.**
- Inclusão: muda decisão prática de uso/compra de IA
- Exclusão: jargão técnico, opinião sem ação, hype sem produto

## Layout do email

Minimal/executive. Cabeçalho preto, fundo branco, destaque azul `#3b82f6`. Mobile-first (renderiza bem em iOS Mail, Gmail Web e Outlook). Template em [`prompts/news/email-template.html`](../../prompts/news/email-template.html).

Cada item no email tem:
- **Tag de categoria** (RELEASE, LAB OFICIAL, IMPRENSA, COMUNIDADE)
- **Título** humano
- **O que aconteceu** (1-2 frases leigas)
- **O que isso significa pra você** (caso de uso concreto)
- **Pra quem importa mais** (perfil específico)
- Botão **Ver fonte →** (link direto à matéria)
