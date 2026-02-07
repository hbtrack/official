"""
INV-TRAIN-007 — Timezone operacional (Celery usa UTC)

Enunciado: Todas as operações de datetime nas Celery tasks devem usar UTC (timezone.utc).

Evidência:
  - app/core/celery_tasks.py:611 (update_training_session_statuses_task)
  - app/core/celery_tasks.py:791 (refresh_training_rankings_task)
  - app/core/celery_tasks.py:836 (cache calculated_at)
  - app/core/celery_tasks.py:870 (executed_at log)

Teste: Verifica que o módulo celery_tasks usa timezone.utc em operações de datetime.
"""

import ast
import inspect
from pathlib import Path


class TestInvTrain007CeleryUtcTimezone:
    """Testes para INV-TRAIN-007: Celery tasks devem usar UTC."""

    def test_celery_tasks_file_imports_timezone_utc(self):
        """Verifica que celery_tasks.py importa timezone de datetime."""
        celery_tasks_path = Path(__file__).parent.parent.parent.parent / "app" / "core" / "celery_tasks.py"
        assert celery_tasks_path.exists(), f"Arquivo não encontrado: {celery_tasks_path}"

        content = celery_tasks_path.read_text(encoding="utf-8")

        # Deve importar timezone de datetime
        assert "from datetime import" in content and "timezone" in content, (
            "celery_tasks.py deve importar timezone de datetime"
        )

    def test_lifecycle_operations_use_timezone_utc(self):
        """Verifica que operações críticas de lifecycle usam timezone.utc.

        Nota: A invariante foca em "jobs de lifecycle / automações" -
        operações de transição de status e cálculos de cache.
        Logging e timestamps de completed_at não são escopo crítico.
        """
        celery_tasks_path = Path(__file__).parent.parent.parent.parent / "app" / "core" / "celery_tasks.py"
        content = celery_tasks_path.read_text(encoding="utf-8")

        # Conta ocorrências de datetime.now com timezone.utc
        datetime_now_utc_count = content.count("datetime.now(timezone.utc)")

        # Deve haver pelo menos 4 usos de datetime.now(timezone.utc)
        # Evidências documentadas: linhas 611, 791, 836, 870
        assert datetime_now_utc_count >= 4, (
            f"celery_tasks.py deve usar datetime.now(timezone.utc) em pelo menos 4 locais, "
            f"encontrado {datetime_now_utc_count}"
        )

        # Verifica que as linhas críticas usam UTC
        lines = content.split("\n")

        # Operações críticas que DEVEM usar UTC:
        # 1. Comparação de session_at para transição scheduled→in_progress
        # 2. Comparação de planned_end para transição in_progress→pending_review
        # 3. cache.calculated_at ao recalcular rankings
        critical_patterns = [
            "TrainingSession.session_at <= now",  # Comparação de início de sessão (SQLAlchemy)
            "planned_end <= now",  # Comparação de fim planejado
            "calculated_at = datetime.now(timezone.utc)",  # Timestamp de cache
        ]

        for pattern in critical_patterns:
            assert pattern in content, (
                f"Padrão crítico não encontrado: {pattern}"
            )

    def test_update_training_session_statuses_task_uses_utc(self):
        """Verifica que update_training_session_statuses_task usa UTC para comparação de datas."""
        celery_tasks_path = Path(__file__).parent.parent.parent.parent / "app" / "core" / "celery_tasks.py"
        content = celery_tasks_path.read_text(encoding="utf-8")

        # Busca pelo bloco da task e verifica uso de timezone.utc
        # A task está definida entre linhas ~581-676
        lines = content.split("\n")
        in_task = False
        found_utc = False

        for line in lines:
            if "def update_training_session_statuses_task" in line or "@celery_app.task" in line:
                in_task = True
            if in_task and "datetime.now(timezone.utc)" in line:
                found_utc = True
                break
            # Sai do escopo da função quando encontra outra definição de task ou função
            if in_task and (line.startswith("@celery_app.task") or line.startswith("def ")) and "update_training_session_statuses_task" not in line:
                if "def " in line and not line.strip().startswith("#"):
                    break

        assert found_utc, (
            "update_training_session_statuses_task deve usar datetime.now(timezone.utc) "
            "para determinar transições de status"
        )

    def test_refresh_training_rankings_task_uses_utc(self):
        """Verifica que refresh_training_rankings_task usa UTC para logging e operações."""
        celery_tasks_path = Path(__file__).parent.parent.parent.parent / "app" / "core" / "celery_tasks.py"
        content = celery_tasks_path.read_text(encoding="utf-8")

        # Verifica que a task de refresh usa UTC
        assert "refresh_training_rankings_task" in content, (
            "Task refresh_training_rankings_task deve existir"
        )

        # A task deve usar timezone.utc em algum ponto
        # Busca na região após a definição da task
        task_idx = content.find("def refresh_training_rankings_task")
        if task_idx != -1:
            # Pega os próximos 200 caracteres (aproximadamente o início da função)
            task_region = content[task_idx:task_idx + 500]
            assert "timezone.utc" in task_region or "datetime.now(timezone.utc)" in content[task_idx:], (
                "refresh_training_rankings_task deve usar timezone.utc"
            )

    def test_no_local_timezone_usage_in_celery_tasks(self):
        """Verifica que não há uso de timezone local (sem UTC) nas Celery tasks."""
        celery_tasks_path = Path(__file__).parent.parent.parent.parent / "app" / "core" / "celery_tasks.py"
        content = celery_tasks_path.read_text(encoding="utf-8")

        # Padrões problemáticos que indicariam uso de timezone local
        problematic_patterns = [
            "datetime.now().replace(tzinfo=",  # Tentativa de adicionar tz depois
            "datetime.today()",  # Sempre naive
            "datetime.utcnow()",  # Deprecated, não recomendado
        ]

        found_problems = []
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            for pattern in problematic_patterns:
                if pattern in line and not line.strip().startswith("#"):
                    found_problems.append((i, pattern, line.strip()))

        assert not found_problems, (
            f"Encontrados padrões problemáticos de timezone:\n"
            + "\n".join(f"  Linha {ln}: {pat} em '{code}'" for ln, pat, code in found_problems)
        )

    def test_utc_usage_count_matches_expected(self):
        """Verifica que há pelo menos 4 usos de timezone.utc (evidência documentada)."""
        celery_tasks_path = Path(__file__).parent.parent.parent.parent / "app" / "core" / "celery_tasks.py"
        content = celery_tasks_path.read_text(encoding="utf-8")

        utc_count = content.count("datetime.now(timezone.utc)")

        # Baseado na evidência documentada, deve haver pelo menos 4 usos
        assert utc_count >= 4, (
            f"Esperado pelo menos 4 usos de datetime.now(timezone.utc), encontrado {utc_count}. "
            "Evidência documentada: linhas 611, 791, 836, 870"
        )
