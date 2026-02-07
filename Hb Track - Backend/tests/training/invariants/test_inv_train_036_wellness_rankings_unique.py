"""
INV-TRAIN-036 — Ranking de wellness é único por time e mês

Enunciado: Não pode haver dois registros de ranking para o mesmo `team_id` e `month_reference`.

Evidência (DB constraint UNIQUE):
  - uq_team_wellness_rankings_team_month (schema.sql:3653)

Teste: Verifica que a constraint UNIQUE existe no schema e tem a lógica correta.
"""

from pathlib import Path


class TestInvTrain036WellnessRankingsUnique:
    """Testes para INV-TRAIN-036: Unicidade team_id + month_reference em team_wellness_rankings."""

    CONSTRAINT_NAME = "uq_team_wellness_rankings_team_month"

    def _get_schema_content(self) -> str:
        schema_path = Path(__file__).parent.parent.parent / "docs" / "_generated" / "schema.sql"
        assert schema_path.exists(), f"Schema não encontrado: {schema_path}"
        return schema_path.read_text(encoding="utf-8")

    def test_constraint_exists_in_schema(self):
        """Verifica que a constraint uq_team_wellness_rankings_team_month existe."""
        content = self._get_schema_content()
        assert self.CONSTRAINT_NAME in content, (
            f"Constraint {self.CONSTRAINT_NAME} não encontrada em schema.sql"
        )

    def test_constraint_is_unique(self):
        """Verifica que a constraint é do tipo UNIQUE."""
        content = self._get_schema_content()
        lines = content.split("\n")

        # Busca a linha com ADD CONSTRAINT que contém UNIQUE
        for i, line in enumerate(lines):
            if self.CONSTRAINT_NAME in line and "UNIQUE" in line:
                return  # Found

        # Também aceita se UNIQUE está na mesma linha de ADD CONSTRAINT
        for i, line in enumerate(lines):
            if "ADD CONSTRAINT" in line and self.CONSTRAINT_NAME in line:
                context = "\n".join(lines[i:i+2])
                if "UNIQUE" in context:
                    return

        raise AssertionError(f"Constraint {self.CONSTRAINT_NAME} deve ser UNIQUE")

    def test_constraint_on_team_wellness_rankings(self):
        """Verifica que a constraint está na tabela team_wellness_rankings."""
        content = self._get_schema_content()
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if self.CONSTRAINT_NAME in line:
                context = "\n".join(lines[max(0, i-5):i+3])
                assert "team_wellness_rankings" in context, (
                    "Constraint deve estar na tabela team_wellness_rankings"
                )
                return

        raise AssertionError(f"Constraint {self.CONSTRAINT_NAME} não encontrada")

    def test_constraint_includes_team_id(self):
        """Verifica que a constraint inclui team_id."""
        content = self._get_schema_content()
        lines = content.split("\n")

        # Busca a linha com ADD CONSTRAINT ou UNIQUE (definição real)
        for i, line in enumerate(lines):
            if self.CONSTRAINT_NAME in line and "UNIQUE" in line:
                assert "team_id" in line, (
                    "Constraint deve incluir team_id na unicidade"
                )
                return

        raise AssertionError(f"Constraint {self.CONSTRAINT_NAME} com UNIQUE não encontrada")

    def test_constraint_includes_month_reference(self):
        """Verifica que a constraint inclui month_reference."""
        content = self._get_schema_content()
        lines = content.split("\n")

        # Busca a linha com ADD CONSTRAINT ou UNIQUE (definição real)
        for i, line in enumerate(lines):
            if self.CONSTRAINT_NAME in line and "UNIQUE" in line:
                assert "month_reference" in line, (
                    "Constraint deve incluir month_reference na unicidade"
                )
                return

        raise AssertionError(f"Constraint {self.CONSTRAINT_NAME} com UNIQUE não encontrada")
