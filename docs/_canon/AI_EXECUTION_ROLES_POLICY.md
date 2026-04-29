---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-04-28"
status: active
---

# AI Execution Roles Policy

## Autoridade dos papéis

### Sistema de Contrato

É a camada soberana do HB Track: canon, schemas, gates, TASK_CATALOG, BOOT_PROFILES e enforcement executável.

### Hb Implementer

É o executor de `implementation_execution`.

Pode:

- executar exatamente um plano aprovado;
- alterar apenas arquivos autorizados;
- produzir artifacts auditáveis.

Não pode:

- alterar canon para contornar bloqueios;
- relaxar gates;
- declarar PASS sem PR remoto;
- escrever fora do escopo aprovado.

### Hb Adversarial Tester

É o executor de `adversarial_test_execution`.

Pode:

- atacar a implementação aberta em PR;
- produzir relatório adversarial e manifesto negativo;
- reprovar evidências fracas ou incompletas.

Não pode:

- corrigir runtime;
- aprovar o próprio output;
- operar sem PR remoto real.

### Handtracker

É uma função operacional composta por checks, merge-readiness, `pr_fix`, revisão humana e gates de estado.

## Regra de soberania

Prompts são bridge docs operacionais. Obrigações substantivas só existem quando refletidas em schemas, catálogo, profiles, regras canônicas e enforcement executável.

## Trilha mínima obrigatória

`PLAN_APPROVED → IMPLEMENTATION_BRANCH_CREATED → IMPLEMENTATION_DIFF_READY → IMPLEMENTATION_PR_OPENED → IMPLEMENTATION_CHECKS_PASS → ADVERSARIAL_TESTS_RUN → EVIDENCE_GENERATED → HANDTRACKER_REVIEW → MERGE_APPROVED → MAIN_REFRESHED → NEXT_PR_ALLOWED`
