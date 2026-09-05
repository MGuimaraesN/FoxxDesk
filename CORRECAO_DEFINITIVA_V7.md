# FoxxDesk — Correção Definitiva V7

## Problema corrigido

A V6 limpou corretamente `hbb_common`, mas o perfil `runtime` não possuía uma regra explícita para quatro campos públicos que o precheck exigia. Em um checkout realmente upstream esses campos continuavam `RustDesk`:

- Android `app_name`;
- Android `<application android:label>`;
- macOS `PRODUCT_NAME`;
- Windows `ProductName`.

Por isso o prepare terminava o rebrand sem pendências e falhava somente no precheck final.

## Solução V7

Foi criado `scripts/foxxdesk_public_brand.py`. Ele é responsável **somente** pelos campos públicos obrigatórios e usa patches semânticos/ancorados.

O fluxo local agora é:

1. sincronizar/verificar `hbb_common`;
2. executar rebrand runtime;
3. aplicar public brand semântico;
4. aplicar runtime defaults no crate principal;
5. conferir ícones;
6. validar usando a mesma função de public brand.

O validator não mantém mais uma política separada para esses quatro campos. Isso elimina a classe de erro “o patch acha que terminou, mas o precheck espera outra coisa”.

## Comportamento Android

`strings.xml` recebe `brand.display_name` em `app_name`. O `<application>` passa a usar `@string/app_name`, centralizando o nome público em um único valor Android.

## Comportamento macOS

Somente a linha `PRODUCT_NAME = ...` de `AppInfo.xcconfig` é alterada. Se a chave desaparecer em uma versão futura, o script falha explicitamente.

## Comportamento Windows

`ProductName` recebe `brand.display_name`. Quando os campos existem, `FileDescription`, `InternalName` e `OriginalFilename` também são alinhados com `display_name`/`slug`. Nenhum `.rc` inteiro é substituído.

## hbb_common

Continua 100% upstream. Nenhum branding é aplicado dentro do submódulo. Para RustDesk 1.4.9 permanece o pin `7e1c392c62d39c364127307cd408421dd5f8cfb0`.

## GitHub Actions

Continua manual-only. O CI não reaplica o rebrand: valida a árvore commitada e compila somente depois do preflight.

## Testes V7

Foi reproduzido o cenário exato com os quatro campos definidos como `RustDesk`.

Primeiro prepare:

- public brand: 4 arquivos alterados;
- precheck: OK.

Segundo prepare:

- rebrand: 0 alterações;
- public brand: 0 alterações;
- runtime defaults: 0 alterações;
- ícones: 0 alterações;
- validation: OK.

Também foi executado `foxxdesk_validate.py --ci` em modo somente leitura e o SHA-256 do `.gitignore` permaneceu inalterado.

## Comando recomendado

```bash
python3 scripts/foxxdesk_prepare.py --target . --apply --yes --sync-deps
python3 scripts/foxxdesk_validate.py --target .
```

Depois revise, faça commit e execute manualmente `FoxxDesk Build`.
