---
task_type: generate_code
version: "2.0.0"
status: active
---

# generate_code — Worker de Geração de Código Backend

> **Stack canônica:** Python 3.12 + Django 5.x + Django Ninja 1.x + PostgreSQL 16 + Django ORM
> **Referência:** `docs/_canon/CODE_ARCHITECTURE.md` (v1.1.0) + ADR-026 + ADR-031
> **Estrutura real:** `backend/apps/<module>/`

---

## Pré-requisitos obrigatórios

Antes de executar este worker, verificar:

1. **ADR-026** existe em `docs/_canon/decisions/`
2. **ADR-031** existe em `docs/_canon/decisions/`
3. **CODE_ARCHITECTURE.md** existe em `docs/_canon/` (versão ≥ 1.1.0)
4. **ADVERSARIAL_ANALYSIS_GATE** PASS para o módulo/recurso alvo
5. **Contrato OpenAPI** do módulo existe e está validado (gate `OPENAPI_ROOT_MODULE_SYNC_GATE` PASS)
6. **JSON Schemas** do módulo existem em `contracts/schemas/<module>/`

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

```
contracts/openapi/paths/<module>.yaml              # endpoints do módulo
contracts/schemas/<module>/                        # schemas JSON
docs/hbtrack/modulos/<module>/
  DOMAIN_RULES_<MODULE>.md                        # regras de negócio
  INVARIANTS_<MODULE>.md                          # invariantes
  STATE_MODEL_<MODULE>.md                         # FSM (se aplicável)
  PERMISSIONS_<MODULE>.md                         # RBAC
docs/_canon/FEATURE_REGISTRY.yaml                 # feature → endpoints
docs/_canon/CODE_ARCHITECTURE.md                  # estrutura canônica
_reports/adversarial/<module>/<resource>.adversarial.json  # resultado adversarial
```

---

## Fase GC2 — Geração da Camada Domain

Para cada entidade identificada no contrato e schemas:

```python
# backend/apps/<module>/domain/entities.py
from dataclasses import dataclass
from uuid import UUID

@dataclass
class <Entity>:
    """
    Entidade: <Entity>
    Módulo: <module>
    Contrato: contracts/schemas/<module>/<entity>.schema.json
    """
    id: UUID
    # ... campos derivados do JSON Schema

    def validate_invariants(self) -> None:
        """Enforce INVARIANTS_<MODULE>.md — nunca validar no router"""
        ...
```

Para entidades com FSM (STATE_MODEL presente):

```python
# backend/apps/<module>/domain/state_machine.py
from enum import StrEnum

class <Entity>Status(StrEnum):
    # estados derivados do STATE_MODEL_<MODULE>.md

class <Entity>StateMachine:
    TRANSITIONS: dict[<Entity>Status, set[<Entity>Status]] = {
        # transições válidas do STATE_MODEL
    }

    @classmethod
    def can_transition(cls, from_status: <Entity>Status, to_status: <Entity>Status) -> bool:
        return to_status in cls.TRANSITIONS.get(from_status, set())
```

---

## Fase GC3 — Geração da Camada Application

Um use case por feature do FEATURE_REGISTRY:

```python
# backend/apps/<module>/application/use_cases.py
from ..domain.entities import <Entity>
from ..infrastructure.repository import <Module>Repository

class <FeatureName>UseCase:
    """
    Feature: <FT-XXX> — <feature name>
    Contrato: <endpoints>
    """
    def __init__(self, repository: <Module>Repository):
        self._repo = repository

    def execute(self, input_dto: dict) -> <Entity>:
        # 1. Validar invariantes de domínio
        # 2. Executar lógica de negócio (DOMAIN_RULES)
        # 3. Persistir via repositório
        # 4. Retornar entidade
```

---

## Fase GC4 — Geração da Camada Infrastructure

