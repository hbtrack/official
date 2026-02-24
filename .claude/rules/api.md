---
paths:
  - "Hb Track - Backend/**/*.py"
  - "Hb Track - Backend/alembic/**/*"
  - "Hb Track - Backend/scripts/**/*.py"
---

# HB Track — Backend / API

- Preserve o padrão existente (routers/dependencies/services). Não introduza arquitetura nova sem necessidade comprovada.
- Multi-tenant obrigatório: toda query e escrita deve estar escopada à organização (sem cross-org).
- RBAC obrigatório: endpoints exigem auth + checagem de permissão conforme padrão do projeto.
- Contrato real = OpenAPI gerado local. Não documentar nada que não exista no OpenAPI/código.
- Migrations: via Alembic, consistentes e revisáveis (nada "manual escondido").