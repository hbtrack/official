"""
INV-TRAIN-008 — Soft delete "reason pair" (deleted_at e deleted_reason coerentes)

Enunciado: deleted_at e deleted_reason são ambos NULL ou ambos preenchidos.

Evidência (DB constraints no módulo TRAINING):
  - ck_training_sessions_deleted_reason (schema.sql:2634)
  - ck_wellness_post_deleted_reason (schema.sql:2829)
  - ck_wellness_pre_deleted_reason (schema.sql:2890)
  - ck_attendance_deleted_reason (schema.sql:674)

Teste: Verifica que as constraints existem no schema e têm a lógica correta.
"""

from pathlib import Path
import re


class TestInvTrain008SoftDeleteReasonPair:
    """Testes para INV-TRAIN-008: Soft delete reason pair constraints."""

    # Tabelas do módulo TRAINING que devem ter a constraint
    TRAINING_TABLES_WITH_SOFT_DELETE = [
        "training_sessions",
        "wellness_post",
        "wellness_pre",
        "attendance",
    ]

    def test_training_tables_have_deleted_reason_constraint(self):
        """Verifica que todas as tabelas TRAINING têm constraint de deleted_reason."""
        schema_path = Path(__file__).parent.parent.parent.parent / "docs" / "ssot" / "schema.sql"
        assert schema_path.exists(), f"Schema não encontrado: {schema_path}"

        content = schema_path.read_text(encoding="utf-8")

        missing_constraints = []
        for table in self.TRAINING_TABLES_WITH_SOFT_DELETE:
            constraint_name = f"ck_{table}_deleted_reason"
            if constraint_name not in content:
                missing_constraints.append(table)

        assert not missing_constraints, (
            f"Tabelas sem constraint de deleted_reason: {missing_constraints}"
        )

    def test_deleted_reason_constraint_logic_is_correct(self):
        """Verifica que a lógica da constraint é: ambos NULL ou ambos NOT NULL."""
        schema_path = Path(__file__).parent.parent.parent.parent / "docs" / "ssot" / "schema.sql"
        content = schema_path.read_text(encoding="utf-8")

        for table in self.TRAINING_TABLES_WITH_SOFT_DELETE:
            constraint_name = f"ck_{table}_deleted_reason"

            # Busca a linha completa da constraint
            lines = content.split("\n")
            constraint_line = None
            for line in lines:
                if constraint_name in line:
                    constraint_line = line
                    break

            assert constraint_line, f"Constraint {constraint_name} não encontrada"

            # Verifica os componentes essenciais da constraint
            # Padrão: ((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR
            #         ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL))
            assert "deleted_at IS NULL" in constraint_line, (
                f"Constraint {constraint_name} deve verificar 'deleted_at IS NULL'"
            )
            assert "deleted_reason IS NULL" in constraint_line, (
                f"Constraint {constraint_name} deve verificar 'deleted_reason IS NULL'"
            )
            assert "deleted_at IS NOT NULL" in constraint_line, (
                f"Constraint {constraint_name} deve verificar 'deleted_at IS NOT NULL'"
            )
            assert "deleted_reason IS NOT NULL" in constraint_line, (
                f"Constraint {constraint_name} deve verificar 'deleted_reason IS NOT NULL'"
            )
            assert " OR " in constraint_line, (
                f"Constraint {constraint_name} deve ter operador OR"
            )

    def test_training_sessions_constraint_exists(self):
        """Verifica constraint específica em training_sessions."""
        schema_path = Path(__file__).parent.parent.parent.parent / "docs" / "ssot" / "schema.sql"
        content = schema_path.read_text(encoding="utf-8")

        assert "ck_training_sessions_deleted_reason" in content, (
            "Constraint ck_training_sessions_deleted_reason não encontrada em schema.sql"
        )

    def test_wellness_pre_constraint_exists(self):
        """Verifica constraint específica em wellness_pre."""
        schema_path = Path(__file__).parent.parent.parent.parent / "docs" / "ssot" / "schema.sql"
        content = schema_path.read_text(encoding="utf-8")

        assert "ck_wellness_pre_deleted_reason" in content, (
            "Constraint ck_wellness_pre_deleted_reason não encontrada em schema.sql"
        )

    def test_wellness_post_constraint_exists(self):
        """Verifica constraint específica em wellness_post."""
        schema_path = Path(__file__).parent.parent.parent.parent / "docs" / "ssot" / "schema.sql"
        content = schema_path.read_text(encoding="utf-8")

        assert "ck_wellness_post_deleted_reason" in content, (
            "Constraint ck_wellness_post_deleted_reason não encontrada em schema.sql"
        )

    def test_attendance_constraint_exists(self):
        """Verifica constraint específica em attendance."""
        schema_path = Path(__file__).parent.parent.parent.parent / "docs" / "ssot" / "schema.sql"
        content = schema_path.read_text(encoding="utf-8")

        assert "ck_attendance_deleted_reason" in content, (
            "Constraint ck_attendance_deleted_reason não encontrada em schema.sql"
        )
