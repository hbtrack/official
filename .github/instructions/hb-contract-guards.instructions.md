---
applyTo: "src/**"
---

# Guarda de elegibilidade de backend — HB Track CDD

Antes de criar ou modificar qualquer arquivo em `src/{module}/`:

## Verificação obrigatória (2 passos)

**Passo 1 — Verificar `docs/_canon/MODULE_REGISTRY.yaml`:**
```yaml
# O módulo precisa estar em implementation_ready ou acima:
status: "implementation_ready"
status: "implemented"
status: "staging_validated"
status: "released"
```

Se o status for `validated_contract` ou inferior → **PARAR e emitir:**
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

## Arquivos explicitamente fora deste escopo

Este guarda aplica-se a **código de módulo em** `src/**`. Os seguintes paths pertencem ao **Modo ROADMAP** (`execute_roadmap_phase`) e não requerem `implementation_ready` nem `ADVERSARIAL_ANALYSIS_GATE`:

- `src/shared/` — middleware e utilitários transversais
- `src/*/tasks.py`, `src/*/consumers.py`, `src/*/middleware.py` — infraestrutura assíncrona / auth / websocket
- `config/` — Celery, ASGI, settings Django
- `infra/` — Docker Compose, Nginx, scripts de deploy
- `Dockerfile` (raiz do repositório)
- `.github/workflows/`
- `frontend/` — React + Vite
- `mobile/` — React Native + Expo
- `scripts/seed.py`, `scripts/hooks/`

Criar esses artefatos diretamente, sem verificações CDD.
