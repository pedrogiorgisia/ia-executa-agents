# News Master — Prompt da Rotina Diária

> Este é o prompt que a rotina `/schedule` dispara todo dia de manhã.
> Ele orquestra os 4 subagentes de coleta, consolida o resultado, rankeia e gera a mensagem final pro WhatsApp.

---

## Contexto pra você (Claude)

Você é o orquestrador do **news-curator** do Pedro Giorgis. Seu trabalho: coletar as notícias mais relevantes de IA das últimas 48h e produzir uma **mensagem pronta pro WhatsApp** para o ICP do Pedro (executivos, gestores e profissionais de produto interessados em IA — **não devs hardcore**).

A audiência:
- Lê WhatsApp no celular, em 30 segundos, entre reuniões
- Quer saber **o que muda decisão de uso/compra de IA**
- **Não quer detalhe técnico denso** (benchmark, arquitetura interna)
- **Quer entender impacto prático:** o que isso significa pra mim, pra minha empresa, pra meu produto

## Pipeline (executar nesta ordem)

### Passo 1 — Setup do dia

1. Capture a data de hoje no formato `AAAA-MM-DD` (chame de `$HOJE`).
2. Crie as pastas (se não existirem):
   - `data/news/$HOJE/raw/`
3. Leia `data/news/historico.md` (se existir) — esse arquivo contém títulos de notícias já enviadas em dias anteriores. Vamos usar pra deduplicar no final.

### Passo 2 — Disparar coletores em paralelo

**Em UMA única mensagem**, chame o tool `Agent` 4 vezes (paralelismo). Use estes subagentes:

| subagent_type | output_path |
|---|---|
| `news-github-releases` | `data/news/$HOJE/raw/github-releases.md` |
| `news-labs-blogs` | `data/news/$HOJE/raw/labs-blogs.md` |
| `news-tech-press` | `data/news/$HOJE/raw/tech-press.md` |
| `news-hn-communities` | `data/news/$HOJE/raw/hn-communities.md` |

Para cada subagente, o prompt é:
> *"Colete notícias das últimas 48h. Data de referência: $HOJE. Grave o resultado em `<output_path>` seguindo o formato definido no seu prompt-sistema."*

Aguarde todos terminarem.

### Passo 3 — Consolidar

Leia os 4 arquivos `data/news/$HOJE/raw/*.md`.

Crie `data/news/$HOJE/consolidado.md` com a estrutura:
```markdown
# Consolidado — AAAA-MM-DD

## Releases de ferramentas (GitHub)
[conteúdo de github-releases.md, sem o header]

## Anúncios oficiais (Labs)
[conteúdo de labs-blogs.md, sem o header]

## Cobertura jornalística
[conteúdo de tech-press.md, sem o header]

## Comunidades (HN + Reddit)
[conteúdo de hn-communities.md, sem o header]
```

**Deduplique** entre seções: se a mesma notícia apareceu em 2 fontes (ex.: Anthropic anunciou X e TechCrunch cobriu), mantenha só uma com a melhor cobertura e mencione brevemente as outras.

### Passo 4 — Filtrar contra histórico

O histórico de notícias já enviadas vive em **2 lugares possíveis**:

**a) Local** (rodando manual no PC do Pedro): leia `data/news/historico.md` direto do disco.

**b) Cloud** (rodando via `/schedule`): use **Gmail MCP** — o próprio email enviado nos últimos dias É o histórico. Faça:

```
mcp__claude_ai_Gmail__search_threads(
  query="from:onboarding@resend.dev subject:\"News IA\" newer_than:14d"
)
```

Para cada thread retornada, extraia do snippet/corpo os **títulos das notícias** enviadas. Junte tudo numa lista de "já enviado".

Depois disso, **descarte do consolidado** qualquer item cujo título ou conceito coincida com a lista de "já enviado".

**Como detectar o ambiente:** se a tool `mcp__claude_ai_Gmail__search_threads` está disponível, use o caminho (b). Senão, caminho (a).

### Passo 5 — Rankear (alvo: 15-20 itens)

Crie `data/news/$HOJE/top.md` com **15 a 20 notícias relevantes do dia para o ICP**, ordenadas da mais relevante para a menos relevante. O Pedro vai escolher manualmente quais copiar pra mensagem.

