"""
TM-045..TM-047 — Ingestion / import rules.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-036, DR-TRAIN-037, DR-TRAIN-038).
target-state: regras de ingestão de dados externos não implementadas.
"""
import json
from pathlib import Path

from training.application.common.services import TrainingServices
from training.application import use_cases as training_use_cases


_REPO_ROOT = Path(__file__).resolve().parents[4]
_ROUTE_SNAPSHOT = _REPO_ROOT / "src/training/tests/unit/_route_snapshot.json"


class TestIngestionRules:
    """DR-TRAIN-036..038: regras de importação de dados externos."""

    def test_route_inventory_has_no_import_or_ingestion_endpoints(self):
        inventory = json.loads(_ROUTE_SNAPSHOT.read_text(encoding="utf-8"))
        paths = [entry["path"].lower() for entry in inventory]
        assert all("import" not in path for path in paths)
        assert all("ingest" not in path for path in paths)

    def test_training_services_exposes_no_ingestion_factories(self):
        public_methods = [
            name for name, value in vars(TrainingServices).items()
            if callable(value) and not name.startswith("_")
        ]
        assert not [name for name in public_methods if "import" in name.lower() or "ingest" in name.lower()]

    def test_application_shim_exports_no_ingestion_use_cases(self):
        exported = dir(training_use_cases)
        assert not [name for name in exported if "import" in name.lower() or "ingest" in name.lower()]
