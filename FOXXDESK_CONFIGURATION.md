# FoxxDesk — Configuração, rebrand, ícones e build

> Arquitetura resiliente para atualizar o RustDesk sem perder o FoxxDesk e sem substituir arquivos de código por snapshots antigos.

## 1. Princípio principal

O FoxxDesk mantém o código upstream o mais próximo possível do RustDesk e aplica somente alterações necessárias, em ordem previsível:

1. lê `.foxxdesk/foxxdesk.config.json`;
2. valida a configuração;
3. sincroniza `hbb_common` com a revisão compatível quando solicitado/CI;
4. reaplica o rebrand por patches textuais;
5. reaplica a identidade pública configurável;
6. reaplica o ícone mestre em todos os assets detectados;
7. restaura os hooks do GitHub Actions;
8. executa o preflight.

A pasta `.foxxdesk/` é persistente e deve ser versionada no Git.

---

## 2. Arquivos principais

| Arquivo | Função |
|---|---|
| `.foxxdesk/foxxdesk.config.json` | Configuração central editável. |
| `.foxxdesk/foxxdesk.config.schema.json` | Schema com descrições e validação para editores. |
| `.foxxdesk/assets/icon.png` | Ícone mestre persistente. Recomendado: PNG quadrado 2048×2048; mínimo padrão: 1024×1024. |
| `.foxxdesk/brand.json` | Compatibilidade com scripts antigos. É gerado/sincronizado automaticamente; não edite manualmente. |
| `.foxxdesk/icon-overlay/` | Fallback dos assets já gerados. Não é a fonte principal. |
| `scripts/foxxdesk_prepare.py` | Entrada principal depois de uma atualização e também no CI. |
| `scripts/foxxdesk_validate.py` | Preflight de brand, ícone, scripts, CI e `hbb_common`. |
| `scripts/apply_foxxdesk_icon.py` | Gera ícones por plataforma usando descoberta segura por nome. |
| `scripts/foxxdesk_identity.py` | Aplica somente campos públicos configuráveis sem renomear identificadores internos sensíveis. |
| `scripts/foxxdesk_build.py` | Wrapper local que traduz o JSON para argumentos realmente suportados pelo `build.py`. |
| `scripts/foxxdesk_sync_hbb_common.py` | Mantém `hbb_common` na revisão compatível; nunca segue `main` independentemente. |
| `.github/workflows/foxxdesk-build.yml` | Preflight automático e build completo manual via GitHub Actions. |

---

## 3. Fluxo recomendado após atualizar o RustDesk

Depois de copiar uma nova atualização por cima do projeto:

```bash
python scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python scripts/foxxdesk_validate.py --target .
```

Se estiver trabalhando em uma release já pinada e não quiser rede no prepare local:

```bash
python scripts/foxxdesk_prepare.py --target . --apply --yes
```

Para visualizar antes:

```bash
python scripts/foxxdesk_prepare.py --target . --dry-run
```

O ícone é aplicado **por padrão**. Para desativá-lo excepcionalmente:

```bash
python scripts/foxxdesk_prepare.py --target . --apply --yes --skip-icons
```

`--skip-icons` é um opt-out; não é recomendado durante atualização.

---

## 4. Configuração central

### `brand`

| Campo | Uso | Recomendação |
|---|---|---|
| `display_name` | Nome visível do aplicativo. | Pode ser alterado. O script mexe somente em superfícies públicas conhecidas. |
| `slug` | Nome interno/crate/binário. | **Mantenha `foxxdesk`**. Alterar pode afetar FFI, caminhos, MSI, scripts e empacotamento. |
| `company` | Empresa nos metadados compatíveis. | Ex.: `MGN Systems`. |
| `maintainer_name` | Nome do mantenedor. | Informativo/metadados. |
| `maintainer_email` | E-mail de pacotes/metadados. | Use um e-mail válido do projeto. |
| `homepage` | URL pública. | Use HTTPS. |
| `copyright_owner` | Titular exibido em copyright. | Não altera licenças upstream. |

### `network`

| Campo | Uso |
|---|---|
| `server` | Servidor rendezvous/ID padrão embutido. |
| `relay` | Relay padrão. Se vazio, pode usar o mesmo host do servidor. |
| `key` | Chave **pública** do hbbs compilada no cliente customizado. |

