
## Prompt Operacional — Promover módulo para `implementation_ready`

**Objetivo**: avaliar se um módulo em `validated_contract` cumpre todos os critérios de maturidade contratual e, se sim, promovê-lo formalmente para `implementation_ready` em `docs/_canon/MODULE_REGISTRY.yaml`.

Este é o **único caminho formal** para atingir o status que habilita o início de implementação controlada.
`implementation_ready` não descongela `generate_frontend` sozinho; o worker de frontend continua congelado até que o workspace real de frontend exista e passe pelo `FRONTEND_CONTRACT_GATE`.

### Leitura mínima obrigatória (ordem)

1. `docs/_canon/MODULE_REGISTRY.yaml` — status atual e `expected_surfaces` do módulo
2. `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` — decisões abertas do módulo
3. `_reports/contract_gates/latest.json` — resultado dos 44 gates
4. `_reports/evidence/module_readiness_scorecard.json` — scorecard atual
5. `docs/hbtrack/modulos/<module>/` — todos os artefatos do módulo

### Bloqueios (falhar cedo)

- Se `module` não existir no MODULE_REGISTRY: **bloquear** com `BLOCKED_MISSING_MODULE`.
- Se status atual não for `validated_contract`: **bloquear** — a promoção exige que o módulo já tenha passado pela fase de contratos validados.
- Se `overall_status` do `latest.json` não for `PASS`: **bloquear** — nenhuma promoção sem pipeline verde.

---

## Fase 1 — Verificação de Pré-Condições (bloqueante)

### P1 — Status atual do módulo

Ler `docs/_canon/MODULE_REGISTRY.yaml` e confirmar:

| Check | Fonte | Falha |
|---|---|---|
| `status: validated_contract` | MODULE_REGISTRY.yaml | Bloquear: "Módulo X está em `<status_atual>`. A promoção para `implementation_ready` exige status `validated_contract`." |
| `expected_surfaces` listadas | MODULE_REGISTRY.yaml | Registrar a lista completa para verificação nas fases seguintes |

### P2 — Pipeline verde

Verificar `_reports/contract_gates/latest.json`:

| Check | Critério | Falha |
|---|---|---|
| `overall_status` | `PASS` | Bloquear: "O pipeline de contratos está em FAIL. Todos os gates devem passar antes da promoção." |
| `OPENAPI_ROOT_STRUCTURE_GATE` | `PASS` ou `SKIP_NOT_APPLICABLE` | Bloquear se `FAIL` ou `ERROR_INFRA` |
| `DERIVED_DRIFT_GATE` | `PASS` | Bloquear se `FAIL` — artefatos derivados estão desatualizados |

### P3 — Decisões arquiteturais

Ler `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` e filtrar pelo módulo:

| Check | Critério | Falha |
|---|---|---|
| Sem decisões `status: open` ou `status: blocked` para o módulo | BACKLOG | Bloquear: "Existem decisões arquiteturais em aberto para o módulo X: [lista]. Resolver antes de promover." |

---

## Fase 2 — Auditoria de Superfícies

Para cada superfície listada em `expected_surfaces` do módulo, verificar existência e integridade:

### Mapa de superfície → artefato canônico

| Superfície | Artefato esperado | Obrigatório? |
|---|---|---|
| `module_docs_minimum` | `docs/hbtrack/modulos/<module>/README.md` + `DOMAIN_RULES_<MODULE>.md` | Sim |
| `openapi_sync` | `contracts/openapi/paths/<module>.yaml` | Sim se declarado |
| `json_schema` | `contracts/schemas/<module>/*.schema.json` | Sim se declarado |
| `asyncapi` | `contracts/asyncapi/channels/` com eventos do módulo | Sim se declarado |
| `arazzo` | `contracts/workflows/<module>/*.arazzo.yaml` | Sim se declarado |
| `state_model` | `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md` | Sim se declarado |
| `ui_contract` | `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md` | Sim se declarado |
| `permissions` | `docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md` | Sim se declarado |
| `test_matrix` | `docs/hbtrack/modulos/<module>/TEST_MATRIX_<MODULE>.md` | Sim se declarado |
| `decision_ir` | `.contract_driven/decisions/DECISION_IR_<MODULE>.yaml` | Sim se houve architecture_review |
| `sport_science` | `docs/hbtrack/modulos/<module>/SPORT_SCIENCE_RULES_<MODULE>.md` | Sim se declarado |

Para **cada superfície declarada em `expected_surfaces`**:

- [ ] Verificar que o artefato existe no path canônico
- [ ] Verificar que o arquivo não está vazio (`> 0 bytes`)
- [ ] Verificar ausência de placeholders (`TODO`, `[PLACEHOLDER]`, `TBD`, `...`) no conteúdo

Se qualquer superfície falhar → **bloquear** com `BLOCKED_REQUIRED_ARTIFACT_MISSING` e listar o que está faltando.

### S1 — Análise adversarial

Verificar se foi executada para este módulo:

- Checar se existe menção ao módulo em qualquer `SESSION_HANDOFF.md` com `task_type: adversarial_analysis`
- Ou verificar se `_reports/session_start.json` registrou uma sessão de `adversarial_analysis` para o módulo

Se não executada → **bloquear com `BLOCKED_ADVERSARIAL_PENDING`** (operação encerrada):
> "🚫 BLOCKED_ADVERSARIAL_PENDING: Análise adversarial não encontrada para o módulo X. Nenhum módulo pode ser promovido para `implementation_ready` sem que `ADVERSARIAL_ANALYSIS_GATE = PASS`. Execute `adversarial_analysis` para este módulo antes de prosseguir."

