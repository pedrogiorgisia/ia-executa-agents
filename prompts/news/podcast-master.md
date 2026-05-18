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
  --instructions "Português brasileiro. Estilo de conversa entre dois apresentadores (uma voz feminina, uma masculina). Duração entre 3 e 5 minutos. Tom: profissional, descontraído, voltado para executivos não-técnicos. Comece com 'No resumo de IA de hoje...'. Cobra os 4-5 itens mais relevantes do top, sempre explicando 'o que aconteceu' e 'por que isso importa pra um gestor'. Termine com uma reflexão curta ou pergunta provocativa." \
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

### Passo 9 — Enviar email com o link via Resend

```bash
cat > /tmp/email-payload.json <<EOF
{
  "from": "Pedro Giorgis <$RESEND_FROM_EMAIL>",
  "to": ["$NEWS_EMAIL_DESTINATARIO"],
  "subject": "🎧 Podcast IA — $(date +%d/%m)",
  "html": "<div style='font-family: sans-serif; max-width: 600px;'><h2>🎧 Podcast IA — $(date +%d/%m)</h2><p>Resumo do dia em áudio (3-5 min):</p><p><a href='$LINK_PUBLICO' style='display: inline-block; padding: 12px 24px; background: #18181b; color: #fff; text-decoration: none; border-radius: 6px;'>▶ Ouvir podcast</a></p><p style='color: #666; font-size: 13px;'>Gerado automaticamente a partir do top.md de hoje.</p></div>"
}
EOF

curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/email-payload.json
```

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
