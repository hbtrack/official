# HB TRACK — PIPELINE SUMMARY (1-pager)
> Referência de emergência • Atualizado: 2026-03-20

---

## 🎯 6 FASES OBRIGATÓRIAS (Sequência Total)

```
FASE 0 ──────→ FASE 1 ──────→ FASE 2 ──────→ FASE 3 ──────→ FASE 4 ──────→ FASE 5
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼
│PRÉ-CONTRATO  │ DECISÃO ARQ  │  AUTORIA     │  VALIDAÇÃO   │  READINESS   │ HANDOFF
│(Boot + 9     │ (ADRs)       │  (Artefatos) │  (10 Gates)  │  (Elegib.)   │ (Evidência)
│Gates)        │ [OPCIONAL]   │              │              │              │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼
│9 Gates       │              │2 Gates       │10 Gates      │2 Gates       │ SEM GATES
│Bloqueantes   │              │Bloqueantes   │Bloqueantes   │Bloqueantes   │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴

✅ IMPLEMENTAÇÃO LIBERADA
```

---

## 🚪 TASK TYPES → WORKERS → PATHS

```
┌──────────────────────────────┬────────────────────┬────────────────────────┐
│ Task Type                    │ Worker             │ Output Path            │
├──────────────────────────────┼────────────────────┼────────────────────────┤
│ new_contract                 │ create_openapi_*   │ contracts/openapi/     │
│ contract_revision            │ create_openapi_*   │ contracts/openapi/     │
│ new_event                    │ create_asyncapi_*  │ contracts/asyncapi/    │
│ new_workflow                 │ create_arazzo_*    │ contracts/workflows/   │
│ new_schema                   │ create_json_schema │ contracts/schemas/     │
│ new_state_model              │ create_state_*     │ docs/hbtrack/modulos/  │
│ new_ui_contract              │ create_ui_*        │ docs/hbtrack/modulos/  │
│ new_module                   │ create_module_*    │ docs/hbtrack/modulos/  │
│ readiness_promotion          │ readiness_*        │ MODULE_REGISTRY.yaml   │
│ architecture_review          │ decision_*         │ docs/_canon/decisions/ │
└──────────────────────────────┴────────────────────┴────────────────────────┘
```

---

## 🔐 21 GATES (Ordem de Execução)

```
PRÉ-CONTRATO (Fase 0):
├─ 0. AXIOM_INTEGRITY        [CRITICAL]
├─ 1. PATH_CANONICALITY      [CRITICAL]
├─ 2. SCOPE_BOUNDARY         [HIGH]
├─ 3. MODULE_REGISTRY        [CRITICAL]
├─ 4. MODULE_SOURCE_AUTH     [CRITICAL]
├─ 5. PRE_CONTRACT_EVIDENCE  [HIGH]
├─ 6. SHADOW_AUTHORITY       [HIGH]
├─ 7. CANON_ALLOWLIST        [HIGH]
└─ 8. TOOLING_CONFIG         [CRITICAL]

AUTORIA (Fase 2):
├─ 9. REQUIRED_ARTIFACTS     [CRITICAL]
└─10. MODULE_DOC_CROSSREF    [HIGH]

VALIDAÇÃO (Fase 3):
├─11. API_DUPLICATION         [WARNING]
├─12. OWASP_API_CONTROL      [CRITICAL]
├─13. BOUNDARY_USERS/IA      [CRITICAL]
├─14. BOUNDARY_WELLNESS/MED  [CRITICAL]
├─15. SCOUT_TAXONOMY         [HIGH]
├─16. ASYNC_REQUIRED         [HIGH]
├─17. EXTERNAL_SOURCE        [CRITICAL]
├─18. PLACEHOLDER_RESIDUE    [HIGH]
├─19. REF_HERMETICITY        [CRITICAL]
└─20. DECISION_IR_CONFORM    [HIGH]

⚡ Total: 19 bloqueantes + 2 warnings
```

---

## 16️⃣ MÓDULOS CANÔNICOS (Todos implementation_ready)

```
BASE (4)          │ HANDEBOL (5)      │ PERFORMANCE (5)   │ INFRA (2)
├─ users          ├─ seasons         ├─ training        ├─ ai_ingestion
├─ identity_access├─ teams           ├─ wellness        ├─ reports
├─ audit          ├─ competitions    ├─ medical         └─ video
└─ notifications  ├─ matches         ├─ exercises       
                  └─ scout           └─ analytics       

❌ Modificar fora dos 16 = bloqueado (PATH_CANONICALITY_GATE)
```

---

## 🎛️ BOOT PROFILES (Seleção Automática por Task)

```
DEFAULT           │ CONTRACT_EXECUTION    │ ARCHITECTURE_DECISION │ DIAGNOSTIC
├─ AGENT_INST.    │ ├─ AGENT_INST.       │ ├─ AGENT_INST.       │ ├─ AGENT_INST.
├─ OPERATIONS     │ ├─ OPERATIONS        │ ├─ OPERATIONS        │ ├─ OPERATIONS
└─ README         │ ├─ CONTRACT_PIPELINE │ ├─ ARCH_DECISIONS    │ └─ RULES
                  │ ├─ GATES_REGISTRY    │ └─ DECISION_POLICY   │
                  │ └─ RULES             │                       │
                  │                       │                       │
(Fallback sempre) │ (Maioria das tasks)   │ (architecture_review) │ (auditorias)
```

