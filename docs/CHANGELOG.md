<!-- STATUS: NEEDS_REVIEW -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [prod-ready-rag-v1] - 2025-12-24

### Added
- Formalizacao RDB2.1 (allowlist para PKs integer/smallint)
- Formalizacao RDB4.1 (allowlist para tabelas sem soft delete)
- Script `validate_rag_conformance.py` com allowlists centralizadas
- Testes automatizados de conformidade FASE 8 (24 testes)
- Evidencias de validacao em `docs/evidence/fase8/`

### Changed
- REGRAS_SISTEMAS.md atualizado com allowlists formais
- Testes de conformidade usando allowlists compartilhadas

### Status
- Conformidade RAG: 100% (15/15 verificacoes)
- FASE 8: aprovada (24/24 testes passando)
- Sistema: production-ready

### Allowlists (RDB2.1, RDB4.1)
```
ALLOWLIST_INT_PK = {roles, categories, permissions, role_permissions, alembic_version}
ALLOWLIST_NO_SOFT_DELETE = {roles, categories, permissions, role_permissions, alembic_version, audit_logs}
```

### Notes
- Nenhuma alteracao de schema de banco de dados
- audit_logs excluida de soft delete por RDB5 (append-only)
