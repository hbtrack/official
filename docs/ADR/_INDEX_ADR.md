# ADR Index — Módulo Training

Este índice lista todas as **Architecture Decision Records (ADRs)** do módulo **Training** do HB Track.

As ADRs documentam **decisões técnicas já tomadas**, derivadas exclusivamente das fontes canônicas. Consulte [00_START_HERE.md](C:/HB TRACK/docs/_canon/00_START_HERE.md) e [01_AUTHORITY_SSOT.md](C:/HB TRACK/docs/_canon/01_AUTHORITY_SSOT.md) para ordem de precedência:
- [PRD_HB_TRACK.md](C:/HB TRACK/docs/_Hb Track/PRD_HB_TRACK.md)
- [PRD_BASELINE_ASIS_TRAINING.md](C:/HB TRACK/docs/02_modulos/training/PRD_BASELINE_ASIS_TRAINING.md)
- [TRD_TRAINING.md](C:/HB TRACK/docs/02_modulos/training/TRD_TRAINING.md)
- [INVARIANTS_TRAINING.md](C:/HB TRACK/docs/02_modulos/training/INVARIANTS/INVARIANTS_TRAINING.md)
- Artefatos [_generated/](C:/HB TRACK/docs/_generated/)

Este índice é a **porta de entrada obrigatória** para compreender as decisões estruturais do módulo.

---

## ADRs Ativas

### 001-ADR-TRAIN — Fonte de Verdade e Precedência de Regras (SSOT)
**Arquivo**: [`001-ADR-TRAIN-ssot-precedencia.md`](C:/HB TRACK/docs/ADR/architecture/001-ADR-TRAIN-ssot-precedencia.md)
**Status**: ACCEPTED
**Resumo**:
Define a hierarquia canônica de fontes de verdade: DB → Service → OpenAPI → Docs.
Base para evitar drift documental e alucinação por agentes IA.

---

### 002-ADR-TRAIN — TRD por Referência, Não por Duplicação
**Arquivo**: [`002-ADR-TRAIN-trd-por-referencia.md`](C:/HB TRACK/docs/ADR/architecture/002-ADR-TRAIN-trd-por-referencia.md)
**Status**: ACCEPTED
**Resumo**:
Estabelece que o TRD não deve duplicar schema ou OpenAPI, apenas referenciar por `constraint_name` e `operationId`.

---

### 003-ADR-TRAIN — Lifecycle e State Machine de Training
**Arquivo**: [`003-ADR-TRAIN-lifecycle-training.md`](C:/HB TRACK/docs/ADR/architecture/003-ADR-TRAIN-lifecycle-training.md)
**Status**: ACCEPTED
**Resumo**:
Define o lifecycle oficial do Training e suas transições permitidas (draft → scheduled → in_progress → pending_review → readonly), incluindo estados finais imutáveis.

---

### 004-ADR-TRAIN — Invariantes como Contrato Testável do Domínio
**Arquivo**: [`004-ADR-TRAIN-invariantes-como-contrato.md`](C:/HB TRACK/docs/ADR/architecture/004-ADR-TRAIN-invariantes-como-contrato.md)
**Status**: ACCEPTED
**Resumo**:
Formaliza invariantes como mecanismo obrigatório para regras críticas do domínio, com SPEC, testes e gates.

---

### 005-ADR-TRAIN — Soft-Delete com Motivo Obrigatório
**Arquivo**: [`005-ADR-TRAIN-soft-delete.md`](C:/HB TRACK/docs/ADR/architecture/005-ADR-TRAIN-soft-delete.md)
**Status**: ACCEPTED
**Resumo**:
Define que exclusões devem ser soft-delete, com motivo obrigatório (`deleted_at` + `deleted_reason` mutuamente obrigatórios) e preservação de histórico.

---

### 006-ADR-TRAIN — Timezone Canônico
**Arquivo**: [`006-ADR-TRAIN-timezone-canonico.md`](C:/HB TRACK/docs/ADR/architecture/006-ADR-TRAIN-timezone-canonico.md)
**Status**: ACCEPTED
**Resumo**:
Estabelece UTC como timezone canônico, com conversão apenas na borda (UI/cliente).

---

