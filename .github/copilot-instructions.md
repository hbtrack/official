# HB TRACK — Copilot Instructions

## Produto
HB Track — plataforma de gestão esportiva para handebol.
CDD (Contract-Driven Development): contratos governam autoria antes de código.
Comunicar em português claro.

## Fontes de verdade
- `docs/_canon/AGENT_INSTRUCTIONS.md`
- `docs/_canon/CONTRACT_PIPELINE.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- `.contract_driven/TASK_CATALOG.yaml`
- `.contract_driven/BOOT_PROFILES.yaml`
- `docs/_canon/MODULE_REGISTRY.yaml`
- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `scripts/hb`
- `scripts/contracts/validate/validate_contracts.py`

## Regra de boot
1. Se existir `SESSION_HANDOFF.md` na raiz, ler antes de qualquer ação.
2. Se não existir, continuar como sessão nova; não inventar contexto ausente.

## Regra operacional para tarefas de contrato

Para tarefas que criam ou alteram artefatos governados:

```text
BOOT     -> ler AGENT_INSTRUCTIONS + SESSION_HANDOFF.md se existir
FASE 0   -> python3 scripts/hb verify --task-type <T> --module <M>
FASE 1   -> python3 scripts/hb check --module <M>
FASE 2   -> ler worker prompt -> criar artefatos -> python3 scripts/hb artifact <path>
COMPILE  -> compile_api_policy.py somente quando contrato/policy mudou
FASE 3   -> python3 scripts/contracts/validate/validate_contracts.py
FASE 4+  -> readiness/adversarial/generate_code somente se o task_type ou pré-condições exigirem
FECHAMENTO -> atualizar SESSION_HANDOFF.md
VCS      -> commit opcional conforme objetivo da sessão; o pre-commit adiciona um checkpoint extra
```

## Sem falsa autonomia

- Worker = prompt especializado carregado pelo mesmo agente.
- Não assumir subagente autônomo, fila ou runtime distribuído.
- Não assumir que commit é o que faz os gates rodarem; os gates já rodam via `hb` e `validate_contracts.py`.

## Handoff

- `SESSION_HANDOFF.md` é o handoff operacional atual.
- O schema `contracts/schemas/shared/session_handoff.schema.json` não deve ser tratado como o validador ativo do markdown operacional.

## Bloqueios canônicos

Quando houver `BLOCKED_*`, informar o humano em português:
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_MISSING_AGENT_PROMPT`
- `BLOCKED_REQUIRED_ARTIFACT_MISSING`
- `BLOCKED_MISSING_ARCH_DECISION`
- `BLOCKED_SCOPE_OVERFLOW`
- `BLOCKED_CONTRACT_CONFLICT`

## Regras de ouro

- Nunca pular `hb verify` antes de authoring.
- Nunca criar artefato fora de path canônico.
- Sempre registrar artefato com `hb artifact`.
- Sempre ler o worker prompt correspondente.
- Sempre atualizar `SESSION_HANDOFF.md` ao fechar a sessão.
- Nunca reescrever a força dos gates por conveniência.
- Nunca usar comandos destrutivos de git (`reset`, `rebase`, `commit --amend`) para mascarar estado.
