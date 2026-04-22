"""
Fase 3 — test_application_layout.py

Garante que a decomposição de application/use_cases.py em subpacotes
mantém invariantes estruturais:
1. Shim use_cases.py re-exporta os 48 UseCases esperados.
2. Nenhum dto.py dos subpacotes ultrapassa 250 linhas.
3. Os subpacotes não importam de django.conf (application permanece framework-agnostic).
"""
from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

APPLICATION_ROOT = Path("src/training/application")

# 48 UseCases que devem estar na surface pública do shim
EXPECTED_USE_CASES = [
    # sessions
    "ListTrainingSessionsUseCase",
    "CreateTrainingSessionUseCase",
    "GetTrainingSessionUseCase",
    "TransitionTrainingSessionUseCase",
    "DeleteTrainingSessionUseCase",
    "UpdateTrainingSessionUseCase",
    # blocks
    "ListSessionBlocksUseCase",
    "AddSessionBlockUseCase",
    "UpdateSessionBlockUseCase",
    "DeleteSessionBlockUseCase",
    "GetSessionBlockUseCase",
    "ReorderSessionBlocksUseCase",
    # wellness
    "SubmitWellnessPreUseCase",
    "SubmitWellnessPostUseCase",
    "GetWellnessPreUseCase",
    "UpdateWellnessPreUseCase",
    "GetWellnessPostUseCase",
    "UpdateWellnessPostUseCase",
    # attendance
    "ListSessionAttendanceUseCase",
    "RecordSessionAttendanceUseCase",
    # execution
    "CreateExecutionRecordUseCase",
    "CreateSessionObjectiveUseCase",
    "ListExecutionRecordsUseCase",
    "GetExecutionRecordUseCase",
    "ListSessionObjectivesUseCase",
    # planning
    "CreateMesocycleUseCase",
    "CreateMicrocycleUseCase",
    "ListMesocyclesUseCase",
    "GetMesocycleUseCase",
    "UpdateMesocycleUseCase",
    "ListMicrocyclesUseCase",
    "GetMicrocycleUseCase",
    "UpdateMicrocycleUseCase",
    # communication
    "ListFeedbackThreadsUseCase",
    "CreateFeedbackThreadUseCase",
    "CloseFeedbackThreadUseCase",
    "ListAttentionQueueItemsUseCase",
    "ResolveAttentionQueueItemUseCase",
    "DismissAttentionQueueItemUseCase",
    "EscalateAttentionQueueItemUseCase",
    "ListRecommendationsUseCase",
    "AcceptRecommendationUseCase",
    "DismissRecommendationUseCase",
    "ListChatMessagesUseCase",
    "SubmitTrainingSuggestionUseCase",
    # eligibility
    "GetIneligibilityStatusUseCase",
    "SubmitIneligibilityDeclarationUseCase",
    # analytics
    "GetLoadChartUseCase",
]


class TestApplicationShimSurface:
    """Garante que o shim re-exporta todos os UseCases esperados."""

    def test_all_use_cases_importable_from_shim(self):
        module = importlib.import_module("training.application.use_cases")
        missing = [uc for uc in EXPECTED_USE_CASES if not hasattr(module, uc)]
        assert missing == [], f"UseCases ausentes no shim: {missing}"

    def test_shim_line_count(self):
        shim = APPLICATION_ROOT / "use_cases.py"
        lines = len(shim.read_text().splitlines())
        assert lines <= 200, (
            f"use_cases.py shim tem {lines} linhas — deve ser <= 200. "
            "Verifique se o original não foi mantido."
        )


class TestDtoSizeContainment:
    """Garante que nenhum dto.py ultrapasse 250 linhas."""

    @pytest.mark.parametrize("path", sorted(APPLICATION_ROOT.rglob("dto.py")))
    def test_dto_size_containment(self, path: Path):
        lines = len(path.read_text().splitlines())
        assert lines <= 250, (
            f"{path} passou de 250 linhas ({lines}) — "
            "faça split em inputs.py / outputs.py"
        )


class TestApplicationSubpackagesFrameworkAgnostic:
    """Subpacotes de application não devem importar django.conf."""

    SUBPACKAGES = [
        "sessions",
        "blocks",
        "wellness",
        "attendance",
        "execution",
        "planning",
        "communication",
        "eligibility",
        "analytics",
    ]

    @pytest.mark.parametrize("subpkg", SUBPACKAGES)
    def test_no_django_conf_in_subpackage(self, subpkg: str):
        subpkg_path = APPLICATION_ROOT / subpkg
        for py_file in subpkg_path.glob("*.py"):
            source = py_file.read_text()
            tree = ast.parse(source, filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module = ""
                    if isinstance(node, ast.ImportFrom) and node.module:
                        module = node.module
                    elif isinstance(node, ast.Import):
                        module = ",".join(alias.name for alias in node.names)
                    assert "django.conf" not in module, (
                        f"{py_file} importa django.conf — application deve ser framework-agnostic"
                    )