```python
# backend/apps/<module>/infrastructure/models.py
import uuid
from django.db import models

class <Entity>Model(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # ... campos alinhados com JSON Schema

    class Meta:
        db_table = "<module>_<entities>"  # snake_case plural
        app_label = "<module>"

# backend/apps/<module>/infrastructure/repository.py
from .models import <Entity>Model
from ..domain.entities import <Entity>

class <Module>Repository:
    def get_by_id(self, id: uuid.UUID) -> <Entity> | None:
        try:
            return self._to_domain(<Entity>Model.objects.get(pk=id))
        except <Entity>Model.DoesNotExist:
            return None

    def save(self, entity: <Entity>) -> <Entity>:
        model, _ = <Entity>Model.objects.update_or_create(pk=entity.id, defaults=self._to_model(entity))
        return self._to_domain(model)

    def list(self, filters: dict) -> list[<Entity>]:
        return [self._to_domain(m) for m in <Entity>Model.objects.filter(**filters)]
```

---

## Fase GC5 — Geração da Camada Interface (Django Ninja)

**REGRA CRÍTICA:** O router deve implementar EXATAMENTE o que está no contrato OpenAPI.
Verificar cada endpoint, parâmetro, status code e response schema antes de gerar.

```python
# backend/apps/<module>/interface/api.py
from ninja import Router
from ninja.errors import HttpError
from ..application.use_cases import <FeatureName>UseCase
from ..infrastructure.repository import <Module>Repository

router = Router(tags=["<module>"])

def get_use_case() -> <FeatureName>UseCase:
    return <FeatureName>UseCase(<Module>Repository())

@router.post(
    "/<resource>",
    response={201: <ResourceOutputSchema>, 400: ErrorSchema, 401: ErrorSchema, 409: ErrorSchema},
    auth=django_auth,  # conforme PERMISSIONS_<MODULE>.md
)
def create_<resource>(request, body: <ResourceInputSchema>):
    """Endpoint conforme contrato: POST /<module>/<resource>"""
    use_case = get_use_case()
    return 201, use_case.execute(body.dict())
```

Registrar o router no `backend/config/api.py`:

```python
# backend/config/api.py
from backend.apps.<module>.interface.api import router as <module>_router
api.add_router("/<module>", <module>_router)
```

---

## Fase GC6 — Geração de Testes

Para cada use case gerado (testes unitários):

```python
# backend/apps/<module>/tests/unit/test_<feature>_use_case.py
import pytest
from unittest.mock import MagicMock

class TestCreate<Feature>:
    def test_success(self): ...
    def test_invalid_input(self): ...
    def test_domain_rule_violation(self): ...
```

Para cada endpoint gerado (testes de integração com pytest-django):

```python
# backend/apps/<module>/tests/integration/test_<resource>_api.py
import pytest

@pytest.mark.django_db
class Test<Resource>Endpoints:
    def test_post_returns_201(self, client): ...
    def test_post_invalid_returns_400(self, client): ...
    def test_unauthorized_returns_401(self, client): ...
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
   - backend/apps/<module>/domain/entities.py
   - backend/apps/<module>/application/use_cases.py
   - backend/apps/<module>/infrastructure/models.py
   - backend/apps/<module>/infrastructure/repository.py
   - backend/apps/<module>/interface/api.py
   - backend/apps/<module>/tests/ (X testes)

🔄 Próximo passo: python manage.py makemigrations && pytest
```

---

## Bloqueios possíveis

| Código | Condição |
|--------|----------|
| `BLOCKED_REQUIRED_ARTIFACT_MISSING` | Contrato OpenAPI ou schema ausente |
| `BLOCKED_ADVERSARIAL_PENDING` | Análise adversarial não executada ou FAIL |
| `BLOCKED_SCHEMA_DRIFT` | Model Django diverge do JSON Schema canônico |
| `BLOCKED_FEATURE_UNREGISTERED` | Feature não registrada no FEATURE_REGISTRY |
| `BLOCKED_HANDOFF_INCOMPLETE` | Camadas anteriores não geradas na ordem correta |

---

## Atualização de SESSION_HANDOFF

Ao concluir a geração, atualizar `SESSION_HANDOFF.md` com:
- Módulo e feature gerados
- Arquivos criados e contagem de linhas
- Status no FEATURE_REGISTRY atualizado
- Próximos passos: migrations, testes, deploy
