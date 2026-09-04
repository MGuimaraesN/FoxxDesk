# FoxxDesk — pacote de scripts e documentação

Este ZIP contém a camada de resiliência do FoxxDesk para aplicar branding/ícones sobre atualizações upstream sem espelhar o projeto inteiro.

## Arquivos principais
- `.foxxdesk/`: configuração persistente, ícone mestre e overlay de assets.
- `scripts/foxxdesk_prepare.py`: preparação principal.
- `scripts/foxxdesk_validate.py`: preflight/validação.
- `scripts/foxxdesk_sync_hbb_common.py`: sincronização de dependência compatível.
- `scripts/foxxdesk_ci_hooks.py`: proteção dos hooks de CI.
- `scripts/apply_foxxdesk_rebrand.py`: rebrand patch-only.
- `scripts/apply_foxxdesk_icon.py`: geração de assets.
- `.github/`: workflow e action de preparação.
- `FOXXDESK_CONFIGURATION.md` e `.html`: documentação.

Edite `.foxxdesk/foxxdesk.config.json` como ponto central de configuração. Nunca coloque a chave real em repositório público; prefira GitHub Secrets no CI.
