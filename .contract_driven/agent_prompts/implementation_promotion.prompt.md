## Prompt Operacional — Promover módulo para `implemented`

**Objetivo**: avaliar se um módulo em `implementation_ready` já materializou código, runtime, testes e cobertura de feature suficientes para ser promovido formalmente para `implemented` em `docs/_canon/MODULE_REGISTRY.yaml`.

Este é o **único caminho formal** para atingir `implemented`.
Nenhum módulo pode ser marcado como `implemented` apenas por edição manual do registry, por conveniência operacional ou por inferência do agente.

### Leitura mínima obrigatória (ordem)

1. `docs/_canon/MODULE_REGISTRY.yaml` — status atual e superfícies esperadas do módulo
2. `docs/_canon/FEATURE_REGISTRY.yaml` — cobertura mínima de feature em status `implemented`
3. `docs/_canon/CONTRACT_PIPELINE.md` — lifecycle oficial
4. `docs/_canon/CODE_ARCHITECTURE.md` — layout canônico de código
5. `_reports/contract_gates/latest.json` — status atual do pipeline
6. `_reports/adversarial/<module>/ALL.adversarial.json` — evidência adversarial do módulo
7. `src/<module>/` — runtime materializado
8. `docs/hbtrack/modulos/<module>/` — documentação do módulo

### Bloqueios (falhar cedo)

- Se `module` não existir no `MODULE_REGISTRY`: **bloquear** com `BLOCKED_MISSING_MODULE`.
- Se status atual não for `implementation_ready`: **bloquear** com `BLOCKED_IMPLEMENTATION_PROMOTION_STATUS`.
- Se `_reports/contract_gates/latest.json` não estiver `PASS`: **bloquear** com `BLOCKED_PIPELINE_NOT_GREEN`.
- Se não existir evidência adversarial `PASS` para o módulo: **bloquear** com `BLOCKED_ADVERSARIAL_PENDING`.

---

## Fase 1 — Verificação de Pré-Condições

### P1 — Status do módulo

Confirmar em `docs/_canon/MODULE_REGISTRY.yaml`:

| Check | Critério | Falha |
| --- | --- | --- |
| status atual | `implementation_ready` | `BLOCKED_IMPLEMENTATION_PROMOTION_STATUS` |
| owner | presente | `BLOCKED_MISSING_OWNER` |
| expected_surfaces | lista não-vazia | `BLOCKED_MISSING_EXPECTED_SURFACES` |

### P2 — Pipeline e gates

Confirmar em `_reports/contract_gates/latest.json`:

| Check | Critério | Falha |
| --- | --- | --- |
| `overall_status` | `PASS` | `BLOCKED_PIPELINE_NOT_GREEN` |
| `CODE_ARCHITECTURE_GATE` | `PASS` | `BLOCKED_CODE_ARCHITECTURE_GATE` |
| `FEATURE_COVERAGE_GATE` | `PASS` ou módulo elegível após atualização confirmada | `BLOCKED_FEATURE_COVERAGE` |
| `ADVERSARIAL_ANALYSIS_GATE` | `PASS` | `BLOCKED_ADVERSARIAL_PENDING` |

### P3 — Evidência de implementação real

Verificar em `src/<module>/`:

- `api.py`
- `schemas.py`
- `tests/` com testes reais do módulo
- superfícies adicionais exigidas por `CODE_ARCHITECTURE.md` e pelo módulo

Se o módulo estiver no piloto de codegen determinístico, verificar também:

- `src/<module>/generated/`
- paridade verde entre camada canônica e camada gerada

Se faltar qualquer superfície obrigatória → **bloquear** com `BLOCKED_IMPLEMENTATION_EVIDENCE_MISSING`.

### P4 — Cobertura mínima de feature

Verificar em `docs/_canon/FEATURE_REGISTRY.yaml`:

- existe ao menos uma feature do módulo com `status: implemented`

Se não existir → **bloquear** com `BLOCKED_FEATURE_IMPLEMENTED_MISSING`.

### P5 — Decisão arquitetural pendente

Verificar backlog/ADRs aplicáveis ao módulo:

- não pode existir decisão bloqueante aberta para a implementação materializada

Se existir → **bloquear** com `BLOCKED_MISSING_ARCH_DECISION`.

---

## Fase 2 — Relatório ao humano

Apresentar relatório objetivo:

```text
📋 Relatório de Promoção — Módulo <MODULE>

✅ Status atual: implementation_ready
✅ Pipeline: PASS
✅ Adversarial: PASS
✅ Código materializado em src/<module>/
✅ Testes reais presentes
✅ Feature coverage mínima: OK

⚠️ Avisos:
  - [lista ou "nenhum"]

🎯 Conclusão: módulo <MODULE> APROVADO para promoção a `implemented`.

Confirma a promoção? (sim / não)
```

**AGUARDAR confirmação explícita do humano antes de editar qualquer arquivo.**

### Gate técnico de confirmação humana

Antes de aceitar a confirmação:

1. Formular **1 pergunta técnica verificável** sobre a implementação real do módulo.
2. Aguardar resposta do humano.
3. Verificar coerência da resposta contra artefatos reais.
4. Só avançar se a resposta estiver correta.

Resposta incoerente → **bloquear** com `BLOCKED_HUMAN_CONFIRMATION_INVALID`.

---

## Fase 3 — Execução da promoção

### A — Atualizar MODULE_REGISTRY

Editar `docs/_canon/MODULE_REGISTRY.yaml`:

```yaml
# antes
  <module>:
    status: implementation_ready

# depois
  <module>:
    status: implemented
```

Sem alterar `owner` ou `expected_surfaces`.

### B — Registrar o artefato no fluxo

```bash
python3 scripts/hb artifact docs/_canon/MODULE_REGISTRY.yaml
```

### C — Revalidar o pipeline completo

```bash
python3 scripts/contracts/validate/validate_contracts.py --profile ci
```

O resultado final deve permanecer `PASS`.

---

## Fase 4 — Handoff

Emitir:

```text
✅ Módulo <MODULE> promovido para `implemented`.

Isso significa:
- O runtime canônico do módulo existe em `src/<module>/`
- Há testes reais do módulo
- O módulo tem cobertura mínima de feature em `FEATURE_REGISTRY.yaml`
- O lifecycle pode seguir para `staging_validated` somente via promoção formal seguinte
```

Atualizar `SESSION_HANDOFF.md` com a promoção registrada.
