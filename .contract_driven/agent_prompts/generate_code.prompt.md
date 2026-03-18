---
task_type: generate_code
version: "1.0.0"
status: FROZEN
frozen_reason: "Backend paths não canonizados - awaiting real workspace structure"
requires: [ADR-026, CODE_ARCHITECTURE.md, ADVERSARIAL_ANALYSIS_GATE=PASS]
stack: python_fastapi_postgresql
---

# generate_code — Worker de Geração de Código

⚠️ **WORKER CONGELADO** ⚠️

Este worker está temporariamente congelado até que:
1. A estrutura real de backend seja implementada no workspace (src/<module>/)
2. CODE_ARCHITECTURE.md seja validado empiricamente
3. ADVERSARIAL_ANALYSIS_GATE esteja PASS para o módulo alvo

**Não executar este worker até implementação da estrutura src/<module>/ no workspace.**

---

## Pré-requisitos obrigatórios

Antes de executar este worker, verificar:

1. **ADR-026** existe em `docs/_canon/decisions/`
2. **CODE_ARCHITECTURE.md** existe em `docs/_canon/`
3. **ADVERSARIAL_ANALYSIS_GATE** PASS para o módulo/recurso alvo
4. **Contrato OpenAPI** do módulo existe e está validado (gate OPENAPI_ROOT_MODULE_SYNC_GATE PASS)
5. **JSON Schemas** do módulo existem em `contracts/schemas/<module>/`

Se qualquer pré-requisito estiver ausente → emitir bloqueio correspondente e parar.

---

## Input esperado

```
module:    <módulo canônico — ex: training>
feature:   <feature do FEATURE_REGISTRY — ex: FT-001>
layer:     <camada a gerar: domain | application | infrastructure | interface | all>
```

---

## Fase GC1 — Montagem de Contexto

Carregar **apenas** os artefatos necessários para o módulo/feature alvo:

```python
# Artefatos a carregar (on-demand, não todos de uma vez)
contracts/openapi/paths/<module>.yaml          # endpoints do módulo
contracts/schemas/<module>/                    # schemas JSON
docs/hbtrack/modulos/<module>/
  DOMAIN_RULES_<MODULE>.md                    # regras de negócio
  INVARIANTS_<MODULE>.md                      # invariantes
  STATE_MODEL_<MODULE>.md                     # FSM (se aplicável)
  PERMISSIONS_<MODULE>.md                     # RBAC
docs/_canon/FEATURE_REGISTRY.yaml             # feature → endpoints
_reports/adversarial/<module>/<resource>.adversarial.json  # resultado adversarial
```

---

## Fase GC2 — Geração da Camada Domain

Para cada entidade identificada no contrato e schemas:

```python
# src/<module>/domain/entities.py
class <Entity>(BaseModel):
    """
    Entidade: <Entity>
    Módulo: <module>
    Contrato: contracts/schemas/<module>/<entity>.schema.json
    """
    id: UUID
    # ... campos derivados do JSON Schema
    
    def validate_invariants(self) -> None:
        """Enforce INVARIANTS_<MODULE>.md"""
        # invariantes implementados aqui, nunca no router
```

Para entidades com FSM (STATE_MODEL presente):

```python
# domain/state_machine.py
from enum import Enum

class <Entity>Status(str, Enum):
    # estados derivados do STATE_MODEL_<MODULE>.md
    
class <Entity>StateMachine:
    TRANSITIONS = {
        # transições válidas do STATE_MODEL
    }
    
    @classmethod
    def can_transition(cls, from_status, to_status) -> bool:
        ...
```

---

## Fase GC3 — Geração da Camada Application

Um use case por feature do FEATURE_REGISTRY:

```python
# src/<module>/application/use_cases.py

class <FeatureName>UseCase:
    """
    Feature: <FT-XXX> — <feature name>
    Contrato: <endpoints>
    """
    def __init__(self, repository: <Module>Repository):
        self._repo = repository
    
    async def execute(self, input_dto: <FeatureInput>) -> <FeatureOutput>:
        # 1. Validar invariantes de domínio
        # 2. Executar lógica de negócio (DOMAIN_RULES)
        # 3. Persistir via repositório
        # 4. Retornar output DTO
```

