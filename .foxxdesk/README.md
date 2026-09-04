# FoxxDesk overlay persistente

Esta pasta é a fonte de verdade do custom build e **não deve ser substituída** ao copiar uma nova versão do RustDesk para o projeto.

- `brand.json`: nome, slug, servidor, relay, chave pública e revisão compatível de `hbb_common`.
- `assets/icon.png`: ícone mestre FoxxDesk.
- `icon-overlay/`: cópias dos assets já gerados para que o GitHub Actions restaure os ícones sem depender de Pillow em cada job.

Fluxo recomendado depois de copiar uma atualização do upstream:

```bash
python scripts/foxxdesk_prepare.py --apply --yes --sync-deps --regenerate-icons
python scripts/foxxdesk_validate.py
```

No GitHub Actions, `foxxdesk_prepare.py --ci` sincroniza `hbb_common` com a revisão correta da versão, reaplica o brand, restaura os ícones e valida os hooks dos workflows antes de compilar.
