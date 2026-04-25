from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml"
SYNC_MANIFEST_PATH = ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml"


def _registry_gates() -> dict[str, dict]:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {g["gate_id"]: g for g in data.get("gates", [])}


# ---------------------------------------------------------------------------
# Registry checks
# ---------------------------------------------------------------------------

def test_context_bundle_freshness_gate_in_registry():
    gates = _registry_gates()
    assert "CONTEXT_BUNDLE_FRESHNESS_GATE" in gates, (
        "CONTEXT_BUNDLE_FRESHNESS_GATE deve estar em GATES_REGISTRY.yaml"
    )
    g = gates["CONTEXT_BUNDLE_FRESHNESS_GATE"]
    assert g.get("status") == "active"
    assert g.get("blocking") is True
    assert "BLOCKED_BUNDLE_STALE" in (g.get("blocking_codes") or [])


def test_impact_analysis_gate_in_registry():
    gates = _registry_gates()
    assert "IMPACT_ANALYSIS_GATE" in gates, (
        "IMPACT_ANALYSIS_GATE deve estar em GATES_REGISTRY.yaml"
    )
    g = gates["IMPACT_ANALYSIS_GATE"]
    assert g.get("status") == "active"
    assert g.get("blocking") is True
    assert "BLOCKED_PARTIAL_CONSUMER_UPDATE" in (g.get("blocking_codes") or [])


def test_partial_update_gate_in_registry():
    gates = _registry_gates()
    assert "PARTIAL_UPDATE_GATE" in gates, (
        "PARTIAL_UPDATE_GATE deve estar em GATES_REGISTRY.yaml"
    )
    g = gates["PARTIAL_UPDATE_GATE"]
    assert g.get("status") == "active"
    assert g.get("blocking") is True
    assert "BLOCKED_ORPHAN_SOURCE_UPDATE" in (g.get("blocking_codes") or [])


def test_gate_orders_are_sequential():
    """20L, 20M, 20N devem existir e ser os três últimos gates."""
    gates = _registry_gates()
    orders = {g["gate_id"]: g.get("order") for g in _registry_gates().values()}
    assert orders.get("CONTEXT_BUNDLE_FRESHNESS_GATE") == "20L"
    assert orders.get("IMPACT_ANALYSIS_GATE") == "20M"
    assert orders.get("PARTIAL_UPDATE_GATE") == "20N"


# ---------------------------------------------------------------------------
# SYNC_MANIFEST structure
# ---------------------------------------------------------------------------

def test_sync_manifest_has_rules():
    data = yaml.safe_load(SYNC_MANIFEST_PATH.read_text(encoding="utf-8"))
    rules = (data or {}).get("rules", [])
    assert len(rules) > 0, "SYNC_MANIFEST.yaml deve ter pelo menos uma regra"


def test_sync_manifest_rules_have_required_fields():
    data = yaml.safe_load(SYNC_MANIFEST_PATH.read_text(encoding="utf-8"))
    rules = (data or {}).get("rules", [])
    for rule in rules:
        assert "rule_id" in rule, f"Regra sem rule_id: {rule}"
        assert "source_master" in rule, f"Regra {rule.get('rule_id')} sem source_master"


def test_sync_manifest_openapi_paths_rules_exist():
    """As 17 regras MODULE_OPENAPI_PATHS_SYNC devem estar no SYNC_MANIFEST."""
    data = yaml.safe_load(SYNC_MANIFEST_PATH.read_text(encoding="utf-8"))
    rules = (data or {}).get("rules", [])
    rule_ids = {r.get("rule_id", "") for r in rules}
    openapi_rules = [r for r in rule_ids if r.endswith("_OPENAPI_PATHS_SYNC")]
    assert len(openapi_rules) == 17, (
        f"Esperado 17 regras _OPENAPI_PATHS_SYNC, encontrado {len(openapi_rules)}: {sorted(openapi_rules)}"
    )


# ---------------------------------------------------------------------------
# Gate logic via subprocess (integration)
# ---------------------------------------------------------------------------

def test_impact_analysis_gate_skips_outside_git_context(tmp_path):
    """Gate deve retornar SKIP quando fora de contexto git (HEAD~1 não existe)."""
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    # Criar SYNC_MANIFEST mínimo
    sync_dir = tmp_path / "docs" / "_canon"
    sync_dir.mkdir(parents=True)
    manifest = {"rules": [
        {
            "rule_id": "TEST_SYNC",
            "source_master": "docs/test/source.yaml",
            "required_consumers": ["contracts/test/consumer.yaml"],
            "blocking_consumers": ["contracts/test/consumer.yaml"],
        }
    ]}
    (sync_dir / "SYNC_MANIFEST.yaml").write_text(
        yaml.dump(manifest), encoding="utf-8"
    )

    result = vc._g_impact_analysis(tmp_path)
    assert result["status"] in ("SKIP_NOT_APPLICABLE", "PASS"), (
        f"Gate deve SKIP ou PASS fora de contexto git, obteve: {result['status']}"
    )


def test_partial_update_gate_skips_without_sync_manifest(tmp_path):
    """Gate deve retornar SKIP quando SYNC_MANIFEST não existe."""
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    result = vc._g_partial_update(tmp_path)
    assert result["status"] == "SKIP_NOT_APPLICABLE", (
        f"Gate deve SKIP sem SYNC_MANIFEST, obteve: {result['status']}"
    )


def test_context_bundle_freshness_gate_skips_without_compilers(tmp_path):
    """Gate deve retornar SKIP quando os scripts de compilação não existem no root."""
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    # tmp_path não tem scripts/compile/ → SKIP
    result = vc._g_context_bundle_freshness(tmp_path)
    assert result["status"] == "SKIP_NOT_APPLICABLE", (
        f"Gate deve SKIP sem compiler scripts, obteve: {result['status']}"
    )


def test_context_bundle_freshness_gate_passes_on_real_repo():
    """Gate deve PASS no repo real com source graphs e context bundles sincronizados.

    Prova que a implementação content-based funciona sem depender de mtime.
    """
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    result = vc._g_context_bundle_freshness(ROOT)
    assert result["status"] == "PASS", (
        f"Gate deve PASS com artefatos sincronizados no repo real. "
        f"Violações: {result.get('violations', [])}"
    )


def test_context_bundle_freshness_gate_fails_on_source_graph_content_drift():
    """Gate deve FAIL quando source graph tem content drift (não depende de mtime).

    Prova adversarial: introduz drift real em generated/source_graph/training/,
    verifica que o gate detecta, restaura o arquivo.
    """
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    drift_target = ROOT / "generated" / "source_graph" / "training" / "training.bundle.yaml"
    original = drift_target.read_text(encoding="utf-8")
    try:
        # Introduzir drift de conteúdo (não é mtime — arquivo é mais novo que fontes)
        drift_target.write_text(original + "\n# STALE_MARKER_TEST\n", encoding="utf-8")
        result = vc._g_context_bundle_freshness(ROOT)
        assert result["status"] == "FAIL", (
            f"Gate deve FAIL com source graph stale (content drift), obteve: {result['status']}"
        )
        violations = result.get("violations", [])
        assert any(
            "training" in v.get("artifact", "") or "training" in v.get("message", "")
            for v in violations
        ), f"Deve haver violação para training. Violations: {violations}"
    finally:
        drift_target.write_text(original, encoding="utf-8")
