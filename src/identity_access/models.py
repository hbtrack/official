# models.py — ponto de entrada obrigatório para Django descobrir os models.
# Importa de infrastructure/models.py (padrão Django para apps com camadas).
from identity_access.infrastructure.models import (  # noqa: F401
    AuthSessionModel,
    UserRoleBindingModel,
)
