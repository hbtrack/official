---
doc_type: canon
version: "1.0.0"
status: active
created: "2026-04-27"
last_reviewed: "2026-04-27"
authority: docs/_canon/DECISION_MATERIALIZATION_POLICY.md
depends_on:
  - docs/_canon/DECISION_POLICY.md
  - docs/_canon/CONTRACT_PIPELINE.md
  - docs/_canon/MODULE_REGISTRY.yaml
  - docs/_canon/gates/GATES_REGISTRY.yaml
---

# Política de Materialização de Decisões — HB Track

Esta política não cria nova fonte semântica. Ela cria uma camada operacional derivada para provar que decisões aprovadas em ADR + Decision IR foram materializadas em runtime, testes adversariais, gates e evidência fresca pós-main.

---

## 1. Objetivo

Impedir que o pipeline aceite "artefato contratual correto" como proxy de "decisão arquitetural viva no runtime".

O sistema deve exigir prova explícita de materialização de decisões arquiteturais aprovadas, conectando:

```
ADR / canon substantivo
→ Decision IR soberana
→ matriz operacional derivada (esta política)
→ runtime obligations
→ testes adversariais negativos
→ testes positivos
→ gate executável (DECISION_MATERIALIZATION_GATE)
→ relatório fresco pós-main
→ PASS agregado
```

Sem essa cadeia completa, feature work em módulo com decisão crítica não materializada é bloqueado.

---

## 2. Cadeia de Autoridade

Esta política não cria nova SSOT semântica. A fonte semântica permanece:

1. **Canon substantivo:** ADRs aceitas, `DECISION_POLICY.md`, `CONTRACT_PIPELINE.md`, `MODULE_REGISTRY.yaml`, artefatos canônicos do módulo.
2. **Decision IR soberana:** `.contract_driven/decisions/DECISION_IR_<MODULE>.yaml`
3. **Contratos/schemas ativos**, conforme hierarquia declarada no pipeline.
4. **Decision Materialization Matrix** — camada operacional derivada (este sistema).
5. **Enforcement técnico:** gate, validator, checklist, CI.

**Regra de conflito:** se enforcement técnico divergir do canon ou da Decision IR soberana, o resultado obrigatório é `FAIL_CANON_ENFORCEMENT_DRIFT`. O gate obedece ao canon. O gate não prevalece sobre o canon.

---

## 3. Fonte Soberana da Decision IR

Para qualquer matriz de materialização, `source_decision_ir` deve apontar para:

```
.contract_driven/decisions/DECISION_IR_<MODULE>.yaml
```

É **proibido** usar como fonte soberana:

```
docs/hbtrack/modulos/**/DECISION_IR_*.yaml
```

Violação obrigatória: `NON_SOVEREIGN_DECISION_IR_SOURCE`.

Para o módulo `training`, a fonte correta é:

```
.contract_driven/decisions/DECISION_IR_TRAINING.yaml
```

O espelho `docs/hbtrack/modulos/training/DECISION_IR_TRAINING.yaml` é legado/não soberano e não pode ser usado como `source_decision_ir`.

---

## 4. Formato da Matriz

A matriz de materialização é um artefato YAML derivado e operacional localizado em:

```
.contract_driven/decisions/materialization/DECISION_MATERIALIZATION_<MODULE>.yaml
```

Template canônico: `docs/_canon/templates/DECISION_MATERIALIZATION_MATRIX.template.yaml`

Campos obrigatórios no nível raiz:

| Campo | Tipo | Descrição |
|---|---|---|
| `module` | string | Nome do módulo (lowercase) |
| `source_decision_ir` | path | Path soberano da Decision IR |
| `source_adr` | list[path] | ADRs que originam as decisões |
| `freshness` | object | Rastreabilidade de freshness contra main |
| `decisions` | list | Lista de decisões com prova por camada |

Campos obrigatórios por decisão:

| Campo | Tipo | Descrição |
|---|---|---|
| `decision_id` | string | ID canônico da decisão |
| `decision_policy_criticality` | enum | `obrigatoria` \| `importante` \| `opcional` |
| `execution_priority` | enum | P0 \| P1 \| P2 \| P3 |
| `canonical_source` | path#anchor | Localização canônica da decisão |
| `decision_ir_refs` | object | Referências no IR soberano |
| `runtime_obligations` | list | Obrigações de comportamento runtime |
| `required_runtime_artifacts` | list | Artefatos runtime obrigatórios |
| `required_behavior_tests_negative` | list | Testes adversariais negativos |
| `required_behavior_tests_positive` | list | Testes comportamentais positivos |
| `enforcement_gate` | string | Gate que executa o enforcement |
| `materialization_status` | enum | Ver §5 |
| `blocks_feature_work` | bool | Se bloqueia feature work quando não materializado |
| `waiver` | object\|null | Waiver ativo quando aplicável |

---

## 5. Estados de Materialização

| Status | Condição de uso |
|---|---|
| `materialized` | Todas as camadas passam: runtime artifact, runtime obligations, testes negativos, testes positivos, gate PASS, relatório fresco. |
| `partially_materialized` | Há materialização real em algumas camadas, mas falta ao menos uma camada obrigatória. |
| `not_materialized` | Não há runtime artifact ou prova comportamental mínima. |
| `blocked_by_contract_conflict` | Há conflito canônico documentado que impede a materialização. |
| `deferred_with_reason` | Adiamento formal com `reason`, `owner` e `resume_condition` ou `expires_at_utc`. |
| `not_applicable_with_reason` | Decisão não se aplica ao módulo ou escopo, com justificativa verificável. |

