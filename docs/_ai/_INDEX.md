# AI Agent Documentation Index (Canônico)

> **Autoridade**: este arquivo é o mapa central para agents (humanos ou IA) no monorepo HB Track.
> Todos os paths são relativos à raiz do monorepo (`C:\HB TRACK\`).
> Se um path não existir no disco, o documento NÃO deve ser referenciado — marcar PENDENTE.

---

## 1. Single Source of Truth — Artefatos Gerados

Os artefatos abaixo são gerados automaticamente e constituem a fonte autoritativa do estado do sistema.
Mirrors existem em `docs/_generated/`, mas a **fonte primária** é o backend.

| Artefato | Path canônico | Descrição |
|----------|---------------|-----------|
| OpenAPI | `Hb Track - Backend/docs/_generated/openapi.json` | Especificação OpenAPI 3.1 da API FastAPI (operationIds, schemas, paths) |
| Schema SQL | `Hb Track - Backend/docs/_generated/schema.sql` | DDL PostgreSQL completo (tabelas, constraints, enums, COMMENT ON COLUMN) |
| Alembic State | `Hb Track - Backend/docs/_generated/alembic_state.txt` | Estado atual das migrations (head + versão corrente) |
| Manifest | `Hb Track - Backend/docs/_generated/manifest.json` | Rastreabilidade: git commit, checksums, timestamps dos artefatos |
| Parity Report | `Hb Track - Backend/docs/_generated/parity_report.json` | Relatório de paridade model↔schema (scan automático) |

**Comando para atualizar SSOT** (executar na raiz do monorepo):
```powershell
.\scripts\inv.ps1 refresh
```

---

## 2. Single Source of Truth — Requisitos

| Documento | Path | Descrição |
|-----------|------|-----------|
| PRD | `docs/Hb Track/PRD_HB_TRACK.md` | PRD v2.1 — Requisitos do produto, user stories, MoSCoW, SLAs, modelo de negócio |
| PRD Review | `docs/Hb Track/PRD_REVIEW.md` | Revisão técnica do PRD — score card, lacunas, oportunidades de melhoria |
| Análise de Coerência | `docs/Hb Track/analise_coerencia_documentacao.md` | Análise de coerência PRD↔TRD↔INVARIANTS (escopo Training) |

---

## 3. Hierarquia Documental

```
docs/Hb Track/PRD_HB_TRACK.md                              (SSOT — requisitos do produto, v2.1)
├── docs/02-modulos/training/PRD_BASELINE_ASIS_TRAINING.md  (estado implementado, v1.2)
│   ├── docs/02-modulos/training/TRD_TRAINING.md            (referência técnica, v1.6)
│   │   ├── docs/02-modulos/training/INVARIANTS_TRAINING.md (invariantes confirmadas/pretendidas/inativas)
│   │   └── docs/02-modulos/training/INVARIANTS_TESTING_CANON.md (protocolo canônico de testes)
│   └── docs/02-modulos/training/UAT_PLAN_TRAINING.md       (25 cenários de aceitação, v1.0)
├── docs/Hb Track/analise_coerencia_documentacao.md         (análise de coerência documental)
└── docs/Hb Track/PRD_REVIEW.md                             (revisão técnica e recomendações)

Artefatos gerados (fontes canônicas):
  Hb Track - Backend/docs/_generated/openapi.json
  Hb Track - Backend/docs/_generated/schema.sql
  Hb Track - Backend/docs/_generated/alembic_state.txt
  Hb Track - Backend/docs/_generated/manifest.json
```

---

## 4. Governança AI — Monorepo (`docs/_ai/`)

| Documento | Path | Descrição |
|-----------|------|-----------|
| Index (este arquivo) | `docs/_ai/_INDEX.md` | Mapa canônico de toda a documentação relevante para agents |
| Agent Protocol | `docs/_ai/INVARIANTS_AGENT_PROTOCOL.md` | Protocolo local-first — SSOT refresh, validação, workflow obrigatório |
| Agent Guardrails | `docs/_ai/INVARIANTS_AGENT_GUARDRAILS.md` | Guardrails anti-alucinação — fontes canônicas, gates, regras de parada |
| Task Template | `docs/_ai/INV_TASK_TEMPLATE.md` | Template para instalar 1 invariante com zero alucinação |
| System Design | `docs/_ai/SYSTEM_DESIGN.md` | Arquitetura unificada do backend (stack, camadas, padrões, convenções) |
| Exec Protocol | `docs/_ai/EXEC_PROTOCOL.md` | *(PENDENTE — conteúdo vazio, aguardando preenchimento)* |

---

## 5. Governança AI — Backend (`Hb Track - Backend/docs/_ai/`)

| Documento | Path | Descrição |
|-----------|------|-----------|
| Canon | `Hb Track - Backend/docs/_ai/CANON.md` | Fontes de verdade, stack, invariantes — filosofia retrieve-then-reason |
| Router | `Hb Track - Backend/docs/_ai/ROUTER.md` | Classificação de tarefas (bugfix/endpoint/refactor) e sequência de recuperação de contexto |
| Checks | `Hb Track - Backend/docs/_ai/CHECKS.md` | Verificação objetiva local (lint, test, type-check, migration) |
| System Design | `Hb Track - Backend/docs/_ai/SYSTEM_DESIGN.md` | Arquitetura e padrões do backend (FastAPI, SQLAlchemy 2.0, Pydantic v2) |
| Playbook Bugfix | `Hb Track - Backend/docs/_ai/PLAYBOOK_bugfix.md` | Playbook para bugfixes |
| Playbook Endpoint | `Hb Track - Backend/docs/_ai/PLAYBOOK_endpoint.md` | Playbook para criação de novos endpoints |
| Playbook Refactor | `Hb Track - Backend/docs/_ai/PLAYBOOK_refactor.md` | Playbook para refactoring |

---

## 6. Módulo Training — Documentação Principal

| Documento | Path | Descrição |
|-----------|------|-----------|
| PRD Baseline AS-IS | `C:/HB TRACK/docs/02_modulos/training/PRD_BASELINE_ASIS_TRAINING.md` | Estado implementado do módulo Training (v1.2, baseline evidence snapshot) |
| TRD | `C:/HB TRACK/docs/02_modulos/training/TRD_TRAINING.md` | Referência técnica — contratos API, regras de negócio, evidências, gaps |
| Invariantes | `C:/HB TRACK/docs/02_modulos/training/INVARIANTS_TRAINING.md` | Invariantes do módulo Training — confirmadas, pretendidas e inativas |
| Canon de Testes | `C:/HB TRACK/docs/02_modulos/training/INVARIANTS_TESTING_CANON.md` | Protocolo canônico (Rule of Law) para testes de invariantes — DoD, classes A-F, anti-alucinação |
| UAT Plan | `C:/HB TRACK/docs/02_modulos/training/UAT_PLAN_TRAINING.md` | Plano de User Acceptance Testing v1.0 — 25 cenários de aceitação |

---

## 7. Módulo Training — Documentação de Suporte

| Documento | Path | Descrição |
|-----------|------|-----------|
| Anchor Map | `C:/HB TRACK/docs/02_modulos/training/ANCHOR_MAP.md` | Mapa de âncoras: fluxos UI → operationIds → tabelas/colunas → invariantes |
| Candidates | `C:/HB TRACK/docs/02_modulos/training/training_invariants_candidates.md` | Worklist de promoção — candidatas a invariantes |
| Backlog | `C:/HB TRACK/docs/02_modulos/training/training_invariants_backlog.md` | Backlog de invariantes pendentes de análise |
| Parity Scan Protocol | `C:/HB TRACK/docs/02_modulos/training/PARITY_SCAN._PROTOCOL.md` | Protocolo de verificação de paridade model↔schema |
| Canon AS-IS | `C:/HB TRACK/docs/02_modulos/training/_CANON_AS_IS.md` | Estado canônico atual do módulo |
| Validação de Testes | `C:/HB TRACK/docs/02_modulos/training/VALIDAR_INVARIANTS_TESTS.md` | Checklist de validação dos testes de invariantes |

---

## 8. Comandos de Validação

Todos os comandos abaixo devem ser executados a partir da **raiz do monorepo** (`C:\HB TRACK\`):

| Comando | Finalidade |
|---------|-----------|
| `.\scripts\inv.ps1 refresh` | Regenerar artefatos SSOT (openapi.json, schema.sql, alembic_state.txt) |
| `.\scripts\inv.ps1 gate INV-TRAIN-XXX` | Validar gate de uma invariante específica |
| `.\scripts\inv.ps1 all` | Rodar todos os gates (esperado: `EXIT_ALL: 0`) |
| `.\scripts\inv.ps1 promote` | Promover candidatas confirmadas para invariantes |
