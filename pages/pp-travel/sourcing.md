# Sourcing — De onde vem o conteúdo do motor

> A criatividade do motor depende da qualidade do que ele LÊ antes de gerar.
> Esse arquivo lista todas as fontes que o motor consulta, na ordem em que consulta,
> e o que extrai de cada uma.

---

## Camadas de sourcing (ordem de consulta)

```
1. HISTÓRICO INTERNO (dedup)
   ↓
2. SAZONAL (calendar)
   ↓
3. PROMOS ATIVAS + CASOS DE CLIENTES (alimentado por Pri/Gabriela)
   ↓
4. GROK X (trending real-time — 7 queries paralelas)
   ↓
5. RSS TRAVEL BR (notícias consolidadas)
   ↓
EU (Claude) sintetizo TUDO e gero 5 candidatos
```

---

## 1. Histórico interno

**Arquivo:** `pages/pp-travel/historico.md`

Cada post publicado vira 1 linha:
```
| Data | Pilar | Formato | Headline | Hook source | Engajamento (24h) |
```

**O motor lê os últimos 60 dias antes de gerar candidatos.**

Regras de dedup:
- **Headline idêntica** → bloqueia
- **Mesmo gancho de trending** dentro de 7 dias → bloqueia
- **Mesmo destino** repetido em 5 dias → bloqueia (varia)
- **Mesma estrutura de hook** ("3 erros...", "Por que X em Y") dentro de 14 dias → bloqueia

---

## 2. Sazonal (calendar)

**Arquivo:** `pages/pp-travel/calendar.md` (a criar)

Lista de momentos do ano com sugestões pré-formatadas:

```markdown
## Janeiro
- Volta às férias / planejamento ano (Inspiração)
- Carnaval se aproximando (sazonal)

## Junho/Julho
- Férias escolares (alta temporada Europa) — Inspiração forte
- Festas Juninas (engajamento brasileiro)

## Novembro
- Black Friday viagem (Conversão)
- Planning Réveillon (Inspiração)

## Dezembro
- Réveillon (Inspiração + Conversão)
- Recap do ano (Engajamento)
```

O motor cruza data do dia com calendar e usa como **input adicional** pro Claude.

---

## 3. Promos ativas + Casos de clientes

**Arquivos (alimentados manualmente pela Pri/Gabriela):**
- `pages/pp-travel/promos-ativas.md` — promos vigentes com destino, preço, prazo
- `pages/pp-travel/casos-clientes.md` — depoimentos/cases (com autorização)

**Formato esperado** (promos-ativas.md):
```markdown
## Ativas
- **Miami** ida e volta a partir de R$ 1.998 (42% off) — saindo Rio · janeiro · prazo até 2026-XX-XX
- **Paris** ida e volta R$ 3.490 — saindo SP · março · prazo até 2026-XX-XX
```

**Formato esperado** (casos-clientes.md):
```markdown
## Disponíveis para usar (com autorização)
- **Ana, 34** — Lisboa em junho/2026 — economizou R$ 4.200 vs Latam balcão
- **Marcos + Carla** — Cancún em set/2026 — voo via milhas Smiles + hotel pacote
```

Se vazio: motor não escolhe Prova Social nem Conversão (ou usa caso evergreen "Nossos 1.247 clientes...").

---

## ⛔ Filtros HARD em TODA query (passar no GLOBAL_FILTERS do prompt)

Estes filtros são **não-negociáveis** — todo prompt de query deve incluir explicitamente:

```
EXCLUA TWEETS/FONTES SOBRE:
- POLÍTICA: políticos, presidentes, ministros, governos (mesmo se trazem dado factual
  positivo — pegue a info de fonte neutra como PANROTAS, Ministério institucional, etc.)
- TRAGÉDIAS: mortes, acidentes, falências, demissões
- CONCORRENTES: CVC, Decolar, 123Milhas, MaxMilhas, Vai de Promo (não citar nem comparar)
- POLÊMICAS COM CIAS: relatos negativos de cliente brigando com cia (não dá pra adaptar)
- FUTEBOL EM GERAL: Copa do Mundo OK como contexto de viagem, mas não vou comentar
  desempenho de seleção/jogador.

CROSS-REFERENCE:
- Tópicos em 2+ contas diferentes = [CROSS-VALIDATED] (sinal forte)
```