### 007-ADR-TRAIN — Automação Assíncrona via Celery
**Arquivo**: [`007-ADR-TRAIN-celery-async.md`](C:/HB TRACK/docs/ADR/architecture/007-ADR-TRAIN-celery-async.md)
**Status**: ACCEPTED
**Resumo**:
Define o uso obrigatório de Celery + Redis para operações assíncronas do módulo Training (analytics, alertas, sugestões).

---

### 008-ADR-TRAIN — Governança por Artefatos Gerados
**Arquivo**: [`008-ADR-TRAIN-governanca-por-artefatos.md`](C:/HB TRACK/docs/ADR/architecture/008-ADR-TRAIN-governanca-por-artefatos.md)
**Status**: ACCEPTED
**Resumo**:
Determina que artefatos `_generated` são obrigatórios antes de mudanças documentais ou promoção de invariantes.

---

### 009-ADR-TRAIN — Modelo de Focus Percentages (7 Áreas)
**Arquivo**: [`009-ADR-TRAIN-focus-percentages.md`](C:/HB TRACK/docs/ADR/architecture/009-ADR-TRAIN-focus-percentages.md)
**Status**: ACCEPTED
**Origem**: Evidence-first (100% derivada de `schema.sql`)
**Resumo**:
Define o modelo de 7 áreas de foco tático (ataque posicionado, defesa posicionada, transição ofensiva/defensiva, ataque técnico, defesa técnica, físico), cada uma 0-100%, soma ≤120%, com trigger de derivação automática de phase_focus booleans.

---

### 010-ADR-TRAIN — Multi-tenancy via Organization ID
**Arquivo**: [`010-ADR-TRAIN-multi-tenancy.md`](C:/HB TRACK/docs/ADR/architecture/010-ADR-TRAIN-multi-tenancy.md)
**Status**: ACCEPTED
**Origem**: Evidence-first (100% derivada de `schema.sql`)
**Resumo**:
Define o isolamento de dados entre organizações via coluna `organization_id` FK em todas as tabelas core, com ON DELETE RESTRICT e índices condicionais.

---

### 011-ADR-TRAIN — RBAC por Papéis e Permissões
**Arquivo**: [`011-ADR-TRAIN-rbac-papeis-permissoes.md`](C:/HB TRACK/docs/ADR/architecture/011-ADR-TRAIN-rbac-papeis-permissoes.md)
**Status**: ACCEPTED
**Origem**: Evidence-first (100% derivada de `schema.sql`)
**Resumo**:
Define o modelo RBAC com tabelas `roles`, `permissions`, `role_permissions` e vinculação via `org_memberships`. Hierarquia: Dirigente > Coordenador > Treinador > Atleta.

---

## Template

**Arquivo**: [`ADR_TEMPLATE.md`](C:/HB TRACK/docs/ADR/architecture/ADR_TEMPLATE.md)
Template padrão para criação de novas ADRs do módulo Training.

---

## Regras de Governança

- Toda decisão estrutural nova do módulo Training **exige ADR**.
- Mudanças em:
  - Lifecycle
  - SSOT / precedência
  - Invariantes
  - Estratégia de persistência ou automação
  **devem**:
  1. Criar ou atualizar ADR
  2. Atualizar este índice
  3. Referenciar o ADR no TRD e/ou Invariantes quando aplicável

---

## Fontes Canônicas

- [00_START_HERE.md](C:/HB TRACK/docs/_canon/00_START_HERE.md) — porta única obrigatória
- [01_AUTHORITY_SSOT.md](C:/HB TRACK/docs/_canon/01_AUTHORITY_SSOT.md) — precedência de fontes
- [PRD_HB_TRACK.md](C:/HB TRACK/docs/_Hb Track/PRD_HB_TRACK.md)
- [PRD_BASELINE_ASIS_TRAINING.md](C:/HB TRACK/docs/02_modulos/training/PRD_BASELINE_ASIS_TRAINING.md)
- [TRD_TRAINING.md](C:/HB TRACK/docs/02_modulos/training/TRD_TRAINING.md)
- [INVARIANTS_TRAINING.md](C:/HB TRACK/docs/02_modulos/training/INVARIANTS/INVARIANTS_TRAINING.md)
- Artefatos [_generated/](C:/HB TRACK/docs/_generated/) — `schema.sql`, `openapi.json`, `alembic_state.txt`, `manifest.json`, `parity_report.json`

---

## Observação Final

Este índice **não é opinativo**.
Ele reflete **decisões já aceitas** e serve como contrato técnico para humanos, agentes IA e gates automáticos.
