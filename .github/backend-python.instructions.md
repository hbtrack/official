---
applyTo: "**/*.py"
---
- Não criar modelos/rotas novos sem antes localizar o padrão existente no codebase.
- Antes de alterar SQLAlchemy/Alembic, localize schema/migration relevante no repo e cite.
- Para validação de modelos, use o `model_requirements.py` com os perfis de validação (strict/fk/lenient) conforme guia em `docs/workflows/model_requirements_guide.md`.