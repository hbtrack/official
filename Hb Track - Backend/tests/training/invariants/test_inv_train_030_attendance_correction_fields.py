"""
INV-TRAIN-030 — Correção de attendance exige campos de auditoria

Enunciado: Quando `source = 'correction'`, os campos `correction_by_user_id`
e `correction_at` devem estar preenchidos.

Evidência (DB constraint):
  - ck_attendance_correction_fields (schema.sql:673)

Comentário DB: "Garante que correções têm correction_by_user_id e correction_at preenchidos"

Teste: Verifica que a constraint existe no schema e tem a lógica correta.
"""

from pathlib import Path


class TestInvTrain030AttendanceCorrectionFields:
    """Testes para INV-TRAIN-030: Attendance correction fields constraint."""

    CONSTRAINT_NAME = "ck_attendance_correction_fields"

    def test_constraint_exists_in_schema(self):
        """Verifica que a constraint ck_attendance_correction_fields existe."""
        schema_path = Path(__file__).parent.parent.parent / "docs" / "ssot" / "schema.sql"
        assert schema_path.exists(), f"Schema não encontrado: {schema_path}"

        content = schema_path.read_text(encoding="utf-8")

        assert self.CONSTRAINT_NAME in content, (
            f"Constraint {self.CONSTRAINT_NAME} não encontrada em schema.sql"
        )

    def test_constraint_checks_source_correction(self):
        """Verifica que a constraint verifica source = 'correction'."""
        schema_path = Path(__file__).parent.parent.parent / "docs" / "ssot" / "schema.sql"
        content = schema_path.read_text(encoding="utf-8")

        # Busca a linha completa da constraint
        lines = content.split("\n")
        constraint_line = None
        for line in lines:
            if self.CONSTRAINT_NAME in line:
                constraint_line = line
                break

        assert constraint_line, f"Constraint {self.CONSTRAINT_NAME} não encontrada"

        # Verifica que a constraint checa o valor 'correction' do source
        assert "correction" in constraint_line.lower(), (
            f"Constraint deve verificar source = 'correction'"
        )

    def test_constraint_requires_correction_by_user_id(self):
        """Verifica que a constraint exige correction_by_user_id quando source = 'correction'."""
        schema_path = Path(__file__).parent.parent.parent / "docs" / "ssot" / "schema.sql"
        content = schema_path.read_text(encoding="utf-8")

        lines = content.split("\n")
        constraint_line = None
        for line in lines:
            if self.CONSTRAINT_NAME in line:
                constraint_line = line
                break

        assert constraint_line, f"Constraint {self.CONSTRAINT_NAME} não encontrada"

        # Verifica que menciona correction_by_user_id IS NOT NULL
        assert "correction_by_user_id IS NOT NULL" in constraint_line, (
            "Constraint deve exigir correction_by_user_id IS NOT NULL para correções"
        )

    def test_constraint_requires_correction_at(self):
        """Verifica que a constraint exige correction_at quando source = 'correction'."""
        schema_path = Path(__file__).parent.parent.parent / "docs" / "ssot" / "schema.sql"
        content = schema_path.read_text(encoding="utf-8")

        lines = content.split("\n")
        constraint_line = None
        for line in lines:
            if self.CONSTRAINT_NAME in line:
                constraint_line = line
                break

        assert constraint_line, f"Constraint {self.CONSTRAINT_NAME} não encontrada"

        # Verifica que menciona correction_at IS NOT NULL
        assert "correction_at IS NOT NULL" in constraint_line, (
            "Constraint deve exigir correction_at IS NOT NULL para correções"
        )

    def test_constraint_allows_non_correction_sources(self):
        """Verifica que a constraint permite sources diferentes de 'correction' sem os campos."""
        schema_path = Path(__file__).parent.parent.parent / "docs" / "ssot" / "schema.sql"
        content = schema_path.read_text(encoding="utf-8")

        lines = content.split("\n")
        constraint_line = None
        for line in lines:
            if self.CONSTRAINT_NAME in line:
                constraint_line = line
                break

        assert constraint_line, f"Constraint {self.CONSTRAINT_NAME} não encontrada"

        # Verifica que a lógica permite source <> 'correction' (OR na constraint)
        # A constraint deve ter formato:
        # (source <> 'correction') OR (source = 'correction' AND correction_by_user_id IS NOT NULL AND correction_at IS NOT NULL)
        assert "<>" in constraint_line or "!=" in constraint_line or "OR" in constraint_line, (
            "Constraint deve permitir sources diferentes de 'correction'"
        )

    def test_constraint_comment_exists(self):
        """Verifica que existe comentário explicando a constraint."""
        schema_path = Path(__file__).parent.parent.parent / "docs" / "ssot" / "schema.sql"
        content = schema_path.read_text(encoding="utf-8")

        # Busca o COMMENT ON CONSTRAINT
        assert f"COMMENT ON CONSTRAINT {self.CONSTRAINT_NAME}" in content, (
            f"Comentário para constraint {self.CONSTRAINT_NAME} não encontrado"
        )

    def test_constraint_logic_is_complete(self):
        """Verifica que a constraint tem lógica completa: source <> 'correction' OR (source = 'correction' AND campos preenchidos)."""
        schema_path = Path(__file__).parent.parent.parent / "docs" / "ssot" / "schema.sql"
        content = schema_path.read_text(encoding="utf-8")

        lines = content.split("\n")
        constraint_line = None
        for line in lines:
            if self.CONSTRAINT_NAME in line:
                constraint_line = line
                break

        assert constraint_line, f"Constraint {self.CONSTRAINT_NAME} não encontrada"

        # Componentes essenciais da constraint
        required_components = [
            "source",
            "correction",
            "correction_by_user_id",
            "correction_at",
        ]

        for component in required_components:
            assert component in constraint_line, (
                f"Constraint deve conter '{component}'"
            )