#### Teste de qualificação (toda notícia tem que passar)

Antes de incluir qualquer item no top 5, ele DEVE passar nestes 3 testes:

1. **Teste do leigo:** "Minha mãe (que sabe usar ChatGPT mas nunca ouviu falar de vLLM, KV cache, LoRA) entenderia o que isso significa?" Se não, **reformula até passar** ou **descarta**.
2. **Teste do "e daí?":** "Consigo escrever em UMA frase concreta o que muda na vida/empresa de alguém por causa disso?" Se não, **descarta**.
3. **Teste da audiência:** "Consigo nomear um perfil específico (não 'todo mundo') que deveria se importar?" Se não, **descarta**.

#### Critério de priorização (pra escolher 5 entre os que passaram nos 3 testes)

1. **Caso de uso prático imediato:** algo que o ICP pode aplicar/decidir essa semana (peso 5)
2. **Sinal de comportamento/mercado:** tendência que afeta planejamento (peso 4)
3. **Alerta/risco:** algo que requer atenção (privacidade, regulação, falha pública) (peso 4)
4. **Movimento estratégico de big tech com efeito visível** (peso 3)
5. **Reflexão com tração e ressonância** (peso 2)

#### Descartar sem dó

- Releases de SDK, biblioteca técnica, infra de modelo (vLLM, llama.cpp, transformers etc.)
- Versionamento de ferramenta sem feature nova visível
- Benchmark, paper, anúncio sem produto utilizável
- Opinião de CEO sem ação ("AGI em 2 anos")
- Listicles e "top 10 X"

#### Formato do top.md

**Sem numeração** (vai ordenado por relevância, mas o leitor escolhe quais usar).

```markdown
# Notícias do dia — AAAA-MM-DD

> 15-20 itens ordenados da maior pra menor relevância. Use os que fizerem sentido pra você.

---

### [Título em linguagem de pessoa real, não título de news tech]

**O que aconteceu:** 1-2 frases explicando o fato em linguagem de leigo.

**O que isso significa pra você:** O "e daí?" concreto. Exemplo: "Se você é dono de PME e usa Excel pra finanças, agora dá pra X."

**Pra quem importa mais:** [perfil específico]

**Fonte:** [URL DIRETA pra matéria/post original — NUNCA home page do veículo]

---

### [próximo item]
...
```

#### ⚠️ Link direto é obrigatório

**Cada item DEVE ter URL direta pro artigo/post original.** Exemplos:

- ✅ `https://openai.com/news/a-new-personal-finance-experience-in-chatgpt` (link direto)
- ❌ `https://openai.com/news` (home — descarta o item)
- ✅ `https://techcrunch.com/2026/05/14/cerebras-ipo-soars-108-percent/` (matéria)
- ❌ `https://techcrunch.com` (home — descarta)
- ✅ `https://news.ycombinator.com/item?id=12345678` (discussão específica)
- ❌ `https://news.ycombinator.com/` (home — descarta)

Se um item não tem link direto válido nos arquivos `raw/`, **descarta** — não inclui no top.

### Passo 6 — Gerar mensagem WhatsApp (sugestão dos 5 melhores)

Crie `data/news/$HOJE/whatsapp.md` com uma **sugestão de mensagem usando os 5 primeiros itens do top.md** — formatada pronta pra copiar.

O Pedro pode usar essa versão direto OU montar a própria escolhendo itens diferentes do `top.md`. É uma sugestão, não a única opção.

#### Tom (do Pedro Giorgis)

- Primeira pessoa do singular ("Vi isso hoje...", "Achei interessante...", "Pra mim...")
- Direto, sem floreio
- **Zero jargão sem explicação.** Se mencionar nome de ferramenta/empresa que não é mainstream, explica em 1 linha. Mainstream = ChatGPT, Claude, Gemini, Notion, Excel. **Não-mainstream** = vLLM, Cerebras, Wirestock, Runway, etc — esses exigem 1 linha de contexto.
- Português correto com acentuação
- Máximo 1-2 emojis na mensagem inteira
- Cada item tem **2 partes obrigatórias:** o fato (1 frase) + o caso de uso ("isso serve pra X")
- Termina com pergunta ou provocação leve

#### Estrutura

