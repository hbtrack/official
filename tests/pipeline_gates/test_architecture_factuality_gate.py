from __future__ import annotations

from pathlib import Path

from scripts.contracts.validate import validate_contracts as gates


ROOT = Path(__file__).resolve().parents[2]


def _build_minimal_repo_with_checker(tmp_path: Path) -> Path:
    (tmp_path / "scripts" / "audit").mkdir(parents=True)
    checker_src = ROOT / "scripts" / "audit" / "check_architecture_docs.py"
    (tmp_path / "scripts" / "audit" / "check_architecture_docs.py").write_text(
        checker_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    infra = tmp_path / "infra"
    infra.mkdir()
    (infra / "docker-compose.yml").write_text(
        "services:\n  postgres:\n    image: postgres:12\n  redis:\n    image: redis:7-alpine\n",
        encoding="utf-8",
    )

    config = tmp_path / "config"
    config.mkdir()
    (config / "urls.py").write_text("urlpatterns = []\n", encoding="utf-8")
    (config / "settings.py").write_text("CHANNEL_LAYERS = {'default': {}}\n", encoding="utf-8")
    (config / "celery.py").write_text("app = object()\n", encoding="utf-8")

    src = tmp_path / "src" / "notifications"
    src.mkdir(parents=True)
    (src / "tasks.py").write_text("def x():\n    return None\n", encoding="utf-8")

    canon = tmp_path / "docs" / "_canon"
    canon.mkdir(parents=True)
    (canon / "RUNTIME_CURRENT_STATE.md").write_text(
        "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
        "| PostgreSQL local | materializado | postgres:12 |\n"
        "| `frontend/` | **materializado** | existe |\n"
        "| Endpoint `GET /health` | **ausente** | não existe |\n",
        encoding="utf-8",
    )
    (canon / "CODE_ARCHITECTURE.md").write_text(
        "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
        "Celery e WebSocket continuam sendo target-state aprovado, nao arquitetura de codigo atual.\n",
        encoding="utf-8",
    )
    (canon / "C4_COMPONENTS_BACKEND.md").write_text(
        "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
        "Backend materializado.\n",
        encoding="utf-8",
    )
    (canon / "ARCHITECTURE.md").write_text(
        "---\ndoc_type: canon\nstate_semantics: governance\n---\n"
        "- postgres:12 (atual) → PostgreSQL 16 (target-state aprovado)\n",
        encoding="utf-8",
    )
    (canon / "C4_CONTAINERS.md").write_text(
        "---\ndoc_type: canon\nstate_semantics: governance\n---\n"
        "| Frontend web SPA | ADR-030 | `frontend/` nao existe no workspace |\n",
        encoding="utf-8",
    )
    (tmp_path / "frontend").mkdir()

    decisions = canon / "decisions"
    decisions.mkdir(parents=True)
    (decisions / "ADR-031-backend-framework.md").write_text(
        "---\nadr_id: ADR-031\nstatus: accepted\n---\n",
        encoding="utf-8",
    )
    (canon / "MODULE_REGISTRY.yaml").write_text(
        "version: '1.0.0'\npolicy:\n  status_order: [scaffold, implemented]\nmodules:\n  notifications:\n    status: implemented\n",
        encoding="utf-8",
    )

    return tmp_path


def test_architecture_factuality_gate_passes_on_real_repo():
    result = gates._g_architecture_factuality(ROOT)

    assert result["status"] == "PASS", result


def test_architecture_factuality_gate_fails_on_bidirectional_drift(tmp_path):
    root = _build_minimal_repo_with_checker(tmp_path)

    result = gates._g_architecture_factuality(root)

    assert result["status"] == "FAIL"
    assert any("C4_CONTAINERS.md" in item["message"] or "CODE_ARCHITECTURE.md" in item["message"] for item in result["violations"])
