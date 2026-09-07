# FoxxDesk Rebrand V11

Pacote autocontido da camada de rebrand. Não contém snapshots do projeto upstream.

## Arquivo principal de configuração

Edite `.foxxdesk/foxxdesk.config.json`.

Principais campos:

- `brand.display_name`: nome público.
- `brand.company`: empresa/créditos.
- `brand.maintainer_email`: e-mail do mantenedor.
- `network.server`: servidor hbbs.
- `network.relay`: relay.
- `network.key`: chave pública.
- `upstream.rustdesk_ref`: `auto` é recomendado.
- `upstream.hbb_common_policy`: deve ser `exact-version`.
- `upstream.force_refresh_each_prepare`: `true` força fetch/checkout do commit exato a cada rebrand local.
- `upstream.persist_resolved_pin`: grava automaticamente o SHA descoberto para versões novas.
- `upstream.allow_main_fallback`: deve permanecer `false`.

## Como o hbb_common é escolhido

1. Detecta `version` no `[package]` do `Cargo.toml` do RustDesk.
2. Se existir pin para essa versão, usa exatamente o SHA pinado.
3. Se for uma versão nova, consulta o gitlink `libs/hbb_common` da mesma versão/tag RustDesk (`X.Y.Z` / `vX.Y.Z`).
4. Grava o SHA resolvido em `upstream.hbb_common_pins`.
5. Faz fetch/checkout exato desse SHA.
6. Nunca usa `hbb_common/main`, `master` ou `latest`.

## Comando recomendado

```bash
python3 scripts/foxxdesk_rebrand.py --target . --apply --yes
```

Como `force_refresh_each_prepare=true` por padrão neste pacote, o comando sempre faz fetch/checkout do hbb_common exato antes do rebrand.

Para apenas validar/simular:

```bash
python3 scripts/foxxdesk_rebrand.py --target . --dry-run
```

Para não refazer o fetch quando o commit já está correto, apenas nesta execução:

```bash
python3 scripts/foxxdesk_rebrand.py --target . --apply --yes --no-force-hbb-refresh
```

## Segurança

- `libs/hbb_common` é preservado do rebrand e fica upstream.
- defaults FoxxDesk de servidor/relay/key ficam no crate principal via `foxxdesk_runtime_defaults.py`.
- patches são pontuais; não há cópia de arquivos upstream inteiros.
- `.gitignore` e `.gitattributes` não fazem parte deste pacote.
