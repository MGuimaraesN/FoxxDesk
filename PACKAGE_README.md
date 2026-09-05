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

## Resilience V4 (2026-09-05)

- CI usa overlay de ícones autenticado e não instala Pillow no runner.
- Windows não valida `chmod +x` via filesystem; Ubuntu preflight valida os modos POSIX.
- `FoxxDesk Build` é somente manual.
- `.gitignore` da raiz é protegido e nunca é alterado.
- Hooks são reparados localmente; CI apenas verifica se foram commitados.

