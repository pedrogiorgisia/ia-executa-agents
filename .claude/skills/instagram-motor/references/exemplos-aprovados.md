# Exemplos aprovados — referência visual

> Histórico do que o Pedro aprovou (com link pros arquivos) e o que rejeitou,
> com o motivo. Consultar sempre antes de definir um candidato pra evitar
> repetir erros já cometidos.

---

## ✅ APROVADOS

### 1. Inspiração — V2 full-bleed (5 mocks PP-Travel)

**Data:** 2026-06-01
**Pilar:** Inspiração, Educação, Engajamento, Prova Social, Conversão (5 mocks)
**Formato:** Single Photo
**Veredito Pedro:** "Agora sim, ficou boa"

**Arquivos:**
- [`data/instagram/pp-travel-mocks-v2/inspiracao.png`](../../../data/instagram/pp-travel-mocks-v2/inspiracao.png)
- [`data/instagram/pp-travel-mocks-v2/educacao.png`](../../../data/instagram/pp-travel-mocks-v2/educacao.png)
- [`data/instagram/pp-travel-mocks-v2/engajamento.png`](../../../data/instagram/pp-travel-mocks-v2/engajamento.png)
- [`data/instagram/pp-travel-mocks-v2/prova_social.png`](../../../data/instagram/pp-travel-mocks-v2/prova_social.png)
- [`data/instagram/pp-travel-mocks-v2/conversao.png`](../../../data/instagram/pp-travel-mocks-v2/conversao.png)

**Por que funcionou:**
- Foto Gemini 3.1 full-bleed (Alfama golden hour, janela avião, fjord, etc.)
- "PP TRAVEL" serifado pequeno no topo center
- Headline grande misturando peso normal/bold/italic
- Pílula branca com sub-headline
- Handle + "arrasta →" no rodapé
- Gradient escuro pro texto contrastar com foto

**Custo médio:** R$ 0,01 (Gemini Image)

---

### 2. Reel Reflexivo — Janela de avião golden hour

**Data:** 2026-06-01
**Pilar:** Inspiração Reflexiva
**Formato:** Reel 6s
**Modelo usado:** Veo 3.1 Fast (depois trocado por Lite)
**Frase overlay:** "Coisas não te seguem na lembrança. Lugares sim."

**Arquivos:**
- [`data/instagram/_veo-test/reflexivo-janela-FINAL.mp4`](../../../data/instagram/_veo-test/reflexivo-janela-FINAL.mp4)

**Por que funcionou:**
- Veo gerou janela de avião com clouds golden hour, ambient audio razoável
- Fade-in 1.2-2.3s, fade-out 4.5-5.7s da frase em 3 linhas centralizadas
- @pptravelinfinite rodapé com alpha 0.85
- Áudio do Veo mantido

**Custo:** R$ 4,32 (depois reduzido pra R$ 2,88 com Lite)

---

### 3. Reel Reflexivo — Pessoa de costas em fjord

**Data:** 2026-06-01
**Pilar:** Inspiração Reflexiva
**Formato:** Reel 6s
**Modelo usado:** Veo 3.1 Lite ✅ (decisão final — 50% mais barato)
**Frase overlay:** "Tem viagem que muda o que você lê, o que come, e quem você é."

**Arquivos:**
- [`data/instagram/_reels-reflexivos/pessoa-fjord-lite-FINAL.mp4`](../../../data/instagram/_reels-reflexivos/pessoa-fjord-lite-FINAL.mp4)

**Por que funcionou:**
- Veo Lite gerou mulher de costas em penhasco com fjord Norueguês ao fundo, blue hour
- 4 linhas da frase (overlay fade-in/out)
- Custo $0.48 (R$ 2,88) — metade do Fast

**Decisão derivada:** Veo 3.1 Lite é o **modelo padrão** pra Reels do motor. Veo Fast só se Lite falhar.

---

## ❌ REJEITADOS (não repetir)

### 1. V1 — Foto top 35% + bloco navy + logo bottom

**Data:** 2026-06-01
**Pilar:** 5 mocks (mesmo conteúdo do V2)
**Veredito Pedro:** "Tá horrível"

**Arquivos (NÃO usar como referência visual):**
- [`data/instagram/pp-travel-mocks/`](../../../data/instagram/pp-travel-mocks/) — pasta dos rejeitados

**Por que não funcionou:**
- Foto era gradient colorido (Pedro pediu: "gradient como foto não funciona")
- Layout "card FAQ" com bloco navy separado pra texto → parecia documento, não Instagram
- Pílula com destino no topo da foto não convencia
- Visual remetia ao `Post_FAQ1.jpg` antigo da PP-Travel — Pedro queria visual MAIS MODERNO

**Lição:** copiar exatamente o template antigo da PP-Travel ≠ entregar o que ela precisa hoje.

---

### 2. Manifesto @ia.executa (texto-only carrossel)

**Data:** 2026-05-28
**Pilar:** (teste inicial — não foi categorizado)
**Veredito Pedro:** "Ficou meio ruim né.. não tem skills que ajuda"

**Arquivos:**
- [`data/instagram/test-manifesto/`](../../../data/instagram/test-manifesto/) — 5 slides