**Por que política está banida:**
1. Audiência de viagem é cross-spectrum (esquerda + direita + apolíticos viajam)
2. Citar político perde 50% da base de cara
3. Mesmo se for dado neutro (ex: recorde de turismo), pegar de fonte INSTITUCIONAL,
   nunca de pessoa pública governante

---

## 4. Grok X — sourcing DIRECIONADO por pilar do dia

> **Mudança de estratégia (2026-06-01):** rodar 7 queries todo dia gerou ~R$ 1,62/exec = R$ 50/mês.
> Custo absurdo porque 70% do material não virava post (cada execução precisa só do que serve pro pilar do dia).
> **Solução:** 1-2 queries direcionadas por dia. Custo final ~R$ 7/mês.

### Mapa: dia → queries ativas

| Dia BRT | Pilar | Queries ativas | Custo aprox |
|---|---|---|---|
| **Segunda** | Educação | **Q2** (milhas) + **Q7** (news travel BR) | R$ 0,46 |
| **Terça** | Inspiração | **Q4** (destinos viral foto/vídeo) | R$ 0,23 |
| **Quarta** | Engajamento | **Q6** (trending geral - hijack criativo) | R$ 0,23 |
| **Quinta** | Prova Social | **Q3** (achei passagem barata real) + casos-clientes.md | R$ 0,23 |
| **Sexta** | Conversão | **Q1** (cias promos) + promos-ativas.md | R$ 0,23 |
| **Sábado** | Inspiração Reflexiva | **nenhuma query** — evergreen (calendar + frases-âncora de voice.md) | R$ 0,00 |
| **Domingo** | Engajamento | **Q6** (trending geral) | R$ 0,23 |

**Total semanal: ~R$ 1,60 · mensal: ~R$ 7.**

### Override: trending viral forte
Se na auditoria diária aparece tweet do nicho viagem com >10k likes nas últimas 12h,
roda 1 query extra de validação (R$ 0,23) pra capturar ele.

---

## 4b. As 7 queries (definições — mas não rodam todas juntas)

**Modelo:** `x-ai/grok-4-fast` via OpenRouter (com `search_parameters: {mode: "on", sources: [{type: "x"}]}`)

**Por que Grok:** único LLM com acesso real-time à timeline do X (Twitter).
Os outros (Claude, GPT, Gemini) leem internet via search mas X bloqueia bots de search,
então só Grok captura virilidade nas primeiras horas.

### As 7 queries

#### Q1. Companhias aéreas BR
```
Buscar tweets em português dos últimos 24h sobre LATAM, GOL, AZUL, AVIANCA, TAP, IBÉRIA
no contexto brasileiro de passagens, promoções, mudanças de regra ou problemas.
Min 200 engagement. Não retweets. Retornar top 10.
```

#### Q2. Programas de milhas
```
Buscar tweets em pt-BR últimos 48h sobre LATAM PASS, SMILES, TUDOAZUL, LIVELO,
ESFERA, MULTIPLUS. Foco em: vencimento, bug, promoção, alteração de regra,
transferência. Min 100 engagement. Top 10.
```

#### Q3. "Achei passagem barata"
```
Buscar tweets em pt-BR últimos 72h com padrões de "achei passagem", "passagem por R$",
"voo barato", "passagem promo". Min 100 retweets. Top 15.
Especificamente tweets de pessoas reais (não bots de promo).
```

#### Q4. Destinos virais
```
Buscar tweets em pt-BR últimos 7 dias sobre destinos turísticos com sentimento
positivo. Foco em fotos/vídeos de viagem que viralizaram. Min 1000 likes. Top 10.
Procurar destinos mencionados frequentemente.
```

#### Q5. Trending hashtags travel
```
Buscar tweets em pt-BR últimos 24h com hashtags: #turismo, #viagem, #milhas,
#dicasdeviagem. Min 300 likes. Top 15.
```

