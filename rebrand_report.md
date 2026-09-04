# Relatório de rebrand FoxxDesk

- Data/hora: `2026-09-04 20:31:23`
- Modo: `apply`
- Projeto alvo: `/home/mateus/_Projects/FoxxDesk`
- Script: `apply_foxxdesk_rebrand_all_files_no_zip_v27.py`
- Versão do script: `v35-resilient-upstream-ci-2026-09-04`
- Payload/ZIP/manifesto externo: `não`
- Espelhamento/substituição de arquivo inteiro por referência antiga: `não`
- Perfil: `full`
- Estratégia: `patch-only; não espelha arquivos inteiros; full = TODOS os arquivos da allowlist + proteção de upstream + fixes Flutter Windows/bridge + portable packer path guard v17 + chmod executável completo + MSI duplicate guard v18 + embedded server/relay/key defaults ocultos + artefatos limpos v20 + ajustes seguros de driver/impressora v21 + AppData Local FoxxDesk e limpeza final de driver v22 + V26 cleanup definitivo do flutter-build.yml`
- Observação: se aparecerem apenas ~13 arquivos, você provavelmente executou a v9 safe ou usou --profile safe.

## Valores dinâmicos

- server: `foxxdesk.mguimaraesn.dev`
- relay: `foxxdesk.mguimaraesn.dev`
- key: `<key ocultada; len=44; sha256=a58bc137d7>`
- maintainer-email: `(não informado)`
- homepage: `https://foxxdesk.mguimaraesn.dev`

## Resumo

- Arquivos permitidos na allowlist: `269`
- Arquivos analisados: `287`
- Arquivos alterados: `245`
- Arquivos já aplicados/sem mudança: `37`
- Arquivos esperados não encontrados: `0`
- Arquivos ignorados: `9`
- Renomeações/cópias criadas: `8`
- Pendências: `0`
- Backup: `/home/mateus/_Projects/FoxxDesk/.rebrand_backup/20260904_203121`
- Log detalhado: `/home/mateus/_Projects/FoxxDesk/rebrand_v35.log`

## Arquivos alterados

