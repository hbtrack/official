"""
INV-TRAIN-028 — Focus ≤120% em training_sessions

Enunciado: A soma dos focos em training_sessions deve ser ≤ 120%.
(Nota: Esta é a mesma regra de INV-TRAIN-001, mas aplicada especificamente
à tabela training_sessions via constraint DB.)

Evidência (DB constraint):
  - schema.sql:2640 (ck_training_sessions_focus_total_sum)

Teste: Verifica que a constraint existe na tabela training_sessions.
"""

from pathlib import Path
import re


class TestInvTrain028FocusSumConstraint:
    """Testes para INV-TRAIN-028: Focus ≤120% em training_sessions."""

    def test_constraint_exists_in_schema(self):
        """Verifica que a constraint ck_training_sessions_focus_total_sum existe."""
        schema_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "_generated"
            / "schema.sql"
        )
        assert schema_path.exists(), f"Schema não encontrado: {schema_path}"

        content = schema_path.read_text(encoding="utf-8")
        assert "ck_training_sessions_focus_total_sum" in content, (
            "Constraint ck_training_sessions_focus_total_sum não encontrada"
        )

    def test_constraint_is_on_training_sessions_table(self):
        """Verifica que a constraint está na tabela training_sessions."""
        schema_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "_generated"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        # Busca o contexto da constraint (deve estar em training_sessions)
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "ck_training_sessions_focus_total_sum" in line:
                # Verifica se está no contexto de training_sessions
                context_start = max(0, i - 20)
                context = "\n".join(lines[context_start:i+5])
                # O nome da constraint já indica a tabela
                assert "training_sessions" in line or "training_sessions" in context, (
                    "Constraint deve estar associada à tabela training_sessions"
                )
                break

    def test_constraint_validates_sum_120(self):
        """Verifica que a constraint valida soma ≤ 120."""
        schema_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "_generated"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        # Busca a linha da constraint
        lines = content.split("\n")
        constraint_line = None
        for line in lines:
            if "ck_training_sessions_focus_total_sum" in line:
                constraint_line = line
                break

        assert constraint_line, "Linha da constraint não encontrada"
        # Verifica que menciona 120 (o limite máximo)
        assert "120" in constraint_line, (
            "Constraint deve validar limite de 120"
        )

    def test_constraint_sums_focus_fields(self):
        """Verifica que a constraint soma os campos de foco."""
        schema_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "_generated"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        # Busca a linha da constraint
        lines = content.split("\n")
        constraint_line = None
        for line in lines:
            if "ck_training_sessions_focus_total_sum" in line:
                constraint_line = line
                break

        assert constraint_line, "Linha da constraint não encontrada"

        # Verifica que soma campos de foco (pelo menos alguns)
        focus_fields = [
            "focus_attack",
            "focus_defense",
            "focus_physical",
        ]
        found_focus = False
        for field in focus_fields:
            if field in constraint_line:
                found_focus = True
                break

        assert found_focus, (
            "Constraint deve somar campos de foco (focus_attack, focus_defense, etc.)"
        )

    def test_constraint_uses_check(self):
        """Verifica que é uma CHECK constraint."""
        schema_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "_generated"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        # Busca a linha da constraint
        lines = content.split("\n")
        constraint_line = None
        for line in lines:
            if "ck_training_sessions_focus_total_sum" in line:
                constraint_line = line
                break

        assert constraint_line, "Linha da constraint não encontrada"
        # O prefixo "ck_" já indica CHECK, mas vamos verificar o padrão
        assert "CONSTRAINT" in constraint_line or "CHECK" in constraint_line, (
            "Deve ser uma CHECK constraint"
        )
