"""
INV-TRAIN-021 — Internal load calculado por trigger no DB

Enunciado: Trigger `tr_calculate_internal_load` calcula automaticamente
o internal_load no wellness_post via fórmula RPE × duração.

Evidência (DB trigger):
  - schema.sql:5194 (tr_calculate_internal_load)
  - Executa: fn_calculate_internal_load()

Teste: Verifica que o trigger existe e está configurado corretamente.
"""

from pathlib import Path
import re


class TestInvTrain021InternalLoadTrigger:
    """Testes para INV-TRAIN-021: Internal load calculado via DB trigger."""

    def test_trigger_exists_in_schema(self):
        """Verifica que o trigger tr_calculate_internal_load existe."""
        schema_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "ssot"
            / "schema.sql"
        )
        assert schema_path.exists(), f"Schema não encontrado: {schema_path}"

        content = schema_path.read_text(encoding="utf-8")
        assert "tr_calculate_internal_load" in content, (
            "Trigger tr_calculate_internal_load não encontrado em schema.sql"
        )

    def test_trigger_is_on_wellness_post_table(self):
        """Verifica que o trigger está na tabela wellness_post."""
        schema_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "ssot"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        # Busca a definição do trigger
        match = re.search(
            r"CREATE TRIGGER tr_calculate_internal_load.*?ON\s+public\.(\w+)",
            content,
            re.DOTALL
        )
        assert match, "Definição do trigger não encontrada"
        table_name = match.group(1)
        assert table_name == "wellness_post", (
            f"Trigger deve estar em wellness_post, encontrado em {table_name}"
        )

    def test_trigger_fires_on_insert_and_update(self):
        """Verifica que o trigger dispara em INSERT e UPDATE."""
        schema_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "ssot"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        # Busca a linha do trigger
        lines = content.split("\n")
        trigger_line = None
        for line in lines:
            if "tr_calculate_internal_load" in line and "CREATE TRIGGER" in line:
                trigger_line = line
                break

        assert trigger_line, "Linha do trigger não encontrada"
        assert "INSERT" in trigger_line, "Trigger deve disparar em INSERT"
        assert "UPDATE" in trigger_line, "Trigger deve disparar em UPDATE"

    def test_trigger_executes_correct_function(self):
        """Verifica que o trigger executa fn_calculate_internal_load."""
        schema_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "ssot"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        # Busca a linha do trigger
        lines = content.split("\n")
        trigger_line = None
        for line in lines:
            if "tr_calculate_internal_load" in line and "CREATE TRIGGER" in line:
                trigger_line = line
                break

        assert trigger_line, "Linha do trigger não encontrada"
        assert "fn_calculate_internal_load" in trigger_line, (
            "Trigger deve executar fn_calculate_internal_load"
        )

    def test_trigger_fires_before_operation(self):
        """Verifica que o trigger dispara BEFORE (para calcular antes de salvar)."""
        schema_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "ssot"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        # Busca a linha do trigger
        lines = content.split("\n")
        trigger_line = None
        for line in lines:
            if "tr_calculate_internal_load" in line and "CREATE TRIGGER" in line:
                trigger_line = line
                break

        assert trigger_line, "Linha do trigger não encontrada"
        assert "BEFORE" in trigger_line, (
            "Trigger deve disparar BEFORE (para calcular valor antes de salvar)"
        )

    def test_function_exists_in_schema(self):
        """Verifica que a função fn_calculate_internal_load existe."""
        schema_path = (
            Path(__file__).parent.parent.parent
            / "docs"
            / "ssot"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        assert "fn_calculate_internal_load" in content, (
            "Função fn_calculate_internal_load não encontrada em schema.sql"
        )
