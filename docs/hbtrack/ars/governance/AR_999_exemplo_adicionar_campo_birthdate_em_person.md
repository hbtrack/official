# AR_999 — Exemplo: Adicionar campo birthdate em Person

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.2.0

## Descrição
Implementar campo opcional birthdate no model Person e migração Alembic. Este é um exemplo de task que toca código e portanto MUST ter write_scope explícito (GATE P3.6).

## Critérios de Aceite
1. Migration criada com ALTER TABLE persons ADD COLUMN birthdate DATE
2. Model Person atualizado com campo birthdate: Mapped[Optional[date]]
3. pytest tests/test_person.py passa
4. Alembic upgrade/downgrade funciona

## Write Scope
- Hb Track - Backend/app/models/person.py
- Hb Track - Backend/alembic/versions/*.py

## SSOT Touches
- [ ] docs/ssot/schema.sql
- [ ] docs/ssot/alembic_state.txt

## Validation Command (Contrato)
```
cd 'Hb Track - Backend'; pytest tests/models/test_person.py::test_birthdate_field -v
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_999/executor_main.log`

## Rollback Plan (Contrato)
```
python scripts/run/hb_cli.py rollback 999
git checkout -- 'Hb Track - Backend/app/models/person.py'
git clean -fd 'Hb Track - Backend/alembic/versions/'
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Task exemplo para demonstrar write_scope estruturado. Não é uma AR real — serve apenas como template.

## Riscos
- Pode quebrar dependências de Person se não houver testes de integração
- Migration irreversível se houver dados em produção (usar default NULL)

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

