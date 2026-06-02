# Assets — Templates estáticos

Templates HTML usados pelos scripts em runtime.

| Arquivo | Usado por | Saída |
|---|---|---|
| [`template-v2-single-photo.html`](template-v2-single-photo.html) | `scripts/post.py` (function `render_single_photo`) | PNG 1080×1080 single photo (Inspiração, Engajamento, Conversão) |
| [`template-carousel-slide.html`](template-carousel-slide.html) | `scripts/render_carousel.py` (function `render_slides`) | PNG 1080×1080 por slide (Educação, Prova Social) |

## Como o script consome

```python
ROOT = Path(__file__).parent.parent  # project root
tpl_path = ROOT / ".claude/skills/instagram-motor/assets/template-v2-single-photo.html"
html_tpl = tpl_path.read_text(encoding="utf-8")
html = html_tpl.replace("__MIME__", mime).replace("__B64__", b64).replace(...)
```

## Quando alterar

- Mudou paleta de marca → edita os 2 arquivos (cores em `#c9a961`, `#0a1a52`, `#fcd34d`)
- Mudou tipografia → atualiza o `@import` do Google Fonts
- Mudou estrutura visual (V3 algum dia) → cria `template-v3-*.html` SEM apagar V2
  (assim conseguimos reverter)

## Validação

Antes de mudar qualquer template, rode um `post.py --dry-run` com data de teste
pra confirmar que o render ainda funciona. Veja `references/exemplos-aprovados.md`
pra comparar com o resultado esperado.
