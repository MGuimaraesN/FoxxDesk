# FoxxDesk Resilience V3

Patch upstream-safe para FoxxDesk.

## Instalação

Extraia na raiz do projeto sem apagar os arquivos existentes e rode:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
```

O patch não distribui nem modifica `.gitignore`.

O workflow `FoxxDesk Build` é manual-only (`workflow_dispatch`).

Consulte `CORRECAO_DEFINITIVA_V3.md` e `FOXXDESK_CONFIGURATION.md`.
