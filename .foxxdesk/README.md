# `.foxxdesk` — fonte persistente do FoxxDesk

Esta pasta deve sobreviver às atualizações do RustDesk e ser versionada no Git.

- `foxxdesk.config.json`: **única configuração editável** do FoxxDesk.
- `foxxdesk.config.schema.json`: schema para validação/autocomplete.
- `assets/icon.png`: ícone mestre oficial.
- `icon-state.json`: SHA-256 do master e parâmetros usados; valida fallback seguro no CI.
- `icon-overlay/`: cache dos assets gerados. É fallback/cache, não fonte principal.
- `icon-overlay-manifest.json`: lista do cache.

O antigo `brand.json` não é mais necessário.

Atualização normal:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
```

O perfil padrão é `runtime`. Use `--bootstrap` somente para primeira conversão/auditoria completa.
