# FoxxDesk — configuração e atualização resiliente v2

Arquitetura para reaplicar o FoxxDesk sobre novas versões do RustDesk com alterações mínimas, reproduzíveis e verificáveis.

## Regra principal

- **Não substituir arquivos de código por snapshots antigos.** O rebrand usa patches textuais e guards.
- **Uma única configuração:** `.foxxdesk/foxxdesk.config.json`.
- **Uma única fonte visual:** `.foxxdesk/assets/icon.png`.
- **Dependência compatível:** `hbb_common` é pinado à revisão da mesma versão do RustDesk; nunca segue `hbb_common/main` isoladamente.
- **Update normal:** perfil `runtime`; `full` fica reservado a bootstrap/auditoria.
- Arquivos upstream renomeados são preservados por padrão. A exceção automática é `RustDesk.wxs` quando `FoxxDesk.wxs` existe, porque o WiX compila ambos e gera IDs duplicados.

## Fluxo recomendado

Depois de copiar uma atualização do RustDesk por cima do projeto:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
```

O `prepare` executa, nesta ordem:

1. lê e valida `.foxxdesk/foxxdesk.config.json`;
2. migra apenas campos vazios de um `brand.json` legado, se ele ainda existir;
3. instala/repara hooks do GitHub Actions;
4. resolve e sincroniza a revisão compatível de `hbb_common`;
5. reaplica o rebrand no perfil configurado;
6. resolve o ícone mestre com fallback seguro por SHA-256;
7. gera/confere os assets de Android, iOS, Windows, macOS e Linux;
8. atualiza o cache do overlay e `icon-state.json`;
9. executa o preflight.

### Perfis

- `safe`: núcleo mínimo; útil para uma correção bem pequena.
- `runtime`: **padrão recomendado para update e CI**. Reaplica o produto/build e exclui documentação/contribuição e arquivos de API/plataforma do `hbb_common`.
- `full`: bootstrap inicial ou auditoria explícita de toda a allowlist.

Use full apenas intencionalmente:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps --bootstrap
```

## Correção do erro `.foxxdesk/assets/icon.png` ausente no GitHub Actions

O erro antigo:

```text
ERRO: Fonte ausente: .../.foxxdesk/assets/icon.png
```

não derruba mais o build imediatamente. O v2 possui uma recuperação segura:

1. procura `icons.source`;
2. se estiver ausente, testa `icons.fallback_sources`;
3. o SHA-256 do fallback precisa corresponder ao `master_sha256` salvo em `.foxxdesk/icon-state.json`;
4. somente então o arquivo mestre é recriado;
5. se o hash for diferente, o prepare **falha** em vez de usar silenciosamente um ícone RustDesk errado.

O composite action instala Pillow antes da preparação, então o CI pode regenerar os assets em vez de depender de snapshots binários antigos.

### Garanta que o master esteja versionado

O `.gitignore` contém exceções explícitas, mas confirme uma vez:

```bash
git check-ignore -v .foxxdesk/assets/icon.png || true
git add .gitignore .gitattributes .foxxdesk scripts .github/actions/prepare-foxxdesk .github/workflows
git ls-files .foxxdesk/assets/icon.png
```

O último comando deve imprimir:

```text
.foxxdesk/assets/icon.png
```

Se não imprimir, faça:

```bash
git add -f .foxxdesk/assets/icon.png .foxxdesk/icon-state.json
```

Depois commit/push.

## `.foxxdesk/foxxdesk.config.json`

### `brand`

| Campo | Uso |
|---|---|
| `display_name` | Nome público do aplicativo. |
| `slug` | Identificador interno. Mantenha `foxxdesk` salvo se você conscientemente habilitar `allow_internal_slug_change`. |
| `company` | Empresa/copyright em superfícies compatíveis. |
| `maintainer_name` | Nome do mantenedor. |
| `maintainer_email` | E-mail de metadados/pacotes. |
| `homepage` | URL pública. |

### `network`

| Campo | Uso |
|---|---|
| `server` | Rendezvous/ID server padrão. |
| `relay` | Relay padrão. |
| `key` | **Chave pública** do hbbs para o cliente customizado. Não coloque chave privada do servidor no cliente. |

### `icons`

