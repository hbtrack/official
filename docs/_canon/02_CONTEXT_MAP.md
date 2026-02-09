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