### `icons`

| Campo | Padrão | Explicação |
|---|---:|---|
| `enabled` | `true` | Ativa o gerenciamento de ícones. |
| `source` | `.foxxdesk/assets/icon.png` | Fonte mestre persistente. |
| `apply_on_prepare` | `true` | Reaplica ícones em toda preparação. |
| `discover_by_name` | `true` | Procura nomes de ícones conhecidos somente em raízes de plataforma permitidas. |
| `create_brand_owned_assets` | `true` | Pode criar apenas assets exclusivos do FoxxDesk, como `FoxxDesk.svg`. |
| `quality_profile` | `best` | Perfil de qualidade. |
| `min_source_size` | `1024` | Abaixo disso o perfil `best` falha para evitar upscale ruim. |
| `recommended_source_size` | `2048` | Recomendação para uma fonte limpa. |
| `padding_ratio` | `0.0` | Espaço transparente ao redor da logo. Use com cautela. |
| `ios_background` | `#FFFFFF` | Fundo usado porque o AppIcon de iOS não deve depender de transparência. |
| `update_ios_contents` | `false` | Só altere `Contents.json` se realmente necessário. |
| `png_compress_level` | `9` | Compressão lossless. Não reduz qualidade visual. |
| `png_optimize` | `true` | Otimização de PNG. |

### Perfis de ícone

- `best`: mínimo 1024 px, Lanczos, PNG otimizado. Recomendado.
- `balanced`: aceita fonte a partir de 512 px.
- `compat`: aceita 256 px para projetos antigos, com menor garantia visual.

A geração preserva proporção e não recorta a arte. Para SVG já existente, preserva `width`, `height` e `viewBox`; apenas o payload visual é atualizado. O script nunca toca `res/logo-header.svg` nem `res/design.svg`.

### Descoberta de ícones por nome

A descoberta não faz uma busca global perigosa. Ela é limitada a contextos conhecidos:

- Android: `ic_launcher.png`, `ic_launcher_round.png`, `ic_launcher_foreground.png`, `ic_stat_logo.png` dentro de `mipmap-*`;
- iOS: `Icon-App-*.png` dentro de `*.appiconset`;
- Windows: `app_icon.ico` dentro de recursos do runner;
- macOS: `AppIcon.icns` dentro do projeto macOS;
- Fastlane Android: `icon.png` somente dentro de `metadata/android/.../images`;
- assets raiz explicitamente conhecidos (`32x32.png`, `64x64.png`, `icon.ico`, etc.).

Isso evita substituir qualquer `icon.png` aleatório usado dentro da interface.

---

## 5. `rebrand`

| Campo | Recomendado | Explicação |
|---|---:|---|
| `profile` | `full` após update | Reaplica a allowlist completa. |
| `scan_all` | `false` | Evita varredura textual ampla. Ative apenas para auditoria manual. |
| `remove_old_renamed` | `false` | Mantém o comportamento conservador. Conflitos comprovados continuam tratados por guards dedicados. |
| `patch_only` | `true` | Regra estrutural: alterar trechos, não copiar snapshots antigos. |
| `replace_whole_source_files` | `false` | Deve permanecer `false`. |
| `protect_upstream_names` | `true` | Preserva nomes que pertencem a dependências/URLs/integrações upstream. |

### Perfis

- `safe`: núcleo crítico/build. Bom para correções pequenas.
- `full`: allowlist completa do rebrand. Recomendado logo depois de copiar uma nova release por cima.

---

## 6. `upstream` e `hbb_common`

`RustDesk` e `hbb_common` evoluem juntos. O FoxxDesk não deve baixar `hbb_common/main` isoladamente.

| Campo | Uso |
|---|---|
| `rustdesk_ref` | `auto` tenta usar a versão detectada no `Cargo.toml`. |
| `sync_hbb_common` | Habilita sincronização segura. |
| `hbb_common_pins` | Mapa `versão RustDesk -> SHA hbb_common`. |

Comando manual:

```bash
python scripts/foxxdesk_sync_hbb_common.py --target . --force --write-pin
```

Validação sem alterar:

```bash
python scripts/foxxdesk_sync_hbb_common.py --target . --check
```

