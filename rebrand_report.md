# Relatório de rebrand FoxxDesk

- Data/hora: `2026-09-04 22:31:07`
- Modo: `apply`
- Projeto alvo: `/home/mateus/_Projects/FoxxDesk`
- Script: `apply_foxxdesk_rebrand_all_files_no_zip_v27.py`
- Versão do script: `v39-submodule-safe-runtime-defaults-2026-09-05`
- Payload/ZIP/manifesto externo: `não`
- Espelhamento/substituição de arquivo inteiro por referência antiga: `não`
- Perfil: `runtime`
- Estratégia: `patch-only; não espelha arquivos inteiros; full = TODOS os arquivos da allowlist + proteção de upstream + fixes Flutter Windows/bridge + portable packer path guard v17 + chmod executável completo + MSI duplicate guard v18 + embedded server/relay/key defaults ocultos + artefatos limpos v20 + ajustes seguros de driver/impressora v21 + AppData Local FoxxDesk e limpeza final de driver v22 + V26 cleanup definitivo do flutter-build.yml`
- Observação: se aparecerem apenas ~13 arquivos, você provavelmente executou a v9 safe ou usou --profile safe.

## Valores dinâmicos

- server: `foxxdesk.mguimaraesn.dev`
- relay: `foxxdesk.mguimaraesn.dev`
- key: `<key ocultada; len=44; sha256=a58bc137d7>`
- maintainer-email: `mateus@mguimaraesn.dev`
- homepage: `https://foxxdesk.mguimaraesn.dev`

## Resumo

- Arquivos permitidos na allowlist: `267`
- Arquivos analisados: `211`
- Arquivos alterados: `64`
- Arquivos já aplicados/sem mudança: `153`
- Arquivos esperados não encontrados: `0`
- Arquivos ignorados: `5`
- Renomeações/cópias criadas: `8`
- Pendências: `0`
- Backup: `/home/mateus/_Projects/FoxxDesk/.rebrand_backup/20260904_223107`
- Log detalhado: `/home/mateus/_Projects/FoxxDesk/rebrand_v39.log`

## Arquivos alterados

- `.github/workflows/bridge.yml`
- `.github/workflows/flutter-build.yml`
- `.github/workflows/foxxdesk-build.yml`
- `.github/workflows/playground.yml`
- `Cargo.lock`
- `Cargo.toml`
- `appimage/AppImageBuilder-aarch64.yml`
- `appimage/AppImageBuilder-x86_64.yml`
- `build.py`
- `entrypoint.sh`
- `flatpak/foxxdesk.json`
- `flutter/build_android.sh`
- `flutter/build_android_deps.sh`
- `flutter/build_fdroid.sh`
- `flutter/build_ios.sh`
- `flutter/ios_arm64.sh`
- `flutter/ios_x64.sh`
- `flutter/lib/common.dart`
- `flutter/lib/common/widgets/dialog.dart`
- `flutter/lib/common/widgets/toolbar.dart`
- `flutter/lib/desktop/pages/desktop_setting_page.dart`
- `flutter/lib/desktop/widgets/remote_toolbar.dart`
- `flutter/macos/Runner/Configs/AppInfo.xcconfig`
- `flutter/ndk_arm.sh`
- `flutter/ndk_arm64.sh`
- `flutter/ndk_x64.sh`
- `flutter/ndk_x86.sh`
- `flutter/run.sh`
- `flutter/windows/runner/Runner.rc`
- `flutter/windows/runner/runner.exe.manifest`
- `libs/portable/Cargo.lock`
- `libs/portable/Cargo.toml`
- `libs/portable/generate.py`
- `libs/portable/src/main.rs`
- `libs/remote_printer/src/lib.rs`
- `libs/remote_printer/src/setup/driver.rs`
- `res/DEBIAN/postinst`
- `res/DEBIAN/postrm`
- `res/DEBIAN/preinst`
- `res/DEBIAN/prerm`
- `res/PKGBUILD`
- `res/job.py`
- `res/manifest.xml`
- `res/msi/CustomActions/CustomActions.cpp`
- `res/msi/CustomActions/RemotePrinter.cpp`
- `res/msi/Package/Components/FoxxDesk.wxs`
- `res/msi/Package/Components/RustDesk.wxs`
- `res/msi/Package/Language/Package.en-us.wxl`
- `res/msi/preprocess.py`
- `res/osx-dist.sh`
- `res/pacman_install`
- `res/rpm-flutter-suse.spec`
- `res/rpm-flutter.spec`
- `res/rpm-suse.spec`
- `res/rpm.spec`
- `scripts/apply_foxxdesk_icon.py`
- `scripts/fix_foxxdesk_windows_flutter_build.py`
- `scripts/fix_generated_bridge_compat.py`
- `src/common.rs`
- `src/core_main.rs`
- `src/flutter_ffi.rs`
- `src/platform/windows.rs`
- `src/privacy_mode/win_topmost_window.rs`
- `src/server/connection.rs`

## Arquivos renomeados/copiados

- `flatpak/com.rustdesk.RustDesk.metainfo.xml -> flatpak/com.foxxdesk.client.metainfo.xml`
- `flatpak/rustdesk.json -> flatpak/foxxdesk.json`
- `res/msi/Package/Components/RustDesk.wxs -> res/msi/Package/Components/FoxxDesk.wxs`
- `res/pam.d/rustdesk.debian -> res/pam.d/foxxdesk.debian`
- `res/pam.d/rustdesk.suse -> res/pam.d/foxxdesk.suse`
- `res/rustdesk-link.desktop -> res/foxxdesk-link.desktop`
- `res/rustdesk.desktop -> res/foxxdesk.desktop`
- `res/rustdesk.service -> res/foxxdesk.service`