**Por que não funcionou (na visão do Pedro):**
- Carrossel text-only no feed do IG fica "vazio"/chato
- Sem visual gancho ⇒ thumb fraca = ninguém desliza
- Estilo "Stratechery dark mode" ≠ Instagram

**Lição:** posts no IG **precisam de foto/vídeo de impacto**. Tipografia sozinha não viraliza.

---

### 3. Sourcing 7 queries Grok todo dia

**Data:** 2026-06-01
**Veredito Pedro:** "Achei o gasto muito alto, não faz sentido"

**Custo rejeitado:** R$ 1,62/exec = R$ 50/mês

**Substituído por:** 1-2 queries direcionadas por dia/pilar = R$ 7-15/mês.

**Lição:** rodar tudo todo dia desperdiça. Direcionar pelo pilar.

---

### 4. Sourcing trazendo @LulaOficial

**Data:** 2026-06-01
**Veredito Pedro:** "Pelo amor de deus nao envolva política"

**O que aconteceu:** tweet do Lula sobre recorde turismo BR (3.3k likes) apareceu no digest.

**Lição → HARD BAN política**: agora aplicado em `voice.md` e nas queries do Grok.

---

### 5. Post Lençóis Maranhenses (1ª versão) — não seguia o guia

**Data:** 2026-06-01 20:04
**Pilar:** Inspiração
**Formato:** Single Photo
**post_id Zernio:** `6a1e100c450e32196d2213be`
**Headline original:** "Junho é a única janela pros Lençóis com lagoas cheias. Depois disso, seca até fevereiro."

**Veredito:** publicado, mas violou checklist do guia. **Republicado** com correções.

**O que faltou (vs `guia-objetivos.md` §Pilar 2 Inspiração):**
- ❌ **Gatilho aspiracional** ("Imagine acordar nesse lugar...") — minha headline era factual
- ❌ **Equilíbrio sonho vs. realidade** ("Você pode estar aqui pagando menos do que imagina")
- ❌ **Link sutil com PP Travel** ("Isso é possível com nossa ajuda" + menção milhas)
- ❌ **CTA emocional/social** ("Com quem você levaria?", "Marca aqui") — meu CTA era reflexivo
- ❌ **Tom sensorial/emocional** — meu texto ficou cabeçalho de jornal

**O que funcionou:**
- ✅ Foto Gemini impactante
- ✅ Destino aspiracional mas acessível
- ✅ Sazonalidade real (urgência sutil)
- ✅ Sem política/tragédia
- ✅ Acentos pt-BR corretos

**Lição:** **Antes de finalizar QUALQUER candidato, rodar mentalmente o checklist do pilar
correspondente no `guia-objetivos.md`.** Se algum item OBRIGATÓRIO falta, refazer headline/caption.

---

### 6. Reel Reflexivo SEM overlay (Veo cru)

**Data:** 2026-06-01
**Veredito Pedro:** "não tem texto, não tem msg nenhuma inspiracional, não entendi.. teria que ter né?"

**O que aconteceu:** mostrei o output cru do Veo (só vídeo da janela) sem aplicar overlay da frase.

**Lição:** **nunca** mostrar Veo cru como entrega final. Sempre aplicar overlay completo (frase + handle) **antes** de mostrar pro Pedro como "Reel pronto".

---

## 📋 Decisões travadas (não retroceder)

| Decisão | Data | Motivo |
|---|---|---|
| Gemini 3.1 > Gemini 2.5 pra Image | 2026-06-01 | Resolução 1536 > 1024, qualidade editorial superior |
| Veo Lite > Veo Fast pra Reels | 2026-06-01 | 50% mais barato, mesma resolução 720p |
| 1-2 queries Grok/dia (não 7) | 2026-06-01 | Custo: R$ 7 vs R$ 50/mês |
| Foco em Inspiração + Engajamento + Reflexiva | 2026-06-01 | Outros 2 pilares dependem de docs alimentados pela Pri |
| Testar no @ia.executa antes do @pptravelinfinite | 2026-06-01 | Sem risco pra marca da Pri |
| SEM Telegram approval | 2026-06-01 | Posta direto, Telegram só notifica |
| Template V2 full-bleed | 2026-06-01 | Substitui template V1 (foto top + navy block) |
| Acentos pt-BR sempre | 2026-06-01 | Eu (Claude) estava escapando "Inspiracao" — corrigido |
| HARD BAN política | 2026-06-01 | Tweet do Lula apareceu, audiência cross-spectrum |
| Posts diretos (sem aprovação) | 2026-06-01 | Decisão de produto — Pedro confia no motor |

---

## 🔁 Como usar este arquivo

**Antes de gerar um candidato:**
1. Confira a lista de aprovados → usar como referência de qualidade
2. Confira a lista de rejeitados → não repetir o erro
3. Confira "Decisões travadas" → não propor algo que já foi descartado

**Depois de cada post no @ia.executa / @pptravelinfinite:**
- Se Pedro elogiar: adicionar ao "Aprovados" com link do post
- Se Pedro criticar: adicionar ao "Rejeitados" com motivo
- Se mudar uma decisão: atualizar "Decisões travadas"
