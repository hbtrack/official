---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-14"
status: active
cross_refs:
  system_scope: "docs/_canon/SYSTEM_SCOPE.md"
  spec_completa: "docs/_canon/CI_CONTRACT_GATES.md"
  registry_machine_readable: "docs/_canon/gates/GATES_REGISTRY.yaml"
  implementation: "scripts/contracts/validate/validate_contracts.py"
---

# Gates de Validação — Índice Rápido

Este diretório é o ponto de entrada de navegação para o sistema de gates do HB Track.

**Spec normativa completa**: [`docs/_canon/CI_CONTRACT_GATES.md`](../CI_CONTRACT_GATES.md) — leia esse documento para entender critérios de PASS/FAIL, blocking codes, política de waiver, determinismo e evidências.

**Registry machine-readable**: [`docs/_canon/gates/GATES_REGISTRY.yaml`](./GATES_REGISTRY.yaml) — lista estruturada de todos os gates, verificada pelo pipeline no `REQUIRED_ARTIFACT_PRESENCE_GATE`.

**Implementação**: [`scripts/contracts/validate/validate_contracts.py`](../../../scripts/contracts/validate/validate_contracts.py) — engine Python que executa os gates na ordem canônica.

---

## Tabela de Gates (ordem canônica obrigatória)

