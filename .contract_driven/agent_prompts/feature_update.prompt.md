---
task_type: feature_update
version: "1.0.0"
status: active
---

# feature_update — Worker de Atualização de Feature em Módulo Existente

> **Escopo:** Atualizar ou adicionar feature em módulo canônico já existente.
> Engloba: revisão de contrato OpenAPI + geração de código derivada (quando aplicável).
> **Não usar para:** novo módulo (`new_module`) ou revisão isolada de contrato sem código (`contract_revision`).

---

## Pré-requisitos obrigatórios

Antes de executar este worker, verificar:

0. **`hb verify` executado** para este módulo: `_reports/session_start.json` com `task_type=feature_update` e `module=<M>`
1. **Módulo canônico** existe em `docs/_canon/MODULE_REGISTRY.yaml` com `status >= implementation_ready`
2. **Feature** existe em `docs/_canon/FEATURE_REGISTRY.yaml` ou é uma nova feature formal a registrar
3. **Contrato OpenAPI** do módulo existe em `contracts/openapi/paths/<module>.yaml`
4. **Source graph** do módulo existe em `docs/hbtrack/modulos/<module>/graph/`
5. **Bundle compilado fresco** existe em `compiled_context/<module>/<feature_id>.json`
   - Se ausente: executar `python3 scripts/compile/compile_context_bundle.py --module <module> --feature <feature_id>` e aguardar PASS
   - Bundle é a única entrada operacional autorizada para esta tarefa (B11-001)

Se qualquer pré-requisito crítico falhar → reportar ao humano e parar.

---

## Input esperado

```
module:      <módulo canônico — ex: users>
feature_id:  <ID da feature — ex: FT-003>
change_type: <extend | fix | deprecate | new_endpoint>
```

---

## Fase FU1 — Diagnóstico do estado atual

1. Ler bundle compilado `compiled_context/<module>/<feature_id>.json`
2. Identificar endpoints afetados pela mudança
3. Verificar invariantes ativos em `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
4. Checar se `change_type=deprecate` exige `CONTRACT_BREAKING_CHANGE_GATE` — se sim, parar e solicitar ADR

```bash
python3 scripts/hb verify --task-type feature_update --module <module>
```

---

## Fase FU2 — Atualização do contrato

Dependendo do `change_type`:

| change_type | Ação no contrato |
|-------------|-----------------|
| `extend` | Adicionar campos/parâmetros opcionais sem quebrar compatibilidade |
| `fix` | Corrigir bug de schema, description ou response code |
| `new_endpoint` | Adicionar novo path/operation ao contrato do módulo |
| `deprecate` | Marcar operação/campo com `deprecated: true` — exige ADR |

Arquivo alvo: `contracts/openapi/paths/<module>.yaml`

Validar após edição:
```bash
python3 scripts/validate_contracts.py --profile ci
```
Bloquear se `OPENAPI_ROOT_STRUCTURE_GATE`, `SPECTRAL_LINTING_GATE` ou `CROSS_SPEC_ALIGNMENT_GATE` falharem.

---

## Fase FU3 — Atualização do source graph (se aplicável)

Se a mudança adiciona ou remove endpoint:
```bash
python3 scripts/compile/compile_source_graph.py --module <module>
python3 scripts/compile/compile_context_bundle.py --module <module> --feature <feature_id>
```

Bloquear se o compiler retornar erro.

---

## Fase FU4 — Código derivado (se `change_type` afeta interface ou domínio)

Para mudanças que afetam `api.py`, `schemas.py` ou `domain/entities.py`:

1. Verificar `ADVERSARIAL_ANALYSIS_GATE` para o endpoint afetado
2. Atualizar `src/<module>/api.py` para refletir o contrato atualizado
3. Atualizar `src/<module>/generated/` via backend_codegen se aplicável
4. Rodar testes:

```bash
pytest src/<module>/tests/ -q --tb=short
pytest tests/parity/test_<module>_codegen_parity.py -q
```

---

## Fase FU5 — Fechamento

```bash
python3 scripts/validate_contracts.py --profile ci   # STATUS: PASS obrigatório
python3 scripts/hb artifact <path_do_artefato_principal>
```

Atualizar `SESSION_HANDOFF.md`:
- `resultado: DONE`
- `proxima_acao_permitida` documentada
- `evidence_paths` com o relatório de gates e o artefato produzido
