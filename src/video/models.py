# models.py — ponto de entrada obrigatório para Django descobrir os models.
# Importa de infrastructure/models.py (padrão Django para apps com camadas).
from video.infrastructure.models import (  # noqa: F401
    MatchMediaSessionModel,
    MediaSegmentModel,
    ClipDefinitionModel,
    DistributionProfileModel,
)