---

## 7. Build local configurável

O wrapper usa somente opções que o `build.py` já oferece:

```bash
python scripts/foxxdesk_build.py --target . --prepare
```

Somente mostrar o comando:

```bash
python scripts/foxxdesk_build.py --target . --dry-run
```

### Opções de `build.build_py`

| JSON | Argumento real | Plataforma/efeito |
|---|---|---|
| `hwcodec` | `--hwcodec` | Habilita `hwcodec`; em Linux exige dependências de VA conforme o ambiente. |
| `vram` | `--vram` | Atualmente usado no fluxo Windows suportado. |
| `unix_file_copy_paste` | `--unix-file-copy-paste` | Habilita cópia/cola de arquivos no caminho Unix suportado. |
| `screencapturekit` | `--screencapturekit` | macOS; integra ScreenCaptureKit onde o source usa a feature. |
| `skip_cargo` | `--skip-cargo` | Pula cargo no caso suportado pelo `build.py`; útil somente em fluxos específicos. |
| `skip_portable_pack` | `--skip-portable-pack` | Windows Flutter; não empacota o portable. |
| `resource_features` | `--feature ...` | Integra recursos externos previstos no `build.py`; atualmente o próprio help informa que não há feature externa ativa por padrão. |
| `build.portable` | `--portable` | Windows. |
| `build.package` | `--package <valor>` | Repassa o package ao build.py. |

### Cargo features encontradas no projeto

Estas features existem no `Cargo.toml`; nem todas devem ser ligadas automaticamente pelo wrapper:

| Feature | Papel no source | Automático pelo wrapper? |
|---|---|---|
| `inline` | Caminho de UI/recursos inline usado especialmente no build não-Flutter. | Gerenciado pelo próprio `build.py`; não force no JSON. |
| `use_samplerate` | Backend de resampling de áudio. | Não. Avançado. |
| `use_rubato` | Backend de resampling de áudio. | Não. Avançado. |
| `use_dasp` | Backend de resampling padrão do projeto. | Vem nos default features. |
| `flutter` | Integra `flutter_rust_bridge` e código Flutter. | Sim, ao usar `build.ui=flutter`. |
| `hwcodec` | Caminhos de codec por hardware. | Sim, via `--hwcodec`. |
| `vram` | Caminhos de frame/codec que usam VRAM. | Sim, via `--vram` no Windows. |
| `mediacodec` | Caminhos MediaCodec, especialmente Android. | Não pelo wrapper local genérico. |
| `plugin_framework` | Compila o framework de plugins junto ao Flutter. | Não por padrão; exige teste específico. |
| `linux-pkg-config` | Faz dependências Linux usarem pkg-config em partes do projeto. | Não por padrão. |
| `unix-file-copy-paste` | Cópia/cola de arquivos em Unix. | Sim. |
| `screencapturekit` | Captura/áudio via ScreenCaptureKit no macOS. | Sim no macOS. |

**Dica:** não habilite várias features de backend de áudio apenas porque existem. Uma feature existente no Cargo não significa que toda combinação é suportada pelo workflow atual.

---

## 8. Argumentos dos scripts

### `foxxdesk_prepare.py`

Pré-requisito local para geração/validação de ícones:

```bash
python -m pip install "Pillow>=10,<13"
```

```text
--target PATH            raiz do projeto
--apply                  aplica (padrão quando não usa --dry-run)
--dry-run                simula sem salvar o projeto
--ci                     modo CI, força sincronização/validação apropriada
--sync-deps              sincroniza hbb_common
--force-sync-deps        força exatamente a revisão esperada
--profile safe|full      sobrescreve o profile do JSON
--regenerate-icons       compatibilidade; ícones já são padrão
--skip-icons             opt-out explícito
--skip-validate          pula o preflight final
```

### `apply_foxxdesk_icon.py`

```text
--target PATH
--source PATH
--ios-background #RRGGBB
--quality-profile best|balanced|compat
--discover-by-name / --no-discover-by-name
--create-brand-owned-assets / --no-create-brand-owned-assets
--update-ios-contents
--dry-run | --apply
--yes
```

### `apply_foxxdesk_rebrand.py`

Principais opções existentes:

