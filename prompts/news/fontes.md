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

Blogs oficiais dos principais laboratórios de IA e fornecedores estratégicos (Microsoft, NVIDIA).

| Lab | Tipo | URL |
|---|---|---|
| Anthropic | HTML | https://www.anthropic.com/news |
| OpenAI | RSS | https://openai.com/news/rss.xml |
| Google DeepMind | RSS | https://deepmind.google/blog/rss.xml |
| Mistral AI | HTML | https://mistral.ai/news |
| Cohere | HTML | https://cohere.com/blog |
| Meta AI | HTML | https://ai.meta.com/blog/ |
| Microsoft Copilot | RSS | https://www.microsoft.com/en-us/microsoft-copilot/blog/feed/ |
| NVIDIA | RSS | https://blogs.nvidia.com/feed/ |

> **Removidas em 16/05/2026:** xAI (`x.ai/news`) e Perplexity (`perplexity.ai/hub/blog`) — bloqueavam todos os WebFetch com HTTP 403. Sem feed alternativo viável.

---

## tech-press

Imprensa especializada e analistas de mercado — cobertura jornalística + análise estratégica.

| Veículo | Tipo | URL |
|---|---|---|
| TechCrunch AI | RSS | https://techcrunch.com/category/artificial-intelligence/feed/ |
| MIT Tech Review (AI) | RSS | https://www.technologyreview.com/topic/artificial-intelligence/feed |
| VentureBeat AI | RSS | https://venturebeat.com/category/ai/feed/ |
| The Register AI | RSS | https://www.theregister.com/headlines.atom |
| Stratechery (Ben Thompson) | RSS | https://stratechery.com/feed/ |
| Latent Space (swyx) | RSS | https://www.latent.space/feed |
| Ben's Bites | RSS | https://bensbites.com/rss |
| The Decoder | RSS | https://the-decoder.com/feed/ |
| Reuters Technology | RSS | https://feeds.reuters.com/reuters/technologyNews |
| Axios AI | HTML | https://www.axios.com/technology/artificial-intelligence |
| Import AI (Jack Clark) | RSS | https://importai.substack.com/feed |

> **Removidas em 16/05/2026:** The Verge AI e Ars Technica AI — bloqueavam WebFetch com HTTP 403 (proteção anti-bot). The Register cobre tema similar e foi adicionado.
> **Adicionadas em 24/05/2026:** The Decoder, Reuters Technology, Axios AI, Import AI — para cobrir histórias que escapam das fontes existentes, especialmente fins de semana.

---

## hn-communities

Hacker News + comunidades dev. Aqui o ICP é gestor, então o subagente deve **filtrar agressivamente** o que é puro técnico.

| Fonte | URL |
|---|---|
| HN frontpage (≥150 pts) | https://hnrss.org/frontpage?points=150 |
| HN newest "AI" (≥50 pts) | https://hnrss.org/newest?q=AI&points=50 |
| HN newest "Claude" | https://hnrss.org/newest?q=Claude |
| HN newest "LLM" (≥50 pts) | https://hnrss.org/newest?q=LLM&points=50 |
| r/LocalLLaMA top semanal | https://old.reddit.com/r/LocalLLaMA/top.rss?t=week |
| r/ChatGPT top semanal | https://old.reddit.com/r/ChatGPT/top.rss?t=week |

> **Tentativa em 16/05/2026:** Reddit `www.reddit.com` foi bloqueado com 403. Trocado por `old.reddit.com` que costuma aceitar mais clientes. Se continuar 403, próxima tentativa é a API JSON pública do Reddit (`/.json`).

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