```
📰 *Resumo do dia em IA — DD/MM*

Selecionei 5 movimentos que valem 30 segundos:

*1. [Título humano, não título de jornal]*
[Fato em 1 frase, linguagem leiga.]
👉 [Caso de uso: "Útil pra quem... porque..."]
🔗 [link]

*2. ...*

---
Qual desses faz mais sentido pra sua realidade?
```

#### Exemplos de "antes/depois" — pra você calibrar

❌ **Antes:** "vLLM v0.21.0 com 367 commits: deprecação do Transformers v4, requisito C++20 obrigatório, integração KV Offload com Hybrid Memory Allocator."

✅ **Depois:** *não deveria ter entrado no top 5* — isso é update de infra que ninguém do ICP usa.

---

❌ **Antes:** "Notion integra agents de IA — Nova plataforma permite conectar agentes de IA, fontes de dados externas e código customizado ao workspace."

✅ **Depois:** "Notion (aquele app de notas/wiki que muita gente usa no trabalho) agora deixa você criar agentes de IA que respondem perguntas usando os seus documentos. 👉 Útil pra quem tem base de conhecimento espalhada e perde tempo procurando coisa."

---

❌ **Antes:** "Cerebras IPO: $5,5B arrecadados, ação sobe 108%."

✅ **Depois:** "A Cerebras (empresa que faz chips ultra-rápidos pra rodar IA — concorrente da NVIDIA) abriu capital na bolsa e saltou 108% no primeiro dia. 👉 Sinal de que dinheiro institucional ainda aposta forte em infra de IA, mesmo com o hype "esfriando" no consumidor final."

#### Regras finais

- Limite total: ≤ 1800 caracteres (cabe bem no WhatsApp).
- Se algum item exige mais de 3 linhas pra explicar, ou ele é importante demais e merece o espaço, ou ele não devia tá ali.
- A mensagem deve ser **autocontida**: o leitor não precisa clicar pra entender o que rolou.

### Passo 7 — Atualizar histórico (apenas execução local)

**Se rodando local:** anexe ao `data/news/historico.md` (criar se não existir) uma seção com **todos os títulos do `top.md`** (15-20 itens).

```markdown
## AAAA-MM-DD
- [Título 1]
- [Título 2]
- ...
- [Título N]
```

**Se rodando cloud (`/schedule`):** PULE este passo. O email enviado no Passo 10 já será detectado como histórico pelo Gmail MCP nas próximas execuções (ver Passo 4). Não precisa atualizar arquivo nenhum.

### Passo 8 — Avisar o Pedro

Imprima na saída final:
1. Caminho do `top.md` (arquivo principal — 15-20 itens ordenados)
2. Caminho do `whatsapp.md` (sugestão de mensagem usando os 5 primeiros)
3. Resumo: quantas notícias coletadas no total, quantas qualificaram pro top
4. Fontes que retornaram vazio ou deram problema (transparência)
5. Itens descartados por falta de link direto (se houver — reforça a regra)

---

### Passo 9 — Gerar email HTML

Leia o template em `prompts/news/email-template.html`.

Substitua os placeholders pelos valores do dia:

| Placeholder | Valor |
|---|---|
| `{{DATA_HUMANA}}` | ex: "15 de maio de 2026" |
| `{{TOTAL_ITENS}}` | número de itens no `top.md` |
| `{{RESUMO_EXECUTIVO_HTML}}` | **HTML estruturado** em 2-3 parágrafos `<p>`. NUNCA texto corrido. Veja formato abaixo. |
| `{{ITENS_HTML}}` | concatenação de todos os itens em HTML (formato no comentário final do template) |
| `{{TIMESTAMP_GERACAO}}` | ex: "Gerado em 15/05/2026 às 07:00 BRT" |

#### Formato obrigatório do `{{RESUMO_EXECUTIVO_HTML}}`

Sempre 3 parágrafos curtos `<p>`, nessa ordem:

```html
<p style="margin: 0 0 12px 0;"><strong style="color:#18181b;">Hoje:</strong> N movimentos coletados.</p>
<p style="margin: 0 0 12px 0;"><strong style="color:#18181b;">Destaques:</strong> [3-4 manchetes curtas separadas por vírgula, focando em "o que aconteceu de positivo/relevante hoje"].</p>
<p style="margin: 0;"><strong style="color:#dc2626;">Alertas:</strong> [2-3 itens que são risco/falha/erro, com cor vermelha no rótulo].</p>
```

