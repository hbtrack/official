"""
TM-045..TM-047 — Ingestion / import rules.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-036, DR-TRAIN-037, DR-TRAIN-038).
target-state: regras de ingestão de dados externos não implementadas.
"""
import pytest


class TestIngestionRules:
    """DR-TRAIN-036..038: regras de importação de dados externos."""

    @pytest.mark.skip(reason="target-state: data ingestion pipeline not yet implemented")
    def test_csv_import_validates_schema(self):
        pass

    @pytest.mark.skip(reason="target-state: data ingestion pipeline not yet implemented")
    def test_duplicate_import_detected(self):
        pass

    @pytest.mark.skip(reason="target-state: data ingestion pipeline not yet implemented")
    def test_invalid_import_produces_error_report(self):
        pass
