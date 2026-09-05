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
