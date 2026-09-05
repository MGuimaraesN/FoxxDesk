# Correção total FoxxDesk v2 — 2026-09-04

## Problemas corrigidos

1. `foxxdesk_prepare.py` usava `.foxxdesk/brand.json` enquanto a configuração nova estava em `foxxdesk.config.json`.
2. GitHub Actions falhava se `.foxxdesk/assets/icon.png` não estivesse no checkout.
3. O rebrand podia sobrescrever o gerador de ícones novo com uma versão antiga embutida.
4. Ícones dependiam demais de overlay pré-gerado em vez da fonte mestre.
5. `full` era amplo demais como padrão de update.
6. Arquivos upstream renomeados eram removidos de forma mais ampla que o necessário.
7. O log do rebrand mostrava `Icon assets: False` mesmo quando o prepare tratava ícones externamente.
8. O sincronizador/validator ainda apontavam para o JSON legado.

## Solução

- Config única: `.foxxdesk/foxxdesk.config.json`.
- `brand.json` legado não é mais necessário.
- Perfil padrão `runtime`; `full` apenas em `--bootstrap`.
- Master icon persistente + `icon-state.json` com SHA-256.
- Fallback do ícone só é aceito quando o hash bate; evita usar logo upstream errado.
- Pillow é instalado pelo composite action do GitHub.
- Assets são regenerados do master e comparados antes de gravar; segundo passe fica idempotente.
- O rebrand não sobrescreve mais `apply_foxxdesk_icon.py` se ele já existe.
- Cleanup automático de renomeados ficou restrito ao conflito comprovado do WiX (`RustDesk.wxs`).
- `.gitignore` possui exceções explícitas para master/state/overlay.

## Testes executados

- `python3 -m py_compile scripts/*.py`: OK.
- JSON/config/schema/state/manifest: OK.
- YAML dos workflows/actions: OK.
- `.gitignore` permite versionar `.foxxdesk/assets/icon.png`: OK.
- Simulação de master icon ausente com fallback correto por SHA-256: OK.
- Geração de 53 assets: 0 erros.
- Segundo prepare sobre a mesma árvore: rebrand 0 / ícones 0.
- `hbb_common` não foi baixado neste ambiente final porque o sandbox não resolve `github.com`; o sincronizador continua pinado à revisão correta e já funcionou no ambiente do usuário.
