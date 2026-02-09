# Context Map: Intenções & Fluxos

Use este mapa: **Tenho intenção de X** → leia Y → gero evidência Z → saída esperada W.

---

## 1. Instalar Nova Invariante de Training

**Intenção:** Adicionar restrição de negócio (ex: "duração de sessão < 180 min")

**Ler Primeiro:**
- [../02-modulos/training/INVARIANTS/INVARIANTS_TESTING_CANON.md](../02-modulos/training/INVARIANTS/INVARIANTS_TESTING_CANON.md)
- [../_ai/INVARIANTS_AGENT_PROTOCOL.md](../_ai/INVARIANTS_AGENT_PROTOCOL.md)
- [../02-modulos/training/INVARIANTS/INVARIANTS_TRAINING.md](../02-modulos/training/INVARIANTS/INVARIANTS_TRAINING.md)

**Evidência Gerada:** Testes em `tests/`, relatório invariante

**Saída Esperada:** PR com gates verdes (tests + linters)

---

## 2. Consertar Divergência Model vs DB

**Intenção:** Há conflito entre `app/models/SessionType.py` e `schema.sql`

**Ler Primeiro:**
- [../ADR/architecture/013-ADR-MODELS.md](../ADR/architecture/013-ADR-MODELS.md)
- [../references/model_requirements_guide.md](../references/model_requirements_guide.md)
- Arquivo: `../_generated/schema.sql`
- Arquivo: `../_generated/alembic_state.txt` (estado atual)

**Evidência Gerada:** `parity_report.json` antes e depois

**Saída Esperada:** `parity_report.json` mostra divergências < versão anterior (ou zero)

---

## 3. Executar Parity Scan

**Intenção:** Validar alinhamento entre DB schema e codebase

**Ler Primeiro:**
- [../02-modulos/training/PROTOCOLS/PARITY_SCAN._PROTOCOL.md](../02-modulos/training/PROTOCOLS/PARITY_SCAN._PROTOCOL.md)
- Arquivo: `../_generated/parity_report.json`

**Evidência Gerada:** `parity_report.json` atualizado com timestamp

**Saída Esperada:** Lista de arquivos a corrigir (ou "tudo ok")

---

## 4. Implementar Exit Code Novo ou Alterado

**Intenção:** Adicionar novo exit code (ex: exit=5 para "feature flag off")

**Ler Primeiro:**
- [../ADR/architecture/001-ADR-TRAIN-ssot-precedencia.md](../ADR/architecture/001-ADR-TRAIN-ssot-precedencia.md)
- [../references/exit_codes.md](../references/exit_codes.md)

**Evidência Gerada:** Scripts alterados, docs atualizadas

**Saída Esperada:** Smoke tests verdes; exit_codes.md reflete nova definição

---

## 5. Usar Model Requirements Validator

**Intenção:** Validar que `app/models/` está conforme `schema.sql` (constraints, tipos)

**Ler Primeiro:**
- [../references/model_requirements_guide.md](../references/model_requirements_guide.md)
- [../ADR/workflows/EXEC_TASK_ADR_MODELS_001.md](../ADR/workflows/EXEC_TASK_ADR_MODELS_001.md)

**Evidência Gerada:** Saída de validador + relatório

**Saída Esperada:** exit=0 (tudo ok) ou exit=4 (correções necessárias com lista clara)

---

## 6. Entender Estrutura de Treino

**Intenção:** Aprender como Training, Session, Week, Cycle se relacionam

**Ler Primeiro:**
- [../02-modulos/training/INVARIANTS/INVARIANTS_TRAINING.md](../02-modulos/training/INVARIANTS/INVARIANTS_TRAINING.md)
- [../ADR/architecture/_INDEX_ADR.md](../ADR/architecture/_INDEX_ADR.md) (busque por "training")

**Evidência Gerada:** Diagrama, schema.sql (tabelas: training_cycles, training_microcycles, etc)

