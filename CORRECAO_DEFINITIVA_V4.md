# FoxxDesk Resilience V4 — correção cross-platform definitiva

## Problemas corrigidos

1. **macOS / PEP 668** — o composite action não executa mais `pip install` no Python Homebrew. No CI, os ícones são restaurados do overlay autenticado por SHA-256.
2. **Windows / 4 pendências falsas** — o rebrand não tenta mais validar/aplicar bits POSIX de execução pelo filesystem Windows. Os quatro scripts `res/DEBIAN/*` são validados no preflight Ubuntu, onde o bit 100755 é real.
3. **Windows / 21 alterações falsas** — `chmod +x` não é mais registrado como alteração em cada job Windows.
4. **hbb_common** — mantém a troca atômica no mesmo volume da V3 e não força reinstalação quando a revisão/API já é compatível.
5. **GitHub Actions** — `FoxxDesk Build` continua somente manual (`workflow_dispatch`). O modo CI apenas verifica hooks; ele não tenta reparar workflows depois que o grafo do Actions já foi resolvido.
6. **Ícone** — CI não depende de Pillow e não gera bytes diferentes por sistema operacional. O master continua `.foxxdesk/assets/icon.png`; localmente o prepare regenera o overlay quando necessário.
7. **.gitignore** — o rebrand nunca altera o `.gitignore` da raiz. `.foxxdesk/.gitignore` re-inclui apenas os assets de propriedade do FoxxDesk.

## Fluxo recomendado

Após copiar uma atualização upstream:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
```

Faça commit das alterações e só então rode **Actions → FoxxDesk Build → Run workflow**.

Se uma atualização upstream substituir `flutter-build.yml` ou `bridge.yml`, o prepare local reinstala os hooks. No CI, hook ausente é erro proposital: o build para antes de compilar uma árvore sem preparação.
