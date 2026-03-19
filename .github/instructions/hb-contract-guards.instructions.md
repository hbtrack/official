---
applyTo: "backend/apps/**"
---

# Guarda de elegibilidade de backend — HB Track CDD

Antes de criar ou modificar qualquer arquivo em `backend/apps/{module}/`:

## Verificação obrigatória (2 passos)

**Passo 1 — Verificar `docs/_canon/MODULE_REGISTRY.yaml`:**
```yaml
# O módulo precisa estar em uma destas categorias:
status: "validated_contract"   # mínimo para generate_code
status: "implementation_ready"  # ideal — passou por readiness_promotion
```

Se o status for `draft_contract` ou inferior → **PARAR e emitir:**
```
BLOCKED_REQUIRED_ARTIFACT_MISSING
Módulo '<module>' está em '<status>'.
Para gerar código, siga a sequência:
  1. readiness_promotion (validated_contract → implementation_ready)
  2. adversarial_analysis (ADVERSARIAL_ANALYSIS_GATE=PASS)
  3. generate_code (somente então)
```

**Passo 2 — Verificar `adversarial_analysis`:**
Confirmar que `_reports/contract_gates/latest.json` contém `ADVERSARIAL_ANALYSIS_GATE: PASS`.

## Nunca gere código backend sem esses dois passos verificados.
