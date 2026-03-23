"""Testes de regressão para governança do pipeline."""

from __future__ import annotations

import datetime
import json
from pathlib import Path

from scripts.contracts.validate import validate_contracts as gates


def _write_structured_handoff(
    root: Path,
    *,
    date_value: str,
    branch: str = "main",
    next_action: str = "Executar o próximo bloco validado do roadmap.",
) -> None:
    handoff = root / "SESSION_HANDOFF.md"
    handoff.write_text(
        f"""---
data_ultima_sessao: {date_value}
branch_ativo: {branch}
ci_status: PASS
modulo_foco: governance
fase_roadmap: 1
task_id: phase-1
resultado: PENDENTE
proxima_acao_permitida: {next_action}
bloqueios_ativos: []
---
# SESSION HANDOFF — HB TRACK

## Estado Geral
**Data:** {date_value} | **Branch:** {branch} | **CI:** PASS

## O que foi feito
- item

## Próxima ação permitida
- {next_action}

## Bloqueios ativos
- Nenhum.
""",
        encoding="utf-8",
    )


def test_handoff_coherence_detects_stale_date(tmp_path):
    contracts_dir = tmp_path / "contracts" / "schemas" / "shared"
    contracts_dir.mkdir(parents=True)
    schema_src = Path("contracts/schemas/shared/session_handoff.schema.json")
    (contracts_dir / "session_handoff.schema.json").write_text(
        schema_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    _write_structured_handoff(tmp_path, date_value="2020-01-01")

    result = gates._g_handoff_coherence(tmp_path)

    assert result["status"] == "FAIL"
    assert any("BLOCKED_HANDOFF_INCOMPLETE" in str(item) for item in result.get("violations", []))


def test_handoff_coherence_rejects_missing_next_action(tmp_path):
    contracts_dir = tmp_path / "contracts" / "schemas" / "shared"
    contracts_dir.mkdir(parents=True)
    schema_src = Path("contracts/schemas/shared/session_handoff.schema.json")
    (contracts_dir / "session_handoff.schema.json").write_text(
        schema_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    handoff = tmp_path / "SESSION_HANDOFF.md"
    handoff.write_text(
        f"""---
data_ultima_sessao: {datetime.date.today().isoformat()}
branch_ativo: main
ci_status: PASS
modulo_foco: governance
fase_roadmap: 1
task_id: phase-1
resultado: PENDENTE
bloqueios_ativos: []
---
# SESSION HANDOFF — HB TRACK

## Estado Geral
**Data:** {datetime.date.today().isoformat()} | **Branch:** main | **CI:** PASS

## O que foi feito
- item

## Próxima ação permitida
- item

## Bloqueios ativos
- Nenhum.
""",
        encoding="utf-8",
    )

    result = gates._g_handoff_coherence(tmp_path)

    assert result["status"] == "FAIL"
    assert any("proxima_acao_permitida" in str(item) for item in result.get("violations", []))


def test_module_status_coherence_blocks_with_adversarial_fail(tmp_path):
    canon = tmp_path / "docs" / "_canon"
    canon.mkdir(parents=True)
    (canon / "MODULE_REGISTRY.yaml").write_text(
        "modules:\n  training:\n    status: implementation_ready\n    expected_surfaces: []\n",
        encoding="utf-8",
    )
    adv_dir = tmp_path / "_reports" / "adversarial"
    adv_dir.mkdir(parents=True)
    (adv_dir / "training.adversarial.json").write_text(
        json.dumps({"module": "training", "overall_status": "FAIL", "risks": []}),
        encoding="utf-8",
    )

    result = gates._g_module_status_coherence(tmp_path)

    assert result["status"] == "FAIL"
    assert result["blocking_code"] == "BLOCKED_REGISTRY_MISMATCH"


def test_ui_alignment_detects_missing_operationid(tmp_path):
    oa_dir = tmp_path / "contracts" / "openapi"
    oa_dir.mkdir(parents=True)
    (oa_dir / "openapi.yaml").write_text("operationId: existingOperation\n", encoding="utf-8")
    ui_dir = tmp_path / "docs" / "hbtrack" / "modulos" / "training"
    ui_dir.mkdir(parents=True)
    (ui_dir / "UI_CONTRACT_TRAINING.md").write_text(
        "Use `getNonExistentOperationXyz` to fetch data.\n",
        encoding="utf-8",
    )

    result = gates._g14_ui_doc_validation(tmp_path)

    assert result["status"] == "FAIL"
    assert any("getNonExistentOperationXyz" in str(item) for item in result.get("violations", []))


def test_waiver_engine_accepts_valid_waiver(tmp_path, monkeypatch):
    baseline_dir = tmp_path / "contracts" / "openapi" / "baseline"
    baseline_dir.mkdir(parents=True)
    (baseline_dir / "openapi_baseline.json").write_text(
        json.dumps(
            {
                "openapi": "3.1.0",
                "paths": {
                    "/sessions": {
                        "get": {
                            "operationId": "listSessions",
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    openapi_dir = tmp_path / "contracts" / "openapi"
    (openapi_dir / "openapi.yaml").write_text("openapi: 3.1.0\npaths: {}\n", encoding="utf-8")

    waivers_dir = tmp_path / "contracts" / "_waivers"
    waivers_dir.mkdir(parents=True)
    expiry = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).isoformat()
    (waivers_dir / "test_waiver.json").write_text(
        json.dumps(
            {
                "gate_id": "CONTRACT_BREAKING_CHANGE_GATE",
                "expires_at_utc": expiry,
            }
        ),
        encoding="utf-8",
    )

    original_which = gates.shutil.which
    monkeypatch.setattr(
        gates.shutil,
        "which",
        lambda name: None if name == "oasdiff" else original_which(name),
    )

    result = gates._g9_contract_breaking_change(tmp_path)

    assert result["status"] == "PASS"
    assert "waiver ativo" in result["summary"].lower()


def test_shadow_authority_detects_docs_guias_without_disclaimer(tmp_path):
    guias = tmp_path / "docs" / "guias"
    guias.mkdir(parents=True)
    (guias / "BAD_GUIDE.md").write_text(
        "# Guia\n> SSOT para decisões futuras.\n",
        encoding="utf-8",
    )

    result = gates._g2k_shadow_authority(tmp_path)

    assert result["status"] == "FAIL"
    assert any("docs/guias/BAD_GUIDE.md" in str(item) for item in result.get("violations", []))


def test_canon_does_not_delegate_to_guias_or_missing_environment_doc():
    system_scope = Path("docs/_canon/SYSTEM_SCOPE.md").read_text(encoding="utf-8")
    global_invariants = Path("docs/_canon/GLOBAL_INVARIANTS.md").read_text(encoding="utf-8")
    architecture = Path("docs/_canon/ARCHITECTURE.md").read_text(encoding="utf-8")

    assert "docs/guias/IDENTITY_RBAC.md" not in system_scope
    assert "docs/guias/MVP_SCOPE.md" not in global_invariants
    assert "docs/_canon/contratos/Ambiente.md" not in architecture


def test_non_sovereign_roots_have_readme_disclaimers():
    assert Path("docs/guias/README.md").exists()
    assert Path("_reports/README.md").exists()