#### Q6. Trending geral do dia (cross-pollinate)
```
Quais são os 5 assuntos mais comentados no Twitter Brasil hoje (últimas 12h)?
Para cada um, descreva em 1 linha + identifique se tem algum ângulo possível
de adaptação pra contexto de viagem/turismo/PP-Travel.
```

#### Q7. News travel BR
```
Buscar últimas 48h notícias jornalísticas brasileiras sobre setor de viagens,
turismo, companhias aéreas. Fontes preferidas: G1, Valor, Folha, Estadão,
PANROTAS, Mercado e Eventos. Top 5 notícias.
```

**Custo REAL medido (2026-06-01):** ~R$ 1,68 por execução (7 queries × Grok-4.3 + plugin web do OpenRouter, ~28k input tokens por query c/ resultados X). Mês: **~R$ 50**.

**Como chamar (validado):**
```python
payload = {
    "model": "x-ai/grok-4.3",
    "messages": [{"role": "user", "content": QUERY}],
    "plugins": [{"id": "web", "max_results": 10}],
}
```
Os tweets vêm como `message.annotations[].url_citation.url` apontando pra `x.com/i/status/...`.

---

## 5. RSS Travel BR

Fontes consolidadas (não real-time mas curadas):

| Fonte | URL feed | Quando usar |
|---|---|---|
| **Melhores Destinos** | https://www.melhoresdestinos.com.br/feed | Promoções diárias, dicas |
| **Passageiro de Primeira** | https://passageirodeprimeira.com/feed/ | Análises de programas de milhas |
| **PANROTAS** | https://www.panrotas.com.br/rss/news | News do trade |
| **Latitude25** | https://www.latitude25.com.br/feed/ | Roteiros aspiracionais |
| **Viaje na Viagem (Ricardo Freire)** | https://www.viajenaviagem.com/feed/ | Roteiros, opinião |

**Como o motor lê:** baixa os feeds, pega itens das últimas 72h, lista títulos e
resumos. Não baixa página inteira (rate limit).

**Custo:** R$ 0 (feeds RSS são públicos).

---

## Síntese — como eu (Claude) processo tudo

Depois das 5 camadas acima, recebo um digest tipo:

```markdown
=== DIGEST PP-TRAVEL · 2026-06-01 ===

## Dia
- Segunda-feira
- Pilar padrão: Educação (pode desviar se trending forte)

## Sazonal
- Junho = baixa temporada Europa, alta temporada Caribe
- Nenhuma data comemorativa hoje

## Promos ativas
- Miami R$ 1.998 (42% off) — prazo 2026-06-08
- Paris R$ 3.490 — prazo 2026-06-15

## Casos disponíveis
- Ana Lisboa R$ 4.200 economia — não postado ainda

## Grok Q1 (cias)
- Viral: "LATAM aumentou taxa de embarque +R$ 80" — 12k likes
- ...

## Grok Q2 (milhas)
- "Smiles tirou regra de transferência rápida" — 3k likes
- ...

[etc]

## RSS Melhores Destinos
- "Programa Lyne abre janela de transferência 100% bônus" (hoje)
- "Black Friday Latam: tarifas voos internacionais" (ontem)
- ...

## Histórico últimos 14 dias
- 2026-05-31 Inspiração single "Lisboa em outubro..." — não repetir Lisboa
- 2026-05-30 Educação carrossel "Como milhas funcionam" — não repetir
- ...
```

**Daí eu (Claude) gero 5 candidatos** seguindo as regras de `pilares.md` e `formatos.md`,
escolho 1, e gero `content.json` que o motor consome pra renderizar e postar.

---

## Custo total de sourcing por execução

| Fonte | Custo aprox. |
|---|---|
| Histórico interno | R$ 0 |
| Sazonal/promos/casos | R$ 0 |
| Grok 7 queries | R$ 1,68 |
| RSS 5 feeds | R$ 0 |
| **Total / execução** | **R$ 0,30** |
| **Total / mês (30 execuções)** | **R$ 9,00** |

Plus mídia (Gemini Image R$ 0,002 ou Veo Reel R$ 0,80) + posting (Zernio free) = ainda barato.

---

*Versão 1 — 2026-06-01.*
