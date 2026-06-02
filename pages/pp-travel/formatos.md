# Roteiros de formato — PP-Travel Instagram

> **Quando o motor gera 5 candidatos, cada um adere a UM destes formatos.**
> Cada formato tem regras estritas de dimensão, estrutura e linguagem.
> Atualizar este arquivo = atualizar o que o motor pode produzir.

---

## Resumo

| # | Formato | Dimensão | Quando usar | Custo Gemini/Veo |
|---|---|---|---|---|
| 1 | **Single Photo Post** | 1080×1350 (portrait 4:5) | Hook rápido, inspiração, promo direta | ~R$ 0,002 |
| 2 | **Carrossel Educativo** | 1080×1080 × 5-7 slides | FAQ, "como funciona X", deep-dive | ~R$ 0,015 |
| 3 | **Carrossel Storytelling** | 1080×1080 × 3-5 slides | Prova social, case real | ~R$ 0,010 |
| 4 | **Reel Vídeo (informativo/viral)** | 1080×1920 vertical, 7s | Engajamento viral, formato de algoritmo | ~R$ 0,80 |
| 5 | **Story** | 1080×1920, expira 24h | Promo flash, behind the scenes, poll | ~R$ 0,002 |
| 6 | **Reel Reflexivo** ★ | 1080×1920 vertical, 7s | Sábado · pilar Inspiração Reflexiva — frases que viralizam | ~R$ 0,80 |

**Regras gerais (todos os formatos):**
- Português brasileiro **com acentos corretos**
- Tom: "amigo dando dica" — não corporativo, não publicidade
- Sempre handle `@pptravelinfinite` visível
- Headlines misturam pesos (regular + **bold** + *itálico*) pra dar ritmo de leitura
- Hashtags fixas no fim de toda caption: `#PPTravelInfinite #PassagensAéreas #DicasDeViagem #ViajarÉPreciso #DestinoCerto #MilhasComSegurança` + 2-3 específicas do tema

---

## 1️⃣ Single Photo Post

> 1 foto, 1 mensagem. Conteúdo se sustenta sem deslizar.

### Quando usar
- **Pilar Inspiração** (destino do mês)
- **Pilar Conversão** (promo simples)
- **Pilar Engajamento** (pergunta curta, "praia ou montanha?")
- **Trending hook único** que cabe em 1 frase

### Estrutura visual

```
┌──────────────────────────┐
│         PP TRAVEL        │ ← logo serifado no topo center
│                          │
│  [FOTO FULL-BLEED]       │
│                          │
│  ╔═══════════════╗       │
│  ║ KICKER (pilar)║       │ ← pílula com kicker amarelo
│  ╚═══════════════╝       │
│  Headline grande         │ ← Inter 70-90px misturando weights
│  misturando peso         │
│                          │
│  ┌─────────────────┐     │
│  │ sub-pílula      │     │ ← branca, subtítulo
│  └─────────────────┘     │
│                          │
│ @pptravelinfinite        │
└──────────────────────────┘
```

### Prompt Gemini Image (template)

```
Professional travel photography of [LOCAL/CENA].
[LIGHTING: golden hour / blue hour / overcast].
Cinematic atmosphere, shallow depth of field, shot on 35mm full-frame.
Aspect ratio: 4:5 portrait (1080x1350).
Composition: [SUBJECT] on the lower-right third, leaving large negative
space in the upper-left for text overlay.
[OPCIONAL: "include 1-2 background figures from behind for human scale"]
No people facing camera. No text in the image. Editorial magazine quality.
```

### Estrutura da caption

```
[Hook 1 linha — pode ser pergunta retórica]

[2-3 linhas: contexto, dado, número que choca, ou storytelling]

[CTA suave — "Quer saber mais?" / "Vai pra direct" / "Comenta aí"]

[Linha em branco]

#PPTravelInfinite #PassagensAéreas #DicasDeViagem #ViajarÉPreciso #DestinoCerto #MilhasComSegurança #[hashtag-específica-1] #[hashtag-específica-2]
```

