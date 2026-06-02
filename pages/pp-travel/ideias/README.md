# Banco de ideias — PP-Travel Instagram

> Sistema de gestão de ideias do motor. Cada ideia tem um ciclo de vida:
>
> **`disponiveis.md` → (motor pega) → `usadas.md`** (dedup permanente)
>
> `templates-engajamento.md` é diferente: são **fórmulas reusáveis** que o motor pode
> aplicar várias vezes com conteúdo diferente, não consomem.

---

## Os 3 arquivos

| Arquivo | O que é | Como o motor usa |
|---|---|---|
| [`templates-engajamento.md`](templates-engajamento.md) | **Fórmulas virais permanentes** (microdecisão, batalha, quiz, polêmica, reações). Cada fórmula vira N posts diferentes. | Pra pilar **Engajamento**, motor escolhe 1 fórmula + preenche com tema do trending do dia. Não consome — fórmula fica disponível sempre. |
| [`disponiveis.md`](disponiveis.md) | **Ideias específicas prontas pra postar**. Ex: "Destino destaque junho: Lençóis". Alimentado por: (a) sourcing Grok do dia, (b) Pedro manualmente, (c) ideias residuais de outros dias. | Motor pega 1 ideia adequada ao pilar → gera post → **MOVE pra usadas.md**. Ideia desaparece daqui. |
| [`usadas.md`](usadas.md) | **Histórico de ideias consumidas**. Garante dedup permanente. | Motor consulta antes de pegar de `disponiveis.md` — se ideia similar já foi usada nos últimos 60 dias, pula. |

## Como o motor preenche `disponiveis.md`

Após cada execução do `run_pp_sourcing.py`, antes de finalizar o post, o motor:

1. Lê o digest da query do dia
2. Identifica **ideias bônus** que apareceram no digest mas não foram escolhidas pra hoje
3. Adiciona como linha em `disponiveis.md` com tag de pilar adequado

Exemplo: hoje o Q4 trouxe "Itália gastronomia viral 750 likes" mas escolhi Lençóis. A "Itália gastronomia" vira:

```
- [inspiracao] Tema: Itália gastronomia. Fonte: Q4 2026-06-01 @chefdangalhardo. Hook potencial: "Tem viagem que muda o que você come."
```

## Quem mais alimenta `disponiveis.md`?

- **Pedro manualmente**: a qualquer momento adiciona ideia que vier na cabeça
- **Pri/Gabriela**: ideias do dia-a-dia do atendimento
- **Auditoria mensal**: motor identifica gaps de pilares e propõe ideias

## Quem alimenta `templates-engajamento.md`?

- **Pedro/Claude** quando descobrir nova fórmula viral
- Atualizado raramente — é fonte estável

## Quem alimenta `usadas.md`?

- **Só o motor automaticamente**. Cada vez que consome uma ideia.
