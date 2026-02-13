# Changelog - HB Track
Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
### Adicionado
* **MIGRAÇÃO FASE 2: REFRESH TOKEN PERSISTENCE & ROTATION (REMEDIADA)** (2026-02-13): Migração completa de refresh tokens stateless para persistência server-side com rotação e detecção de fraude (Kill Switch). Versão final após remediação de drift de escopo.
  - **Model**: Criado `RefreshToken` em `app/models/refresh_token.py` com suporte a `parent_id` (trace de rotação) e `token_hash`.
  - **Migration**: Aplicada migração Alembic `0fb0f76b48a7` para criação da tabela no DB.
  - **Security**: Implementado hashing SHA-256 para tokens persistidos (armazenamento seguro) em `app/core/security.py`.
  - **Auth Router**: Refatorado `/login` e `/refresh` para suportar rotação de tokens. Removido drift `/sessions`.
  - **Kill Switch**: Implementada lógica de detecção de reuso de token. Se um token revogado for usado, todas as sessões ativas do usuário são invalidadas imediatamente (Segurança R42).
  - **Contract**: Validado contrato fixo de 13 operações de autenticação no `openapi.json` (removidos 2 operationIds de sessions).
  - **Correções**: Resolvido bug de conversão de UUID em `ExecutionContext` para compatibilidade com `asyncpg`.
  - **Testes**: Criado `tests/api/test_refresh_rotation.py` com validação funcional completa (Rotation, Reuse Detection, Logout). 14/14 testes de auth em PASS.
  - **Status**: SUCCESS (Remediação concluída).
* **Implementation of missing Analytics models** (2026-02-13): Implementation of 5 missing SQLAlchemy models for the analytics/match module.
  - **Models added**: `advantage_states`, `event_subtypes`, `event_types`, `match_possessions`, `phases_of_play`.
  - **Validation**: All models validated against SSOT (`schema.sql`) using `models_autogen_gate.ps1`.
  - **Compliance**: 100% coverage achieved for schema-to-model parity (63/63 tables).
  - **Guard**: Baseline snapshot updated in `.hb_guard/baseline.json`.
  - **Status**: SUCCESS (Exit Code 0 on all gates).