**Limite caption:** primeiros 125 caracteres visíveis antes do "...ver mais". Hook DEVE caber aí.

---

## 2️⃣ Carrossel Educativo

> Explica algo complexo em passos. Funciona pra "como X", "3 erros", "guia rápido".

### Quando usar
- **Pilar Educação** (35% do feed) — FAQ, como milhas funcionam, vencimento
- **Trending educativo** ("LATAM mudou regra" → carrossel "o que mudou")

### Estrutura

| Slide | Conteúdo | Foto |
|---|---|---|
| 1 | **Capa**: pergunta/promessa forte ("3 erros que matam suas milhas") | Foto editorial relacionada |
| 2 | Setup: por que esse assunto importa AGORA | Foto contextual |
| 3 | Ponto 1 (com headline + 1 frase explicativa) | Foto/ícone |
| 4 | Ponto 2 | Foto/ícone |
| 5 | Ponto 3 | Foto/ícone |
| 6 | Síntese: "Por isso quem usa a PP nem precisa pensar nisso" | Foto positiva |
| 7 | **CTA**: "Salva esse post + DM pra cotar" | Foto + emoji 📌 |

### Variação curta (5 slides)
Quando o tema é mais simples: pula slide 2 (setup) e slide 6 (síntese).

### Prompt Gemini (varia por slide)

**Slide 1 (capa):**
```
[mesma do single, mas com PROMPT específico que evoca a pergunta]
```

**Slides intermediários:**
- Ou foto coerente narrativamente (mesma sessão fotográfica)
- Ou ícones grandes + cor (deixa Claude decidir)

### Captions
1 caption geral (não por slide). Primeiros 125 chars = título do carrossel + emoji 👇

---

## 3️⃣ Carrossel Storytelling

> Conta a história de UM cliente, UM destino, UMA viagem. Emoção > educação.

### Quando usar
- **Pilar Prova Social** (15%) — "Ana economizou R$ 4.2k pra Lisboa"
- **Pilar Inspiração aspiracional** — "10 dias em Bali, com milhas"

### Estrutura (3-5 slides)

| Slide | Conteúdo |
|---|---|
| 1 | **Hook**: número que choca + nome ("Economizei R$ 4.200 — Ana, 34") |
| 2 | Contexto: cenário antes, o que ela queria, qual foi a frustração |
| 3 | Virada: o que a PP fez de diferente |
| 4 | Resultado: foto/print/depoimento |
| 5 | CTA: "Quer ser a próxima? Manda 'CONSULTORIA' no direct" |

### Fotos
- **Slide 1**: foto da pessoa por trás (anonimato) num aeroporto / chegando em hotel / com mala
- **Slides 2-3**: foto do destino que ela foi
- **Slide 4**: foto positiva (pessoa de costas vendo o destino, gente em restaurante)
- **Slide 5**: foto de aspiração + CTA visual

**Importante:** Nunca mostrar rosto reconhecível sem autorização. Usar 3/4 de costas ou silhueta contra a paisagem.

---

## 4️⃣ Reel Vídeo (7s)

> Vídeo curto vertical, gerado via Google Veo 3.1 Fast. Pra captura de algoritmo.

### Quando usar
- **Pilar Engajamento** (15%) — viral pattern (POV, transição, "you have to see this")
- **Pilar Inspiração** — destino com mvto (ondas, voo de drone, time-lapse)
- **Trending viral hijack** — formato do momento

### Estrutura temporal (7s)

| Tempo | Conteúdo |
|---|---|
| 0-1s | **HOOK visual**: imagem inesperada / movimento dramático / texto curto chamativo |
| 1-5s | Desenvolvimento (cena principal) |
| 5-7s | **CTA visual**: logo PP TRAVEL + handle + "save this" / "salva esse" |