- `.github/FUNDING.yml`
- `.github/ISSUE_TEMPLATE/bug_report.yaml`
- `.github/workflows/playground.yml`
- `.gitignore`
- `AGENTS.md`
- `Cargo.lock`
- `Cargo.toml`
- `Dockerfile`
- `README.md`
- `appimage/AppImageBuilder-aarch64.yml`
- `appimage/AppImageBuilder-x86_64.yml`
- `build.py`
- `docs/CONTRIBUTING-DE.md`
- `docs/CONTRIBUTING-FR.md`
- `docs/CONTRIBUTING-ID.md`
- `docs/CONTRIBUTING-IT.md`
- `docs/CONTRIBUTING-JP.md`
- `docs/CONTRIBUTING-KR.md`
- `docs/CONTRIBUTING-NL.md`
- `docs/CONTRIBUTING-NO.md`
- `docs/CONTRIBUTING-PL.md`
- `docs/CONTRIBUTING-RO.md`
- `docs/CONTRIBUTING-RU.md`
- `docs/CONTRIBUTING-TR.md`
- `docs/CONTRIBUTING-ZH.md`
- `docs/CONTRIBUTING.md`
- `docs/README-AR.md`
- `docs/README-CS.md`
- `docs/README-DA.md`
- `docs/README-DE.md`
- `docs/README-EO.md`
- `docs/README-ES.md`
- `docs/README-FA.md`
- `docs/README-FI.md`
- `docs/README-FR.md`
- `docs/README-GR.md`
- `docs/README-HU.md`
- `docs/README-ID.md`
- `docs/README-IT.md`
- `docs/README-JP.md`
- `docs/README-KR.md`
- `docs/README-ML.md`
- `docs/README-NL.md`
- `docs/README-NO.md`
- `docs/README-PL.md`
- `docs/README-PTBR.md`
- `docs/README-RO.md`
- `docs/README-RU.md`
- `docs/README-TR.md`
- `docs/README-UA.md`
- `docs/README-VN.md`
- `docs/README-ZH.md`
- `docs/SECURITY-DE.md`
- `docs/SECURITY-FR.md`
- `docs/SECURITY-IT.md`
- `docs/SECURITY-JP.md`
- `docs/SECURITY-KR.md`
- `docs/SECURITY-NL.md`
- `docs/SECURITY-NO.md`
- `docs/SECURITY-PL.md`
- `docs/SECURITY-RO.md`
- `docs/SECURITY-TR.md`
- `docs/SECURITY.md`
- `entrypoint.sh`
- `fastlane/metadata/android/en-US/full_description.txt`
- `fastlane/metadata/android/fr-FR/full_description.txt`
- `fastlane/metadata/android/nl-NL/full_description.txt`
- `fastlane/metadata/android/zh-CN/full_description.txt`
- `flatpak/com.foxxdesk.client.metainfo.xml`
- `flatpak/com.rustdesk.RustDesk.metainfo.xml`
- `flatpak/foxxdesk.json`
- `flatpak/rustdesk.json`
- `flutter/.gitignore`
- `flutter/android/app/src/main/AndroidManifest.xml`
- `flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/BootReceiver.kt`
- `flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/FloatingWindowService.kt`
- `flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/MainService.kt`
- `flutter/android/app/src/main/res/values/strings.xml`
- `flutter/build_android.sh`
- `flutter/build_android_deps.sh`
- `flutter/build_fdroid.sh`
- `flutter/build_ios.sh`
- `flutter/ios/Runner/GoogleService-Info.plist`
- `flutter/ios/Runner/Info.plist`
- `flutter/ios/exportOptions.plist`
- `flutter/ios_arm64.sh`
- `flutter/ios_x64.sh`
- `flutter/lib/common.dart`
- `flutter/lib/common/widgets/dialog.dart`
- `flutter/lib/common/widgets/login.dart`
- `flutter/lib/common/widgets/toolbar.dart`
- `flutter/lib/desktop/pages/desktop_setting_page.dart`
- `flutter/lib/desktop/widgets/remote_toolbar.dart`
- `flutter/lib/mobile/pages/settings_page.dart`
- `flutter/lib/plugin/manager.dart`
- `flutter/lib/plugin/widgets/desc_ui.dart`
- `flutter/lib/utils/platform_channel.dart`
- `flutter/linux/CMakeLists.txt`
- `flutter/linux/my_application.cc`
- `flutter/macos/Runner.xcodeproj/project.pbxproj`
- `flutter/macos/Runner.xcodeproj/xcshareddata/xcschemes/Runner.xcscheme`
- `flutter/macos/Runner/Base.lproj/MainMenu.xib`
- `flutter/macos/Runner/Configs/AppInfo.xcconfig`
- `flutter/macos/Runner/Info.plist`
- `flutter/macos/Runner/MainFlutterWindow.swift`
- `flutter/ndk_arm.sh`
- `flutter/ndk_arm64.sh`
- `flutter/ndk_x64.sh`
- `flutter/ndk_x86.sh`
- `flutter/run.sh`
- `flutter/windows/CMakeLists.txt`
- `flutter/windows/runner/Runner.rc`
- `flutter/windows/runner/main.cpp`
- `flutter/windows/runner/runner.exe.manifest`
- `libs/clipboard/README.md`
- `libs/clipboard/src/lib.rs`
- `libs/clipboard/src/platform/unix/fuse/mod.rs`
- `libs/enigo/src/linux/xdo.rs`
- `libs/hbb_common/src/config.rs`
- `libs/hbb_common/src/platform/linux.rs`
- `libs/hbb_common/src/platform/mod.rs`
- `libs/portable/Cargo.lock`
- `libs/portable/Cargo.toml`
- `libs/portable/generate.py`
- `libs/portable/src/bin_reader.rs`
- `libs/portable/src/main.rs`
- `libs/remote_printer/src/lib.rs`
- `libs/remote_printer/src/setup/driver.rs`
- `libs/virtual_display/dylib/src/lib.rs`
- `libs/virtual_display/dylib/src/win10/IddController.c`
- `res/DEBIAN/postinst`
- `res/DEBIAN/postrm`
- `res/DEBIAN/preinst`
- `res/DEBIAN/prerm`
- `res/PKGBUILD`
- `res/foxxdesk-link.desktop`
- `res/foxxdesk.desktop`
- `res/foxxdesk.service`
- `res/job.py`
- `res/manifest.xml`
- `res/msi/CustomActions/CustomActions.cpp`
- `res/msi/CustomActions/RemotePrinter.cpp`
- `res/msi/Package/Components/FoxxDesk.wxs`
- `res/msi/Package/Components/RustDesk.wxs`
- `res/msi/Package/Language/Package.en-us.wxl`
- `res/msi/Package/Language/WixExt_en-us.wxl`
- `res/msi/README.md`
- `res/msi/preprocess.py`
- `res/osx-dist.sh`
- `res/pacman_install`
- `res/pam.d/rustdesk.debian`
- `res/pam.d/rustdesk.suse`
- `res/rpm-flutter-suse.spec`
- `res/rpm-flutter.spec`
- `res/rpm-suse.spec`
- `res/rpm.spec`
- `res/rustdesk-link.desktop`
- `res/rustdesk.desktop`
- `res/rustdesk.service`
- `scripts/apply_foxxdesk_icon.py`
- `scripts/fix_foxxdesk_windows_flutter_build.py`
- `scripts/fix_generated_bridge_compat.py`
- `src/clipboard.rs`
- `src/common.rs`
- `src/core_main.rs`
- `src/custom_server.rs`
- `src/flutter.rs`
- `src/flutter_ffi.rs`
- `src/hbbs_http/account.rs`
- `src/ipc.rs`
- `src/ipc/auth.rs`
- `src/ipc/fs.rs`
- `src/lang.rs`
- `src/lang/ar.rs`
- `src/lang/be.rs`
- `src/lang/bg.rs`
- `src/lang/ca.rs`
- `src/lang/cn.rs`
- `src/lang/cs.rs`
- `src/lang/da.rs`
- `src/lang/de.rs`
- `src/lang/el.rs`
- `src/lang/en.rs`
- `src/lang/eo.rs`
- `src/lang/es.rs`
- `src/lang/et.rs`
- `src/lang/eu.rs`
- `src/lang/fa.rs`
- `src/lang/fi.rs`
- `src/lang/fr.rs`
- `src/lang/ge.rs`
- `src/lang/he.rs`
- `src/lang/hi.rs`
- `src/lang/hr.rs`
- `src/lang/hu.rs`
- `src/lang/id.rs`
- `src/lang/it.rs`
- `src/lang/ja.rs`
- `src/lang/ko.rs`
- `src/lang/kz.rs`
- `src/lang/lt.rs`
- `src/lang/lv.rs`
- `src/lang/nb.rs`
- `src/lang/nl.rs`
- `src/lang/pl.rs`
- `src/lang/pt_PT.rs`
- `src/lang/ptbr.rs`
- `src/lang/ro.rs`
- `src/lang/ru.rs`
- `src/lang/sc.rs`
- `src/lang/sk.rs`
- `src/lang/sl.rs`
- `src/lang/sq.rs`
- `src/lang/sr.rs`
- `src/lang/sv.rs`
- `src/lang/ta.rs`
- `src/lang/th.rs`
- `src/lang/tr.rs`
- `src/lang/tw.rs`
- `src/lang/uk.rs`
- `src/naming.rs`
- `src/platform/delegate.rs`
- `src/platform/gtk_sudo.rs`
- `src/platform/linux.rs`
- `src/platform/linux_desktop_manager.rs`
- `src/platform/macos.rs`
- `src/platform/privileges_scripts/agent.plist`
- `src/platform/privileges_scripts/daemon.plist`
- `src/platform/privileges_scripts/install.scpt`
- `src/platform/privileges_scripts/uninstall.scpt`
- `src/platform/privileges_scripts/update.scpt`
- `src/platform/windows.rs`
- `src/platform/windows_delete_test_cert.cc`
- `src/plugin/callback_msg.rs`
- `src/plugin/errno.rs`
- `src/plugin/manager.rs`
- `src/privacy_mode/win_topmost_window.rs`
- `src/rendezvous_mediator.rs`
- `src/server/clipboard_service.rs`
- `src/server/connection.rs`
- `src/server/dbus.rs`
- `src/server/input_service.rs`
- `src/ui/index.tis`
- `src/ui_session_interface.rs`
- `src/virtual_display_manager.rs`

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

