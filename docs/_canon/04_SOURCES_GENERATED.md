# Arquivos Gerados: Função & Uso

Estes arquivos são **derivados** de SSOT (schema.sql, código, ADRs). Consulte para validação; **não edite manualmente**.

---

## Tabela de Referência

| Arquivo | Função | Use Para | Como Regenerar |
|---------|--------|----------|-----------------|
| `schema.sql` | Constraints, triggers, defaults reais do BD | Debugar divergências DB vs model; validar tipos | Executar script de export (verificar em docs/scripts/) |
| `openapi.json` | Contratos API (schemas, operationIds, parâmetros) | Validar endpoints, verificar breaking changes | Gerado a partir de code docstrings/FastAPI |
| `alembic_state.txt` | Estado atual de migrações rodadas | Verificar qual versão está deploy; auditar histórico | `alembic current` + export |
| `parity_report.json` | Divergências model ↔ schema | Detectar conflicts antes de merge | Executar parity scanner (ver EXEC_TASK_ADR_MODELS_001.md) |
| `manifest.json` | Índice de todos arquivos commitados + hash | Auditar integridade, rastrear versão | Gerado por build process |
| `trd_training_permissions_report.txt` | Análise de permissões no módulo training | Validar RBAC, auditoria de acesso | Script em docs/scripts/ ou via agent |
| `trd_training_openapi_operationIds.txt` | Lista de operationIds training | Rastrear endpoints training disponíveis | Customization de openapi.json |

---

## Quando Regenerar

- **Sempre que:** mudar `schema.sql` diretamente, commitar novo código de modelo, adicionar/remover endpoint
- **Teste:** regenerate → integre no CI/CD (pull sempre antes de merge)
- **Dúvida:** vá para [001-ADR-TRAIN-ssot-precedencia.md](C:/HB TRACK/docs/ADR/architecture/001-ADR-TRAIN-ssot-precedencia.md) (SSOT wins)

---

## Path Completo

Todos arquivos estão em: [_generated/](C:/HB TRACK/docs/_generated/)

Acesso direto via `docs/_generated/schema.sql`, etc.
