"""
INV-TRAIN-031 — Derivação automática de phase_focus a partir dos percentuais

Enunciado: Os campos booleanos `phase_focus_attack`, `phase_focus_defense`,
`phase_focus_transition_offense` e `phase_focus_transition_defense` são derivados
automaticamente quando a soma dos percentuais correspondentes ≥ 5%.

Evidência (DB trigger + constraints):
  - tr_derive_phase_focus (schema.sql:5201)
  - fn_derive_phase_focus (schema.sql:190-220)
  - ck_phase_focus_attack_consistency (schema.sql:2629)
  - ck_phase_focus_defense_consistency (schema.sql:2630)
  - ck_phase_focus_transition_defense_consistency (schema.sql:2631)
  - ck_phase_focus_transition_offense_consistency (schema.sql:2632)

Comentário DB: "Step 3: Deriva automaticamente phase_focus_* baseado no threshold de 5%"

Teste: Verifica que o trigger, função e constraints existem no schema com a lógica correta.
"""

from pathlib import Path


class TestInvTrain031DerivePhasceFocus:
    """Testes para INV-TRAIN-031: Derivação automática de phase_focus."""

    TRIGGER_NAME = "tr_derive_phase_focus"
    FUNCTION_NAME = "fn_derive_phase_focus"
    THRESHOLD = 5
    CONSISTENCY_CONSTRAINTS = [
        "ck_phase_focus_attack_consistency",
        "ck_phase_focus_defense_consistency",
        "ck_phase_focus_transition_defense_consistency",
        "ck_phase_focus_transition_offense_consistency",
    ]

    def _get_schema_content(self) -> str:
        schema_path = Path(__file__).parent.parent.parent / "docs" / "_generated" / "schema.sql"
        assert schema_path.exists(), f"Schema não encontrado: {schema_path}"
        return schema_path.read_text(encoding="utf-8")

    def test_trigger_exists_in_schema(self):
        """Verifica que o trigger tr_derive_phase_focus existe."""
        content = self._get_schema_content()
        assert self.TRIGGER_NAME in content, (
            f"Trigger {self.TRIGGER_NAME} não encontrado em schema.sql"
        )

    def test_function_exists_in_schema(self):
        """Verifica que a função fn_derive_phase_focus existe."""
        content = self._get_schema_content()
        assert self.FUNCTION_NAME in content, (
            f"Função {self.FUNCTION_NAME} não encontrada em schema.sql"
        )

    def test_trigger_on_training_sessions(self):
        """Verifica que o trigger está na tabela training_sessions."""
        content = self._get_schema_content()
        lines = content.split("\n")

        trigger_line = None
        for line in lines:
            if self.TRIGGER_NAME in line and "CREATE TRIGGER" in line:
                trigger_line = line
                break

        assert trigger_line, f"Trigger {self.TRIGGER_NAME} CREATE não encontrado"
        assert "training_sessions" in trigger_line, (
            "Trigger deve estar na tabela training_sessions"
        )

    def test_trigger_fires_on_focus_columns(self):
        """Verifica que o trigger dispara nas colunas de foco."""
        content = self._get_schema_content()
        lines = content.split("\n")

        trigger_line = None
        for line in lines:
            if self.TRIGGER_NAME in line and "CREATE TRIGGER" in line:
                trigger_line = line
                break

        assert trigger_line, f"Trigger {self.TRIGGER_NAME} não encontrado"

        # Colunas que devem disparar o trigger
        expected_columns = [
            "focus_attack_positional_pct",
            "focus_attack_technical_pct",
            "focus_defense_positional_pct",
            "focus_defense_technical_pct",
            "focus_transition_offense_pct",
            "focus_transition_defense_pct",
            "focus_physical_pct",
        ]

        for col in expected_columns:
            assert col in trigger_line, (
                f"Trigger deve disparar na coluna {col}"
            )

    def test_function_uses_threshold_5(self):
        """Verifica que a função usa threshold de 5%."""
        content = self._get_schema_content()

        # Busca a definição da função
        assert "v_threshold CONSTANT NUMERIC := 5" in content, (
            "Função deve usar threshold de 5%"
        )

    def test_function_derives_phase_focus_attack(self):
        """Verifica que a função deriva phase_focus_attack."""
        content = self._get_schema_content()

        assert "NEW.phase_focus_attack" in content, (
            "Função deve derivar phase_focus_attack"
        )
        assert "focus_attack_positional_pct" in content, (
            "Função deve usar focus_attack_positional_pct"
        )
        assert "focus_attack_technical_pct" in content, (
            "Função deve usar focus_attack_technical_pct"
        )

    def test_function_derives_phase_focus_defense(self):
        """Verifica que a função deriva phase_focus_defense."""
        content = self._get_schema_content()

        assert "NEW.phase_focus_defense" in content, (
            "Função deve derivar phase_focus_defense"
        )
        assert "focus_defense_positional_pct" in content, (
            "Função deve usar focus_defense_positional_pct"
        )
        assert "focus_defense_technical_pct" in content, (
            "Função deve usar focus_defense_technical_pct"
        )

    def test_function_derives_phase_focus_transition_offense(self):
        """Verifica que a função deriva phase_focus_transition_offense."""
        content = self._get_schema_content()

        assert "NEW.phase_focus_transition_offense" in content, (
            "Função deve derivar phase_focus_transition_offense"
        )
        assert "focus_transition_offense_pct" in content, (
            "Função deve usar focus_transition_offense_pct"
        )

    def test_function_derives_phase_focus_transition_defense(self):
        """Verifica que a função deriva phase_focus_transition_defense."""
        content = self._get_schema_content()

        assert "NEW.phase_focus_transition_defense" in content, (
            "Função deve derivar phase_focus_transition_defense"
        )
        assert "focus_transition_defense_pct" in content, (
            "Função deve usar focus_transition_defense_pct"
        )

    def test_consistency_constraints_exist(self):
        """Verifica que as constraints de consistência existem."""
        content = self._get_schema_content()

        for constraint in self.CONSISTENCY_CONSTRAINTS:
            assert constraint in content, (
                f"Constraint {constraint} não encontrada em schema.sql"
            )

    def test_constraints_validate_threshold_5(self):
        """Verifica que as constraints validam threshold de 5."""
        content = self._get_schema_content()

        for constraint in self.CONSISTENCY_CONSTRAINTS:
            # Busca a linha da constraint
            lines = content.split("\n")
            constraint_line = None
            for line in lines:
                if constraint in line:
                    constraint_line = line
                    break

            assert constraint_line, f"Constraint {constraint} não encontrada"
            assert ">= (5)" in constraint_line or ">= 5" in constraint_line, (
                f"Constraint {constraint} deve validar threshold >= 5"
            )

    def test_function_comment_exists(self):
        """Verifica que existe comentário explicando a função."""
        content = self._get_schema_content()

        assert f"COMMENT ON FUNCTION public.{self.FUNCTION_NAME}" in content, (
            f"Comentário para função {self.FUNCTION_NAME} não encontrado"
        )

    def test_function_comment_mentions_threshold(self):
        """Verifica que o comentário menciona o threshold de 5%."""
        content = self._get_schema_content()
        lines = content.split("\n")

        comment_line = None
        for line in lines:
            if f"COMMENT ON FUNCTION public.{self.FUNCTION_NAME}" in line:
                comment_line = line
                break

        assert comment_line, f"Comentário para {self.FUNCTION_NAME} não encontrado"
        assert "5%" in comment_line, (
            "Comentário deve mencionar threshold de 5%"
        )

    def test_trigger_is_before_insert_or_update(self):
        """Verifica que o trigger é BEFORE INSERT OR UPDATE."""
        content = self._get_schema_content()
        lines = content.split("\n")

        trigger_line = None
        for line in lines:
            if self.TRIGGER_NAME in line and "CREATE TRIGGER" in line:
                trigger_line = line
                break

        assert trigger_line, f"Trigger {self.TRIGGER_NAME} não encontrado"
        assert "BEFORE INSERT OR UPDATE" in trigger_line, (
            "Trigger deve ser BEFORE INSERT OR UPDATE"
        )
