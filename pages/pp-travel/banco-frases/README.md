# Banco de Frases Reflexivas — PP-Travel

> Sistema dedicado a **frases prontas pra Reels Reflexivos** (sábados) e referências
> emocionais usadas em captions de outros pilares.
>
> Mesma lógica do `ideias/`: **disponíveis → (motor pega) → usadas**.
>
> Diferente do `ideias/` que tem TEMAS de post, aqui são **frases curadas** com fonte
> rastreável. Vital pra evitar inventar metáfora quebrada (lição aprendida com
> "Acumular janela de avião" rejeitada em 2026-06-01).

---

## Os 2 arquivos

| Arquivo | Conteúdo |
|---|---|
| [`reflexivas-disponiveis.md`](reflexivas-disponiveis.md) | Frases prontas pra usar, com fonte (autor, link X se viral, contexto). Alimentado por: (a) pesquisa web/Grok do copy-specialist, (b) Pedro manualmente. |
| [`reflexivas-usadas.md`](reflexivas-usadas.md) | Histórico de frases já viraram Reel/caption. Dedup permanente — motor não usa mesma frase 2x. |

---

## Regra de ouro

**Nunca invente metáfora reflexiva do zero.** Sempre:

1. Pesquisar no banco
2. Se vazio ou tudo já usado → fazer web search + Grok pra frases novas
3. Adicionar novas ao banco com FONTE
4. Pegar 1, aplicar pro post, MOVER pra usadas.md

Se quiser combinar 2 frases (mash-up), declare no `_review` do `content.json` quais foram
as fontes — pra auditoria.

---

## Fontes pesquisadas (rotacionar quando o banco esvaziar)

### Sites de quote curado pt-BR
- Carpe Mundi (https://www.carpemundi.com.br/melhores-frases-de-viagem/)
- Ligado em Viagem (frases viagem)
- Pinterest Brasil (carpe_mundi/frases-de-viagem)
- Goodreads (travel quotes section em pt e en)

### Autores brasileiros confiáveis pra mineração
- Mario Quintana
- Amyr Klink
- Martha Medeiros
- Manoel de Barros
- Cecília Meireles
- Adélia Prado

### Autores estrangeiros traduzidos
- Mark Twain
- Henry Miller
- Susan Sontag
- Anaïs Nin
- Pico Iyer
- Bill Bryson

### X/Twitter via Grok
- Query: "tweets pt-BR últimos 6 meses sobre viagem, min_likes:2000, aforismo/paradoxo"
- Roda 1x por mês pra capturar virais frescos

### Reddit
- r/TravelBR
- r/wanderlust
- r/travel (em inglês — traduzir cuidadosamente)

---

## Critérios de qualidade

Antes de uma frase entrar em `disponiveis.md`, ela precisa passar em:

1. **Teste de leitura em voz alta** — flui sem travar?
2. **Teste do "caraca, é verdade"** — gera reconhecimento imediato?
3. **Teste da metáfora intacta** — funciona literal OU figurativo (não pode quebrar nos 2)?
4. **Concordância pt-BR perfeita** — sem "ainda dá" suspenso, sem genérico
5. **< 25 palavras** — cabe num overlay de Reel
6. **Sem clichê esvaziado** — "sonhe alto", "acredite", "os limites apenas mentais" estão fora
7. **Sem HARD BANS** (política, religião, tragédia, concorrentes)

Se uma frase falha em qualquer item, **não entra**. Melhor banco pequeno e bom do que grande e medíocre.
