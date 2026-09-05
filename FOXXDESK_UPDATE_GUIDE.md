# FoxxDesk — guia seguro de atualização upstream (V7)

## 1. Atualize o RustDesk

Aplique/copiei a nova versão upstream preservando os arquivos próprios do FoxxDesk:

- `.foxxdesk/`
- `scripts/foxxdesk_*.py`
- `scripts/apply_foxxdesk_rebrand.py`
- `scripts/apply_foxxdesk_icon.py`
- `.github/actions/prepare-foxxdesk/`
- `.github/workflows/foxxdesk-build.yml`

Não substitua workflows upstream por snapshots antigos deste pacote: a V7 não inclui `flutter-build.yml`, `bridge.yml` nem `ci.yml`.

## 2. Prepare localmente

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
```

O comando:

1. carrega `.foxxdesk/foxxdesk.config.json`;
2. remove hooks FoxxDesk legados de workflows upstream;
3. resolve/sincroniza o `hbb_common` da mesma versão do RustDesk;
4. restaura alterações FoxxDesk legadas que existiam dentro do submódulo;
5. aplica o rebrand `runtime` fora de `hbb_common`;
6. aplica o **brand público semântico** em Android/macOS/Windows;
7. gera/atualiza `src/foxxdesk_defaults.rs` e os patches runtime mínimos;
8. gera/confere os assets do ícone mestre;
9. valida a árvore final usando as mesmas regras semânticas do patch.

## 3. Valide explicitamente

```bash
python3 scripts/foxxdesk_validate.py --target .
```

## 4. Confirme arquivos que nunca devem ser alterados pelo FoxxDesk

```bash
git diff -- .gitignore .gitattributes
```

A saída deve estar vazia, exceto se você mesmo já tivesse alterações nesses arquivos antes do prepare.

## 5. Revise e faça commit

```bash
git status --short
git diff --submodule=log
```

Se `libs/hbb_common` mudou de commit, isso é o gitlink da revisão compatível e precisa entrar no commit.

```bash
git add -A
git commit -m "chore: prepare FoxxDesk upstream update"
git push
```

## 6. Compile manualmente

Abra:

`GitHub > Actions > FoxxDesk Build > Run workflow`

Não existe gatilho automático de push, PR ou schedule no workflow FoxxDesk.

O preflight do Actions é somente leitura. Se falhar, corrija **localmente**, faça novo commit e execute o workflow novamente.

## Diagnóstico

### hbb_common com alteração desconhecida

```bash
git -C libs/hbb_common status --short
git -C libs/hbb_common diff
```

A V7 não apaga alterações desconhecidas automaticamente. Se você realmente quiser restaurar a revisão upstream compatível:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --force-sync-deps
```

### Verificar idempotência

Rode o prepare novamente. Em estado estável, ele deve terminar com 0 alterações relevantes.

### Trocar o ícone

Substitua apenas:

`.foxxdesk/assets/icon.png`

Depois rode o prepare local novamente. Os assets derivados serão regenerados e o cache determinístico atualizado.
