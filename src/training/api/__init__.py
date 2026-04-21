"""Router django-ninja — módulo training.

Agregador fino: registra os sub-roteadores de domínio.
Implementa endpoints do contrato contracts/openapi/paths/training.yaml.
ADR-007 (JWT), ADR-008 (RBAC), ADR-031 (Django).
OWASP API1/2/3/5 enforcement via domain rules.
"""
from __future__ import annotations

# CODEGEN CUTOVER — generated use cases linked
from ..generated.application import use_cases as _gen_use_cases  # noqa: F401
from ..generated.infrastructure import repository as _gen_repository  # noqa: F401

from ninja import Router

from ..domain.rules import RoleLabel  # noqa: F401 — usado em testes via training.api.RoleLabel

from . import (
    analytics,
    attendance,
    attention,
    blocks,
    chat,
    eligibility,
    execution,
    feedback,
    planning,
    recommendations,
    sessions,
    wellness,
)

router = Router(tags=["training"])

sessions.register(router)
blocks.register(router)
wellness.register(router)
attendance.register(router)
execution.register(router)
planning.register(router)
feedback.register(router)
attention.register(router)
recommendations.register(router)
chat.register(router)
eligibility.register(router)
analytics.register(router)
