# `.foxxdesk` — fonte persistente do FoxxDesk V6

Esta pasta pertence ao FoxxDesk, deve sobreviver às atualizações do RustDesk e deve ser versionada no Git.

- `foxxdesk.config.json`: única configuração editável.
- `foxxdesk.config.schema.json`: schema de validação/autocomplete.
- `assets/icon.png`: ícone mestre oficial.
- `icon-state.json`: hash e parâmetros do master.
- `icon-overlay/`: cache determinístico dos assets gerados.
- `icon-overlay-manifest.json`: manifesto do cache.
- `.gitignore`: regras locais apenas desta pasta; não altera o `.gitignore` upstream.

O antigo `brand.json` não é necessário.

Atualização normal:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
```

Na V6, `libs/hbb_common` permanece upstream/limpo. Os defaults de nome/server/relay/key ficam no crate principal via `src/foxxdesk_defaults.rs`.

O CI é somente leitura e o build é manual.

## V8 — assets opcionais de marca

`res/FoxxDesk.png`, `res/FoxxDesk.svg` e `res/foxxdesk-banner.svg` são conveniências de branding. O prepare pode gerá-los e armazená-los no overlay, mas o CI não os exige porque não são dependências do build e podem ser ignorados pelas regras upstream. O `.gitignore` da raiz não é alterado.
