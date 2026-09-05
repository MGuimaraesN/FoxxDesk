# FoxxDesk — configuração e scripts V7

## Arquitetura

A V7 usa uma única configuração:

`.foxxdesk/foxxdesk.config.json`

Princípio operacional:

**local prepara → Git registra → CI valida → build compila o commit**.

O GitHub Actions não reaplica o rebrand. Isso é proposital: evita depender da posição de `actions/checkout` nos workflows do RustDesk e garante que todas as plataformas compilem a mesma árvore versionada.

`libs/hbb_common` é tratado como submódulo upstream. Nenhum nome, servidor, relay ou chave FoxxDesk é escrito dentro dele.

## Comando principal

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
```

Ordem da V7:

1. carrega/valida o JSON central;
2. remove hooks FoxxDesk legados de workflows upstream;
3. resolve a revisão correta do `hbb_common`;
4. restaura branding legado dentro do submódulo, se reconhecido;
5. aplica rebrand `runtime` com `--preserve-hbb-common`;
6. aplica o brand público semântico (`foxxdesk_public_brand.py`) em Android/macOS/Windows;
7. aplica `src/foxxdesk_defaults.rs` e patches runtime no crate principal;
8. gera/confere ícones e cache determinístico;
9. executa a validação final com a mesma regra semântica do patch.

## `brand`

| Campo | Função | Recomendação |
|---|---|---|
| `display_name` | Nome público exibido ao usuário. | `FoxxDesk` |
| `slug` | Identificador interno/pacote. | Mantenha `foxxdesk`. |
| `company` | Empresa/copyright/metadados. | Personalizável. |
| `maintainer_name` | Nome do mantenedor. | Opcional. |
| `maintainer_email` | E-mail em metadados compatíveis. | Opcional. |
| `homepage` | Site público do produto. | HTTPS recomendado. |

Alterar `slug` é uma operação mais invasiva. Por padrão `allow_internal_slug_change=false` impede mudanças acidentais.

## `network`

| Campo | Função |
|---|---|
| `server` | Rendezvous/ID server padrão compilado no FoxxDesk. |
| `relay` | Relay padrão; se vazio, o loader herda `server`. |
| `key` | Chave pública usada para validar a conexão com o servidor. |

Na V7 estes defaults são materializados em `src/foxxdesk_defaults.rs`, não em `libs/hbb_common`.

## `icons`

| Campo | Função |
|---|---|
| `enabled` | Ativa o pipeline FoxxDesk de ícones. |
| `source` | Fonte mestre. Padrão: `.foxxdesk/assets/icon.png`. |
| `apply_on_prepare` | Confere/regenera ícones no prepare local. |
| `discover_by_name` | Procura nomes conhecidos apenas em raízes de plataforma seguras. |
| `create_brand_owned_assets` | Permite criar assets próprios FoxxDesk ausentes. |
| `quality_profile` | `best`, `balanced` ou `fast`. |
| `min_source_size` | Resolução mínima aceita. |
| `recommended_source_size` | Resolução recomendada. |
| `padding_ratio` | Margem transparente de 0 até <0,45. |
| `ios_background` | Fundo ao remover transparência do AppIcon iOS. |
| `png_compress_level` | Compressão PNG 0–9, sem perda visual. |
| `png_optimize` | Ativa otimização PNG. |
| `fallback_sources` | Fontes de recuperação permitidas. |
| `auto_seed_missing_source` | Só recupera master ausente quando o hash esperado comprova identidade. |

No CI não há Pillow/renderização. O cache em `.foxxdesk/icon-overlay/` é conferido byte a byte/hash.

## `rebrand`

| Campo | Função |
|---|---|
| `profile` | Perfil normal. V7 recomenda `runtime`. |
| `ci_profile` | Mantido para compatibilidade; CI V7 é somente leitura. |
| `bootstrap_profile` | Perfil usado por `--bootstrap`, normalmente `full`. |
| `scan_all` | Varredura ampla. Deixe `false` em updates normais. |
| `remove_old_renamed` | Remove originais após cópias/renomes. Deixe `false` por segurança. |
| `patch_only` | Política de patch textual/cirúrgico. |
| `replace_whole_source_files` | Deve permanecer `false`. |
| `protect_upstream_names` | Preserva identificadores upstream quando necessário à compatibilidade. |
| `allow_internal_slug_change` | Libera mudança invasiva do slug. |

Perfis:

- `safe`: núcleo mínimo;
- `runtime`: produto/build, padrão de atualização;
- `full`: bootstrap/auditoria intencional.

Mesmo no `full`, quando iniciado pelo `foxxdesk_prepare.py`, `hbb_common` é preservado.

## `upstream`

| Campo | Função |
|---|---|
| `rustdesk_ref` | `auto` ou uma ref explícita do RustDesk. |
| `sync_hbb_common` | Habilita conferência/sincronização local. |
| `hbb_common_pins` | Mapa `versão RustDesk -> SHA hbb_common`. |

Para versão conhecida, o pin é determinístico. Para versão nova, o helper tenta resolver o gitlink da mesma ref/versão do RustDesk e persiste o SHA. Ele nunca segue `hbb_common/main` isoladamente.

## `build`

O wrapper `scripts/foxxdesk_build.py` converte apenas opções que o `build.py` instalado suporta no contexto atual.

Campos principais:

- `flutter`
- `portable` (Windows)
- `hwcodec`
- `vram` (Windows)
- `unix_file_copy_paste` (Linux/macOS)
- `screencapturekit` (macOS)
- `skip_cargo`
- `skip_portable_pack` (Windows)
- `package`
- `resource_features`
- `cargo_features` (reservado/configurável; não é habilitado cegamente)

Ver comando sem compilar:

```bash
python3 scripts/foxxdesk_build.py --target . --dry-run
```

Preparar e compilar localmente:

```bash
python3 scripts/foxxdesk_build.py --target . --prepare
```

## `github_actions`

Configuração V7 esperada:

```json
{
  "enabled": true,
  "validate_before_build": true,
  "install_icon_dependencies": false,
  "deterministic_icon_cache_in_ci": true,
  "manual_build_only": true,
  "ci_mutates_source": false,
  "require_prepared_commit": true,
  "inject_prepare_hooks_into_upstream_workflows": false
}
```

O workflow `.github/workflows/foxxdesk-build.yml` deve ter somente `workflow_dispatch` como gatilho FoxxDesk.

O composite `.github/actions/prepare-foxxdesk/action.yml` executa **somente validação**:

```bash
python scripts/foxxdesk_validate.py --target . --ci
```

## `safety`

| Campo | Função |
|---|---|
| `fail_on_missing_required_files` | Falha quando componente necessário desapareceu. |
| `fail_on_incompatible_hbb_common` | Bloqueia dependência incompatível. |
| `backup_before_patch` | Mantém backups nas rotinas legadas aplicáveis. |
| `require_nonempty_server` | Impede build sem server. |
| `require_nonempty_key` | Impede build sem chave pública. |
| `allow_unverified_icon_fallback` | Deve permanecer `false`; evita usar logo errada. |

## Argumentos do `foxxdesk_prepare.py`

| Argumento | Uso |
|---|---|
| `--target PATH` | Raiz do projeto. |
| `--apply` | Aplica mudanças locais. |
| `--dry-run` | Mostra mudanças sem aplicar. |
| `--yes` | Compatibilidade com fluxo não interativo. |
| `--ci` | **Somente leitura**: valida a árvore commitada. |
| `--bootstrap` | Usa o perfil de bootstrap/full. |
| `--sync-deps` | Confere/sincroniza `hbb_common` quando necessário. |
| `--force-sync-deps` | Força restaurar a revisão esperada; use apenas conscientemente. |
| `--profile safe|runtime|full` | Sobrescreve perfil da execução. |
| `--regenerate-icons` | Compatibilidade; o prepare já confere os ícones. |
| `--skip-icons` | Não trata ícones nesta execução. |
| `--skip-validate` | Pula validação final; não recomendado. |

## Argumentos de `foxxdesk_sync_hbb_common.py`

```text
--target PATH
--force
--check
--write-pin
```

Se um submódulo real possuir alteração local desconhecida, o modo normal **não descarta** essa alteração. Revise primeiro:

```bash
git -C libs/hbb_common status --short
git -C libs/hbb_common diff
```


## `foxxdesk_public_brand.py`

A V7 separa o **nome público obrigatório** do rebrand genérico. Esse helper é a única fonte de verdade para:

- `flutter/android/app/src/main/res/values/strings.xml` → `app_name`;
- `flutter/android/app/src/main/AndroidManifest.xml` → `application android:label`;
- `flutter/macos/Runner/Configs/AppInfo.xcconfig` → `PRODUCT_NAME`;
- `flutter/windows/runner/Runner.rc` → `ProductName` e metadados equivalentes quando presentes.

Uso manual:

```bash
python3 scripts/foxxdesk_public_brand.py --target . --apply
python3 scripts/foxxdesk_public_brand.py --target . --check
```

O `foxxdesk_prepare.py` já executa `--apply` automaticamente no preparo local. O `foxxdesk_validate.py` usa **o mesmo helper em modo de verificação**, evitando divergência entre quem corrige e quem valida.

O helper não faz busca global por `RustDesk` e não substitui arquivos inteiros. Ele altera somente os campos conhecidos acima. Se uma versão futura remover ou reformular um desses anchors, o prepare falha com mensagem específica em vez de aplicar substituição cega.

## `foxxdesk_runtime_defaults.py`

Uso interno recomendado:

```bash
python3 scripts/foxxdesk_runtime_defaults.py --target . --apply
python3 scripts/foxxdesk_runtime_defaults.py --target . --check
```

Patches V7 são marker-based e idempotentes. Se um anchor upstream desaparecer, o helper termina com erro específico.

## `apply_foxxdesk_rebrand.py`

É o engine de rebrand de baixo nível. Prefira chamar `foxxdesk_prepare.py`.

Flags especialmente importantes para V7:

- `--profile runtime`
- `--icons-managed-externally`
- `--preserve-hbb-common`
- `--skip-hbb-common-download`

O prepare define essas políticas automaticamente.

## `apply_foxxdesk_icon.py`

Opções úteis:

- `--source`
- `--ios-background`
- `--discover-by-name`
- `--create-brand-owned-assets`
- `--quality-profile best|balanced|fast`
- `--padding-ratio`
- `--png-compress-level`
- `--min-source-size`
- `--recommended-source-size`
- `--no-png-optimize`

Troque somente `.foxxdesk/assets/icon.png` e rode o prepare; não edite manualmente dezenas de derivados.

## Checklist antes do commit

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
git diff -- .gitignore .gitattributes
git -C libs/hbb_common status --short
git status --short
```

Esperado:

- validação OK;
- `.gitignore`/`.gitattributes` sem mudanças do FoxxDesk;
- `hbb_common` worktree limpa;
- segunda execução do prepare com 0 alterações relevantes.