## Arquivos esperados que não foram encontrados

Nenhum.

## Arquivos ignorados

- `libs/hbb_common/src/config.rs (submódulo upstream preservado; defaults FoxxDesk ficam no crate principal)`
- `scripts/apply_foxxdesk_brand.py (opcional ausente)`
- `scripts/apply_foxxdesk_brand_DEFINITIVE.py (opcional ausente)`
- `scripts/apply_foxxdesk_brand_SAFE.py (opcional ausente)`
- `scripts/apply_foxxdesk_brand_with_fixes.py (opcional ausente)`

## Alterações

| Status | Arquivo | Linha | Ação | Mensagem |
|---|---|---:|---|---|
| alterado | `.github/workflows/foxxdesk-build.yml` | 4 | garantir workflow FoxxDesk manual-only | arquivo gerado pela V25; sem payload/ZIP e sem snapshot de projeto antigo |
| criado | `scripts/fix_generated_bridge_compat.py` | 1 | criar/atualizar helper de compatibilidade flutter_rust_bridge | arquivo gerado pela V25; sem payload/ZIP e sem snapshot de projeto antigo |
| criado | `scripts/fix_foxxdesk_windows_flutter_build.py` | 1 | criar/atualizar fixer FoxxDesk Windows Flutter build | arquivo gerado pela V25; sem payload/ZIP e sem snapshot de projeto antigo |
| criado | `flatpak/com.foxxdesk.client.metainfo.xml` | 1 | copiar arquivo renomeado | origem: flatpak/com.rustdesk.RustDesk.metainfo.xml |
| criado | `flatpak/foxxdesk.json` | 1 | copiar arquivo renomeado | origem: flatpak/rustdesk.json |
| criado | `res/foxxdesk-link.desktop` | 1 | copiar arquivo renomeado | origem: res/rustdesk-link.desktop |
| criado | `res/foxxdesk.desktop` | 1 | copiar arquivo renomeado | origem: res/rustdesk.desktop |
| criado | `res/foxxdesk.service` | 1 | copiar arquivo renomeado | origem: res/rustdesk.service |
| criado | `res/pam.d/foxxdesk.debian` | 1 | copiar arquivo renomeado | origem: res/pam.d/rustdesk.debian |
| criado | `res/pam.d/foxxdesk.suse` | 1 | copiar arquivo renomeado | origem: res/pam.d/rustdesk.suse |
| criado | `res/msi/Package/Components/FoxxDesk.wxs` | 1 | copiar arquivo renomeado | origem: res/msi/Package/Components/RustDesk.wxs |
| removido | `res/msi/Package/Components/RustDesk.wxs` | 1 | remover arquivo antigo substituído pelo novo brand | res/msi/Package/Components/RustDesk.wxs foi substituído por res/msi/Package/Components/FoxxDesk.wxs; evita build duplicado/branding misto |
| alterado | `.github/workflows/bridge.yml` | 89 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `.github/workflows/flutter-build.yml` | 259 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `.github/workflows/playground.yml` | 151 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `Cargo.lock` | 7251 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `Cargo.toml` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `appimage/AppImageBuilder-aarch64.yml` | 13 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `appimage/AppImageBuilder-x86_64.yml` | 13 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `build.py` | 27 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flatpak/foxxdesk.json` | 8 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/common.dart` | 1806 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/common/widgets/dialog.dart` | 1369 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/common/widgets/toolbar.dart` | 800 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/desktop/pages/desktop_setting_page.dart` | 1822 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/desktop/widgets/remote_toolbar.dart` | 282 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/macos/Runner/Configs/AppInfo.xcconfig` | 14 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/windows/runner/Runner.rc` | 92 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/windows/runner/runner.exe.manifest` | 20 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/portable/Cargo.lock` | 163 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/portable/Cargo.toml` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/portable/generate.py` | 103 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/portable/src/main.rs` | 20 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/remote_printer/src/lib.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/remote_printer/src/setup/driver.rs` | 84 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/DEBIAN/postinst` | 8 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/DEBIAN/prerm` | 14 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/PKGBUILD` | 29 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/job.py` | 208 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/manifest.xml` | 36 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/msi/CustomActions/CustomActions.cpp` | 209 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/msi/CustomActions/RemotePrinter.cpp` | 21 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/msi/Package/Components/FoxxDesk.wxs` | 25 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/msi/Package/Language/Package.en-us.wxl` | 54 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/msi/preprocess.py` | 199 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/osx-dist.sh` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/pacman_install` | 8 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/rpm-flutter-suse.spec` | 7 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/rpm-flutter.spec` | 7 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/rpm-suse.spec` | 24 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/rpm.spec` | 7 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/common.rs` | 2204 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/core_main.rs` | 144 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/flutter_ffi.rs` | 2817 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/windows.rs` | 1231 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/privacy_mode/win_topmost_window.rs` | 33 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/server/connection.rs` | 5701 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| chmod +x | `build.py` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `entrypoint.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `flutter/build_android.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `flutter/build_android_deps.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `flutter/build_fdroid.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `flutter/build_ios.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `flutter/ios_arm64.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `flutter/ios_x64.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `flutter/ndk_arm.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `flutter/ndk_arm64.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `flutter/ndk_x64.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `flutter/ndk_x86.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `flutter/run.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `res/DEBIAN/postinst` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `res/DEBIAN/postrm` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `res/DEBIAN/preinst` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `res/DEBIAN/prerm` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `res/osx-dist.sh` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `scripts/apply_foxxdesk_icon.py` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `scripts/fix_foxxdesk_windows_flutter_build.py` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `scripts/fix_generated_bridge_compat.py` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |

## Pendências

Nenhuma.
