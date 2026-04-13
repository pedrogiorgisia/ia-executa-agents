# Fase Atual: Fase 1 Light — arranque

> Atualize este arquivo cada vez que avançar ou mudar de fase.
> Ele é o "onde estamos agora" — se alguém abre o repo, lê isso antes.

---

## Estamos em: **Fase 0 → Fase 1A**

**Fase 0 — Fundação do repo** ✅ concluída em 2026-04-13
- [x] Estrutura de pastas criada
- [x] CLAUDE.md do repo tech escrito
- [x] .gitignore, .env.example, requirements.txt prontos
- [x] Repo git inicializado e enviado pro GitHub

**Fase 1A — 1 post manual fim-a-fim** 🔜 próxima
- [ ] Pedro cria conta `@ia.executa` no Instagram + converte pra Business
- [ ] Pedro cria Página do Facebook conectada
- [ ] Submeter App Review da Meta pra permissão de publicação (2-7 dias)
- [ ] Pedro cria conta no Google AI Studio + gera API key do Gemini
- [ ] Pedro cria conta no Anthropic (ou usa Claude Pro local)
- [ ] Escrever `shared/db.py` — schema + init
- [ ] Escrever `shared/drive_reader.py` — lê fontes de verdade do `../01-negocio/`
- [ ] Escrever `shared/claude_client.py` — com prompt caching
- [ ] Escrever `shared/gemini_client.py` — gera imagens
- [ ] Escrever `shared/instagram_client.py` — publica via Graph API
- [ ] Escrever `cli.py` mínimo
- [ ] Criar 1 card manual no SQLite
- [ ] Rodar pipeline fim-a-fim: card → imagens → post publicado
- [ ] **Critério de sucesso:** 1 post real no feed do `@ia.executa`

## O que VEM depois

Ver [../tecnica/00-arquitetura.md §11](../tecnica/00-arquitetura.md) — Roadmap completo de Fase 1A até Fase 1E + Fase 2.

## Bloqueios atuais

- **App Review da Meta** — não inicia sem ele (ou paga Late). Iniciar em paralelo no dia 1 de desenvolvimento.

## Decisões pendentes pro Pedro

- [ ] Criar conta `@ia.executa` no Instagram e me passar confirmação
- [ ] Definir se prefere Claude API paga (~R$20/mês) OU rodar no PC 24/7 com Claude Pro — já decidido em 2026-04-13: **rodar no PC** na Fase 1, migrar depois se necessário
