# Setup do dev-browser com perfil dedicado (Windows)

> **Doc técnico.** Como configurar o `dev-browser` pra automação de navegação em contas já logadas (Google, Meta, Anthropic, GitHub, Railway), de forma robusta no Windows.
>
> **Descoberto em 2026-04-13** ao tentar usar `dev-browser --connect` com o Chrome principal do Pedro. A abordagem ingênua falhou; a abordagem com perfil dedicado funciona de forma permanente.

---

## Por que o approach ingênuo falha

Chrome no Windows tem **singleton por user-data-dir**:

> Dois processos `chrome.exe` **nunca** coexistem usando a mesma pasta de perfil. Se um Chrome novo é lançado apontando pra um perfil já em uso, ele envia um IPC pro processo existente e morre — passando argumentos, **ignorando flags**.

Combinado com **background apps** (Chrome continua rodando mesmo sem janelas abertas, via extensões, Google Update, notification push), o resultado é:

1. Você fecha as janelas do Chrome
2. Mas processos fantasma continuam segurando o lock do perfil padrão
3. Você roda `chrome.exe --remote-debugging-port=9222`
4. O novo processo detecta o lock, delega, e morre **sem abrir a porta 9222**

Tentar matar todos os processos (`Stop-Process -Name chrome -Force`) **às vezes** funciona, mas é frágil — Google Update respawn, background apps voltam, etc.

## A solução profissional — perfil dedicado paralelo

**Padrão usado por devs de automação há anos:**

Criar uma pasta de perfil **separada** pro Chrome debug, permitindo que ele rode **ao lado** do Chrome normal, totalmente independente.

**Vantagens:**
- Seu Chrome normal continua aberto, intocado
- A porta 9222 funciona 100% das vezes (pasta diferente = instância diferente)
- Logins persistem nesse perfil dedicado (cookies salvos separados do Chrome normal)
- Você loga uma vez em cada conta (Google, Meta, etc), daí é automático

**Desvantagem:**
- Primeira vez requer login manual em cada serviço que quer automatizar
- Ocupa disco (~300 MB após logins completos)

---

## Setup (passo a passo)

### 1. Pré-requisitos

- `dev-browser` instalado globalmente: `npm install -g dev-browser`
- Chromium do Playwright instalado: `dev-browser install`
- Node 20+ e npm 10+

### 2. Criar a pasta do perfil dedicado

```bash
mkdir -p "C:/Users/pedro/chrome-debug-profile"
```

### 3. Lançar o Chrome debug em background

```bash
"C:/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:\Users\pedro\chrome-debug-profile" \
  "about:blank" &
disown
```

**O que acontece:**
- Abre uma janela nova do Chrome em paralelo ao Chrome normal
- Perfil limpo (primeira vez) ou perfil persistente (próximas vezes)
- Porta 9222 ativa
- Chrome fica rodando em background; fechar o terminal não mata

### 4. Verificar que a porta está ativa

```bash
powershell.exe -Command "Get-NetTCPConnection -LocalPort 9222 -ErrorAction SilentlyContinue | Format-Table"
curl -s http://localhost:9222/json/version
```

Deve mostrar a porta ativa + um JSON com `"Browser": "Chrome/X.Y.Z.W"`.

### 5. Primeira vez — logar manualmente

Na janela do Chrome debug que tá aberta, **logar manualmente** em todas as contas que você quer automatizar:

- **Google** (`accounts.google.com`) — pro Gemini API, Google AI Studio, GitHub via OAuth Google, etc.
- **Meta / Facebook** (`facebook.com`) — pra Meta Developer Console, App Review
- **Anthropic** (`console.anthropic.com`) — pra Claude API
- **GitHub** (`github.com`) — pra operações no repo
- **Railway** (`railway.app`) — pra deploys
- **Instagram** (`instagram.com`) — pra view de conta existente (mas NÃO pra signup — Instagram bloqueia signup automatizado via device fingerprint)

Uma vez logado, cookies persistem nessa pasta. Próxima sessão = já logado.

### 6. Testar a conexão via dev-browser

