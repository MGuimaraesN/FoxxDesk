# Relatório de rebrand FoxxDesk

- Data/hora: `2026-07-06 08:54:10`
- Modo: `apply`
- Projeto alvo: `/home/mateus/_Projects/FoxxDesk`
- Script: `apply_foxxdesk_rebrand_all_files_no_zip_v27.py`
- Versão do script: `v32-macos-dmg-rename-and-linux-deb-permissions-2026-07-05`
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
- Arquivos analisados: `288`
- Arquivos alterados: `7`
- Arquivos já aplicados/sem mudança: `278`
- Arquivos esperados não encontrados: `0`
- Arquivos ignorados: `9`
- Renomeações/cópias criadas: `0`
- Pendências: `2`
- Backup: `/home/mateus/_Projects/FoxxDesk/.rebrand_backup/20260706_085408`
- Log detalhado: `/home/mateus/_Projects/FoxxDesk/rebrand_v32.log`

## Arquivos alterados

- `.github/workflows/flutter-build.yml`
- `.github/workflows/playground.yml`
- `build.py`
- `res/DEBIAN/postinst`
- `res/DEBIAN/postrm`
- `res/DEBIAN/preinst`
- `res/DEBIAN/prerm`

## Arquivos renomeados/copiados

Nenhum.

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
| alterado | `.github/workflows/flutter-build.yml` | 870 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `.github/workflows/playground.yml` | 221 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| alterado | `build.py` | 340 | aplicar regras standalone de rebrand | conteúdo textual mudou por regra segura; sem payload/ZIP |
| chmod +x | `res/DEBIAN/postinst` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `res/DEBIAN/postrm` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `res/DEBIAN/preinst` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |
| chmod +x | `res/DEBIAN/prerm` | 1 | garantir bit executável no Git/CI | marca como executável; rode git add para registrar modo 100755 |

## Pendências

- `.github/workflows/flutter-build.yml`: V31: ainda contém RustDesk.app/rustdesk.app; deve usar FoxxDesk.app
- `.github/workflows/playground.yml`: V31: ainda contém RustDesk.app/rustdesk.app; deve usar FoxxDesk.app
