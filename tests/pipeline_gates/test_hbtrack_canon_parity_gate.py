from __future__ import annotations

from pathlib import Path

from scripts.contracts.validate import validate_contracts as gates


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_minimal_hbtrack_workspace(root: Path) -> None:
    _write(
        root / "docs" / "_canon" / "MODULE_REGISTRY.yaml",
        """modules:
  identity_access:
    status: implemented
    expected_surfaces: [permissions]
  training:
    status: implemented
    expected_surfaces: [permissions, state_model]
""",
    )
    _write(
        root / "docs" / "_canon" / "MODULE_SOURCE_AUTHORITY_MATRIX.yaml",
        """modules:
  identity_access:
    inference:
      must_not_infer: []
  training:
    inference:
      must_not_infer: [authentication_logic]
""",
    )
    _write(root / "docs" / "_canon" / "decisions" / "ADR-017-training-session-state-machine.md", "# ADR-017\n")

    _write(
        root / "docs" / "hbtrack" / "modulos" / "identity_access" / "PERMISSIONS_IDENTITY_ACCESS.md",
        """---
module: "identity_access"
type: "permissions"
---
# PERMISSIONS_IDENTITY_ACCESS.md

> **Nota canônica:** Este módulo é a fonte soberana de autenticação e autorização (ADR-007, ADR-008).
""",
    )
    _write(
        root / "docs" / "hbtrack" / "modulos" / "training" / "PERMISSIONS_TRAINING.md",
        """---
module: "training"
type: "permissions"
---
# PERMISSIONS_TRAINING.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autenticação e autorização.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008; ADR-007 para JWT/session).
""",
    )
    _write(
        root / "docs" / "hbtrack" / "modulos" / "training" / "STATE_MODEL_TRAINING.md",
        """---
module: "training"
type: "state-model"
adr_ref: "../../../_canon/decisions/ADR-017-training-session-state-machine.md"
---
# STATE_MODEL_TRAINING.md
""",
    )


def test_hbtrack_canon_parity_gate_passes_when_modules_respect_global_authority(tmp_path):
    _write_minimal_hbtrack_workspace(tmp_path)

    result = gates._g2q_hbtrack_canon_parity(tmp_path)

    assert result["status"] == "PASS"


def test_hbtrack_canon_parity_gate_fails_for_module_dir_outside_registry(tmp_path):
    _write_minimal_hbtrack_workspace(tmp_path)
    _write(
        tmp_path / "docs" / "hbtrack" / "modulos" / "ghost" / "PERMISSIONS_GHOST.md",
        """---
module: "ghost"
type: "permissions"
---
# ghost
""",
    )

    result = gates._g2q_hbtrack_canon_parity(tmp_path)

    assert result["status"] == "FAIL"
    assert any("ghost" in item["artifact"] for item in result.get("violations", []))


def test_hbtrack_canon_parity_gate_fails_when_permissions_doc_does_not_point_to_identity_access(tmp_path):
    _write_minimal_hbtrack_workspace(tmp_path)
    _write(
        tmp_path / "docs" / "hbtrack" / "modulos" / "training" / "PERMISSIONS_TRAINING.md",
        """---
module: "training"
type: "permissions"
---
# PERMISSIONS_TRAINING.md

Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
""",
    )

    result = gates._g2q_hbtrack_canon_parity(tmp_path)

    assert result["status"] == "FAIL"
    assert any("PERMISSIONS_TRAINING.md" in item["artifact"] for item in result.get("violations", []))


def test_hbtrack_canon_parity_gate_fails_when_state_model_has_no_canonical_anchor(tmp_path):
    _write_minimal_hbtrack_workspace(tmp_path)
    _write(
        tmp_path / "docs" / "hbtrack" / "modulos" / "training" / "STATE_MODEL_TRAINING.md",
        """---
module: "training"
type: "state-model"
---
# STATE_MODEL_TRAINING.md
""",
    )

    result = gates._g2q_hbtrack_canon_parity(tmp_path)

    assert result["status"] == "FAIL"
    assert any("STATE_MODEL_TRAINING.md" in item["artifact"] for item in result.get("violations", []))
