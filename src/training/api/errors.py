"""Mapeamento domínio → HTTP para a camada training.api.

Expõe o decorator @map_exceptions que encapsula o padrão
try/except → HttpError repetido em cada handler.

Fase 1.3 — split estrutural do api/__init__.py monolítico.
"""
from __future__ import annotations

import functools
import logging
from typing import Callable, TypeVar

from django.db import DataError, IntegrityError
from ninja.errors import HttpError

from training.domain.common.exceptions import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    PreconditionError,
    StateError,
    ValidationError as DomainValidationError,
)

_F = TypeVar("_F", bound=Callable)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tabela de mapeamento: nome-da-classe-de-exceção → código HTTP
# Lookup por __name__ para evitar import circular com domain.rules.
# ---------------------------------------------------------------------------
_EXCEPTION_STATUS_MAP: dict[str, int] = {
    # 404 — Not Found
    "TrainingSessionNotFound": 404,
    "SessionBlockNotFound": 404,
    "MesocycleNotFound": 404,
    "MicrocycleNotFound": 404,
    "ExecutionRecordNotFound": 404,
    "WellnessEntryNotFound": 404,
    "FeedbackThreadNotFound": 404,
    "AttentionQueueItemNotFound": 404,
    "RecommendationNotFound": 404,
    "IneligibilityDeclarationNotFound": 404,
    # 403 — Forbidden
    "InsufficientPrivilege": 403,
    # 409 — Conflict
    "AttentionQueueConflict": 409,
    "RecommendationConflict": 409,
    "DuplicateWellnessEntry": 409,
    "FeedbackThreadAlreadyClosed": 409,
    "IneligibilityStateConflict": 409,
    "SuggestionStateConflict": 409,
    # 422 — Unprocessable Entity
    "InvalidStatusTransition": 422,
    "SessionNotMutable": 422,
    "ElasticSumRuleViolation": 422,
    # 400 — Bad Request
    "WellnessWindowClosed": 400,
}


def map_exceptions(func: _F) -> _F:
    """Decorator que converte exceções de domínio em HttpError.

    Ordem de captura:
    1. HttpError já formado — re-raise sem alteração.
    2. Exceções mapeadas em _EXCEPTION_STATUS_MAP — converte para HttpError(code, str(exc)).
    3. IntegrityError / DataError (Django ORM) — 422.
    4. ValueError — 422 (validação de negócio genérica).
    5. Qualquer outra exceção — re-raise (não silencia bugs).

    Handlers que precisam de mapeamento especial (e.g. ValueError → 400 ou 409
    condicional) devem capturar e lançar HttpError explicitamente *dentro* do
    corpo da função; o decorator re-levanta HttpError sem alteração.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError:
            raise
        except Exception as exc:
            # 1. Verifica tabela de exceções de domínio (lookup por nome de classe)
            code = _EXCEPTION_STATUS_MAP.get(type(exc).__name__)
            if code is not None:
                raise HttpError(code, str(exc)) from exc
            # 2. Fallback isinstance para bases semânticas do domínio (Fase 5.2)
            _DOMAIN_BASE_MAP = (
                (NotFoundError, 404),
                (AuthorizationError, 403),
                (ConflictError, 409),
                (PreconditionError, 400),
                (StateError, 422),
                (DomainValidationError, 422),
            )
            for base_cls, http_code in _DOMAIN_BASE_MAP:
                if isinstance(exc, base_cls):
                    raise HttpError(http_code, str(exc)) from exc
            # 3. Erros de ORM do Django — mascarar detalhes de schema (OWASP API3)
            if isinstance(exc, (IntegrityError, DataError)):
                logger.warning(
                    "db_constraint_error",
                    extra={"detail": str(exc)},
                    exc_info=True,
                )
                raise HttpError(
                    422, "Dados inválidos: violação de constraint de integridade"
                ) from exc
            # 3. ValueError genérico (validação de negócio)
            if isinstance(exc, ValueError):
                raise HttpError(422, str(exc)) from exc
            # 4. Desconhecido — propaga para não silenciar bugs
            raise

    return wrapper  # type: ignore[return-value]