```text
--target
--dry-run | --apply
--yes
--display-name
--server
--relay
--key
--maintainer-email
--homepage
--profile safe|full
--scan-all
--max-size
--remove-old-renamed
--refresh-hbb-common
--skip-hbb-common-download
--apply-icon-assets
--icon-source
--icon-ios-background
--icon-update-ios-contents
--log-file
--verbose
--quiet
```

Normalmente você **não precisa chamar esse script diretamente**. `foxxdesk_prepare.py` lê o JSON e o chama na ordem segura.

### `foxxdesk_validate.py`

```bash
python scripts/foxxdesk_validate.py --target .
```

Falha antes da build se detectar, entre outros:

- configuração inválida;
- ícone mestre ausente/pequeno;
- brand principal não aplicado;
- server/relay/key não aplicados;
- incompatibilidade de API em `hbb_common`;
- helper Python corrompido;
- hooks do GitHub Actions ausentes.

---

## 9. GitHub Actions

Workflow principal:

```text
.github/workflows/foxxdesk-build.yml
```

Comportamento:

- `push`/PR: executa preflight;
- `workflow_dispatch`: executa preflight e depois chama a matriz Flutter reutilizável;
- o composite action instala Pillow somente se necessário;
- executa `foxxdesk_prepare.py --ci`;
- `hbb_common` é sincronizado antes do rebrand;
- o ícone mestre é reaplicado automaticamente;
- os hooks FoxxDesk são reafirmados.

Para compilar manualmente:

1. abra **Actions**;
2. escolha **FoxxDesk Build**;
3. clique **Run workflow**;
4. escolha `upload_artifact` e `upload_tag`;
5. acompanhe o preflight antes da matriz completa.

O workflow completo mantém a matriz upstream por segurança. As opções do `build.py` no JSON controlam principalmente o wrapper local; mudar flags de todas as arquiteturas do workflow deve ser feito somente quando testado, para não quebrar uma plataforma ao tentar otimizar outra.

---

## 10. Dicas de qualidade e segurança

1. Mantenha `.foxxdesk/assets/icon.png` com 2048×2048 ou mais e transparência correta.
2. Não use JPEG como master do ícone.
3. Não use `scan_all=true` como padrão.
4. Não altere `brand.slug` sem necessidade.
5. Não faça download de `hbb_common/main` para uma release específica.
6. Execute `--dry-run` quando trocar de uma versão grande do RustDesk para outra.
7. Depois de aplicar, rode o prepare uma segunda vez; o resultado ideal é `0` mudanças.
8. Faça `git diff` antes de commit e confirme que alterações grandes são esperadas.
9. Mantenha os backups `.rebrand_backup` e `.icon_asset_backup` fora dos commits se forem apenas locais.
10. Se um update mudar a localização de um ícone, a descoberta por nome tenta encontrar a nova localização dentro do escopo permitido sem recriar caminhos antigos.

---

## 11. Exemplo de personalização segura

```json
{
  "brand": {
    "display_name": "Minha Assistência Remota",
    "slug": "foxxdesk",
    "maintainer_email": "dev@empresa.com",
    "homepage": "https://remote.empresa.com"
  },
  "network": {
    "server": "remote.empresa.com",
    "relay": "remote.empresa.com",
    "key": "SUA_CHAVE_PUBLICA_HBBS"
  },
  "icons": {
    "source": ".foxxdesk/assets/icon.png",
    "quality_profile": "best",
    "apply_on_prepare": true,
    "discover_by_name": true
  }
}
```

O nome público muda, mas o slug interno continua `foxxdesk`. Essa separação é intencional para reduzir regressões.

---

## 12. Comandos rápidos

```bash
# Validar JSON
python scripts/foxxdesk_config.py --target . --sync-legacy

# Simular atualização
python scripts/foxxdesk_prepare.py --target . --dry-run

# Aplicar atualização + dependência compatível
python scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps

# Regerar somente ícones
python scripts/apply_foxxdesk_icon.py --target . --apply --yes

# Preflight
python scripts/foxxdesk_validate.py --target .

# Ver build local sem executar
python scripts/foxxdesk_build.py --target . --dry-run

# Build local seguindo o JSON
python scripts/foxxdesk_build.py --target . --prepare
```
