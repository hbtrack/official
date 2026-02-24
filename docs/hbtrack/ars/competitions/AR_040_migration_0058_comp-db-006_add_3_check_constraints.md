# AR_040 — Migration 0058 COMP-DB-006: ADD 3 CHECK constraints status/modality (competitions+matches)

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.1.0

## Descrição
Criar arquivo Hb Track - Backend/db/alembic/versions/0058_comp_db_006_status_check_constraints.py com revision='0058', down_revision='0057'.

Upgrade:
  op.create_check_constraint(
      'ck_competitions_status',
      'competitions',
      "status IN ('draft', 'active', 'finished', 'cancelled')"
  )
  op.create_check_constraint(
      'ck_competitions_modality',
      'competitions',
      "modality IN ('masculino', 'feminino', 'misto')"
  )
  op.create_check_constraint(
      'ck_competition_matches_status',
      'competition_matches',
      "status IN ('scheduled', 'in_progress', 'finished', 'cancelled')"
  )

Downgrade:
  op.drop_constraint('ck_competition_matches_status', 'competition_matches', type_='check')
  op.drop_constraint('ck_competitions_modality', 'competitions', type_='check')
  op.drop_constraint('ck_competitions_status', 'competitions', type_='check')

Docstring MUST incluir: 'COMP-DB-006: CHECK constraints em competitions.status, competitions.modality, competition_matches.status'.
NAO modificar nenhum outro arquivo.

## Critérios de Aceite
1) alembic upgrade head retorna exit_code=0. 2) SELECT constraint_name FROM information_schema.table_constraints WHERE constraint_name IN ('ck_competitions_status','ck_competitions_modality','ck_competition_matches_status') retorna 3 linhas. 3) INSERT com valor inválido (ex: status='INVALID') levanta CheckViolation. 4) alembic downgrade -1 retorna exit_code=0. 5) alembic upgrade head novamente retorna exit_code=0.

## SSOT Touches
- [ ] docs/ssot/schema.sql
- [ ] docs/ssot/alembic_state.txt

## Validation Command (Contrato)
```
python -c "import pathlib; f=pathlib.Path('Hb Track - Backend/db/alembic/versions/0061_comp_db_006_status_check_constraints.py'); assert f.exists(),'FAIL: migration file not found'; c=f.read_text(encoding='utf-8'); assert "revision = '0061'" in c,'FAIL: wrong revision id'; assert "down_revision = '0060'" in c or "down_revision='0060'" in c,'FAIL: wrong down_revision'; ck=['ck_competitions_status','ck_competitions_modality','ck_competition_matches_status']; missing=[k for k in ck if k not in c]; assert not missing,f'FAIL: missing constraints {missing}'; assert 'create_check_constraint' in c,'FAIL: create_check_constraint not used'; print('PASS: migration 0061 content validated with 3 CHECK constraints')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_040_comp_db_006_check_constraints_migration.log`

## Rollback Plan (Contrato)
```
alembic downgrade -1
# OU manualmente:
# ALTER TABLE competition_matches DROP CONSTRAINT IF EXISTS ck_competition_matches_status;
# ALTER TABLE competitions DROP CONSTRAINT IF EXISTS ck_competitions_modality;
# ALTER TABLE competitions DROP CONSTRAINT IF EXISTS ck_competitions_status;
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Se existirem registros com valores de status/modality que não estejam nos conjuntos permitidos, a migration falhará com CheckViolation. Pré-flight recomendado: SELECT DISTINCT status FROM competitions; SELECT DISTINCT modality FROM competitions; SELECT DISTINCT status FROM competition_matches.
- op.create_check_constraint em Alembic pode gerar nomes diferentes dependendo da versão. Usar o nome explícito fornecido.
- Se COMP-DB-005 for implementado no futuro, sua migration deverá usar um slot de revision diferente (ex: 0058a) para não conflitar com a cadeia linear. Arquiteto deverá reorganizar nesse momento.
- PostgreSQL cria locks ACCESS EXCLUSIVE para ALTER TABLE ADD CONSTRAINT. Em produção com dados, executar em janela de manutenção.

## Análise de Impacto
**Executor**: Roo (💻 Code Mode)
**Data**: 2026-02-22

**Escopo da Implementação**:
1. **Criar Migration 0058**: Novo arquivo de migração Alembic para adicionar constraints de check às tabelas `competitions` e `competition_matches`.
2. **Constraints de Domínio**:
   - `ck_competitions_status`: Restringe status a `draft`, `active`, `finished`, `cancelled`.
   - `ck_competitions_modality`: Restringe modalidade a `masculino`, `feminino`, `misto`.
   - `ck_competition_matches_status`: Restringe status de jogos a `scheduled`, `in_progress`, `finished`, `cancelled`.
3. **Robustez**: Previne a inserção de strings arbitrárias que poderiam quebrar a lógica de negócio dos serviços.

**Impacto**:
- Qualidade de dados: Garante que apenas estados válidos do ciclo de vida da competição e dos jogos sejam persistidos.
- Lock de tabela: Requer `ACCESS EXCLUSIVE` curto em `competitions` e `competition_matches`.
- Compatibilidade: SQL padrão PostgreSQL, sem dependências de versão específicas além do suporte básico a constraints de check.

**Conclusão**: O banco de dados agora protege o domínio através de integridade declarativa.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; f=pathlib.Path('Hb Track - Backend/db/alembic/versions/0058_comp_db_006_status_check_constraints.py'); assert f.exists(),'FAIL: migration file not found'; c=f.read_text(encoding='utf-8'); assert \"revision = '0058'\" in c,'FAIL: wrong revision id'; assert \"down_revision = '0057'\" in c or \"down_revision='0057'\" in c,'FAIL: wrong down_revision'; ck=['ck_competitions_status','ck_competitions_modality','ck_competition_matches_status']; missing=[k for k in ck if k not in c]; assert not missing,f'FAIL: missing constraints {missing}'; assert 'create_check_constraint' in c,'FAIL: create_check_constraint not used'; print('PASS: migration 0058 content validated with 3 CHECK constraints')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_040_comp_db_006_check_constraints_migration.log`
**Python Version**: 3.11.9

