<!-- STATUS: VERIFIED | evidencia: _generated/* -->

# Fontes da Verdade (Dev Local)

## Artefatos Canonicos

| Artefato | Localizacao | Descricao |
|----------|-------------|-----------|
| OpenAPI | `docs/_generated/openapi.json` | Especificacao completa da API |
| Schema DB | `docs/_generated/schema.sql` | DDL do banco PostgreSQL |
| Alembic State | `docs/_generated/alembic_state.txt` | Estado das migrations |

## Regra de Validacao

Qualquer documento marcado como `NEEDS_REVIEW` pode divergir da realidade.

**Antes de confiar em um doc NEEDS_REVIEW:**
1. Verifique o campo relevante em `_generated/`
2. Se houver divergencia, `_generated/` prevalece
3. Atualize o doc ou marque como DEPRECATED

## Regenerar Artefatos

```bash
cd "C:\HB TRACK\Hb Track - Backend"
python scripts/generate_docs.py --all
```
