# Atualizar RustDesk sem perder o FoxxDesk

1. Faça backup/branch.
2. Copie a nova versão upstream por cima preservando `.foxxdesk/`, `scripts/foxxdesk_*` e o workflow FoxxDesk.
3. Rode:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
```

4. Rode o prepare uma segunda vez. Em uma árvore estável, ele deve ficar idempotente.
5. Confira `git diff`/`rebrand_report.md`.
6. Commit/push e execute **FoxxDesk Build** no Actions.

## Primeira aplicação sobre um upstream limpo

Use bootstrap apenas na primeira conversão ou auditoria total:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps --bootstrap
```

Depois volte para o perfil `runtime` padrão.

## Se o Actions disser que o icon.png está ausente

O v2 tenta recuperar `icons.source` de um fallback somente se o SHA-256 corresponder a `.foxxdesk/icon-state.json`. Mesmo assim, o correto é versionar o master:

```bash
git add -f .foxxdesk/assets/icon.png .foxxdesk/icon-state.json
git commit -m "fix: commit FoxxDesk master icon"
git push
```

## V3 — fluxo upstream-safe

A V3 não distribui `.gitignore`, `.gitattributes`, `ci.yml`, `bridge.yml`, `flutter-build.yml` ou arquivos `res/*` do RustDesk. Os hooks necessários são aplicados cirurgicamente sobre os workflows da versão presente na pasta.

O workflow `FoxxDesk Build` é somente manual (`workflow_dispatch`). Hooks legados do FoxxDesk em `ci.yml` são removidos automaticamente.

No Windows, `hbb_common` é preparado em staging no mesmo volume do workspace, evitando `WinError 17` e troca parcial de diretórios.