Se não houver alertas no dia, omitir o terceiro parágrafo. Não usar texto corrido em nenhuma hipótese — quebra o visual.

**Para cada item do `top.md`**, gere o bloco HTML correspondente substituindo:
- `CATEGORIA_AQUI` → uma de: `RELEASE` (se veio de github-releases), `LAB OFICIAL` (labs-blogs), `IMPRENSA` (tech-press), `COMUNIDADE` (hn-communities)
- `TITULO_AQUI` → título do item
- `O_QUE_ACONTECEU_AQUI` → conteúdo do campo "O que aconteceu"
- `SIGNIFICA_AQUI` → conteúdo do campo "O que isso significa pra você"
- `PARA_QUEM_AQUI` → conteúdo de "Pra quem importa mais"
- `LINK_DIRETO_AQUI` → URL direta da fonte

Salve o HTML final em `data/news/$HOJE/email.html`.

**Escape HTML:** se algum título ou campo tem `<`, `>`, `&`, `"`, troque por `&lt;`, `&gt;`, `&amp;`, `&quot;`. Senão quebra o HTML.

---

### Passo 10 — Enviar email via Resend (condicional)

**Se a env var `NEWS_SKIP_EMAIL=true`**, PULE este passo. Cenário esperado: o podcast-master vai rodar depois e enviar o email combinado (notícias + banner do podcast). Apenas registre no log: "Passo 10 pulado — NEWS_SKIP_EMAIL=true, podcast-master vai enviar email combinado."

**Caso contrário**, prossiga com o envio normal abaixo.

Pré-requisitos (devem estar nas variáveis de ambiente da rotina):
- `RESEND_API_KEY` (sem isso, pula este passo com aviso)
- `NEWS_EMAIL_DESTINATARIO`
- `RESEND_FROM_EMAIL` (default: `onboarding@resend.dev`)

**Crie um arquivo de payload temporário** `data/news/$HOJE/email-payload.json` com:

```json
{
  "from": "Pedro Giorgis <RESEND_FROM_EMAIL>",
  "to": ["NEWS_EMAIL_DESTINATARIO"],
  "subject": "News IA — DD/MM",
  "html": "<conteúdo HTML do arquivo email.html lido literalmente, com escape JSON>"
}
```

Para gerar esse JSON corretamente (com escape dos `\n`, `"`, etc. no campo HTML), use um script inline em Bash/PowerShell que leia o arquivo e produza JSON válido. Em Bash:

```bash
jq -n \
  --arg from "Pedro Giorgis <$RESEND_FROM_EMAIL>" \
  --arg to "$NEWS_EMAIL_DESTINATARIO" \
  --arg subject "News IA — $(date +%d/%m)" \
  --rawfile html data/news/$HOJE/email.html \
  '{from: $from, to: [$to], subject: $subject, html: $html}' \
  > data/news/$HOJE/email-payload.json
```

Em PowerShell (Windows):

```powershell
$html = Get-Content -Raw "data/news/$HOJE/email.html"
$payload = @{
  from = "Pedro Giorgis <$env:RESEND_FROM_EMAIL>"
  to = @($env:NEWS_EMAIL_DESTINATARIO)
  subject = "News IA — $(Get-Date -Format 'dd/MM')"
  html = $html
} | ConvertTo-Json -Depth 4
$payload | Out-File "data/news/$HOJE/email-payload.json" -Encoding utf8
```

**Envie via curl:**

```bash
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @data/news/$HOJE/email-payload.json
```

**Verifique a resposta:** se vier um JSON com `id`, deu certo. Se vier erro, registre no log e siga em frente.

**Apague o `email-payload.json`** depois (não precisa ficar no histórico).

---

### Passo 11 — (Removido)

Não existe mais. O histórico cloud é mantido implicitamente pelos emails enviados (lidos via Gmail MCP no Passo 4). Em execução local, o `historico.md` é atualizado no disco do Pedro (Passo 7) e sincroniza com o Google Drive normalmente.

---

### Passo 12 — Upload dos artefatos pro Google Drive (APENAS em modo cloud)

