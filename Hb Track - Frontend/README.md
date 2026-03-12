# HB Track — Frontend (Next.js)

Aplicação web (SPA) do HB Track, construída em **Next.js** + **TypeScript**.

## Pré-requisitos

- Node.js 18+ (recomendado 20+)

## Comandos

```bash
npm install
npm run dev
```

Outros comandos úteis:

- `npm run gate` (typecheck + lint + higiene)
- `npm run build` / `npm run start`
- `npm run test:e2e` (Playwright)

## Client de API (OpenAPI → TypeScript)

Quando aplicável, o client HTTP gerado vive em `src/api/generated/`.

- `npm run sync:openapi` baixa o OpenAPI do backend local e gera o client (script PowerShell).
- `npm run api:sync` faz a mesma ação via comando inline (usa `Invoke-WebRequest` + `openapi-generator`).

## Referências de governança (CDD)

- Regras/layout/templates de contratos: `.contract_driven/CONTRACT_SYSTEM_RULES.md`, `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`, `.contract_driven/GLOBAL_TEMPLATES.md`
- SSOT de regras/templates de API HTTP: `.contract_driven/templates/API_RULES/API_RULES.yaml`
- Canon global: `docs/_canon/README.md`

* Fixed JSvectormap rendering issues

### v1.3.3 (June 20, 2024)

* Fixed build error related to Loader component

### v1.3.2 (June 19, 2024)

* Added ClickOutside component for dropdown menus
* Refactored sidebar components
* Updated Jsvectormap package

### v1.3.1 (Feb 12, 2024)

* Fixed layout naming consistency
* Updated styles

### v1.3.0 (Feb 05, 2024)

* Upgraded to Next.js 14
* Added Flatpickr integration
* Improved form elements
* Enhanced multiselect functionality
* Added default layout component

## License

TailAdmin Next.js Free Version is released under the MIT License.

## Support
If you find this project helpful, please consider giving it a star on GitHub. Your support helps us continue developing and maintaining this template.
