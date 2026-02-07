"""
INV-TRAIN-004: Janela de edição por autoria/hierarquia

Regra documentada:
- Autor: pode editar até 10min após criação
- Superior: pode editar até 24h

Evidência:
- training_session_service.py:54 (AUTHOR_EDIT_WINDOW_MINUTES = 10)
- training_session_service.py:55 (SUPERIOR_EDIT_WINDOW_HOURS = 24)
- training_session_service.py:407-436 (_validate_edit_permission - validação por role)

NOTA: As constantes de tempo estão definidas, mas a lógica de validação
por tempo (autor vs superior) NÃO está implementada. A validação atual
é apenas por role (dirigente/coordenador/treinador podem editar).
"""

import pytest

from app.services.training_session_service import TrainingSessionService


class TestInvTrain004EditWindowConstants:
    """Testes para INV-TRAIN-004: Constantes de janela de edição."""

    def test_author_edit_window_is_10_minutes(self):
        """Constante AUTHOR_EDIT_WINDOW_MINUTES deve ser 10."""
        assert TrainingSessionService.AUTHOR_EDIT_WINDOW_MINUTES == 10, \
            "Janela de edição do autor deve ser 10 minutos"

    def test_superior_edit_window_is_24_hours(self):
        """Constante SUPERIOR_EDIT_WINDOW_HOURS deve ser 24."""
        assert TrainingSessionService.SUPERIOR_EDIT_WINDOW_HOURS == 24, \
            "Janela de edição do superior deve ser 24 horas"

    def test_immutability_days_is_60(self):
        """Constante IMMUTABILITY_DAYS deve ser 60 (relacionado à INV-TRAIN-005)."""
        assert TrainingSessionService.IMMUTABILITY_DAYS == 60, \
            "Prazo de imutabilidade deve ser 60 dias"

    def test_constants_are_class_attributes(self):
        """As constantes devem ser atributos de classe, não de instância."""
        # Verifica que são atributos de classe
        assert hasattr(TrainingSessionService, 'AUTHOR_EDIT_WINDOW_MINUTES')
        assert hasattr(TrainingSessionService, 'SUPERIOR_EDIT_WINDOW_HOURS')
        assert hasattr(TrainingSessionService, 'IMMUTABILITY_DAYS')

    def test_edit_window_constants_are_positive(self):
        """As janelas de edição devem ser valores positivos."""
        assert TrainingSessionService.AUTHOR_EDIT_WINDOW_MINUTES > 0
        assert TrainingSessionService.SUPERIOR_EDIT_WINDOW_HOURS > 0
        assert TrainingSessionService.IMMUTABILITY_DAYS > 0