**Saída Esperada:** Compreensão de: parent-child, constraints, sequência temporal

---

## 7. Adicionar Nova Posição Defensiva ou Ofensiva

**Intenção:** Criar novo tipo de posição (defensive_positions ou offensive_positions)

**Ler Primeiro:**
- Arquivo: `../_generated/schema.sql` (tabelas `defensive_positions`, `offensive_positions`)
- [../ADR/architecture/002-ADR-TRAIN-dominio-treino.md](../ADR/architecture/002-ADR-TRAIN-dominio-treino.md)
- [../02-modulos/training/INVARIANTS/INVARIANTS_TRAINING.md](../02-modulos/training/INVARIANTS/INVARIANTS_TRAINING.md) (busque por "posição")

**Evidência Gerada:** Schema alterado, migration file gerada, testes passando

**Saída Esperada:** Novas posições refletem em openapi.json, schema.sql atualizado, parity_report.json limpo

---

## 8. Integrar Dados de Wellness (Pre/Post)

**Intenção:** Conectar wellness_pre com wellness_post para análise de atleta

**Ler Primeiro:**
- Arquivo: `../_generated/schema.sql` (tabelas `wellness_pre`, `wellness_post`)
- [../02-modulos/training/INVARIANTS/INVARIANTS_TRAINING.md](../02-modulos/training/INVARIANTS/INVARIANTS_TRAINING.md) (busque por "wellness")
- [../references/model_requirements_guide.md](../references/model_requirements_guide.md) (validação de relações)

**Evidência Gerada:** Nova view/modelo, endpoint de wellness, testes de integridade

**Saída Esperada:** Queries de wellness retornam dados pré/pós consistentes; parity report "clean"

---

## 9. Auditar Permissões e Roles

**Intenção:** Verificar ou adicionar nova permissão (ex: "edit_training_session")

**Ler Primeiro:**
- Arquivo: `../_generated/schema.sql` (tabelas `roles`, `permissions`, `role_permissions`)
- Arquivo: `../_generated/trd_training_permissions_report.txt` (análise de permissões vigentes)
- [../ADR/architecture/010-ADR-TRAIN-rbac.md](../ADR/architecture/010-ADR-TRAIN-rbac.md)

**Evidência Gerada:** Permissão no BD, policy/middleware no serviço, tests de RBAC

**Saída Esperada:** Nova permissão funciona em endpoints; relatório de permissões reflete mudança

---

## 10. Debugar Match/Possession/Events

**Intenção:** Há dados inconsistentes em match_events ou match_possessions

**Ler Primeiro:**
- Arquivo: `../_generated/schema.sql` (tabelas `matches`, `match_periods`, `match_events`, `match_possessions`)
- [../ADR/architecture/004-ADR-TRAIN-match-modeling.md](../ADR/architecture/004-ADR-TRAIN-match-modeling.md)
- [../02-modulos/training/INVARIANTS/INVARIANTS_TRAINING.md](../02-modulos/training/INVARIANTS/INVARIANTS_TRAINING.md) (invariantes de match)

**Evidência Gerada:** alembic migration ou data correction script, parity_report.json, validation queries

**Saída Esperada:** Dados retornam consistentes; período/evento/possession alinhados com invariantes

---

## 11. Gerar Relatório de Desempenho de Atleta

**Intenção:** Criar novo tipo de report ou view (ex: top scorers, attendance rate)

**Ler Primeiro:**
- Arquivo: `../_generated/openapi.json` (endpoints de reports disponíveis)
- [../references/model_requirements_guide.md](../references/model_requirements_guide.md)
- [../ADR/architecture/009-ADR-TRAIN-analytics.md](../ADR/architecture/009-ADR-TRAIN-analytics.md)

**Evidência Gerada:** Nova view SQL, endpoint REST, testes de cálculo, dashboard data

**Saída Esperada:** Relatório está em openapi.json, parity_report.json válido, testes de agregação verdem