| Campo | Padrão | Função |
|---|---:|---|
| `enabled` | `true` | Gerencia ícones. |
| `source` | `.foxxdesk/assets/icon.png` | Fonte oficial. |
| `fallback_sources` | `res/icon.png`, overlay | Recuperação se o master não chegar ao checkout. |
| `auto_seed_missing_source` | `true` | Permite recuperar apenas fallback verificado. |
| `apply_on_prepare` | `true` | Ícone é parte normal do prepare. |
| `discover_by_name` | `true` | Descobre **somente** nomes conhecidos em raízes de plataforma seguras. |
| `create_brand_owned_assets` | `true` | Pode criar assets exclusivos FoxxDesk. |
| `quality_profile` | `best` | Lanczos + PNG lossless otimizado. |
| `min_source_size` | `512` | Abaixo disso falha. |
| `recommended_source_size` | `1024` | Recomendação. A fonte atual 1024×1024 atende. |
| `padding_ratio` | `0.0` | Padding transparente sem recorte. |
| `ios_background` | `#FFFFFF` | Fundo para AppIcon RGB sem alpha. |
| `png_compress_level` | `9` | Compressão lossless. |
| `png_optimize` | `true` | Otimização sem perda. |

O gerador nunca toca `res/logo-header.svg` e `res/design.svg`. SVG existente preserva `width`, `height` e `viewBox`; apenas o payload visual é atualizado.

### Descoberta segura por nome

A descoberta não procura todo `*.png` do projeto. Ela é limitada a raízes conhecidas (`res`, Fastlane metadata, Android `res`, iOS AppIcon e recursos Windows) e nomes de aplicativo como `ic_launcher.png`, `ic_stat_logo.png`, `app_icon.png` e `icon.png` em contextos permitidos.

### `rebrand`

```json
{
  "profile": "runtime",
  "ci_profile": "runtime",
  "bootstrap_profile": "full",
  "scan_all": false,
  "remove_old_renamed": false,
  "patch_only": true,
  "replace_whole_source_files": false,
  "protect_upstream_names": true,
  "allow_internal_slug_change": false
}
```

`patch_only=true` e `replace_whole_source_files=false` são invariantes de segurança.

### `upstream`

`hbb_common_pins` registra `versão RustDesk -> commit hbb_common`. Para RustDesk 1.4.9:

```text
7e1c392c62d39c364127307cd408421dd5f8cfb0
```

Comando manual:

```bash
python3 scripts/foxxdesk_sync_hbb_common.py --target . --force --write-pin
```

## Ícones

Rodar diretamente:

```bash
python3 scripts/apply_foxxdesk_icon.py \
  --target . \
  --source .foxxdesk/assets/icon.png \
  --quality-profile best \
  --discover-by-name \
  --create-brand-owned-assets \
  --png-compress-level 9 \
  --apply --yes
```

Normalmente não é necessário: `foxxdesk_prepare.py` já faz isso.

## Build local

Mostrar o comando resolvido:

```bash
python3 scripts/foxxdesk_build.py --target . --dry-run
```

Preparar e compilar:

```bash
python3 scripts/foxxdesk_build.py --target . --prepare
```

O wrapper somente traduz opções que o `build.py` suporta na plataforma atual, como `--flutter`, `--hwcodec`, `--vram` (Windows), `--portable` (Windows), `--unix-file-copy-paste`, `--screencapturekit` (macOS), `--skip-cargo`, `--skip-portable-pack` (Windows) e `--package`.

## GitHub Actions

O composite action `.github/actions/prepare-foxxdesk/action.yml`:

1. instala `Pillow>=10,<13`;
2. executa `foxxdesk_prepare.py --ci`;
3. usa `rebrand.ci_profile` (`runtime` por padrão);
4. sincroniza `hbb_common` exatamente;
5. regenera ícones do master/fallback verificado;
6. valida antes do build.

O workflow `FoxxDesk Build` executa preflight em push/PR. A matriz completa é disparada manualmente com `workflow_dispatch`.

## Argumentos principais do prepare

```text
--target PATH
--apply
--dry-run
--ci
--bootstrap
--sync-deps
--force-sync-deps
--profile safe|runtime|full
--regenerate-icons      compatibilidade; geração já é automática
--skip-icons            opt-out explícito
--skip-validate
```

## Checklist antes do push

```bash
python3 -m py_compile scripts/*.py
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
git status --short
git ls-files .foxxdesk/assets/icon.png
git add .
git commit -m "chore: prepare FoxxDesk update"
git push
```

Se o segundo `prepare` na mesma árvore ainda alterar dezenas de arquivos, pare e revise o relatório. Em estado estável, a execução seguinte deve ser essencialmente idempotente: rebrand `0` e ícones `0` quando nada mudou.

## Resilience V4 (2026-09-05)

- CI usa overlay de ícones autenticado e não instala Pillow no runner.
- Windows não valida `chmod +x` via filesystem; Ubuntu preflight valida os modos POSIX.
- `FoxxDesk Build` é somente manual.
- `.gitignore` da raiz é protegido e nunca é alterado.
- Hooks são reparados localmente; CI apenas verifica se foram commitados.

