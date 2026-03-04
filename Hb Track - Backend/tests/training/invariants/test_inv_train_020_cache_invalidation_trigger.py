"""
INV-TRAIN-020 — Cache invalidation automático após mudanças em sessões

Enunciado: Trigger `tr_invalidate_analytics_cache` invalida cache de analytics
automaticamente quando training_sessions é modificado.

Evidência (DB trigger):
  - schema.sql:5208 (tr_invalidate_analytics_cache)
  - Executa: fn_invalidate_analytics_cache()

Teste: Verifica que o trigger existe e está configurado corretamente.
"""

from pathlib import Path
import re


class TestInvTrain020CacheInvalidationTrigger:
    """Testes para INV-TRAIN-020: Cache invalidation via DB trigger."""

    def test_trigger_exists_in_schema(self):
        """Verifica que o trigger tr_invalidate_analytics_cache existe."""
        schema_path = (
            Path(__file__).parent.parent.parent.parent
            / "docs"
            / "ssot"
            / "schema.sql"
        )
        assert schema_path.exists(), f"Schema não encontrado: {schema_path}"

        content = schema_path.read_text(encoding="utf-8")
        assert "tr_invalidate_analytics_cache" in content, (
            "Trigger tr_invalidate_analytics_cache não encontrado em schema.sql"
        )

    def test_trigger_is_on_training_sessions_table(self):
        """Verifica que o trigger está na tabela training_sessions."""
        schema_path = (
            Path(__file__).parent.parent.parent.parent
            / "docs"
            / "ssot"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        # Busca a definição do trigger
        match = re.search(
            r"CREATE TRIGGER tr_invalidate_analytics_cache.*?ON\s+public\.(\w+)",
            content,
            re.DOTALL
        )
        assert match, "Definição do trigger não encontrada"
        table_name = match.group(1)
        assert table_name == "training_sessions", (
            f"Trigger deve estar em training_sessions, encontrado em {table_name}"
        )

    def test_trigger_fires_on_insert_update_delete(self):
        """Verifica que o trigger dispara em INSERT, UPDATE e DELETE."""
        schema_path = (
            Path(__file__).parent.parent.parent.parent
            / "docs"
            / "ssot"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        # Busca a linha do trigger
        lines = content.split("\n")
        trigger_line = None
        for line in lines:
            if "tr_invalidate_analytics_cache" in line and "CREATE TRIGGER" in line:
                trigger_line = line
                break

        assert trigger_line, "Linha do trigger não encontrada"
        assert "INSERT" in trigger_line, "Trigger deve disparar em INSERT"
        assert "UPDATE" in trigger_line, "Trigger deve disparar em UPDATE"
        assert "DELETE" in trigger_line, "Trigger deve disparar em DELETE"

    def test_trigger_executes_correct_function(self):
        """Verifica que o trigger executa fn_invalidate_analytics_cache."""
        schema_path = (
            Path(__file__).parent.parent.parent.parent
            / "docs"
            / "ssot"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        # Busca a linha do trigger
        lines = content.split("\n")
        trigger_line = None
        for line in lines:
            if "tr_invalidate_analytics_cache" in line and "CREATE TRIGGER" in line:
                trigger_line = line
                break

        assert trigger_line, "Linha do trigger não encontrada"
        assert "fn_invalidate_analytics_cache" in trigger_line, (
            "Trigger deve executar fn_invalidate_analytics_cache"
        )

    def test_trigger_fires_after_operation(self):
        """Verifica que o trigger dispara AFTER (não BEFORE)."""
        schema_path = (
            Path(__file__).parent.parent.parent.parent
            / "docs"
            / "ssot"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        # Busca a linha do trigger
        lines = content.split("\n")
        trigger_line = None
        for line in lines:
            if "tr_invalidate_analytics_cache" in line and "CREATE TRIGGER" in line:
                trigger_line = line
                break

        assert trigger_line, "Linha do trigger não encontrada"
        assert "AFTER" in trigger_line, (
            "Trigger deve disparar AFTER (para invalidar cache após mudança)"
        )

    def test_function_exists_in_schema(self):
        """Verifica que a função fn_invalidate_analytics_cache existe."""
        schema_path = (
            Path(__file__).parent.parent.parent.parent
            / "docs"
            / "ssot"
            / "schema.sql"
        )
        content = schema_path.read_text(encoding="utf-8")

        assert "fn_invalidate_analytics_cache" in content, (
            "Função fn_invalidate_analytics_cache não encontrada em schema.sql"
        )