- `BRAND_CHANGELOG.md (opcional ausente)`
- `FOXXDESK_MAX_SAFE_BRAND_REPORT.md (opcional ausente)`
- `FOXXDESK_SERVER_DEFAULTS.md (opcional ausente)`
- `NOTICE.md (opcional ausente)`
- `icon assets (flag --apply-icon-assets não informada)`
- `scripts/apply_foxxdesk_brand.py (opcional ausente)`
- `scripts/apply_foxxdesk_brand_DEFINITIVE.py (opcional ausente)`
- `scripts/apply_foxxdesk_brand_SAFE.py (opcional ausente)`
- `scripts/apply_foxxdesk_brand_with_fixes.py (opcional ausente)`

## Alterações

| Status | Arquivo | Linha | Ação | Mensagem |
|---|---|---:|---|---|
| criado | `flatpak/com.foxxdesk.client.metainfo.xml` | 1 | copiar arquivo renomeado | origem: flatpak/com.rustdesk.RustDesk.metainfo.xml |
| criado | `flatpak/foxxdesk.json` | 1 | copiar arquivo renomeado | origem: flatpak/rustdesk.json |
| criado | `res/foxxdesk-link.desktop` | 1 | copiar arquivo renomeado | origem: res/rustdesk-link.desktop |
| criado | `res/foxxdesk.desktop` | 1 | copiar arquivo renomeado | origem: res/rustdesk.desktop |
| criado | `res/foxxdesk.service` | 1 | copiar arquivo renomeado | origem: res/rustdesk.service |
| criado | `res/pam.d/foxxdesk.debian` | 1 | copiar arquivo renomeado | origem: res/pam.d/rustdesk.debian |
| criado | `res/pam.d/foxxdesk.suse` | 1 | copiar arquivo renomeado | origem: res/pam.d/rustdesk.suse |
| criado | `res/msi/Package/Components/FoxxDesk.wxs` | 1 | copiar arquivo renomeado | origem: res/msi/Package/Components/RustDesk.wxs |
| removido | `flatpak/com.rustdesk.RustDesk.metainfo.xml` | 1 | remover arquivo antigo substituído pelo novo brand | flatpak/com.rustdesk.RustDesk.metainfo.xml foi substituído por flatpak/com.foxxdesk.client.metainfo.xml; evita build duplicado/branding misto |
| removido | `flatpak/rustdesk.json` | 1 | remover arquivo antigo substituído pelo novo brand | flatpak/rustdesk.json foi substituído por flatpak/foxxdesk.json; evita build duplicado/branding misto |
| removido | `res/rustdesk-link.desktop` | 1 | remover arquivo antigo substituído pelo novo brand | res/rustdesk-link.desktop foi substituído por res/foxxdesk-link.desktop; evita build duplicado/branding misto |
| removido | `res/rustdesk.desktop` | 1 | remover arquivo antigo substituído pelo novo brand | res/rustdesk.desktop foi substituído por res/foxxdesk.desktop; evita build duplicado/branding misto |
| removido | `res/rustdesk.service` | 1 | remover arquivo antigo substituído pelo novo brand | res/rustdesk.service foi substituído por res/foxxdesk.service; evita build duplicado/branding misto |
| removido | `res/pam.d/rustdesk.debian` | 1 | remover arquivo antigo substituído pelo novo brand | res/pam.d/rustdesk.debian foi substituído por res/pam.d/foxxdesk.debian; evita build duplicado/branding misto |
| removido | `res/pam.d/rustdesk.suse` | 1 | remover arquivo antigo substituído pelo novo brand | res/pam.d/rustdesk.suse foi substituído por res/pam.d/foxxdesk.suse; evita build duplicado/branding misto |
| removido | `res/msi/Package/Components/RustDesk.wxs` | 1 | remover arquivo antigo substituído pelo novo brand | res/msi/Package/Components/RustDesk.wxs foi substituído por res/msi/Package/Components/FoxxDesk.wxs; evita build duplicado/branding misto |
| alterado | `.github/FUNDING.yml` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `.github/ISSUE_TEMPLATE/bug_report.yaml` | 38 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `.github/workflows/playground.yml` | 151 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `.gitignore` | 25 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `AGENTS.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `Cargo.lock` | 7251 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `Cargo.toml` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `Dockerfile` | 49 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `README.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `appimage/AppImageBuilder-aarch64.yml` | 5 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `appimage/AppImageBuilder-x86_64.yml` | 5 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `build.py` | 17 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-DE.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-FR.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-ID.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-IT.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-JP.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-KR.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-NL.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-NO.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-PL.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-RO.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-RU.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-TR.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING-ZH.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/CONTRIBUTING.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-AR.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-CS.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-DA.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-DE.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-EO.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-ES.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-FA.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-FI.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-FR.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-GR.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-HU.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-ID.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-IT.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-JP.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-KR.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-ML.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-NL.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-NO.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-PL.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-PTBR.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-RO.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-RU.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-TR.md` | 3 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-UA.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-VN.md` | 4 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/README-ZH.md` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/SECURITY-DE.md` | 6 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/SECURITY-FR.md` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/SECURITY-IT.md` | 7 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/SECURITY-JP.md` | 6 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/SECURITY-KR.md` | 5 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/SECURITY-NL.md` | 6 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/SECURITY-NO.md` | 6 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/SECURITY-PL.md` | 6 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/SECURITY-RO.md` | 6 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/SECURITY-TR.md` | 6 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `docs/SECURITY.md` | 6 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `entrypoint.sh` | 3 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `fastlane/metadata/android/en-US/full_description.txt` | 5 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `fastlane/metadata/android/fr-FR/full_description.txt` | 5 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `fastlane/metadata/android/nl-NL/full_description.txt` | 5 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `fastlane/metadata/android/zh-CN/full_description.txt` | 5 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flatpak/com.foxxdesk.client.metainfo.xml` | 3 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flatpak/foxxdesk.json` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/.gitignore` | 56 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/android/app/src/main/AndroidManifest.xml` | 28 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/BootReceiver.kt` | 39 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/FloatingWindowService.kt` | 306 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/MainService.kt` | 49 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/android/app/src/main/res/values/strings.xml` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/build_android_deps.sh` | 7 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/build_fdroid.sh` | 4 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/build_ios.sh` | 6 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/ios/Runner/GoogleService-Info.plist` | 18 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/ios/Runner/Info.plist` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/ios/exportOptions.plist` | 12 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/common.dart` | 1806 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/common/widgets/dialog.dart` | 1369 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/common/widgets/login.dart` | 440 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/common/widgets/toolbar.dart` | 800 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/desktop/pages/desktop_setting_page.dart` | 1822 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/desktop/widgets/remote_toolbar.dart` | 282 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/mobile/pages/settings_page.dart` | 533 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/plugin/manager.dart` | 132 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/plugin/widgets/desc_ui.dart` | 208 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/lib/utils/platform_channel.dart` | 8 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/linux/CMakeLists.txt` | 7 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/linux/my_application.cc` | 36 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/macos/Runner.xcodeproj/project.pbxproj` | 63 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/macos/Runner.xcodeproj/xcshareddata/xcschemes/Runner.xcscheme` | 18 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/macos/Runner/Base.lproj/MainMenu.xib` | 16 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/macos/Runner/Configs/AppInfo.xcconfig` | 8 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/macos/Runner/Info.plist` | 29 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/macos/Runner/MainFlutterWindow.swift` | 96 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/windows/CMakeLists.txt` | 3 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/windows/runner/Runner.rc` | 92 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/windows/runner/main.cpp` | 60 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `flutter/windows/runner/runner.exe.manifest` | 20 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/clipboard/README.md` | 142 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/clipboard/src/lib.rs` | 52 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/clipboard/src/platform/unix/fuse/mod.rs` | 128 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/enigo/src/linux/xdo.rs` | 43 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/hbb_common/src/config.rs` | 63 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/hbb_common/src/platform/linux.rs` | 31 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/hbb_common/src/platform/mod.rs` | 58 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/portable/Cargo.lock` | 163 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/portable/Cargo.toml` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/portable/generate.py` | 42 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/portable/src/bin_reader.rs` | 76 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/portable/src/main.rs` | 20 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/remote_printer/src/lib.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/remote_printer/src/setup/driver.rs` | 84 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/virtual_display/dylib/src/lib.rs` | 15 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `libs/virtual_display/dylib/src/win10/IddController.c` | 97 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/DEBIAN/postinst` | 8 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/DEBIAN/postrm` | 7 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/DEBIAN/preinst` | 9 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/DEBIAN/prerm` | 8 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/PKGBUILD` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/foxxdesk-link.desktop` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/foxxdesk.desktop` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/foxxdesk.service` | 2 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/job.py` | 208 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/manifest.xml` | 36 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/msi/CustomActions/CustomActions.cpp` | 209 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/msi/CustomActions/RemotePrinter.cpp` | 21 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/msi/Package/Components/FoxxDesk.wxs` | 25 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/msi/Package/Language/Package.en-us.wxl` | 13 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/msi/Package/Language/WixExt_en-us.wxl` | 13 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/msi/README.md` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/msi/preprocess.py` | 51 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/osx-dist.sh` | 8 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/pacman_install` | 8 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/rpm-flutter-suse.spec` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/rpm-flutter.spec` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/rpm-suse.spec` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `res/rpm.spec` | 1 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/clipboard.rs` | 17 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/common.rs` | 1009 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/core_main.rs` | 144 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/custom_server.rs` | 116 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/flutter.rs` | 102 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/flutter_ffi.rs` | 2817 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/hbbs_http/account.rs` | 40 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/ipc.rs` | 746 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/ipc/auth.rs` | 982 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/ipc/fs.rs` | 203 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang.rs` | 226 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/ar.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/be.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/bg.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/ca.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/cn.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/cs.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/da.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/de.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/el.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/en.rs` | 5 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/eo.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/es.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/et.rs` | 148 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/eu.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/fa.rs` | 148 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/fi.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/fr.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/ge.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/he.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/hi.rs` | 280 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/hr.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/hu.rs` | 148 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/id.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/it.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/ja.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/ko.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/kz.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/lt.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/lv.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/nb.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/nl.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/pl.rs` | 148 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/pt_PT.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/ptbr.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/ro.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/ru.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/sc.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/sk.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/sl.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/sq.rs` | 148 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/sr.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/sv.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/ta.rs` | 279 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/th.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/tr.rs` | 148 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/tw.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/lang/uk.rs` | 10 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/naming.rs` | 21 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/delegate.rs` | 212 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/gtk_sudo.rs` | 43 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/linux.rs` | 2066 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/linux_desktop_manager.rs` | 1129 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/macos.rs` | 121 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/privileges_scripts/agent.plist` | 9 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/privileges_scripts/daemon.plist` | 9 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/privileges_scripts/install.scpt` | 7 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/privileges_scripts/uninstall.scpt` | 6 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/privileges_scripts/update.scpt` | 5 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/windows.rs` | 1231 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/platform/windows_delete_test_cert.cc` | 290 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/plugin/callback_msg.rs` | 18 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/plugin/errno.rs` | 6 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/plugin/manager.rs` | 61 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/privacy_mode/win_topmost_window.rs` | 33 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/rendezvous_mediator.rs` | 65 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/server/clipboard_service.rs` | 289 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/server/connection.rs` | 3299 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/server/dbus.rs` | 4 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/server/input_service.rs` | 579 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/ui/index.tis` | 1562 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/ui_session_interface.rs` | 2024 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `src/virtual_display_manager.rs` | 417 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
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
