# FoxxDesk Resilience V6 — correção definitiva submodule-safe

## O que foi corrigido

A V6 elimina três acoplamentos que ainda podiam quebrar o FoxxDesk em um checkout limpo ou em uma atualização futura do RustDesk:

1. **Nenhum branding é gravado dentro de `libs/hbb_common`.**
   `hbb_common` é um submódulo Git e agora permanece exatamente na revisão upstream compatível.
2. **Nenhum hook FoxxDesk é injetado em `flutter-build.yml`, `bridge.yml` ou outros workflows upstream.**
   Mudanças na quantidade/posição de `actions/checkout` não quebram mais o preflight.
3. **O GitHub Actions é somente leitura.**
   Ele não rebrandiza, não instala Pillow, não sincroniza arquivos e não altera o checkout. Ele valida o commit preparado e compila.

O workflow `FoxxDesk Build` continua exclusivamente manual por `workflow_dispatch`.

## Fluxo recomendado

Depois de colocar uma nova versão do RustDesk sobre o projeto:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
```

Revise:

```bash
git status --short
git diff -- .gitignore .gitattributes
```

O segundo comando não deve mostrar alterações causadas pelo FoxxDesk.

Faça commit/push de tudo que o prepare gerou, inclusive uma possível mudança do gitlink `libs/hbb_common`:

```bash
git add -A
git commit -m "chore: prepare FoxxDesk update"
git push
```

Depois inicie manualmente:

`GitHub > Actions > FoxxDesk Build > Run workflow`

## Runtime defaults fora do submódulo

Os defaults FoxxDesk agora são gerados em:

`src/foxxdesk_defaults.rs`

O helper `scripts/foxxdesk_runtime_defaults.py` aplica patches mínimos no crate principal para:

- nome runtime do aplicativo;
- rendezvous server padrão;
- relay server padrão;
- public key padrão.

Os pontos atuais são `src/lib.rs`, `src/common.rs`, `src/client.rs` e `src/rendezvous_mediator.rs`.

Se uma versão futura mudar materialmente um desses anchors, o prepare falha com uma mensagem específica em vez de aplicar substituição cega.

## hbb_common

Para RustDesk 1.4.9 o pin conhecido é:

`7e1c392c62d39c364127307cd408421dd5f8cfb0`

Para uma versão nova, o sincronizador tenta resolver o gitlink de `libs/hbb_common` da **mesma versão/ref do RustDesk** e persiste o SHA no JSON. Ele nunca usa `hbb_common/main` isoladamente.

Quando `hbb_common` é um submódulo real:

- alterações FoxxDesk legadas conhecidas são removidas automaticamente;
- alterações locais desconhecidas **não são descartadas**: o prepare falha e pede revisão;
- `--force-sync-deps` existe apenas para um reparo explícito em que você deseja descartar alterações locais.

No Windows, qualquer staging fallback é criado ao lado de `libs/hbb_common`, no mesmo volume do workspace, evitando `WinError 17` e rollback quebrado entre `C:` e `D:`.

## GitHub Actions

O composite action `.github/actions/prepare-foxxdesk/action.yml` agora executa somente:

```bash
python scripts/foxxdesk_validate.py --target . --ci
```

Ele não:

- roda `foxxdesk_prepare.py --apply`;
- instala Pillow;
- altera workflows;
- baixa/regrava assets;
- troca `hbb_common` dentro do runner.

O objetivo é garantir que todos os jobs compilem exatamente os mesmos bytes que foram preparados e commitados.

## Ícones

A fonte oficial continua:

`.foxxdesk/assets/icon.png`

Localmente o prepare gera/confere os 53 assets e atualiza o cache determinístico em `.foxxdesk/icon-overlay/`.

No CI, o cache e os assets são apenas conferidos por SHA-256/bytes. Não existe renderização diferente por runner.

O FoxxDesk não modifica o `.gitignore` da raiz. A própria pasta `.foxxdesk` contém seu `.gitignore` local para permitir o versionamento dos assets FoxxDesk.

## Perfis

- `runtime` — padrão; rebrand necessário ao produto/build sem varrer documentação inteira.
- `safe` — superfície ainda menor para diagnóstico.
- `full` — primeira conversão/auditoria intencional; não é o padrão de atualização.

Mesmo no `full`, `hbb_common` é preservado quando o fluxo é iniciado por `foxxdesk_prepare.py`.

## Idempotência esperada

Em uma árvore já preparada, repetir:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
```

deve resultar essencialmente em:

- rebrand: 0 alterações;
- runtime defaults: 0 alterações;
- ícones: 0 alterações / 53 já corretos;
- hbb_common: revisão correta e worktree limpa;
- pendências: 0.

## Princípio de segurança

A V6 prefere **parar cedo** quando o upstream mudou de forma não reconhecida. Ela não tenta “consertar” silenciosamente uma versão nova substituindo arquivos completos antigos. Isso mantém o projeto próximo do RustDesk upstream e torna cada atualização auditável.
