---
doc_type: canon
version: "1.1.0"
last_reviewed: "2026-03-16"
status: active
---

# TOOLCHAIN_HEALTH_POLICY.md

## 0. Objetivo

Definir a política canônica de saúde da toolchain do pipeline contract-driven do HB Track.

Esta policy separa:
- erro de configuração/tooling;
- erro semântico de contrato;
- degradação local explicitamente permitida;
- evidência obrigatória de execução.

Ela não substitui:
- o que é obrigatório em `RULES`;
- quando o estágio acontece em `CONTRACT_PIPELINE.md`;
- como o gate bloqueia em `GATES_REGISTRY.yaml`.

---

## 1. Ferramentas obrigatórias por superfície

| Superfície | Ferramenta | Obrigatória em CI | Permitido `DEGRADED` local |
| --- | --- | :---: | :---: |
| OpenAPI estrutura | `redocly` | sim | não |
| OpenAPI ruleset | `spectral` | sim | não |
| Breaking change HTTP | `oasdiff` | sim | sim |
| Runtime HTTP | `schemathesis` | sim | sim |
| AsyncAPI | `@asyncapi/cli` | sim | não |

Regra:
- ausência de ferramenta obrigatória em CI resulta em `FAIL`;
- ausência de `oasdiff` ou `schemathesis` fora de CI pode gerar `DEGRADED`, nunca `PASS` silencioso;
- erro semântico do contrato não pode ser reportado pelo gate de tooling.

## 1A. Modelo de consumo pelo agente

| Artefato | Classe de leitura | Uso permitido |
| --- | --- | --- |
| `docs/_canon/TOOLCHAIN_HEALTH_POLICY.md` | `boot_condicional` | tasks que executam validação, readiness, handoff ou health-check pré-worker |
| `TOOLING_CONFIG_GATE` | `gate_only` | auditoria local, CI e validação automática |

Regra:
- o agente só pode usar `DEGRADED` nos casos previstos nesta policy;
- prompt nenhum pode inventar exceção local fora desta policy;
- health-check de tooling não substitui validação semântica do contrato.

---

## 2. Timeouts e health-check pré-worker

- `redocly`, `spectral`, `asyncapi`: timeout máximo de 10 segundos por invocação local do gate.
- `oasdiff`: timeout máximo de 10 segundos.
- `schemathesis`: timeout explícito por execução e seed fixa obrigatória.

Antes de qualquer worker pré-contrato:
1. verificar disponibilidade do prompt de destino;
2. verificar `TOOLING_CONFIG_GATE`;
3. carregar esta policy quando o perfil de boot indicar validação, readiness ou handoff;
4. registrar o resultado em evidência machine-readable.

---

## 3. Estado `DEGRADED`

`DEGRADED` só é permitido em auditoria local.

Condição válida:
- fallback local por ausência de `oasdiff`; ou
- ausência de `schemathesis` fora de CI.

Condição inválida:
- usar `DEGRADED` para mascarar erro de schema, OpenAPI inválido, refs quebrados ou config incompatível.

Quando `DEGRADED` ocorrer, o relatório deve expor:
- ferramenta ausente;
- estágio afetado;
- motivo do fallback;
- ação corretiva.

---

## 4. Evidência obrigatória

Toda execução do pipeline deve produzir:
- `_reports/contract_gates/latest.json`
- `_reports/evidence/module_readiness_scorecard.json`

Quando a fase pré-contrato for executada, produzir também:
- `_reports/agent_execution/<timestamp>_<session>.json`

Quando houver resolução de boot, produzir:
- `_reports/evidence/boot_resolution_report.json`

Regra:
- a evidência deve deixar claro se a policy foi lida em `boot_condicional` ou aplicada apenas por gate;
- `DEGRADED` local sem evidência explícita deve ser tratado como não conforme.

---

## 5. Ações corretivas mínimas

- drift de config/tooling → corrigir `package.json`, `redocly.yaml` ou instalação local;
- mudança em input global → rodar `python3 scripts/contracts/validate/api/compile_api_policy.py --all`;
- `DEGRADED` local → instalar a ferramenta ausente antes de promover o contrato.
