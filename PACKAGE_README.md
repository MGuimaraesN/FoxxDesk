# FoxxDesk Resilience V7

Pacote patch-only para manter o FoxxDesk resiliente a atualizações do RustDesk.

## Aplicar

Extraia este pacote na raiz do projeto e execute:

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
```

Depois revise `git status --short`, faça commit/push e rode **manualmente** `FoxxDesk Build` no GitHub Actions.

## Regra da V7

**Local prepara; Git registra; CI valida; build compila o commit.**

- `libs/hbb_common` permanece upstream/limpo;
- defaults FoxxDesk ficam no crate principal;
- brand público obrigatório é aplicado semanticamente em Android/macOS/Windows;
- patch e validator compartilham a mesma regra de brand público;
- CI não reaplica rebrand;
- nenhum hook é inserido em workflows upstream;
- `.gitignore` e `.gitattributes` da raiz não são modificados;
- o build FoxxDesk só possui `workflow_dispatch`.

Leia `CORRECAO_DEFINITIVA_V7.md`, `FOXXDESK_UPDATE_GUIDE.md` e `FOXXDESK_CONFIGURATION.md`.


## V8 — assets obrigatórios x opcionais

O cache de ícones agora separa `files` (obrigatórios para compilar) de `optional_files` (assets de conveniência da marca). `res/FoxxDesk.png`, `res/FoxxDesk.svg` e `res/foxxdesk-banner.svg` são opcionais: podem ser gerados localmente, mas a ausência deles no checkout do GitHub não bloqueia o build. Se estiverem presentes, continuam sendo validados contra o cache. O `.gitignore` da raiz não é modificado.

Por padrão, `icons.create_brand_owned_assets=false`; ative somente se quiser gerar esses três assets extras de apresentação.

`Contents.json` do AppIcon iOS só entra no cache obrigatório quando `icons.update_ios_contents=true`; com `false`, o arquivo fica sob controle do upstream e não causa falso positivo em atualizações.
