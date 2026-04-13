# Fontes de Negócio — Ponte pro `01-negocio/`

> **Este arquivo é uma ponte, não uma cópia.** Ele lista os documentos funcionais e estratégicos que vivem na pasta irmã `01-negocio/` — a documentação real da empresa. Todos os agentes e desenvolvedores deste projeto tech precisam ler esses documentos antes de produzir qualquer coisa.
>
> **Regra:** estes arquivos são **somente-leitura** pra este repo. Nunca editar a partir daqui. Se precisar atualizar, atualize direto no `01-negocio/`.

---

## Por que existe essa separação

O projeto de negócio (`01-negocio/`) e o projeto tech (`02-maquina-agentes/`) são **dois projetos distintos** que vivem lado a lado:

- **`01-negocio/`** — projeto de **gestão**, aplica o `estrutura-template` do Pedro. É onde a empresa é documentada, pensada e gerida.
- **`02-maquina-agentes/`** — projeto de **código**, usa layout Python padrão. É onde os agentes são desenvolvidos.

Este arquivo serve pra quem tá no projeto tech saber onde encontrar os **fundamentos funcionais** sem precisar explorar a outra pasta.

---

## Documentos canônicos do negócio

### 🎯 Marca e posicionamento

**[`../../../01-negocio/01-arquivos-projeto/01-marca-posicionamento/00-posicionamento.md`](../../../01-negocio/01-arquivos-projeto/01-marca-posicionamento/00-posicionamento.md)**

Fonte única de marca, identidade, ICP, tom, metodologia, objeções, linguagem. **Leitura obrigatória** pra qualquer agente antes de gerar conteúdo.

Conteúdo resumido:
- Sentença-canônica da marca
- Headline principal
- Manifesto e pitch elevator
- Ângulo dominante ("A IA como funcionária") + analogia central
- 4 pilares da metodologia
- ICP + 19 perfis típicos com dor específica
- "O que o cliente deve sentir"
- Dores em ordem de força
- Transformação (antes → depois)
- Exemplos concretos ("me prepara pra reunião")
- Diferenciadores
- Objeções típicas
- Territórios de linguagem (o que usar, o que evitar)
- Tom de voz
- Regras não-negociáveis

### 💰 Escada de valor (produtos e funil)

**[`../../../01-negocio/01-arquivos-projeto/02-ofertas/00-escada-de-valor.md`](../../../01-negocio/01-arquivos-projeto/02-ofertas/00-escada-de-valor.md)**

Roadmap completo dos produtos: lead magnets → turma → 1:1 → corporativo → curso gravado. Preços, triggers de ativação, funil, métricas, regras de negócio, decisões tomadas.

**Leitura obrigatória** pro Agente 3 (Captação) e Agente 1 (Estratégia).

### 📚 Programa da mentoria (produto ativo)

**[`../../../01-negocio/01-arquivos-projeto/02-ofertas/mentoria-1-1/00-programa.md`](../../../01-negocio/01-arquivos-projeto/02-ofertas/mentoria-1-1/00-programa.md)**

Descrição operacional do único produto ativo hoje: formato das 3 sessões, entregáveis, cronograma, pré-requisitos, métricas de sucesso.

### 💵 Precificação (deep-dive operacional)

**[`../../../01-negocio/01-arquivos-projeto/02-ofertas/mentoria-1-1/04-precificacao.md`](../../../01-negocio/01-arquivos-projeto/02-ofertas/mentoria-1-1/04-precificacao.md)**

ROI por perfil de cliente, cálculo de capacidade mensal, argumento de venda, estratégia de escalada de preço.

### ✍️ Copys prontas

**[`../../../01-negocio/01-arquivos-projeto/02-ofertas/mentoria-1-1/landing/copys.md`](../../../01-negocio/01-arquivos-projeto/02-ofertas/mentoria-1-1/landing/copys.md)**

Textos prontos pra uso imediato: pitch elevator, WhatsApp (direto + provocativo), LinkedIn post, email, frases pra stories/reels, respostas a objeções, bio do instrutor.

Use como **referência de tom** — mostra como o Pedro escreve na prática.

### 🌐 Landing publicada (HTML)

**[`../../../01-negocio/01-arquivos-projeto/02-ofertas/mentoria-1-1/landing/site/index.html`](../../../01-negocio/01-arquivos-projeto/02-ofertas/mentoria-1-1/landing/site/index.html)**

Versão publicada em [mentoria-pedro-giorgis.netlify.app](https://mentoria-pedro-giorgis.netlify.app/). Use como referência de copy final, hierarquia de argumentos e CTAs.

⚠️ **Não confundir** com `landing/landing-page.html` — esse é versão antiga/draft.

### 📦 Estrutura template (entregável da mentoria — INTOCADO)

**[`../../../01-negocio/01-arquivos-projeto/02-ofertas/mentoria-1-1/entregaveis/estrutura-template/`](../../../01-negocio/01-arquivos-projeto/02-ofertas/mentoria-1-1/entregaveis/estrutura-template/)**

Este é o **entregável principal da mentoria** — o template de projeto que o aluno recebe. **NÃO editar, nem consultar como fonte de verdade operacional.** Ele existe como entregável, nada mais.

O `01-negocio/` em si é uma **aplicação** desse template em um projeto real — esse sim serve como referência viva.

---

## Como os agentes consomem essas fontes

Em runtime, `src/shared/drive_reader.py` carrega os arquivos canônicos e injeta como system prompt via prompt caching. Isso reduz custo em ~90% a partir da 2ª chamada de cada agente.

Ordem de prioridade na hora de gerar conteúdo:
1. Posicionamento (sempre)
2. Escada de valor (sempre)
3. Programa da mentoria (quando referenciar o produto)
4. Copys (como referência de tom)

Os arquivos de precificação e landing HTML são usados sob demanda (quando o contexto exige).

---

## Quando atualizar essas fontes

**Nunca a partir daqui.** Sempre editar direto no `01-negocio/`. Motivos:

1. A Pedro que gere o negócio — é o humano no loop.
2. Código autônomo editando doc de marca é anti-padrão (loop de reforço viciado).
3. Se uma atualização é necessária por conta de dados da máquina (ex.: Agente 5 detecta que um ângulo funciona melhor), o Agente 5 propõe via Telegram e o Pedro decide se atualiza.

---

*Última atualização: 2026-04-13. Este arquivo é uma ponte — se a estrutura do `01-negocio/` mudar, atualizar os caminhos daqui.*
