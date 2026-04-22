"""
Contrato da taxonomia de exceções do domínio training.

Todas as exceções concretas em `training.domain.rules` (e em módulos de
agregado futuros) devem herdar de exatamente uma das 6 classes-base
semânticas em `training.domain.common.exceptions`, que por sua vez
herdam de `TrainingDomainError`.

Este teste é a guarda estrutural: se uma nova exceção for adicionada
sem herança semântica, ou se uma existente for despromovida, o teste
falha — bloqueando regressão silenciosa em `api/errors.py`.
"""
from __future__ import annotations

import pytest

from training.domain import rules
from training.domain.common.exceptions import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    PreconditionError,
    StateError,
    TrainingDomainError,
    ValidationError,
)


# Pares (exceção concreta, base semântica esperada) — 22 entradas.
EXCEPTION_TAXONOMY: list[tuple[type[BaseException], type[TrainingDomainError]]] = [
    # AuthorizationError (403)
    (rules.InsufficientPrivilege, AuthorizationError),
    # NotFoundError (404)
    (rules.TrainingSessionNotFound, NotFoundError),
    (rules.SessionBlockNotFound, NotFoundError),
    (rules.WellnessEntryNotFound, NotFoundError),
    (rules.AttendanceRecordNotFound, NotFoundError),
    (rules.MesocycleNotFound, NotFoundError),
    (rules.MicrocycleNotFound, NotFoundError),
    (rules.ExecutionRecordNotFound, NotFoundError),
    (rules.FeedbackThreadNotFound, NotFoundError),
    (rules.AttentionQueueItemNotFound, NotFoundError),
    (rules.RecommendationNotFound, NotFoundError),
    (rules.IneligibilityDeclarationNotFound, NotFoundError),
    # ConflictError (409)
    (rules.DuplicateWellnessEntry, ConflictError),
    (rules.AttentionQueueConflict, ConflictError),
    (rules.RecommendationConflict, ConflictError),
    (rules.FeedbackThreadAlreadyClosed, ConflictError),
    (rules.IneligibilityStateConflict, ConflictError),
    (rules.SuggestionStateConflict, ConflictError),
    # StateError (422)
    (rules.InvalidStatusTransition, StateError),
    (rules.SessionNotMutable, StateError),
    # ValidationError (422)
    (rules.ElasticSumRuleViolation, ValidationError),
    # PreconditionError (400)
    (rules.WellnessWindowClosed, PreconditionError),
]


@pytest.mark.parametrize("concrete,base", EXCEPTION_TAXONOMY)
def test_concrete_exception_inherits_from_semantic_base(
    concrete: type[BaseException],
    base: type[TrainingDomainError],
) -> None:
    assert issubclass(concrete, base), (
        f"{concrete.__name__} deve herdar de {base.__name__}. "
        f"Atualize domain/rules.py ou a taxonomia em "
        f"domain/common/exceptions.py."
    )


@pytest.mark.parametrize("concrete,_base", EXCEPTION_TAXONOMY)
def test_concrete_exception_inherits_from_training_domain_error(
    concrete: type[BaseException],
    _base: type[TrainingDomainError],
) -> None:
    assert issubclass(concrete, TrainingDomainError), (
        f"{concrete.__name__} deve herdar (transitivamente) de TrainingDomainError."
    )


# Compat: exceções originalmente herdadas de ValueError devem continuar
# compatíveis com `except ValueError` para não quebrar consumidores legados.
VALUEERROR_COMPAT_EXCEPTIONS: list[type[BaseException]] = [
    rules.FeedbackThreadAlreadyClosed,
    rules.IneligibilityStateConflict,
    rules.SuggestionStateConflict,
]


@pytest.mark.parametrize("concrete", VALUEERROR_COMPAT_EXCEPTIONS)
def test_legacy_valueerror_exceptions_still_valueerror(
    concrete: type[BaseException],
) -> None:
    assert issubclass(concrete, ValueError), (
        f"{concrete.__name__} historicamente herda de ValueError — "
        f"remover essa herança quebra consumidores que fazem `except ValueError`."
    )


# ---------------------------------------------------------------------------
# A6 — Varredura automática: toda subclasse de TrainingDomainError tem mapeamento
# ---------------------------------------------------------------------------

def _all_subclasses(cls: type) -> list[type]:
    """Retorna todas as subclasses concretas (folha) recursivamente."""
    result = []
    for sub in cls.__subclasses__():
        deeper = _all_subclasses(sub)
        if deeper:
            result.extend(deeper)
        else:
            result.append(sub)
    return result


# Bases semânticas cobertas pelo fallback isinstance em errors.py
_FALLBACK_BASES = (
    NotFoundError,
    AuthorizationError,
    ConflictError,
    PreconditionError,
    StateError,
    ValidationError,
)


def test_all_training_domain_errors_have_mapping() -> None:
    """Garante que toda exceção concreta de TrainingDomainError:
    - está em _EXCEPTION_STATUS_MAP por nome (lookup string), OU
    - é coberta pelo fallback isinstance das 6 bases semânticas.

    Se este teste falhar, adicione a nova exceção à EXCEPTION_TAXONOMY acima
    e ao _EXCEPTION_STATUS_MAP em api/errors.py.
    """
    from training.api.errors import _EXCEPTION_STATUS_MAP  # noqa: PLC0415

    concrete_classes = _all_subclasses(TrainingDomainError)
    unmapped: list[str] = []
    for cls in concrete_classes:
        in_map = cls.__name__ in _EXCEPTION_STATUS_MAP
        in_fallback = issubclass(cls, _FALLBACK_BASES)
        if not in_map and not in_fallback:
            unmapped.append(cls.__name__)

    assert not unmapped, (
        f"As seguintes subclasses de TrainingDomainError não têm mapeamento HTTP "
        f"(nem em _EXCEPTION_STATUS_MAP nem coberta por fallback isinstance): "
        f"{unmapped}. "
        f"Adicione-as em api/errors.py e na EXCEPTION_TAXONOMY deste teste."
    )
