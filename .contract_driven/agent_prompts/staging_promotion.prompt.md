## Prompt Operacional — Promover módulo para `staging_validated`

**Objetivo**: avaliar se um módulo em `implemented` possui evidência operacional suficiente para promoção formal a `staging_validated` em `docs/_canon/MODULE_REGISTRY.yaml`.

Este é o **único caminho formal** para atingir `staging_validated`.
Nenhum módulo pode ser marcado como `staging_validated` apenas por existir workflow versionado, por inferência do agente ou por edição manual do registry.

### Leitura mínima obrigatória

1. `docs/_canon/MODULE_REGISTRY.yaml`
2. `docs/_canon/CONTRACT_PIPELINE.md`
3. `docs/_canon/DEPLOY_PIPELINE.md`
4. `_reports/contract_gates/latest.json`
5. `.github/workflows/deploy.yml`
6. `SESSION_HANDOFF.md` (se existir)

### Bloqueios

- Se `module` não existir no `MODULE_REGISTRY`: `BLOCKED_MISSING_MODULE`
- Se status atual não for `implemented`: `BLOCKED_STAGING_PROMOTION_STATUS`
- Se `_reports/contract_gates/latest.json` não estiver `PASS`: `BLOCKED_PIPELINE_NOT_GREEN`
- Se `DEPLOY_READINESS_GATE` não estiver `PASS`: `BLOCKED_DEPLOY_NOT_READY`
- Se não houver evidência de staging live compatível com `DEPLOY_PIPELINE.md`: `BLOCKED_STAGING_EVIDENCE_MISSING`

## Fase 1 — Pré-condições

Confirmar:

- status atual do módulo = `implemented`
- `overall_status = PASS`
- `DEPLOY_READINESS_GATE = PASS`
- `HTTP_RUNTIME_CONTRACT_GATE = PASS` quando aplicável; se o gate estiver `SKIP_NOT_APPLICABLE`, a promoção continua bloqueada até staging real existir
- health check de staging comprovado
- referência de rollback disponível

Se qualquer item falhar, bloquear.

## Fase 2 — Relatório ao humano

Apresentar:

```text
📋 Relatório de Promoção — Módulo <MODULE>

✅ Status atual: implemented
✅ Pipeline: PASS
✅ Deploy readiness: PASS
✅ Evidência de staging: OK
✅ Health check de staging: OK
✅ Referência de rollback: OK

🎯 Conclusão: módulo <MODULE> APROVADO para promoção a `staging_validated`.

Confirma a promoção? (sim / não)
```

**AGUARDAR confirmação explícita do humano antes de editar qualquer arquivo.**

## Fase 3 — Execução

Editar `docs/_canon/MODULE_REGISTRY.yaml`:

```yaml
# antes
  <module>:
    status: implemented

# depois
  <module>:
    status: staging_validated
```

Depois:

```bash
python3 scripts/hb artifact docs/_canon/MODULE_REGISTRY.yaml
python3 scripts/contracts/validate/validate_contracts.py --profile ci
```

O resultado final deve permanecer `PASS`.

## Fase 4 — Handoff

Registrar em `SESSION_HANDOFF.md` que o módulo foi promovido para `staging_validated` com referência explícita à evidência de staging e ao rollback.