| Ordem | Gate ID | Bloqueante | Paralelizável | Descrição resumida | Seção |
|------:|---------|:----------:|:-------------:|--------------------|-------|
| 0 | `AXIOM_INTEGRITY_GATE` | Sim | Não | Valida `.contract_driven/DOMAIN_AXIOMS.json` — integridade estrutural e semântica dos axiomas globais | §9.0 |
| 1 | `PATH_CANONICALITY_GATE` | Sim | Não | Garante que nenhum artefato normativo existe fora do path canônico; bloqueia duplicatas soberanas | §9.1 |
| 2 | `REQUIRED_ARTIFACT_PRESENCE_GATE` | Sim | Não | Presença obrigatória de artefatos globais e por módulo | §9.2 |
| 2A | `MODULE_DOC_CROSSREF_GATE` | Sim | Não | Header YAML canônico nos docs de módulo; cross-refs apontam para paths soberanos | §9.2A |
| 2B | `API_NORMATIVE_DUPLICATION_GATE` | Não (warning) | Não | Detecta duplicação normativa HTTP fora da SSOT `api_rules.yaml` | §9.2B |
| 2C | `OWASP_API_CONTROL_MATRIX_GATE` | Sim | Não | `docs/_canon/security/OWASP_API_CONTROL_MATRIX.yaml` presente, validado por schema, IDs únicos | §9.2C |
| 2D | `MODULE_SOURCE_AUTHORITY_MATRIX_GATE` | Sim | Não | `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml` presente, válido, alinhado com os 16 módulos | §9.2D |
| 2E | `BOUNDARY_USERS_IDENTITY_ACCESS_GATE` | Sim | Não | `users` sem credenciais/auth; `identity_access` sem athlete/profile | §9.2E |
| 2F | `WELLNESS_MEDICAL_BOUNDARY_GATE` | Sim | Não | `wellness` sem diagnóstico/tratamento/prontuário (responsabilidade de `medical`) | §9.2F |
| 2G | `SCOUT_TAXONOMY_GATE` | Sim | Não | Campos de taxonomia em `scout` exigem artefato canônico de taxonomia | §9.2G |
| 2H | `ASYNC_REQUIRED_MODULE_GATE` | Sim | Não | Módulos com OpenAPI paths reais e workflows/eventos exigem Arazzo/AsyncAPI | §9.2H |
| 2I | `EXTERNAL_SOURCE_AUTHORITY_GATE` | Sim | Não | Bloqueia benchmarks externos (XPS/Teamworks) tratados como SSOT | §9.2I |
| 3 | `PLACEHOLDER_RESIDUE_GATE` | Sim | Não | Sem TODO, TBD, placeholders em artefatos prontos | §9.3 |
| 4 | `REF_HERMETICITY_GATE` | Sim | Não | `$ref` dentro do grafo soberano permitido; sem refs para derivados como se fossem fontes | §9.4 |
| 5 | `OPENAPI_ROOT_STRUCTURE_GATE` | Sim | Não | OpenAPI estruturalmente válido via Redocly CLI | §9.5 |
| 6 | `OPENAPI_POLICY_RULESET_GATE` | Sim | Não | Regras normativas HB Track via Spectral + `.spectral.yaml` | §9.6 |
| 7 | `JSON_SCHEMA_VALIDATION_GATE` | Sim | Não | Todos `contracts/schemas/**/*.schema.json` válidos (JSON Schema Draft 2020-12) | §9.7 |
| 8 | `CROSS_SPEC_ALIGNMENT_GATE` | Sim | Não | Coerência semântica cross-artifact: OpenAPI × JSON Schema × AsyncAPI × Arazzo × docs | §9.8 |
| 9 | `CONTRACT_BREAKING_CHANGE_GATE` | Sim | Não | Breaking change HTTP via oasdiff — exige waiver machine-readable com fingerprint SHA-256 | §9.9 |
| 10 | `TRANSFORMATION_FEASIBILITY_GATE` | Sim | Não | Contrato transformável e geração determinística (idempotente) de derivados | §9.10 |
| 11 | `HTTP_RUNTIME_CONTRACT_GATE` | Sim | Não | Schemathesis testa runtime HTTP com seed fixa, reset de estado, fixtures conhecidas | §9.11 |
| 12 | `ASYNCAPI_VALIDATION_GATE` | Sim | Sim (após pré-reqs) | AsyncAPI parser valida documento quando há evento real | §9.12 |
| 13 | `ARAZZO_VALIDATION_GATE` | Sim | Sim (após pré-reqs) | Arazzo parser valida workflows; operationIds existem no OpenAPI | §9.13 |
| 14 | `UI_DOC_VALIDATION_GATE` | Sim | Sim (após pré-reqs) | Storybook build quando houver UI documentada | §9.14 |
| 15 | `DERIVED_DRIFT_GATE` | Sim | Não | Derivados em `generated/` == fonte soberana recompilada; qualquer drift bloqueia | §9.15 |
| 16 | `READINESS_SUMMARY_GATE` | Sim | Não | Sumário final binário — todos os gates bloqueantes aplicáveis PASS = sistema pronto | §9.16 |
| 2J | `DECISION_IR_CONFORMANCE_GATE` | Sim | Não | Valida `MODULE_DECISION_IR` em `.dev/` — bloqueia materialização se IR for ambíguo, incompleto ou não-determinístico | §9.17 |

---

## Entrypoints CLI

```bash
# Executa todos os gates (canônico)
python3 scripts/validate_contracts.py

# Verifica toolchain antes de rodar
source ./setup-env.sh && bash scripts/contract_gates/verify_tools.sh
```

O pipeline gera `_reports/contract_gates/latest.json` (evidência machine-readable obrigatória).

---

## Artefatos relacionados

| Artefato | Papel |
|----------|-------|
| `docs/_canon/CI_CONTRACT_GATES.md` | Spec normativa completa dos 16 gates (SSOT) |
| `docs/_canon/gates/GATES_REGISTRY.yaml` | Registry machine-readable verificado pelo pipeline |
| `scripts/contracts/validate/validate_contracts.py` | Engine Python — implementação dos gates |
| `_reports/contract_gates/latest.json` | Evidência da última execução do pipeline |
| `contracts/_waivers/` | Waivers machine-readable (exceções formais) |
| `.github/workflows/contract-gates.yml` | CI — executa `validate_contracts.py` no GitHub Actions |
| `scripts/git-hooks/pre-commit` | Hook local — executa gates antes de cada commit |

---

*Última revisão: 2026-03-14*