---

## Fase GC4 — Geração da Camada Infrastructure

```python
# src/<module>/infrastructure/models.py
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
import uuid

class <Entity>Model(Base):
    __tablename__ = "<module>_<entities>"  # snake_case plural
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # ... campos alinhados com JSON Schema

# src/<module>/infrastructure/repository.py
class <Module>Repository:
    async def get_by_id(self, id: UUID) -> <Entity> | None: ...
    async def save(self, entity: <Entity>) -> <Entity>: ...
    async def list(self, filters: dict) -> list[<Entity>]: ...
```

---

## Fase GC5 — Geração da Camada Interface

**REGRA CRÍTICA:** O router deve implementar EXATAMENTE o que está no contrato.
Verificar cada endpoint, parâmetro, status code e response schema antes de gerar.

```python
# src/<module>/interface/router.py
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/<module>", tags=["<module>"])

@router.post(
    "/<resource>",
    status_code=status.HTTP_201_CREATED,
    response_model=<ResourceOutput>,
    # responses conforme contrato OpenAPI
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    }
)
async def create_<resource>(
    body: <ResourceInput>,
    use_case: <Feature>UseCase = Depends(get_use_case),
) -> <ResourceOutput>:
    return await use_case.execute(body)
```

---

## Fase GC6 — Geração de Testes

Para cada use case gerado (testes unitários):

```python
# tests/<module>/unit/test_<feature>_use_case.py
import pytest

class TestCreate<Feature>:
    def test_success(self): ...
    def test_invalid_input(self): ...
    def test_domain_rule_violation(self): ...
```

Para cada endpoint gerado (testes de integração):

```python
# tests/<module>/integration/test_<resource>_router.py
import pytest
from httpx import AsyncClient

class Test<Resource>Endpoints:
    async def test_post_returns_201(self, client: AsyncClient): ...
    async def test_post_invalid_returns_400(self, client: AsyncClient): ...
    async def test_unauthorized_returns_401(self, client: AsyncClient): ...
```

---

## Output

Após geração:

1. Listar todos os arquivos gerados com caminho canônico
2. Atualizar `FEATURE_REGISTRY.yaml` — status da feature: `validated` → `implemented`
3. Atualizar `SESSION_HANDOFF.md` com o que foi gerado e próximos passos
4. Reportar em linguagem de produto:

```
🏆 CÓDIGO GERADO — <Feature em português>

✅ Arquivos criados:
   - src/<module>/domain/entities.py (X linhas)
   - src/<module>/application/use_cases.py (X linhas)
   - src/<module>/infrastructure/ (X arquivos)
   - src/<module>/interface/router.py (X linhas)
   - tests/<module>/ (X testes)

🔄 Próximo passo: rodar pytest para validar geração
```

---

## Bloqueios possíveis

| Código | Condição |
|--------|----------|
| `BLOCKED_REQUIRED_ARTIFACT_MISSING` | Contrato OpenAPI ou schema ausente |
| `BLOCKED_ADVERSARIAL_PENDING` | Análise adversarial não executada ou FAIL |
| `BLOCKED_SCHEMA_DRIFT` | Schema Pydantic diverge do JSON Schema canônico |
| `BLOCKED_FEATURE_UNREGISTERED` | Feature não registrada no FEATURE_REGISTRY |
| `BLOCKED_HANDOFF_INCOMPLETE` | Camadas anteriores não geradas na ordem correta |

---

## Atualização de SESSION_HANDOFF

Ao concluir a geração, atualizar `SESSION_HANDOFF.md` com:
- Módulo e feature gerados
- Arquivos criados e contagem de linhas
- Status no FEATURE_REGISTRY atualizado
- Próximos passos: testes, migration, deploy
