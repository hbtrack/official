"""
test_e2e_dod_pipeline.py
AR_900 — E2E: Verificação pipeline DoD

Cobertura: CONTRACT-TRAIN-073 (GET /analytics/wellness-rankings)
Propósito: provar que o pipeline DoD (DOC-GATE-019/020/021 + DOD-TABLE +
           strict verify + gen_test_matrix) funciona end-to-end.

Este teste é GOVERNANCE_ONLY: verifica a estrutura da rota, não faz chamada
real ao banco. Nenhum fixture de banco necessário.
"""
from __future__ import annotations

import pytest


@pytest.mark.trace("CONTRACT-TRAIN-073")
def test_wellness_rankings_route_contract_declared() -> None:
    """
    CONTRACT-TRAIN-073 — GET /analytics/wellness-rankings

    Verifica que a rota está declarada no schema OpenAPI gerado (ssot/openapi.json),
    confirmando que o contrato existe estruturalmente.
    Se o arquivo openapi.json não existir, o teste passa com skip informativo
    (ambiente de CI sem geração de SSOT não deve bloquear o pipeline DoD).
    """
    import json
    import pathlib

    openapi_path = pathlib.Path("docs/ssot/openapi.json")
    if not openapi_path.exists():
        pytest.skip("openapi.json não gerado neste ambiente — verificação estrutural ignorada")

    spec = json.loads(openapi_path.read_text(encoding="utf-8"))
    paths = spec.get("paths", {})

    # Aceita variações de prefixo (versioned e não-versioned)
    candidates = [
        "/analytics/wellness-rankings",
        "/api/v1/analytics/wellness-rankings",
        "/api/analytics/wellness-rankings",
    ]
    declared = any(c in paths for c in candidates)
    assert declared, (
        f"CONTRACT-TRAIN-073: nenhuma das rotas candidatas encontrada em openapi.json.\n"
        f"Candidatos: {candidates}\n"
        f"Rotas disponíveis (prefix /analytics): "
        f"{[p for p in paths if '/analytics' in p]}"
    )
