# Visão Geral do Projeto Tech

> Para entender **o que este projeto é em 2 páginas**. Ideal pra alguém que abre o repo pela primeira vez (ou pra o próprio Pedro depois de 3 meses).

---

## Propósito

Construir uma **operação automatizada por agentes de IA** que:
1. Cria conteúdo orgânico diário pro Instagram (e depois LinkedIn)
2. Captura leads via 3 lead magnets paralelos
3. Nutre os leads com email sequences até convidar pra turma
4. Mede resultados e realimenta a estratégia

**O objetivo:** Pedro só precisa dar a mentoria. A máquina cuida do resto — com gates de aprovação humana em pontos críticos.

## O que é (e o que não é)

**É:**
- Um conjunto de 5 agentes especializados orquestrados por um supervisor
- Rodando em cima de Claude (texto) + Gemini (imagens) + Meta Graph API (publicação)
- Com SQLite como fonte de verdade do Kanban de tarefas
- Operado inicialmente via Claude Code (Fase 1 Light), migrando pra scripts agendados (Fase 2)

**Não é:**
- Um produto SaaS pra vender
- Um sistema pra múltiplos usuários
- Código que precisa de alta disponibilidade
- Código que roda em infra cloud (ainda — Fase 1 é 100% local)

## Diagrama mental

```
┌────────────────────────────────────────────────┐
│ FONTES DE VERDADE (Drive, ../01-negocio/)      │
│                                                │
│ • Marca, ICP, tom de voz                       │
│ • Escada de valor (produtos, preços)           │
│ • Programa da mentoria                         │
└────────────────────────────────────────────────┘
                    ↓ (somente-leitura)
┌────────────────────────────────────────────────┐
│ SUPERVISOR                                     │
│ orquestra os agentes                           │
└────────────────────────────────────────────────┘
     ↓        ↓         ↓         ↓         ↓
  Ag 1     Ag 2      Ag 3      Ag 4      Ag 5
  Pauta  Produção  Captação  Publicar Analytics
     ↓        ↓         ↓         ↓         ↓
┌────────────────────────────────────────────────┐
│ SQLITE (agents.db)                             │
│ cards, events, leads                           │
└────────────────────────────────────────────────┘
     ↓                      ↓
Telegram bot         Instagram Graph API
(gates humanos)      (publicação real)
```

## Fase atual

**Fase 1 Light — operação via Claude Code no PC.** Nenhum agente roda sozinho ainda. Tudo é disparado via chat ou CLI enquanto a arquitetura é validada.

Para entendimento completo, ver [../tecnica/00-arquitetura.md](../tecnica/00-arquitetura.md) (seção §11 — Roadmap de fases).

## Quem opera

**Pedro Giorgis** — dono da empresa, único operador. Não é programador profissional, é Product/Delivery Manager. Decisões de código são delegadas pro Claude Code, mas **ele aprova tudo** (arquitetura, prompts, publicações).

## Métricas de sucesso

Copiadas da arquitetura (§5):

- **Fase 1A:** 1 post manual publicado de verdade no `@ia.executa`
- **Fase 1B:** Agente 2 produzindo posts com 90% de aprovação do Pedro
- **Fase 1C:** Agente 1 gerando pauta semanal aceita sem grandes ajustes
- **Fase 1D:** 3 funis de captação rodando, 1º lead real entrando
- **Fase 1E:** Máquina fechada — relatório semanal alimenta pauta automaticamente

Longo prazo: 2 turmas/mês preenchidas com leads originados pela máquina.
