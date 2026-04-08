---
applyTo: "frontend/src/api/**"
---

# Proibição de edição manual de schema.d.ts — HB Track

**NUNCA edite `frontend/src/api/schema.d.ts` manualmente.**

Este arquivo é gerado automaticamente a partir do contrato OpenAPI via `openapi-typescript`.

## Comando correto

```bash
npm run api:generate
```

## Fluxo correto

1. Altere o contrato OpenAPI em `contracts/openapi/`
2. Execute `npm run api:generate` para regenerar `schema.d.ts`
3. Atualize os componentes que consomem os tipos

## Por que esta regra existe

- `schema.d.ts` é um artefato derivado — o contrato OpenAPI é a fonte de verdade
- Edições manuais serão sobrescritas na próxima geração
- Divergências entre contrato e tipos TypeScript causam bugs silenciosos em runtime