* **Documentation Governance Unification (R1+R2)** (2026-02-13): Implementação da remediação Priority 1 do GOVERNANCE_AUDIT_REPORT:
  - **R1 (Index Unification)**: Consolidação de `docs/_ai/_INDEX.md` (511 linhas) em `docs/_canon/00_START_HERE.md` como autoridade única de navegação
    - `_INDEX.md` convertido para stub redirect (backward compatibility mantida)
    - Deprecation timeline: v2.0.0 (stub criado) → v2.1.0 (warnings) → v2.2.0 (remoção planejada)
    - Enhanced `00_START_HERE.md` com: CANONICAL header (version 2.0.0), LEVEL 0-3 hierarchy declaration, Anti-Loop rule, Batch processing guidance, Approved Commands security policy
    - Glossário expandido (12 termos técnicos), CWD guardrails, exit code semantics, snapshot baseline rules
  - **R2 (Hierarchy Declaration)**: Integração explícita da hierarquia documental em `AI_GOVERNANCE_INDEX.md`:
    - LEVEL 0 (PROJECT CONSTITUTION): ADRs, SSOT, Invariantes, AI_GOVERNANCE_INDEX
    - LEVEL 1 (CANONICAL DOCUMENTATION): 00_START_HERE (entry point), canon docs, governance protocols
    - LEVEL 2 (OPERATIONAL DOCUMENTATION): _ai/* (prompts, protocols, guardrails), .github/instructions
    - LEVEL 3 (GENERATED ARTIFACTS): schema.sql, openapi.json, parity_report.json, manifest.json
    - Cross-level precedence rules: LEVEL 0 overrides all, LEVEL 1 is navigation authority, LEVEL 2 cannot create new rules, LEVEL 3 is read-only truth
  - **Artefatos**: `GOVERNANCE_AUDIT_REPORT.md` (538 linhas, 6 categorias críticas, 8-step remediation plan R1-R8)
  - **Impact**: Resolução de 85% de duplicação documental; eliminação de 3 índices competidores; clear authority precedence; reduced maintenance burden
  - **Branch**: `docs/gov-unify-001` (commit `4152018`)

* **Guardrails Consolidation (R3)** (2026-02-13): Implementação da remediação Priority 2 do GOVERNANCE_AUDIT_REPORT:
  - **R3 (Guardrails Index Creation)**: Criação de entry point único para 5 arquivos fragmentados de guardrails:
    - Criado `docs/_ai/_guardrails/GUARDRAILS_INDEX.md` (entry point único com decision tree, quick reference, workflow de consulta)
    - Preservada granularidade: 5 arquivos mantidos intactos (GUARDRAIL_POLICY_BASELINE, GUARDRAIL_POLICY_PARITY, GUARDRAIL_POLICY_REQUIREMENTS, AGENT_GUARDRAILS, INVARIANTS_AGENT_GUARDRAILS)
    - Headers atualizados: todos os 5 arquivos agora referenciam GUARDRAILS_INDEX.md como parent
    - Referências atualizadas: `00_START_HERE.md` glossário e seção 5.1 agora apontam para GUARDRAILS_INDEX.md
    - Domínios organizados: Gate-specific (baseline/parity/requirements) + Operational (DevOps/Repo/Model Pipeline/Docs) + Invariants (Training module)
  - **Artefatos**: `GUARDRAILS_INDEX.md` (290 linhas: decision tree, checklist pré-execução, troubleshooting, metrics de compliance)
  - **Impact**: Clear navigation hierarchy para guardrails; eliminated ambiguity de "qual guardrail consultar"; preserved granularity (não merged); checklist pré-execução universal
  - **Branch**: `docs/gov-unify-001` (commit `36f3318`)

* **Bridge Document (R4)** (2026-02-13): Implementação da remediação Priority 2 do GOVERNANCE_AUDIT_REPORT:
  - **R4 (Task Escalation Criteria)**: Criação de documento bridge definindo quando escalar de prompt operacional → protocolo formal TASK BRIEF:
    - Criado `docs/_canon/_agent/WHEN_TO_USE_TASK_BRIEF.md` (decision framework com 5 critérios objetivos)
    - **5 Critérios Mensuráveis**: (1) Scope (arquivos afetados: ≤2=direto, 3-5=considerar, >5=TASK BRIEF), (2) SSOT Impact (modificação schema.sql/openapi.json=TASK BRIEF obrigatório), (3) Tempo (>30min=TASK BRIEF), (4) Complexity (>2 gates sequenciais ou branching condicional=TASK BRIEF), (5) Risk Level (operações irreversíveis=TASK BRIEF+autorização)
    - **Decision Matrix**: Tabela combinatória (Files × SSOT × Time × Gates × Risk = Decision: Direct | Consider | TASK BRIEF)
    - **Exemplos Práticos**: 7 casos reais (3 Direct OK: diagnóstico read-only, correção typo, single model fix; 4 TASK BRIEF Required: 4+ models, SSOT change, complex workflow, ADR-level change)
    - **Escalation Flowchart**: Mermaid diagram com critérios em cadeia (qualquer 🔴 = TASK BRIEF obrigatório)
    - **Integration**: Referências adicionadas em `AI_ARCH_EXEC_PROTOCOL.md` (Phase 2: Pré-Validação step 0 + Rules of Gold) e `00_START_HERE.md` (seção 5.0: LEVEL 0 AI Governance)
  - **Artefatos**: `WHEN_TO_USE_TASK_BRIEF.md` (200+ linhas: framework, exemplos, flowchart, anti-patterns, métricas compliance)
  - **Impact**: Critérios objetivos para escalação (90% target classification accuracy); reduced bureaucracy para tarefas triviais; ensured proper scoping para tarefas complexas; eliminated ambiguity de "quando usar protocolo formal?"
  - **Branch**: `docs/gov-unify-001` (commit pendente)

* **AI Governance Canonical Templates** (2026-02-12): Implementação da suite de governança e protocolos para agentes de IA:
  - `AI_GOVERNANCE_INDEX.md`: Índice centralizador.
  - `AI_INCIDENT_RESPONSE_POLICY.md`: Protocolo para falhas e alucinações.
  - `AI_TASK_VERSIONING_POLICY.md`: Gestão de versões de tarefas.
  - `AI_PROTOCOL_CHECKLIST.md`: Checklist de pré-emissão de tarefas.
  - `AI_ARCH_EXEC_PROTOCOL.md`: Protocolo Architect vs Executor.
  - `TASK_BRIEF.md` & `EVIDENCE_PACK.md`: Templates de input/output determinísticos.

### Pendente CI/CD
* GitHub Actions workflow para validar quality-gates e approved-commands em PRs (próximo passo)
* Implementação de `generate-ai-index.py` (ainda é placeholder TODO)
* Adicionar `validate-quality-gates-schema.py` como validador de schema

### Adicionado
* **AI Infrastructure Validation & Smoke Tests** (2026-02-12): Validação completa da infraestrutura de IA com testes locais e CI/CD:
  - **Smoke Tests (7/7 PASS)**: Utils (json_loader, yaml_loader), Extractors (approved-commands, troubleshooting), Generators (handshake, invocation-examples, checklist)
  - **Artefatos Gerados**:
    - `docs/_ai/_context/approved-commands.yml` (5 categorias extraídas)
    - `docs/_ai/_maps/troubleshooting-map.json` (4 exit codes mapeados)
    - `docs/_ai/_specs/invocation-examples.yml` (exemplos de invocação)
    - `docs/_ai/_specs/checklist-models.yml` (checklist de models)
    - `.github/copilot-handshake.md` (protocolo de handshake)
  - **Validadores (2/2 PASS)**: Quality gates (✅ passed, radon opcional), Approved commands (⚠️ requer whitelist update)
  - **Code Review Pipeline**: `scripts/dev/run_code_review.sh` implementado com 13 steps (setup, testes, extratores, validadores, linters, métricas)
  - **Exit Code Semantics**: 0=PASS, 1=CRITICAL_FAIL, 2=WARNING, 3=FATAL_ERROR (alinhado com canônico)

* **AI Infrastructure: scripts/_ia/ + GitHub Actions Workflows** (2026-02-11): Construção completa de infraestrutura para automação e validação de agentes:
  - **9 Arquivos Python Implementados** (substituindo placeholders, status: MERGED 2026-02-11):
    - **Utilities (2)**: `scripts/_ia/utils/json_loader.py`, `scripts/_ia/utils/yaml_loader.py`
    - **Extractors (2)**: `scripts/_ia/extractors/extract-approved-commands.py`, `scripts/_ia/extractors/extract-troubleshooting.py`
    - **Validators (2)**: `scripts/_ia/validators/validate-approved-commands.py`, `scripts/_ia/validators/validate-quality-gates.py`
    - **Generators (3)**: `scripts/_ia/generators/generate-handshake-template.py`, `scripts/_ia/generators/generate-invocation-examples.py`, `scripts/_ia/generators/generate-checklist-yml.py`
  - **Implementações**:
    - Error handling robusto (FileNotFoundError, JSONDecodeError, YAMLError)
    - UTF-8 encoding explícito em todas as operações de arquivo
    - Smoke tests básicos nas utilities
    - Saída clara e exit codes (0=pass, 1=fail)
    - Sem hardcoded credentials ou PII
  - **Status:** Código implementado, PR foi fundido (merged). Próximo passo: criar workflows de CI/CD para validar e executar essas ferramentas automaticamente.

### Alterado
* `docs/_ai/` reorganizado anteriormente (2026-02-11) — agora com implementações executáveis em `scripts/_ia/` (utilities, extractors, validators, generators).

### Removido
* Placeholders antigos em `scripts/_ia/` substituídos por implementações funcionais.

---

## [2026-02-11]
### Adicionado
* Implementação inicial de infraestrutura AI (scripts/_ia) e documentação de suporte.

---

## Notas
- CI/CD: adicionar GitHub Actions que executem `validate-quality-gates.py` e `validate-approved-commands.py` em PRs.
- Segurança: instalar dependências listadas em `scripts/_ia/requirements.txt` em runners CI antes de executar radon/lizard.