"""
Taxonomia hierárquica de exceções do domínio training.

6 classes-base semânticas abaixo de `TrainingDomainError`. Cada exceção
concreta definida em `domain/rules.py` (ou futuros módulos por agregado)
deve herdar de exatamente uma dessas bases — o mapeamento para código
HTTP vive em `api/errors.py` e pode depender do `isinstance()` contra
estas bases.

Bases semânticas (código HTTP típico entre parênteses):

- AuthorizationError (403)
- NotFoundError       (404)
- ConflictError       (409)
- StateError          (422)  — máquina de estado / mutabilidade
- ValidationError     (422)  — violação de invariante de domínio
- PreconditionError   (400)  — precondição temporal / janela

Note: alguns concretos históricos herdam adicionalmente de `ValueError`
para preservar `except ValueError` em consumidores legados. Use
multi-herança explícita nessas classes — não no topo da taxonomia.
"""
from __future__ import annotations


class TrainingDomainError(Exception):
    """Raiz de todas exceções semânticas do domínio training."""


class AuthorizationError(TrainingDomainError):
    """403 — ator sem privilégio para a operação (OWASP API5 / BFLA)."""


class NotFoundError(TrainingDomainError):
    """404 — recurso referenciado não encontrado."""


class ConflictError(TrainingDomainError):
    """409 — estado atual do recurso incompatível com a operação."""


class StateError(TrainingDomainError):
    """422 — máquina de estado ou mutabilidade (FSM / edição)."""


class ValidationError(TrainingDomainError):
    """422 — violação de invariante de domínio (dados inválidos)."""


class PreconditionError(TrainingDomainError):
    """400 — precondição temporal / janela de tempo não satisfeita."""


__all__ = [
    "TrainingDomainError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "StateError",
    "ValidationError",
    "PreconditionError",
]
