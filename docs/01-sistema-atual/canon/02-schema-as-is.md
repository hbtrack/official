<!-- STATUS: VERIFIED | evidencia: _generated/schema.sql, _generated/alembic_state.txt -->

# Schema As-Is

## Fontes Canonicas

| Artefato | Localizacao | Regenerar |
|----------|-------------|-----------|
| Schema DDL | `docs/_generated/schema.sql` | `python scripts/generate_docs.py --schema` |
| Alembic State | `docs/_generated/alembic_state.txt` | `python scripts/generate_docs.py --alembic` |

## Checklist de Verificacao Minima

- [ ] `schema.sql` existe e nao esta vazio
- [ ] `schema.sql` contem `CREATE TABLE` ou `CREATE SCHEMA`
- [ ] `alembic_state.txt` contem secao `=== ALEMBIC HEADS ===`
- [ ] `alembic_state.txt` contem secao `=== ALEMBIC CURRENT ===`
- [ ] Heads mostra revision (ex: `0052 (head)`)

## Notas

- O schema.sql e gerado via `pg_dump --schema-only`
- O alembic_state requer DATABASE_URL configurado para mostrar `current`
- Se `current` mostrar erro de conexao, o script foi executado sem banco local
