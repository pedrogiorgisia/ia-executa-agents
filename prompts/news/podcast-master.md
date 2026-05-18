# Podcast Master — Geração de Podcast Diário via NotebookLM

> Pipeline que pega o `top.md` mais recente, gera um podcast (audio overview) no NotebookLM, baixa o MP3, sobe na pasta pública do Drive e dispara email com o link.
>
> **Quando executar:** depois que o `news-master` já rodou e tem o `top.md` do dia.

---

## Contexto pra você (Claude)

Você é responsável por **transformar a curadoria de notícias do dia em um podcast curto** (3-5 minutos) que o Pedro vai enviar pra alunos da mentoria e/ou ouvir de manhã. A audiência é a mesma do news-master: **executivos, gestores e profissionais de produto interessados em IA, sem viés técnico hardcore**.

## Pré-requisitos

- `notebooklm-py` instalada e autenticada (Pedro já fez `notebooklm login`)
- Skill `notebooklm` registrada no Claude Code
- `top.md` do dia gerado pelo news-master em `data/news/$HOJE/top.md`
- Env vars carregadas: `GDRIVE_PODCASTS_PUBLIC_FOLDER_ID`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `NEWS_EMAIL_DESTINATARIO`

## Pipeline (executar nesta ordem)

### Passo 1 — Setup

```bash
export HOJE=$(date -u +%Y-%m-%d)
```

Crie a pasta `data/podcasts-publicos/` se não existir.

**Validar:** confirme que `data/news/$HOJE/top.md` existe. Se não existir, **aborte** com mensagem clara — sem `top.md` não tem o que virar podcast.

### Passo 2 — Criar notebook do dia no NotebookLM

Use a Skill `notebooklm`:

```
notebooklm create "News IA — Podcast $HOJE"
```

Capture o `notebook_id` retornado.

**Regra:** 1 notebook por dia. NÃO acumular fontes num notebook longo (degrada qualidade do áudio porque o NotebookLM cobre todas as fontes).

### Passo 3 — Adicionar `top.md` como fonte

```
notebooklm add-source <notebook_id> --file data/news/$HOJE/top.md
```

### Passo 4 — Gerar audio overview

```
notebooklm generate audio <notebook_id> \
  --instructions "Português brasileiro. Dois apresentadores com papéis distintos: (1) Apresentador/jornalista — voz feminina — apresenta cada notícia de forma objetiva e direta. (2) Especialista em IA — voz masculina — comenta cada notícia trazendo perspectiva analítica, contexto de mercado e implicações práticas pra empresas. Ritmo DINÂMICO E ÁGIL — sem pausas longas, sem voltar atrás, sem floreio. Falem rápido, em ritmo de podcast informativo profissional (NÃO em ritmo lento de podcast contemplativo). Cobra TODOS os itens do top.md, não só 4-5 — cada notícia ganha 20-40 segundos: a apresentadora descreve em 1-2 frases, o especialista comenta em 2-3 frases. Duração total 5-8 minutos. Comece com 'O que rolou no mundo da IA hoje, em poucos minutos.' Termine com uma observação curta do especialista sobre a notícia mais importante do dia." \
  --wait
```

`--wait` faz o CLI aguardar (1-3 min).

### Passo 5 — Baixar MP3 local (backup + fonte pro upload)

```
notebooklm download audio <notebook_id> --output data/podcasts/$HOJE.mp3
```

Validar: arquivo existe e tem **> 100KB**. Senão, aborte e não envie email.

### Passo 6 — Copiar MP3 pra pasta pública sincronizada

```bash
NOME_PODCAST="news-ia-podcast-$HOJE.mp3"
cp "data/podcasts/$HOJE.mp3" "data/podcasts-publicos/$NOME_PODCAST"
```

O Drive Desktop vai sincronizar automaticamente em ~10-30s (depende do tamanho).

### Passo 7 — Aguardar sincronização e pegar file_id do Drive

Aguarde 30 segundos pra dar tempo do Drive Desktop subir o arquivo.

```bash
sleep 30
```

Use **Google Drive MCP** pra encontrar o arquivo que acabou de subir:

```python
mcp__claude_ai_Google_Drive__search_files(
  query=f"title = '{NOME_PODCAST}' and parentId = '{GDRIVE_PODCASTS_PUBLIC_FOLDER_ID}'"
)
```

Capture o `id` do arquivo retornado. **Se não retornar nada após 30s**, tente mais 30s (até 3 tentativas). Se mesmo assim falhar, **registre erro e envie email com fallback usando o link da PASTA inteira:**