---

## Fase 3 — Apresentação ao Humano

Antes de promover, apresentar um relatório de maturidade no formato:

```
📋 Relatório de Maturidade — Módulo <MODULE>

✅ Status atual: validated_contract
✅ Pipeline: PASS (<N> gates verificados)
✅ Decisões abertas: nenhuma

📦 Superfícies verificadas (<N>/<TOTAL>):
  ✅ openapi_sync       → contracts/openapi/paths/<module>.yaml
  ✅ asyncapi           → <N> eventos registrados
  ✅ state_model        → STATE_MODEL_<MODULE>.md
  ✅ ui_contract        → UI_CONTRACT_<MODULE>.md
  ✅ decision_ir        → DECISION_IR_<MODULE>.yaml
  [...]

⚠️ Avisos (não bloqueantes):
  - [lista ou "nenhum"]

🎯 Conclusão: módulo <MODULE> APROVADO para promoção a `implementation_ready`.

Confirma a promoção? (sim / não)
```

**AGUARDAR confirmação explícita do humano antes de editar qualquer arquivo.**

### Gate técnico de confirmação humana (6-001 — READINESS_HUMAN_CONFIRMATION_GATE)

**Antes de aceitar o "sim" do humano como confirmação válida**, executar este protocolo anti-rubber-stamp:

1. **Formular 1 pergunta técnica** sobre o conteúdo real do módulo — derivada de uma das superfícies verificadas. Exemplos:
   - "Quantos eventos AsyncAPI foram registrados para este módulo?"
   - "Qual é o valor do campo obrigatório X no schema Y deste módulo?"
   - "O módulo tem STATE_MODEL? Se sim, quantos estados estão definidos?"
   - "Qual ADR rege o design de autenticação deste módulo?"

2. **Aguardar resposta do humano.**

3. **Verificar coerência da resposta** contra os artefatos reais inspecionados na Fase 2:
   - ✅ Resposta coerente (coincide com artefato real) → registrar confirmação como **HUMANO_CONFIRMADO = true**
   - ❌ Resposta incoerente ou evasiva (ex: "não sei", resposta errada) → rejeitar promoção com: `"🚫 Confirmação não-aceita: resposta não corresponde ao conteúdo real do módulo. Revise os artefatos e responda novamente."`

4. **Só avançar para Fase 4 após HUMANO_CONFIRMADO = true.**

> **Justificativa:** Este gate garante que confirmação humana seja substantiva, não formal. Previne a falha sistêmica onde o humano aprova sem ter lido o relatório (Parte 2 — Falha: "Confirmação humana como rubber stamp").

---

## Fase 4 — Execução da Promoção (após confirmação)

### PRE-CHECK — Gate READINESS_GENERATION_COMPATIBILITY_GATE

Antes de efetuar qualquer alteração de arquivo, verificar que o módulo satisfaz TODOS os bloqueadores de `generate_code`:

| Condição | Como verificar | Ação se falhar |
| --- | --- | --- |
| `ADVERSARIAL_ANALYSIS_GATE = PASS` | Conferir `_reports/adversarial/<module>.json` | Bloquear — retornar à Fase 1 de adversarial |
| Sem decisões `status: open` que referenciem geração de código | Verificar BACKLOG e SESSION_HANDOFF | Bloquear — resolver decisões antes de prosseguir |
| Sem `BLOCKED_MISSING_ARCH_DECISION` ativo no último `hb verify` | Conferir `_reports/contract_gates/latest.json` | Bloquear — resolver decisão arquitetural |

Se qualquer condição falhar → **bloquear promoção com `READINESS_GENERATION_COMPATIBILITY_GATE = FAIL`**. Não editar nenhum arquivo. Informar o humano sobre o bloqueio e retornar à etapa anterior.

### A — Atualizar MODULE_REGISTRY.yaml

Editar `docs/_canon/MODULE_REGISTRY.yaml`:

```yaml
# antes:
  <module>:
    status: "validated_contract"

# depois:
  <module>:
    status: "implementation_ready"
```

Manter todos os outros campos intactos (`owner`, `expected_surfaces`, etc.).

### B — Atualizar scorecard

Editar `_reports/evidence/module_readiness_scorecard.json`:

- Localizar a entrada do módulo
- Atualizar `"status"` para `"implementation_ready"`
- Adicionar campo `"promoted_at": "<YYYY-MM-DDTHH:MM:SSZ>"`

### C — Executar hb artifact para o registry

```bash
python3 scripts/hb artifact docs/_canon/MODULE_REGISTRY.yaml
```

### D — Revalidar pipeline

```bash
python3 scripts/contracts/validate/validate_contracts.py
```

Confirmar que `overall_status` continua `PASS`.

---

## Fase 5 — Handoff

Emitir ao humano:

```
✅ Módulo <MODULE> promovido para `implementation_ready`.

Isso significa:
- Os contratos do módulo estão maduros e prontos para implementação
- O worker `generate_code` pode ser ativado para este módulo, desde que a elegibilidade de geração continue PASS
- O worker `generate_frontend` continua dependente de `frontend/` real, toolchain versionada e `FRONTEND_CONTRACT_GATE`

Próximos passos sugeridos:
1. Verificar se `generate_code` continua elegível para este módulo
2. Só avaliar `generate_frontend` quando o workspace frontend existir e o gate correspondente sair de SKIP
```

Atualizar `SESSION_HANDOFF.md` com a promoção registrada.
