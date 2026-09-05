# FoxxDesk Resilience V6

Pacote patch-only para manter o FoxxDesk resiliente a atualizações do RustDesk.

## Aplicar

Extraia este pacote na raiz do projeto e execute:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
```

Depois revise `git status --short`, faça commit/push e rode **manualmente** `FoxxDesk Build` no GitHub Actions.

## Regra da V6

**Local prepara; Git registra; CI valida; build compila o commit.**

- `libs/hbb_common` permanece upstream/limpo;
- defaults FoxxDesk ficam no crate principal;
- CI não reaplica rebrand;
- nenhum hook é inserido em workflows upstream;
- `.gitignore` e `.gitattributes` da raiz não são modificados;
- o build FoxxDesk só possui `workflow_dispatch`.

Leia `CORRECAO_DEFINITIVA_V6.md`, `FOXXDESK_UPDATE_GUIDE.md` e `FOXXDESK_CONFIGURATION.md`.
