# Fontes do News Curator

> **Fonte única de verdade das URLs varridas pelos subagentes.**
> Pra adicionar/remover uma fonte: edita a tabela correspondente abaixo. Os subagentes leem esse arquivo no início de cada execução.

---

## github-releases

Releases de repositórios estratégicos via feed `.atom` nativo do GitHub.

| Repo | URL do feed | Por quê monitorar |
|---|---|---|
| anthropics/claude-code | https://github.com/anthropics/claude-code/releases.atom | Ferramenta principal da mentoria |
| openai/codex | https://github.com/openai/codex/releases.atom | Concorrente direto do Claude Code |
| google-gemini/gemini-cli | https://github.com/google-gemini/gemini-cli/releases.atom | CLI do Google, segunda opção popular |
| Aider-AI/aider | https://github.com/Aider-AI/aider/releases.atom | Alternativa madura de pair programming |
| continuedev/continue | https://github.com/continuedev/continue/releases.atom | Extensão VS Code/JetBrains com tração |
| elevenlabs/elevenlabs-python | https://github.com/elevenlabs/elevenlabs-python/releases.atom | SDK de voz — relevante pra agentes |
| ggerganov/llama.cpp | https://github.com/ggerganov/llama.cpp/releases.atom | Sinal de movimento local-first |
| vllm-project/vllm | https://github.com/vllm-project/vllm/releases.atom | Inferência rápida — sinal de mercado |
| openai/openai-python | https://github.com/openai/openai-python/releases.atom | SDK do OpenAI, sinal de novos endpoints |

---

## labs-blogs

Blogs oficiais dos principais laboratórios de IA.

| Lab | Tipo | URL |
|---|---|---|
| Anthropic | HTML | https://www.anthropic.com/news |
| OpenAI | RSS | https://openai.com/news/rss.xml |
| Google DeepMind | RSS | https://deepmind.google/blog/rss.xml |
| Mistral AI | HTML | https://mistral.ai/news |
| xAI | HTML | https://x.ai/news |
| Perplexity | HTML | https://www.perplexity.ai/hub/blog |
| Cohere | HTML | https://cohere.com/blog |
| Meta AI | HTML | https://ai.meta.com/blog/ |

---

## tech-press

Imprensa especializada — cobertura jornalística com análise.

| Veículo | URL (RSS) |
|---|---|
| TechCrunch AI | https://techcrunch.com/category/artificial-intelligence/feed/ |
| The Verge AI | https://www.theverge.com/ai-artificial-intelligence/rss/index.xml |
| Ars Technica AI | https://arstechnica.com/ai/feed/ |
| MIT Tech Review (AI) | https://www.technologyreview.com/topic/artificial-intelligence/feed |
| VentureBeat AI | https://venturebeat.com/category/ai/feed/ |

---

## hn-communities

Hacker News + comunidades dev. Aqui o ICP é gestor, então o subagente deve **filtrar agressivamente** o que é puro técnico.

| Fonte | URL |
|---|---|
| HN frontpage (≥150 pts) | https://hnrss.org/frontpage?points=150 |
| HN newest "AI" (≥50 pts) | https://hnrss.org/newest?q=AI&points=50 |
| HN newest "Claude" | https://hnrss.org/newest?q=Claude |
| HN newest "LLM" (≥50 pts) | https://hnrss.org/newest?q=LLM&points=50 |
| r/LocalLLaMA top semanal | https://www.reddit.com/r/LocalLLaMA/top.rss?t=week |

---

## Como adicionar uma fonte nova

1. Identifique a categoria certa (releases? lab oficial? imprensa? comunidade?)
2. Encontre a URL do feed/HTML
3. Adicione 1 linha na tabela correspondente acima
4. Salve e commite

Sem mudar nenhum subagente — eles leem essa tabela em runtime.

## Como remover uma fonte

Apague a linha da tabela. Pronto.

## Como mover uma fonte de categoria

Move a linha entre tabelas. Sem mudança de código.
