"""
INV-TRAIN-037 — Data de início do ciclo deve ser anterior à data de término

Enunciado: O campo `start_date` deve ser menor que `end_date` em training_cycles.

Evidência (DB constraint):
  - check_cycle_dates (schema.sql:2402)

Teste: Verifica que a constraint existe no schema e tem a lógica correta.
"""

from pathlib import Path


class TestInvTrain037CycleDates:
    """Testes para INV-TRAIN-037: start_date < end_date em training_cycles."""

    CONSTRAINT_NAME = "check_cycle_dates"

    def _get_schema_content(self) -> str:
        schema_path = Path(__file__).parent.parent.parent.parent / "docs" / "ssot" / "schema.sql"
        assert schema_path.exists(), f"Schema não encontrado: {schema_path}"
        return schema_path.read_text(encoding="utf-8")

    def test_constraint_exists_in_schema(self):
        """Verifica que a constraint check_cycle_dates existe."""
        content = self._get_schema_content()
        assert self.CONSTRAINT_NAME in content, (
            f"Constraint {self.CONSTRAINT_NAME} não encontrada em schema.sql"
        )

    def test_constraint_on_training_cycles_table(self):
        """Verifica que a constraint está na tabela training_cycles."""
        content = self._get_schema_content()
        lines = content.split("\n")

        in_training_cycles = False
        constraint_found = False

        for line in lines:
            if "CREATE TABLE public.training_cycles" in line:
                in_training_cycles = True
            elif in_training_cycles and line.strip().startswith(");"):
                break
            elif in_training_cycles and self.CONSTRAINT_NAME in line:
                constraint_found = True
                break

        assert constraint_found, (
            f"Constraint {self.CONSTRAINT_NAME} deve estar na tabela training_cycles"
        )

    def test_constraint_checks_start_date(self):
        """Verifica que a constraint verifica o campo start_date."""
        content = self._get_schema_content()
        lines = content.split("\n")

        constraint_line = None
        for line in lines:
            if self.CONSTRAINT_NAME in line:
                constraint_line = line
                break

        assert constraint_line, f"Constraint {self.CONSTRAINT_NAME} não encontrada"
        assert "start_date" in constraint_line, (
            "Constraint deve verificar o campo start_date"
        )

    def test_constraint_checks_end_date(self):
        """Verifica que a constraint verifica o campo end_date."""
        content = self._get_schema_content()
        lines = content.split("\n")

        constraint_line = None
        for line in lines:
            if self.CONSTRAINT_NAME in line:
                constraint_line = line
                break

        assert constraint_line, f"Constraint {self.CONSTRAINT_NAME} não encontrada"
        assert "end_date" in constraint_line, (
            "Constraint deve verificar o campo end_date"
        )

    def test_constraint_uses_less_than_operator(self):
        """Verifica que a constraint usa operador < para comparação."""
        content = self._get_schema_content()
        lines = content.split("\n")

        constraint_line = None
        for line in lines:
            if self.CONSTRAINT_NAME in line:
                constraint_line = line
                break

        assert constraint_line, f"Constraint {self.CONSTRAINT_NAME} não encontrada"
        assert "start_date < end_date" in constraint_line or "start_date <" in constraint_line, (
            "Constraint deve usar start_date < end_date"
        )
