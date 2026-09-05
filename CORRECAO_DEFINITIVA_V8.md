# Correção Definitiva V8 — cache de ícones sem falso positivo no CI

## Problema corrigido

O prepare local gerava `res/FoxxDesk.png`, `res/FoxxDesk.svg` e `res/foxxdesk-banner.svg` e os colocava no cache determinístico. Como esses arquivos podem ser ignorados pelo `.gitignore` upstream, eles existiam localmente mas não no checkout do GitHub. O preflight tratava a ausência como erro, embora nenhum deles seja requisito da compilação.

## Solução

- O manifesto passou para schema 3.
- `files`: somente assets obrigatórios para build.
- `optional_files`: assets extras de conveniência FoxxDesk.
- Manifests V1/V2 são compatíveis: os três paths conhecidos são reclassificados automaticamente no validator.
- Se um asset opcional estiver ausente no CI, não há erro.
- Se estiver presente, ele precisa ser byte-a-byte igual ao cache.
- `.gitignore` e `.gitattributes` continuam intocados.

## Assets opcionais

- `res/FoxxDesk.png`
- `res/FoxxDesk.svg`
- `res/foxxdesk-banner.svg`

## Assets obrigatórios

Continuam exigidos os assets efetivamente usados por Windows, macOS, Linux, Android, iOS, Flutter e Fastlane presentes no `files` do manifesto.

Por padrão, `icons.create_brand_owned_assets=false`; ative somente se quiser gerar esses três assets extras de apresentação.

`Contents.json` do AppIcon iOS só entra no cache obrigatório quando `icons.update_ios_contents=true`; com `false`, o arquivo fica sob controle do upstream e não causa falso positivo em atualizações.
