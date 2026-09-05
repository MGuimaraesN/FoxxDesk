# FoxxDesk — correção definitiva V3

## Objetivo

Esta versão foi desenhada para receber novas versões do RustDesk sem sobrescrever arquivos upstream com snapshots antigos e sem disparar o build FoxxDesk automaticamente.

## Mudanças principais

### 1. `.gitignore` nunca é alterado

O rebrand possui um bloqueio explícito para `.gitignore`, `flutter/.gitignore` e `.gitattributes`, inclusive em `--scan-all`. O pacote V3 também não distribui esses arquivos.

Se o Git já ignorar PNG por regra upstream, adicione o ícone mestre uma única vez com:

```bash
git add -f .foxxdesk/assets/icon.png
```

Arquivos já rastreados continuam rastreados mesmo que uma regra de ignore exista.

### 2. FoxxDesk Build é somente manual

`.github/workflows/foxxdesk-build.yml` possui somente `workflow_dispatch`. Não há `push` nem `pull_request`.

Os hooks `prepare-foxxdesk` são mantidos apenas em:

- `.github/workflows/flutter-build.yml`
- `.github/workflows/bridge.yml`

Hooks antigos injetados em `ci.yml` ou outros workflows automáticos são removidos pelo `foxxdesk_ci_hooks.py`.

### 3. `hbb_common` Windows — WinError 17/183 corrigidos

O erro anterior ocorria porque o clone temporário era criado em `C:\...\Temp` e movido para o workspace `D:\a\...`. No Windows isso pode falhar com `WinError 17`.

A V3 cria o staging diretamente em:

```text
libs/.hbb_common.foxxdesk-new
```

ou seja, no mesmo volume de `libs/hbb_common`. A instalação usa troca por rename no mesmo filesystem e backup transacional:

```text
libs/hbb_common
  -> libs/.hbb_common.foxxdesk-old
libs/.hbb_common.foxxdesk-new
  -> libs/hbb_common
```

Se a troca falhar, o diretório anterior é restaurado. A limpeza também trata arquivos Git read-only no Windows.

### 4. CI não força mais download do `hbb_common`

`--ci` não equivale mais a `--force-sync-deps`.

O comportamento normal é:

1. detectar a versão RustDesk;
2. resolver o commit compatível;
3. conferir o `hbb_common` atual;
4. sincronizar somente se necessário/incompatível;
5. validar após a sincronização.

Para realmente forçar uma restauração:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --force-sync-deps
```

### 5. Pacote V3 não contém snapshots upstream

O ZIP de patch contém apenas:

- `.foxxdesk/**`
- `scripts/**`
- `.github/actions/prepare-foxxdesk/action.yml`
- `.github/workflows/foxxdesk-build.yml`
- documentação FoxxDesk

Ele não contém `.gitignore`, `.gitattributes`, `ci.yml`, `bridge.yml`, `flutter-build.yml` ou arquivos `res/*` do upstream.

O prepare aplica mudanças cirúrgicas sobre a versão que estiver na pasta.

## Fluxo recomendado após atualizar RustDesk

Extraia o pacote V3 sobre a raiz do projeto e execute:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
```

Depois confira:

```bash
git status --short
git diff -- .gitignore
```

O segundo comando deve ficar vazio.

Para garantir que o ícone mestre esteja rastreado:

```bash
git add -f .foxxdesk/assets/icon.png
git add .foxxdesk scripts .github/actions/prepare-foxxdesk .github/workflows/foxxdesk-build.yml
```

Depois execute o build manualmente em **Actions → FoxxDesk Build → Run workflow**.