**Regra crítica:** `materialized` somente é permitido quando **todas** as seguintes camadas passam:
- `canonical_source` resolve
- `sovereign_decision_ir` existe e é soberana
- `decision_ir_refs` resolvem para artefatos existentes
- `runtime_artifacts` existem no filesystem
- `runtime_obligations` estão implementadas
- `negative_tests` existem e passam
- `positive_tests` existem e passam
- `enforcement_gate` retorna PASS
- `fresh_report` está atualizado contra o SHA da main

Se qualquer camada faltar, **nunca** pode ser `materialized`.

---

## 6. Criticidade Normativa vs Prioridade Operacional

`decision_policy_criticality` vem da política canônica e da Decision IR soberana — não pode ser alterada na matriz.

`execution_priority` (P0/P1/P2/P3) é operacional e reflete urgência de remediação:
- **P0** — bloqueia qualquer feature work no módulo
- **P1** — bloqueia feature work no contexto específico da decisão
- **P2** — registrado, não bloqueia imediatamente
- **P3** — informativo, sem impacto de bloqueio

---

## 7. Waivers

Waivers de `DECISION_MATERIALIZATION_GATE` são armazenados em:

```
contracts/_waivers/DECISION_MATERIALIZATION_GATE/<module>/<decision_id>.yaml
```

Campos mínimos obrigatórios:

```yaml
waiver_id: DECISION_MATERIALIZATION_GATE-<module>-<decision_id>-<date>
module: <module>
decision_id: <DECISION-ID>
gate_id: DECISION_MATERIALIZATION_GATE
reason: "<justificativa>"
allowed_status: <blocked_by_contract_conflict|deferred_with_reason>
approved_by: "<human>"
approved_at_utc: "<ISO 8601>"
expires_at_utc: "<ISO 8601>"
scope:
  - "<path>"
allowed_changed_files:
  - "<glob>"
notes: "<notas>"
```

Waiver sem `expires_at_utc`, `approved_by` e `scope` é inválido.

---

## 8. Changed-Files Determinístico

O `DECISION_MATERIALIZATION_GATE` não pode depender de inferência implícita de quais arquivos mudaram.

- **Em CI de PR:** usa `GITHUB_BASE_REF` + `GITHUB_SHA` + `github.event.pull_request.base.sha`.
- **Em execução local:** usa `--changed-files <path>` com lista determinística.
- **Sem diff:** opera em `mode: full_scan` — varre todos os módulos com matriz existente.

---

## 9. Freshness

Um relatório é `FRESH` quando `report.main_ref == base SHA` da main no momento da execução.

Em CI:
```
fresh = report.main_ref == github.event.pull_request.base.sha
```

Em local:
```
fresh = report.main_ref == git rev-parse origin/main
```

Se `origin/main` não existir: `freshness_status: UNKNOWN` → `status: FAIL_DECISION_MATERIALIZATION`.

---

## 10. Relatório Granular

Path:
```
_reports/decision_materialization/<module>.json
```

O relatório deve conter:
- `module`, `status`, `truth_scope`, `main_ref`, `generated_at_utc`, `freshness_status`
- `source_decision_ir` (path soberano)
- `decisions_total`, `summary` (contagem por status)
- `decisions[]` com prova por camada e `blocking_reasons`

O relatório deve alimentar:
- `_reports/contract_gates/latest.json`
- `_reports/pipeline_health.json`
- `_reports/evidence/module_readiness_scorecard.json`

**Regra:** PASS geral é impossível se `DECISION_MATERIALIZATION_GATE != PASS`, salvo `SKIP_NOT_APPLICABLE` com justificativa verificável.

---

## 11. Integração com PASS Geral

| Situação | Status do pipeline |
|---|---|
| Todas as camadas PASS | `PASS` |
| Estrutura/contrato OK, decisão crítica não provada no runtime | `PARTIAL_PASS_STRUCTURAL_ONLY` |
| Decisão crítica `blocks_feature_work=true` não materializada e PR toca produto | `FAIL_DECISION_MATERIALIZATION` |
| Gate/validator contradiz canon ou Decision IR | `FAIL_CANON_ENFORCEMENT_DRIFT` |

---

## 12. Sequência de Implementação (PRs 1–4)

Esta política é introduzida na sequência:

| PR | Nome | Objetivo |
|---|---|---|
| PR 1 | `DECISION_MATERIALIZATION_CANON_BOOTSTRAP` | Política, template, registro canônico, matriz inicial de training. Gate `deferred`. |
| PR 2 | `DECISION_MATERIALIZATION_GATE` | Implementar enforcement executável. Gate `active`. |
| PR 3 | `TRAINING_DECISION_MATERIALIZATION_BACKFILL` | Classificar honestamente as decisões críticas de training. |
| PR 4 | `TRAINING_RUNTIME_REMEDIATION` | Corrigir comportamento runtime de training. |

Não pular PRs. Não juntar PRs.

---

## 13. Cláusula de Bootstrap Canônico

Todo PR que introduz novo artefato canônico em `docs/_canon/` deve atualizar simultaneamente:

1. `docs/_canon/README.md`, na tabela de Artefatos Canônicos Globais.
2. A allowlist implementada pelo `CANON_ALLOWLIST_GATE` em `validate_contracts.py`.
3. `docs/_canon/gates/GATES_REGISTRY.yaml`, se `DECISION_MATERIALIZATION_GATE` for registrado como `deferred` ou `active`.

Se qualquer camada faltar, o PR deve falhar com `CANON_REGISTRATION_INCOMPLETE`.