```bash
dev-browser --connect <<'EOF'
const page = await browser.getPage("main");
await page.goto("https://aistudio.google.com/app/apikey");
console.log("URL atual:", page.url());
console.log("Título:", await page.title());
EOF
```

Se retornar a página real (não tela de login), o setup está completo.

---

## Uso recorrente

Nas próximas sessões, o fluxo é mais simples:

```bash
# 1. Verificar se o Chrome debug ainda tá rodando
powershell.exe -Command "Get-NetTCPConnection -LocalPort 9222 -ErrorAction SilentlyContinue | Format-Table"

# 2. Se não tá, relançar (mesmo comando do passo 3 do setup)
# 3. Testar dev-browser --connect
```

O Chrome debug pode ficar rodando 24/7 sem problema. Pra fechar:
```bash
powershell.exe -Command "Get-Process chrome -ErrorAction SilentlyContinue | Where-Object { \$_.Path -like '*chrome.exe' } | ForEach-Object { \$_.MainWindowTitle }"
```

Pra matar só o debug (cuidado pra não matar o Chrome normal) — simples é fechar a janela dele manualmente.

---

## Segurança

**Porta 9222 é localhost-only por padrão.** Não escuta na rede, só 127.0.0.1. Então o debug só é acessível por processos **na sua máquina**. Segurança aceitável pra uso pessoal.

**Se você rodar numa VM compartilhada, VPS ou cloud instance**, revise antes de ativar.

**Não commitar o perfil** — `chrome-debug-profile` contém cookies de sessão. Adicionar ao `.gitignore` se estiver dentro de um repo:
```
chrome-debug-profile/
```

---

## O que dev-browser CONSEGUE e NÃO CONSEGUE fazer

**Consegue:**
- ✅ Navegar páginas, clicar, preencher formulários, tirar screenshots
- ✅ Reutilizar sessões logadas (via `--connect`)
- ✅ Automatizar fluxos em contas já autenticadas
- ✅ Scraping de páginas dinâmicas
- ✅ Testes end-to-end de sites

**Não consegue (limites físicos):**
- ❌ **CAPTCHAs** — Google reCAPTCHA, hCaptcha, Cloudflare Turnstile detectam browser automation
- ❌ **SMS 2FA** — o código vai no celular, não há como ler
- ❌ **Device fingerprinting** — Instagram, Meta, Amazon detectam via fingerprint mesmo com perfil persistente
- ❌ **Signup de conta nova** em sites rigorosos (Instagram, Meta) — combina CAPTCHA + SMS + fingerprint
- ❌ **Inserção de cartão de crédito** — por segurança, deve ser feito manualmente pelo usuário

**O modelo mental:** dev-browser é **automação assistida**, não **substituição do humano**. Tarefas que exigem login em contas suas já existentes = viável. Tarefas que exigem provar que você é humano = requerem você.

---

## Skills comportamentais recomendadas

Quando escrever um script dev-browser:

1. **Primeiro passo sempre é um probe**: navegar, tirar screenshot, verificar URL/title. Não assumir estado.
2. **`waitForSelector` antes de clicar** — a página pode estar renderizando.
3. **Capturar screenshots em pontos-chave** — facilita debug se der erro.
4. **Timeout generoso** (30s+) em redes lentas ou páginas pesadas (Google, Meta).
5. **Tratar erros graciosamente** — se um seletor mudar, o script deve falhar com mensagem clara, não explodir.

---

## Referência do dev-browser

- **Repo:** https://github.com/sawyerhood/dev-browser
- **Docs:** `dev-browser --help`
- **API disponível no sandbox:** Playwright Page API (`goto`, `click`, `fill`, `locator`, `screenshot`, etc.)
- **Sandbox:** QuickJS WASM — sem acesso a `require`, `fs`, `fetch`, `process`. Só `browser`, `console`, `setTimeout`, `saveScreenshot`, `writeFile`, `readFile`.

---

*Última atualização: 2026-04-13. Documento criado após resolver o problema de `--connect` não funcionar com o Chrome principal. Atualizar se a solução mudar.*
