## Prompt Operacional — Promover módulo de `implementation_ready` → `implemented`

**Objetivo**: avaliar se um módulo em `implementation_ready` cumpre todos os critérios de
implementação real (testes passando, CI verde, código presente em `src/<module>/`) e, se sim,
promovê-lo formalmente para `implemented` em `docs/_canon/MODULE_REGISTRY.yaml`.

### Leitura mínima obrigatória (ordem)

1. `docs/_canon/MODULE_REGISTRY.yaml` — status atual e módulos canônicos
2. `_reports/contract_gates/latest.json` — pipeline deve estar PASS
3. `_reports/evidence/module_readiness_scorecard.json` — scorecard atual
4. `docs/hbtrack/modulos/<module>/` — artefatos do módulo

### Bloqueios (falhar cedo)

- Se `module` não existir no MODULE_REGISTRY: **bloquear** com `BLOCKED_MISSING_MODULE`.
- Se status atual não for `implementation_ready`: **bloquear** — promover apenas de `implementation_ready`.
- Se pipeline (`latest.json`) não for `PASS`: **bloquear** — nenhuma promoção sem pipeline verde.
- Se `src/<module>/` não existir ou estiver vazio: **bloquear** — código real deve existir.
- Se `tests/<module>/` não tiver testes passando: **bloquear** — cobertura mínima obrigatória.

---

## Fase 1 — Verificação de Pré-Condições

### P1 — Status atual

Ler `docs/_canon/MODULE_REGISTRY.yaml` e confirmar que `modules.<module>.status == implementation_ready`.

### P2 — Pipeline verde

Verificar `_reports/contract_gates/latest.json`.`overall_status == PASS`.
Se não: **bloquear**.

### P3 — Código presente

Verificar que `src/<module>/` existe e tem pelo menos um arquivo Python.
Se não: **bloquear**.

### P4 — Testes passando

Executar `pytest tests/<module>/ -q --tb=short`.
Se falhar: **bloquear**.

---

## Fase 2 — Promoção Formal

### P5 — Atualizar MODULE_REGISTRY.yaml

Alterar `modules.<module>.status` de `implementation_ready` para `implemented`.

### P6 — Registrar evidência

Criar `_reports/evidence/promotion_<module>_<YYYYMMDD>.json`:
```json
{
  "module": "<module>",
  "promoted_from": "implementation_ready",
  "promoted_to": "implemented",
  "date": "<YYYYMMDD>",
  "evidence_ref": "_reports/evidence/module_readiness_scorecard.json",
  "gates_report": "_reports/contract_gates/latest.json"
}
```

### P7 — Commit

Commitar MODULE_REGISTRY.yaml + evidência com mensagem:
`feat(governance): promote <module> to implemented — criteria satisfied`

---

## Output esperado

```
MÓDULO: <module>
STATUS ANTES: implementation_ready
STATUS DEPOIS: implemented
PROMOÇÃO: APROVADA
EVIDÊNCIA: _reports/evidence/promotion_<module>_<YYYYMMDD>.json
```
