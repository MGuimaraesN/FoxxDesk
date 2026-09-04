# Atualização segura do FoxxDesk

## Objetivo

O brand, os servidores e os ícones ficam persistidos em `.foxxdesk/`. Ao copiar uma nova versão do RustDesk para esta pasta, **não substitua a pasta `.foxxdesk/` nem os scripts `foxxdesk_*.py`**.

O problema antigo era baixar `hbb_common` da branch `main`. RustDesk e `hbb_common` precisam estar no mesmo conjunto de revisões; misturar versões gera erros de compilação diferentes em Windows, Linux e Android.

## Depois de copiar uma nova atualização

Execute na raiz do projeto:

```bash
python scripts/foxxdesk_prepare.py --apply --yes --sync-deps --regenerate-icons
python scripts/foxxdesk_validate.py
```

O primeiro comando:

1. restaura o ícone mestre e os assets persistentes;
2. detecta a versão do `Cargo.toml`;
3. usa primeiro um pin conhecido e, em versões novas, resolve o commit de `hbb_common` do mesmo release RustDesk; um gitlink local só é usado como fallback e ainda precisa passar pela validação de compatibilidade;
4. reinstala automaticamente os hooks FoxxDesk nos workflows upstream que uma atualização pode sobrescrever;
5. reaplica o brand FoxxDesk em modo idempotente, preservando nomes internos de compatibilidade que não devem ser renomeados;
6. regenera os ícones quando `--regenerate-icons` é usado;
7. executa o preflight.

Se a máquina local não tiver Pillow, omita apenas `--regenerate-icons`; o overlay existente continuará sendo restaurado:

```bash
python scripts/foxxdesk_prepare.py --apply --yes --sync-deps
```

## Nova versão ainda não cadastrada

Normalmente o sincronizador resolve automaticamente o SHA do submódulo a partir da versão. Se você estiver usando um commit/nightly que não corresponde a uma tag, defina `upstream.rustdesk_ref` em `.foxxdesk/brand.json` para a tag ou SHA do RustDesk usado.

Também é possível fixar explicitamente uma revisão em `upstream.hbb_common_pins`.

## GitHub Actions

Use **Actions → FoxxDesk Build → Run workflow**.

Antes de cada job que realmente compila, o workflow executa `.github/actions/prepare-foxxdesk`, que:

- restaura brand/ícones;
- força a revisão compatível de `hbb_common`;
- valida os invariantes;
- só então inicia bridge/build.

Pushes para `main` e pull requests executam o `preflight`; a matriz completa de builds é iniciada manualmente por `workflow_dispatch` para evitar gastar runners a cada commit. O preflight também verifica se uma atualização sobrescreveu os hooks dos workflows antes de chamar o workflow reutilizável.

## Arquivos que devem ser preservados ao atualizar

- `.foxxdesk/**`
- `scripts/foxxdesk_prepare.py`
- `scripts/foxxdesk_sync_hbb_common.py`
- `scripts/foxxdesk_validate.py`
- `scripts/foxxdesk_ci_hooks.py`
- `.github/actions/prepare-foxxdesk/action.yml`
- `.github/workflows/foxxdesk-build.yml`

O script legado `scripts/apply_foxxdesk_rebrand.py` continua existindo por compatibilidade, mas agora a entrada recomendada é `foxxdesk_prepare.py`. O download direto de `hbb_common/main` foi removido.