### Estrutura visual (1080×1920)

```
┌────────────────────┐
│                    │
│   [VÍDEO Veo 7s]   │ ← Vídeo full-bleed
│                    │
│ Texto overlay      │ ← Texto sobreposto via Playwright (ou MoviePy)
│ que aparece e some │
│                    │
│      [LOGO]        │
└────────────────────┘
```

### Prompt Veo 3.1 Fast (template)

```
A 7-second cinematic vertical (9:16) video.
[SCENE: descrição clara da cena]
[CAMERA: slow dolly forward / pan right / aerial drone]
[LIGHTING: golden hour / blue hour]
[MOOD: aspirational, calm, premium / fast-paced, dynamic, exciting]
No on-screen text. No people facing camera directly.
1080x1920 aspect ratio, 30fps.
```

**Exemplo:**
```
A 7-second cinematic vertical 9:16 video. Slow aerial drone shot
descending toward Christ the Redeemer at sunset, golden hour light
bathing the statue and Sugarloaf Mountain in the background.
Mood: aspirational, calm, premium. Camera glides smoothly, no jumps.
No on-screen text, no people. 1080x1920, 30fps.
```

### Caption do Reel
**Curtíssima** (Reels têm caption truncada brutalmente):
```
[Hook 1 linha — máx 60 chars]
[1 linha extra opcional]

#PPTravelInfinite #Reels #[hashtag-específica]
```

### Texto overlay (Playwright)
- 0-1s: hook em texto branco grande no centro
- 1-5s: sem texto (vídeo fala)
- 5-7s: handle `@pptravelinfinite` no canto inferior

---

## 5️⃣ Story (24h)

> Sem feed permanente. Pra promo flash, behind, engajamento ágil.

### Quando usar
- **Promo de janela curta** ("só hoje", "últimas 3 vagas")
- **Behind the scenes** ("a Pri tá fechando uma promo agora")
- **Engajamento rápido** ("vai pra praia ou montanha?" com poll sticker)

### Estrutura (1080×1920)

```
┌────────────────────┐
│                    │
│   [FOTO ou VÍDEO]  │
│                    │
│  Texto grande      │
│  centralizado      │
│                    │
│  [STICKER POLL/    │
│   QUIZ se aplic]   │
│                    │
│   @pptravelinfinite│
└────────────────────┘
```

**Limitações Zernio/Meta:**
- Link sticker NÃO funciona via API (limitação Meta)
- Sticker de poll/quiz NÃO via API
- Só texto + foto/vídeo
- Por isso Story via motor é simples: promo + texto

### Prompt Gemini Story

```
Same as Single Photo but aspect ratio 9:16 (1080x1920) portrait.
Composition: large negative space in the center for big text overlay.
```

---

## 6️⃣ Reel Reflexivo ★

> Vídeo aspiracional curto com frase contemplativa. Tipo "viaje agora, a vida é curta".
> Funciona quando posicionado com sutileza — vira viral no algoritmo.

### Quando usar
- **Sábado** (dia padrão · pilar Inspiração Reflexiva)
- Quando NÃO tem trending forte e não cabe um post informativo
- Como "respiro" no feed entre conteúdos transacionais

### Estrutura temporal (7s)

| Tempo | Conteúdo |
|---|---|
| 0-1s | Cena ampla, atmosférica (vista de pico, janela de avião, mar) |
| 1-5s | Cena continuada com leve movimento (slow dolly, pan) + **frase aparece sobreposta** em fade-in |
| 5-7s | Frase completa + handle `@pptravelinfinite` discreto no canto |

### Estrutura visual (1080×1920)

```
┌────────────────────┐
│                    │
│   [VÍDEO VEO 7s]   │  ← Cena aspiracional sem cortes bruscos
│                    │
│                    │
│  Frase reflexiva   │  ← Texto sobreposto (fade-in, branco, serifado)
│  centralizada      │
│                    │
│                    │
│   @pptravelinfinite│
└────────────────────┘
```

