## Prompt Operacional — Promover módulo para `released`

**Objetivo**: avaliar se um módulo em `staging_validated` possui evidência operacional e aprovação humana suficientes para promoção formal a `released` em `docs/_canon/MODULE_REGISTRY.yaml`.

Este é o **único caminho formal** para atingir `released`.
Nenhum módulo pode ser marcado como `released` por inferência, por deploy presumido ou por edição manual do registry.

### Leitura mínima obrigatória

1. `docs/_canon/MODULE_REGISTRY.yaml`
2. `docs/_canon/CONTRACT_PIPELINE.md`
3. `docs/_canon/DEPLOY_PIPELINE.md`
4. `_reports/contract_gates/latest.json`
5. `SESSION_HANDOFF.md`

### Bloqueios

- Se `module` não existir no `MODULE_REGISTRY`: `BLOCKED_MISSING_MODULE`
- Se status atual não for `staging_validated`: `BLOCKED_RELEASE_PROMOTION_STATUS`
- Se `_reports/contract_gates/latest.json` não estiver `PASS`: `BLOCKED_PIPELINE_NOT_GREEN`
- Se não houver aprovação humana rastreável: `BLOCKED_RELEASE_APPROVAL_MISSING`
- Se não houver evidência de produção saudável e rollback referenciado: `BLOCKED_RELEASE_EVIDENCE_MISSING`

## Fase 1 — Pré-condições

Confirmar:

- status atual do módulo = `staging_validated`
- `overall_status = PASS`
- aprovação humana registrada para produção
- health check de produção comprovado
- referência de rollback válida

Se qualquer item falhar, bloquear.

## Fase 2 — Relatório ao humano

Apresentar:

```text
📋 Relatório de Promoção — Módulo <MODULE>

✅ Status atual: staging_validated
✅ Pipeline: PASS
✅ Aprovação humana registrada
✅ Evidência de produção: OK
✅ Health check de produção: OK
✅ Referência de rollback: OK

🎯 Conclusão: módulo <MODULE> APROVADO para promoção a `released`.

Confirma a promoção? (sim / não)
```

**AGUARDAR confirmação explícita do humano antes de editar qualquer arquivo.**

## Fase 3 — Execução

Editar `docs/_canon/MODULE_REGISTRY.yaml`:

```yaml
# antes
  <module>:
    status: staging_validated

# depois
  <module>:
    status: released
```

Depois:

```bash
python3 scripts/hb artifact docs/_canon/MODULE_REGISTRY.yaml
python3 scripts/contracts/validate/validate_contracts.py --profile ci
```

O resultado final deve permanecer `PASS`.

## Fase 4 — Handoff

Registrar em `SESSION_HANDOFF.md` que o módulo foi promovido para `released` com aprovação humana, evidência de produção e rollback referenciado.