---

## 📦 CANONICAL PATHS (SSOT)

```
contracts/
├── openapi/openapi.yaml
├── openapi/paths/{module}.yaml (×16)
├── schemas/{module}/{schema}.json
├── workflows/{module}/{workflow}.arazzo.yaml
└── asyncapi/asyncapi.yaml

docs/_canon/
├── AGENT_INSTRUCTIONS.md [BOOT OBRIGATÓRIO]
├── MODULE_REGISTRY.yaml  [16 módulos + status]
├── CONTRACT_PIPELINE.md
├── DOMAIN_AXIOMS.json
└── gates/GATES_REGISTRY.yaml

docs/hbtrack/modulos/{module}/
├── README.md
├── DOMAIN_RULES_{MODULE}.md
├── STATE_MODEL_{MODULE}.md (opcional)
└── UI_CONTRACT_{MODULE}.md (opcional)

.contract_driven/
├── TASK_CATALOG.yaml
├── BOOT_PROFILES.yaml
├── agent_prompts/ (18 worker prompts)
└── templates/

❌ Artefatos fora destes paths = bloqueado
```

---

## 🔄 VALIDAÇÃO AUTOMÁTICA

```
python3 scripts/contracts/validate/validate_contracts.py
                          ↓
        _reports/contract_gates/latest.json
                          ↓
        21 gates executam em ordem de dependência
                          ↓
        ✅ PASS: próxima fase liberada
        ❌ FAIL: identifica gate que falhou + blocking_code
```

---

## ⚠️ REGRAS CRÍTICAS (NÃO QUEBRAR)

```
1. ❌ Nunca pular fases do pipeline        → Gates detectam
2. ❌ Nunca criar artefatos fora de paths  → PATH_CANONICALITY_GATE
3. ❌ Nunca deixar TODO/TBD em produção    → PLACEHOLDER_RESIDUE_GATE
4. ❌ Nunca adicionar módulo novo          → MODULE_REGISTRY_GATE
5. ❌ Nunca ref fora do grafo soberano     → REF_HERMETICITY_GATE
6. ❌ Nunca commit sem SESSION_HANDOFF     → PRE_CONTRACT_EVIDENCE_GATE
7. ❌ Nunca usar toolchain incompleta      → TOOLING_CONFIG_GATE
```

---

## 📋 PRÉ-COMMIT CHECKLIST

```
☐ SESSION_HANDOFF.md atualizado
☐ _reports/session_start.json válido
☐ _reports/contract_gates/latest.json = PASS
☐ MODULE_REGISTRY.yaml atualizado (se readiness)
☐ Nenhum TODO/TBD em artefatos
☐ Refs herméticos
☐ Todos artefatos em paths canônicos

ENTÃO:
git add SESSION_HANDOFF.md [artefatos] MODULE_REGISTRY.yaml
git commit -m "feat(contract): {module} — {task_type} pipeline PASS"
```

---

## 🔗 DOCUMENTAÇÃO CANÔNICA

| Documento | Path | Propósito |
|-----------|------|----------|
| 📖 Bootstrap obrigatório | docs/_canon/AGENT_INSTRUCTIONS.md | Seções 0-6, boot entry point |
| 📊 Mapa JSON completo | PIPELINE_MAPPING.json | Dados estruturados (este doc) |
| 📖 Guia visual expandido | PIPELINE_REAL_MAP.md | Explicações detalhadas |
| ⚡ Consulta rápida | PIPELINE_QUICK_REFERENCE.md | Matrizes e fluxogramas |
| 📋 Pipeline formal | docs/_canon/CONTRACT_PIPELINE.md | Estágios, fases, regras |
| 🎯 Registry de tasks | .contract_driven/TASK_CATALOG.yaml | 14 task types |
| 🎛️ Profiles de boot | .contract_driven/BOOT_PROFILES.yaml | 4 profiles |
| 🚪 Gates | docs/_canon/gates/GATES_REGISTRY.yaml | 21 gates completos |

---

## 🆘 TROUBLESHOOTING RÁPIDO

```
❌ "task_type não encontrado"
└─ Verificar: .contract_driven/TASK_CATALOG.yaml (ativo?)

❌ "Fase não permitida para task_type"
└─ Verificar: TASK_CATALOG.yaml::task:stage_allowed [0,1,2]

❌ "Gate bloqueante xx falhou"
└─ Ler: docs/_canon/gates/GATES_REGISTRY.yaml::gate::description
└─ Corrigir: O blocking_code identifica o problema

❌ "Worker prompt não encontrado"
└─ Verificar: .contract_driven/agent_prompts/{worker_id}.prompt.md

❌ "Artefato em path errado"
└─ Mover → contracts/ ou docs/_canon/ ou docs/hbtrack/modulos/

❌ "Commit rejeitado por PRE_CONTRACT_EVIDENCE"
└─ Adicionar: SESSION_HANDOFF.md ao commit
```

---

**⏱️ Última atualização:** 2026-03-20 · **Status:** ✅ PASS · **Próximo:** Implementação liberada