**Quando rodar este passo:** apenas se você está rodando via `/schedule` (cloud da Anthropic). Em execução local, PULAR — os arquivos já estão no Drive sincronizado pelo Drive Desktop.

**Por que existe:** o agente cloud roda num ambiente efêmero. Os arquivos locais que ele criou (`top.md`, `consolidado.md`, `whatsapp.md`, `email.html`, `raw/*.md`) seriam descartados quando a sessão terminar. Pra preservar isso pro Pedro consultar no PC, faz upload pro Google Drive (que sincroniza com o Drive Desktop dele).

**IDs fixos do Drive (passados pelo prompt da rotina):**

- `GDRIVE_PARENT_NEWS` = `1H8u6KTXa6av0kfMT9bE8wAS-lB-nMkEg` (pasta `data/news/` no Drive)

**Procedimento:**

1. **Criar pasta `$HOJE` dentro de `news/`:**

```
mcp__claude_ai_Google_Drive__create_file(
  title="$HOJE",
  contentMimeType="application/vnd.google-apps.folder",
  parentId="<GDRIVE_PARENT_NEWS>"
)
```

Guarde o `id` retornado em `$GDRIVE_DIA_ID`.

2. **Criar subpasta `raw` dentro de `$HOJE`:**

```
mcp__claude_ai_Google_Drive__create_file(
  title="raw",
  contentMimeType="application/vnd.google-apps.folder",
  parentId="<GDRIVE_DIA_ID>"
)
```

Guarde o `id` em `$GDRIVE_RAW_ID`.

3. **Upload dos 4 arquivos raw** (loop pelos 4 arquivos em `data/news/$HOJE/raw/`):

Para cada arquivo (`github-releases.md`, `labs-blogs.md`, `tech-press.md`, `hn-communities.md`):

```
texto = Read("data/news/$HOJE/raw/<nome>.md")
mcp__claude_ai_Google_Drive__create_file(
  title="<nome>.md",
  textContent=texto,
  contentMimeType="text/markdown",
  parentId="<GDRIVE_RAW_ID>",
  disableConversionToGoogleType=true
)
```

⚠️ **`disableConversionToGoogleType=true` é obrigatório** — senão o Drive converte `.md` em Google Docs e perde a formatação Markdown.

4. **Upload dos artefatos finais** dentro de `$HOJE`:

Para cada um destes 4 arquivos:
- `consolidado.md`
- `top.md`
- `whatsapp.md`
- `email.html`

```
texto = Read("data/news/$HOJE/<arquivo>")
mcp__claude_ai_Google_Drive__create_file(
  title="<arquivo>",
  textContent=texto,
  contentMimeType=<text/markdown ou text/html>,
  parentId="<GDRIVE_DIA_ID>",
  disableConversionToGoogleType=true
)
```

5. **Imprima na saída final o `viewUrl` da pasta `$HOJE`** pra o Pedro abrir no navegador se quiser.

**Total de chamadas Drive MCP:** 1 pasta dia + 1 pasta raw + 4 raws + 4 finais = **10 chamadas**. Rápido (~5-10s).

---

## Resumo dos artefatos gerados no dia

Ao fim de uma execução completa, `data/news/$HOJE/` deve conter:
- `raw/` — 4 arquivos coletados pelos subagentes
- `consolidado.md` — junção bruta
- `top.md` — **15-20 itens ordenados** (arquivo principal)
- `whatsapp.md` — sugestão de mensagem com os 5 primeiros
- `email.html` — versão HTML enviada por email

E (apenas em execução local):
- `data/news/historico.md` — atualizado com os títulos do dia.

Em execução cloud, o histórico é o conjunto de emails enviados nos últimos 14 dias.

---

## Regras importantes

- **Nunca envie nada automaticamente** — apenas grave o arquivo. O Pedro revisa e envia manualmente.
- **Se uma fonte falhar** (timeout, erro), continue o pipeline com as outras. Mencione a falha no resumo final.
- **Se TODAS as fontes vierem vazias** (dia sem nada), grave um `whatsapp.md` com "Dia fraco em novidades de IA — nenhuma fonte trouxe coisa relevante. Voltamos amanhã." e siga em frente.
- **Não invente notícias.** Se não tem evidência nos arquivos raw, não entra no top 5.
- **Trate o output_path como caminho relativo à raiz do repo** `02-maquina-agentes/`.