```
https://drive.google.com/drive/folders/$GDRIVE_PODCASTS_PUBLIC_FOLDER_ID
```

### Passo 8 — Construir link público

Quando tiver o `file_id`:

```
LINK_PUBLICO=https://drive.google.com/file/d/<file_id>/view?usp=sharing
```

### Passo 9 — Montar e enviar o email COMBINADO via Resend

Este passo monta UM email único: **banner do podcast no topo + todos os itens das notícias logo abaixo** (SEM cabeçalho "News IA" e SEM resumo executivo — só itens diretamente).

#### 9.1 — Obter os itens HTML

Você precisa do HTML formatado dos itens (já com "O que aconteceu / O que significa / Pra quem importa / botão Ver fonte").

**Estratégia mais simples:** **regere os itens** a partir do `top.md`. Cada item do `top.md` vira um bloco HTML usando o formato:

```html
<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin:20px 0; border-bottom:1px solid #e4e4e7; padding-bottom:20px;">
  <tr><td>
    <h2 style="margin:0 0 12px 0; font-size:17px; font-weight:600; color:#18181b; line-height:1.35;">TÍTULO_AQUI</h2>
    <p style="margin:0 0 10px 0; font-size:14px; color:#3f3f46;"><strong style="color:#18181b;">O que aconteceu:</strong> ...</p>
    <p style="margin:0 0 10px 0; font-size:14px; color:#3f3f46;"><strong style="color:#18181b;">O que isso significa pra você:</strong> ...</p>
    <p style="margin:0 0 14px 0; font-size:13px; color:#71717a;"><strong style="color:#52525b;">Pra quem importa mais:</strong> ...</p>
    <a href="LINK" style="display:inline-block; padding:8px 14px; background-color:#18181b; color:#fafafa; text-decoration:none; border-radius:6px; font-size:13px; font-weight:500;">Ver fonte →</a>
  </td></tr>
</table>
```

Lembre de escapar `<`, `>`, `&`, `"` no conteúdo de cada campo.

#### 9.2 — Aplicar `combined-email-template.html`

Leia `prompts/news/combined-email-template.html` e substitua:

| Placeholder | Valor |
|---|---|
| `{{DATA_HUMANA}}` | ex: "18 de maio de 2026" |
| `{{PODCAST_LINK}}` | URL pública do MP3 (do Passo 8) |
| `{{ITENS_HTML}}` | concatenação de todos os blocos de itens do 9.1 |
| `{{TIMESTAMP_GERACAO}}` | ex: "Gerado em 18/05/2026 às 07:30 BRT" |
| `{{TOTAL_ITENS}}` | número de itens do top.md |

Salve em `data/news/$HOJE/email-combinado.html`.

#### 9.3 — Enviar via Resend

```bash
jq -n \
  --arg from "Pedro Giorgis <$RESEND_FROM_EMAIL>" \
  --arg to "$NEWS_EMAIL_DESTINATARIO" \
  --arg subject "🎧 News IA — $(date +%d/%m)" \
  --rawfile html data/news/$HOJE/email-combinado.html \
  '{from: $from, to: [$to], subject: $subject, html: $html}' \
  > /tmp/email-combinado-payload.json

curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/email-combinado-payload.json
```

#### 9.4 — FALLBACK: se o podcast falhou

Se o podcast não foi gerado (NotebookLM caiu, MP3 < 100KB, link não obtido):
- **NÃO envie o email combinado** (não tem link de podcast)
- Envie o email original do news-master que está em `data/news/$HOJE/email.html` (assunto "📰 News IA — DD/MM")
- Marque no log que foi fallback

### Passo 10 — Output final

Imprima:
1. Notebook ID criado
2. Tamanho do MP3 (em MB)
3. File ID no Drive (ou aviso de fallback)
4. Link público final
5. Status HTTP do envio do email
6. Quaisquer erros encontrados

---

## Regras

- **1 notebook por dia.** Não acumular fontes.
- **Sempre baixar MP3 localmente** mesmo que o upload falhe — fica de backup.
- **Não envie email se o áudio falhou ou ficou < 100KB.**
- **Tom:** áudio é pro ICP executivo, não dev. As instruções de estilo no Passo 4 são críticas.
- **Limite:** 50 queries/dia no tier free do NotebookLM. Gerar podcast conta como query. Folga grande pra 1/dia.
- **Fallback do link:** se a busca via Drive MCP falhar, manda link da PASTA — funciona, só não é tão limpo.