### Prompt Veo 3.1 Fast (templates)

**Tipo A — Janela de avião / vista aérea:**
```
A 7-second cinematic vertical 9:16 video. View from an airplane window looking out
over clouds at golden hour, with the wing visible at the bottom-left frame.
Camera: subtle gentle pan, no jumps. Lighting: warm sunset, dreamlike.
Mood: contemplative, aspirational, calm. No on-screen text. No people visible.
1080x1920, 30fps.
```

**Tipo B — Pessoa de costas em paisagem:**
```
A 7-second cinematic vertical 9:16 video. Wide shot of a person seen from behind,
standing on a cliff or beach looking at a vast horizon — sea, mountains, or sunset
landscape. Person is silhouetted, not recognizable. Camera: slow push-in.
Mood: introspective, aspirational, "life is meant to be experienced".
Warm golden hour lighting. No on-screen text, no faces visible. 1080x1920, 30fps.
```

**Tipo C — Idoso contemplando:**
```
A 7-second cinematic vertical 9:16 video. Older person (60-70s) sitting on a bench
overlooking a beautiful landscape — Mediterranean coast, mountains, sunset over water.
Seen from behind or 3/4, face not recognizable. They look peaceful, reflective.
Camera: subtle slow zoom out revealing more of the landscape.
Mood: wisdom, calm, "experiences over things". No text. 1080x1920, 30fps.
```

### Frases reflexivas aprovadas (rotacionam — ver `voice.md`)

Exemplos do banco (cada Reel usa 1):
- "Coisas não te seguem na lembrança. Lugares sim."
- "Quando você tiver 70, o que vai te lembrar você foi feliz?"
- "A gente acumula objeto. Devia acumular janela de avião."
- "Tem viagem que muda o que você lê, o que você come, e quem você é."
- "O melhor presente é uma data marcada no calendário."

### Caption do Reel Reflexivo
Curta. Repete ou complementa a frase do vídeo:

```
A vida não cabe em uma agenda corrida.

Bora?

#PPTravelInfinite #ViajarÉPreciso #ExperienciasQueValem
```

### Anti-patterns específicos
❌ Frase clichê esvaziada ("Sonhe alto", "Acredite", "Os limites são apenas mentais")
❌ Música emotiva muito carregada (Veo às vezes injeta — pedir audio neutro)
❌ Texto AI dentro do vídeo (Veo erra)
❌ Mostrar rosto reconhecível (LGPD + perde universalidade)

---

## Anti-patterns (não fazer)

❌ **Foto com texto AI dentro** — Gemini erra texto, sempre overlay externo via HTML
❌ **Caption começando com "Olha que legal..."** — soa publicidade
❌ **Mais de 30 hashtags** — IG limita 30
❌ **Reel acima de 7s no Veo Fast** — sai borrado/repetitivo
❌ **Mostrar rostos reconhecíveis** sem autorização (LGPD)
❌ **Promo sem cidade origem específica** ("Miami R$ 1.998" sem dizer "saindo do Rio")
❌ **Misturar tom: trecho formal + trecho coloquial no mesmo post**

---

## Como o motor escolhe formato

A cada execução, **eu (Claude) decido** baseado em:

1. **Pilar do dia** (rotação semanal — ver `pilares.md`)
2. **Trending capturado**: viral em vídeo → Reel; viral em texto/data → Carrossel; foto inspiracional → Single
3. **Recente histórico**: se últimos 3 posts foram carrosséis, esse precisa ser Reel ou Single
4. **Custo**: Reel custa 400x mais que foto — só uso quando o ganho de engajamento justifica
5. **Diversidade na semana**: meta = 50% single, 30% carrossel, 15% Reel, 5% story (calibrar)

---

*Versão 1 — 2026-06-01. Atualizar quando aprendermos o que funciona/não funciona no algoritmo.*
