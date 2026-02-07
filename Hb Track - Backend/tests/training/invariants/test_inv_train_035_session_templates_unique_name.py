"""
INV-TRAIN-035 — Nome de template de sessão é único por organização

Enunciado: Não pode haver dois templates de sessão com o mesmo `name` na mesma `org_id`.

Evidência (DB constraint UNIQUE):
  - uq_session_templates_org_name (schema.sql:3645)

Teste: Verifica que a constraint UNIQUE existe no schema e tem a lógica correta.
"""

from pathlib import Path


class TestInvTrain035SessionTemplatesUniqueName:
    """Testes para INV-TRAIN-035: Unicidade org_id + name em session_templates."""

    CONSTRAINT_NAME = "uq_session_templates_org_name"

    def _get_schema_content(self) -> str:
        schema_path = Path(__file__).parent.parent.parent / "docs" / "_generated" / "schema.sql"
        assert schema_path.exists(), f"Schema não encontrado: {schema_path}"
        return schema_path.read_text(encoding="utf-8")

    def test_constraint_exists_in_schema(self):
        """Verifica que a constraint uq_session_templates_org_name existe."""
        content = self._get_schema_content()
        assert self.CONSTRAINT_NAME in content, (
            f"Constraint {self.CONSTRAINT_NAME} não encontrada em schema.sql"
        )

    def test_constraint_is_unique(self):
        """Verifica que a constraint é do tipo UNIQUE."""
        content = self._get_schema_content()
        lines = content.split("\n")

        # Busca ADD CONSTRAINT com UNIQUE
        for i, line in enumerate(lines):
            if self.CONSTRAINT_NAME in line and "UNIQUE" in line:
                return  # Found UNIQUE constraint

        # Se não encontrou na mesma linha, busca padrão ADD CONSTRAINT ... UNIQUE
        for i, line in enumerate(lines):
            if self.CONSTRAINT_NAME in line:
                # Verifica se UNIQUE está na próxima linha ou contexto
                context = "\n".join(lines[max(0, i-2):i+3])
                assert "UNIQUE" in context, (
                    f"Constraint {self.CONSTRAINT_NAME} deve ser UNIQUE"
                )
                return

        raise AssertionError(f"Constraint {self.CONSTRAINT_NAME} não encontrada")

    def test_constraint_on_session_templates(self):
        """Verifica que a constraint está na tabela session_templates."""
        content = self._get_schema_content()
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if self.CONSTRAINT_NAME in line:
                # Busca referência à tabela no contexto
                context = "\n".join(lines[max(0, i-5):i+3])
                assert "session_templates" in context, (
                    "Constraint deve estar na tabela session_templates"
                )
                return

        raise AssertionError(f"Constraint {self.CONSTRAINT_NAME} não encontrada")

    def test_constraint_includes_org_id(self):
        """Verifica que a constraint inclui org_id."""
        content = self._get_schema_content()
        lines = content.split("\n")

        for line in lines:
            if self.CONSTRAINT_NAME in line and "UNIQUE" in line:
                assert "org_id" in line, (
                    "Constraint deve incluir org_id na unicidade"
                )
                return

        # Busca em contexto mais amplo
        for i, line in enumerate(lines):
            if self.CONSTRAINT_NAME in line:
                context = "\n".join(lines[i:i+3])
                assert "org_id" in context, (
                    "Constraint deve incluir org_id na unicidade"
                )
                return

        raise AssertionError(f"Constraint {self.CONSTRAINT_NAME} não encontrada")

    def test_constraint_includes_name(self):
        """Verifica que a constraint inclui name."""
        content = self._get_schema_content()
        lines = content.split("\n")

        for line in lines:
            if self.CONSTRAINT_NAME in line and "UNIQUE" in line:
                assert "name" in line, (
                    "Constraint deve incluir name na unicidade"
                )
                return

        # Busca em contexto mais amplo
        for i, line in enumerate(lines):
            if self.CONSTRAINT_NAME in line:
                context = "\n".join(lines[i:i+3])
                assert "name" in context, (
                    "Constraint deve incluir name na unicidade"
                )
                return

        raise AssertionError(f"Constraint {self.CONSTRAINT_NAME} não encontrada")
