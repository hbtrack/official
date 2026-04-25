"""
Testes de regressão para o checker de drift arquitetural.

Garante que:
1. O checker PASSA no estado atual e válido do repositório.
2. O checker FALHA quando condições de drift são injetadas:
   - ADR com ID duplicado
   - MODULE_REGISTRY com status errado para módulo já implementado
   - Doc current-state afirmando frontend como presente quando ausente
   - Doc current-state afirmando Celery como runtime quando ausente
   - RUNTIME_CURRENT_STATE.md não documentando ausência de /health
   - RUNTIME_CURRENT_STATE.md não documentando versão real do PostgreSQL
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

# Adicionar raiz ao path para importar o checker
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "audit"))

from check_architecture_docs import (
    check_adr_id_uniqueness,
    check_health_endpoint_claim,
    check_module_registry_coherence,
    check_no_async_runtime_claims,
    check_no_frontend_claim_in_current_state,
    check_postgres_version_consistency,
    check_runtime_topology_claims,
    run_all_checks,
)


# ── Helpers de fixture ────────────────────────────────────────────────────────

def _build_minimal_repo(tmp_path: Path) -> Path:
    """
    Constrói um repositório mínimo válido para testes.
    Reflete o estado atual do workspace real.
    """
    # infra/docker-compose.yml
    infra = tmp_path / "infra"
    infra.mkdir()
    (infra / "docker-compose.yml").write_text(
        "services:\n  postgres:\n    image: postgres:12\n  redis:\n    image: redis:7-alpine\n",
        encoding="utf-8",
    )

    # config/urls.py — sem /health
    config = tmp_path / "config"
    config.mkdir()
    (config / "urls.py").write_text(
        "urlpatterns = [\n    path('api/', api.urls),\n]\n",
        encoding="utf-8",
    )
    (config / "settings.py").write_text(
        "DATABASES = {'default': {}}\n",
        encoding="utf-8",
    )

    # src/ — módulo de exemplo
    src = tmp_path / "src" / "training"
    src.mkdir(parents=True)
    (src / "api.py").write_text("router = None\n", encoding="utf-8")
    (src / "migrations").mkdir()
    (src / "tests").mkdir()

    # docs/_canon/decisions/ — Uma ADR sem duplicata
    decs = tmp_path / "docs" / "_canon" / "decisions"
    decs.mkdir(parents=True)
    (decs / "ADR-031-backend-framework.md").write_text(
        "---\nadr_id: ADR-031\ntitle: Backend\nstatus: accepted\n---\n# ADR-031\n",
        encoding="utf-8",
    )

    # MODULE_REGISTRY.yaml
    canon = tmp_path / "docs" / "_canon"
    registry = {
        "version": "1.0.0",
        "policy": {
            "status_order": [
                "scaffold", "draft_contract", "validated_contract",
                "implementation_ready", "implemented", "staging_validated", "released",
            ],
            "status_semantics": {
                "implemented": "Código materializado.",
                "staging_validated": "Validado em staging.",
                "released": "Em produção.",
            },
        },
        "modules": {
            "training": {
                "status": "implemented",
                "owner": "performance-tech",
                "expected_surfaces": ["module_docs_minimum"],
            }
        },
    }
    (canon / "MODULE_REGISTRY.yaml").write_text(
        yaml.dump(registry, allow_unicode=True),
        encoding="utf-8",
    )

    # ARCHITECTURE.md — §5 declara o delta de versão do PostgreSQL
    (canon / "ARCHITECTURE.md").write_text(
        "---\ndoc_type: canon\nstate_semantics: governance\n---\n"
        "# Arquitectura\n"
        "## §5 Deltas de estado atual → target-state\n"
        "- postgres:12 (atual) → PostgreSQL 16 (target-state aprovado)\n",
        encoding="utf-8",
    )

    # RUNTIME_CURRENT_STATE.md — declara ausências corretamente
    (canon / "RUNTIME_CURRENT_STATE.md").write_text(
        "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
        "# Runtime Atual\n"
        "| PostgreSQL local | materializado | infra/docker-compose.yml — serviço `postgres:12` |\n"
        "| `frontend/` | **ausente** | não existe no workspace |\n"
        "| Endpoint `GET /health` | **ausente** | `config/urls.py` não declara rota `/health` |\n",
        encoding="utf-8",
    )

    # C4_COMPONENTS_BACKEND.md e CODE_ARCHITECTURE.md — sem claims problemáticas
    (canon / "C4_COMPONENTS_BACKEND.md").write_text(
        "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
        "# C4 Componentes\n"
        "Backend Django + Django Ninja materializado.\n",
        encoding="utf-8",
    )
    (canon / "CODE_ARCHITECTURE.md").write_text(
        "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
        "# Code Architecture\n"
        "Interface -> Application -> Domain -> Infrastructure.\n",
        encoding="utf-8",
    )

    return tmp_path


# ── Teste de sanidade: passo no estado válido ─────────────────────────────────

class TestFullPassOnValidState:
    """O checker deve passar em todos os checks com um repositório válido."""

    def test_all_checks_pass_on_minimal_valid_repo(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        report = run_all_checks(root)

        failures = [c for c in report.checks if c.status == "FAIL"]
        assert not failures, (
            f"Checks falharam em repositório válido: "
            + ", ".join(f"{c.name}: {c.message}" for c in failures)
        )
        assert report.status == "PASS"

    def test_all_checks_pass_on_real_repo(self):
        """Validação contra o repositório real atual."""
        report = run_all_checks(ROOT)

        failures = [c for c in report.checks if c.status == "FAIL"]
        assert not failures, (
            "Checker falhou no repositório real — indica drift arquitetural:\n"
            + "\n".join(
                f"  [{c.name}] {c.message}\n"
                + "\n".join(f"    → {d}" for d in c.details)
                for c in failures
            )
        )
        assert report.status == "PASS"


# ── Testes de detecção de drift ───────────────────────────────────────────────

class TestAdrIdUniqueness:
    """CHECK 1: Detectar duplicatas de adr_id."""

    def test_passes_with_unique_ids(self, tmp_path):
        decs = tmp_path / "docs" / "_canon" / "decisions"
        decs.mkdir(parents=True)
        (decs / "ADR-031-backend.md").write_text(
            "---\nadr_id: ADR-031\nstatus: accepted\n---\n",
            encoding="utf-8",
        )
        (decs / "ADR-032-training.md").write_text(
            "---\nadr_id: ADR-032\nstatus: accepted\n---\n",
            encoding="utf-8",
        )
        result = check_adr_id_uniqueness(tmp_path)
        assert result.status == "PASS"

    def test_fails_with_duplicate_id(self, tmp_path):
        decs = tmp_path / "docs" / "_canon" / "decisions"
        decs.mkdir(parents=True)
        (decs / "ADR-031-backend-framework.md").write_text(
            "---\nadr_id: ADR-031\nstatus: accepted\n---\n",
            encoding="utf-8",
        )
        # Segunda ADR com MESMO adr_id (simulando o bug histórico ADR-031/ADR-034)
        (decs / "ADR-031-scope-boundary.md").write_text(
            "---\nadr_id: ADR-031\nstatus: proposed\n---\n",
            encoding="utf-8",
        )
        result = check_adr_id_uniqueness(tmp_path)
        assert result.status == "FAIL"
        assert "ADR-031" in result.details[0]

    def test_skips_when_no_adr_files(self, tmp_path):
        decs = tmp_path / "docs" / "_canon" / "decisions"
        decs.mkdir(parents=True)
        result = check_adr_id_uniqueness(tmp_path)
        assert result.status == "SKIP"


class TestPostgresVersionConsistency:
    """CHECK 2: Detectar inconsistências de versão do PostgreSQL."""

    def test_passes_when_runtime_doc_matches_compose(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        result = check_postgres_version_consistency(root)
        assert result.status == "PASS"

    def test_fails_when_runtime_doc_does_not_mention_compose_version(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        # RUNTIME_CURRENT_STATE.md sem menção à versão real do compose
        (root / "docs" / "_canon" / "RUNTIME_CURRENT_STATE.md").write_text(
            "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
            "# Runtime Atual\n"
            "Banco de dados: PostgreSQL (sem versão especificada).\n",
            encoding="utf-8",
        )
        result = check_postgres_version_consistency(root)
        assert result.status == "FAIL"
        assert "postgres:12" in result.message or "postgres:12" in str(result.details)

    def test_skips_when_compose_missing(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        (root / "infra" / "docker-compose.yml").unlink()
        result = check_postgres_version_consistency(root)
        assert result.status == "SKIP"


class TestNoFrontendClaimInCurrentState:
    """CHECK 3: Detectar claims de frontend em docs current-state quando frontend/ ausente."""

    def test_passes_when_frontend_absent_and_not_claimed(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        # frontend/ não existe por padrão no repo mínimo
        result = check_no_frontend_claim_in_current_state(root)
        assert result.status == "PASS"

    def test_passes_when_frontend_exists_and_no_doc_claims_absence(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        (root / "frontend").mkdir()
        canon = root / "docs" / "_canon"
        (canon / "RUNTIME_CURRENT_STATE.md").write_text(
            "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
            "# Runtime Atual\n"
            "| PostgreSQL local | materializado | infra/docker-compose.yml — serviço `postgres:12` |\n"
            "| `frontend/` | **materializado** | existe no workspace |\n"
            "| Endpoint `GET /health` | **ausente** | `config/urls.py` não declara rota `/health` |\n",
            encoding="utf-8",
        )
        result = check_no_frontend_claim_in_current_state(root)
        assert result.status == "PASS"

    def test_fails_when_frontend_exists_but_doc_claims_absence(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        (root / "frontend").mkdir()
        canon = root / "docs" / "_canon"
        (canon / "C4_CONTAINERS.md").write_text(
            "---\ndoc_type: canon\nstate_semantics: governance\n---\n"
            "| Frontend web SPA | ADR-030 | `frontend/` nao existe no workspace |\n",
            encoding="utf-8",
        )
        result = check_no_frontend_claim_in_current_state(root)
        assert result.status == "FAIL"
        assert "C4_CONTAINERS.md" in str(result.details)

    def test_fails_when_current_state_doc_claims_frontend_present(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        # Injetar claim positiva de frontend em doc current-state
        canon = root / "docs" / "_canon"
        (canon / "C4_COMPONENTS_BACKEND.md").write_text(
            "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
            "| frontend/ | ✓ | materializado no workspace |\n",
            encoding="utf-8",
        )
        result = check_no_frontend_claim_in_current_state(root)
        assert result.status == "FAIL"
        assert "C4_COMPONENTS_BACKEND.md" in str(result.details)


class TestNoAsyncRuntimeClaims:
    """CHECK 4: Detectar claims de Celery/Channels em docs current-state quando ausentes."""

    def test_passes_when_async_absent_and_not_claimed(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        result = check_no_async_runtime_claims(root)
        assert result.status == "PASS"

    def test_passes_when_celery_config_exists_and_docs_do_not_claim_absence(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        (root / "config" / "celery.py").write_text("app = Celery()\n", encoding="utf-8")
        result = check_no_async_runtime_claims(root)
        assert result.status == "PASS"

    def test_fails_when_async_runtime_exists_but_doc_claims_target_state_only(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        (root / "config" / "celery.py").write_text("app = Celery()\n", encoding="utf-8")
        (root / "config" / "settings.py").write_text(
            "CHANNEL_LAYERS = {'default': {}}\n",
            encoding="utf-8",
        )
        canon = root / "docs" / "_canon"
        (canon / "CODE_ARCHITECTURE.md").write_text(
            "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
            "Celery e WebSocket continuam sendo target-state aprovado, nao arquitetura de codigo atual.\n",
            encoding="utf-8",
        )
        result = check_no_async_runtime_claims(root)
        assert result.status == "FAIL"
        assert "CODE_ARCHITECTURE.md" in str(result.details)

    def test_fails_when_current_state_doc_claims_celery_running(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        canon = root / "docs" / "_canon"
        # Injetar claim positiva de Celery em doc current-state
        (canon / "RUNTIME_CURRENT_STATE.md").write_text(
            "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
            "# Runtime Atual\n"
            "| Celery configurado | ✓ | config/celery.py presente |\n"
            "| `frontend/` | **ausente** | não existe no workspace |\n"
            "| Endpoint `GET /health` | **ausente** | config/urls.py não tem /health |\n"
            "| PostgreSQL local | materializado | postgres:12 |\n",
            encoding="utf-8",
        )
        result = check_no_async_runtime_claims(root)
        assert result.status == "FAIL"

    def test_passes_when_celery_mentioned_as_absent(self, tmp_path):
        """Linhas que documentam ausência do Celery não devem ser flagadas."""
        root = _build_minimal_repo(tmp_path)
        canon = root / "docs" / "_canon"
        (canon / "C4_COMPONENTS_BACKEND.md").write_text(
            "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
            "# Componentes\n"
            "| Worker Celery | ausente | nenhum config/celery.py nem tasks.py |\n",
            encoding="utf-8",
        )
        result = check_no_async_runtime_claims(root)
        assert result.status == "PASS"


class TestRuntimeTopologyClaims:
    def test_passes_when_topology_docs_match_repo(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        config = root / "config"
        (config / "asgi.py").write_text("application = object()\n", encoding="utf-8")
        notifications = root / "src" / "notifications"
        notifications.mkdir(parents=True)
        (notifications / "middleware.py").write_text("class TokenAuthMiddleware: ...\n", encoding="utf-8")
        (root / "Dockerfile.frontend").write_text("FROM nginx:alpine\n", encoding="utf-8")
        infra = root / "infra"
        (infra / "docker-compose.staging.yml").write_text("services: {}\n", encoding="utf-8")
        canon = root / "docs" / "_canon"
        (canon / "C4_CONTAINERS.md").write_text(
            "---\ndoc_type: canon\nstate_semantics: governance\n---\n"
            "| Backend ASGI | config/asgi.py | runtime ASGI materializado |\n"
            "| Auth middleware websocket | src/notifications/middleware.py | TokenAuthMiddleware presente |\n"
            "| Frontend deploy | Dockerfile.frontend | imagem SPA materializada |\n",
            encoding="utf-8",
        )
        result = check_runtime_topology_claims(root)
        assert result.status == "PASS"

    def test_fails_when_topology_doc_denies_materialized_runtime(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        config = root / "config"
        (config / "asgi.py").write_text("application = object()\n", encoding="utf-8")
        notifications = root / "src" / "notifications"
        notifications.mkdir(parents=True)
        (notifications / "middleware.py").write_text("class TokenAuthMiddleware: ...\n", encoding="utf-8")
        (root / "Dockerfile.frontend").write_text("FROM nginx:alpine\n", encoding="utf-8")
        infra = root / "infra"
        (infra / "docker-compose.staging.yml").write_text("services: {}\n", encoding="utf-8")
        canon = root / "docs" / "_canon"
        (canon / "C4_CONTAINERS.md").write_text(
            "---\ndoc_type: canon\nstate_semantics: governance\n---\n"
            "config/asgi.py continua target-state aprovado.\n"
            "src/notifications/middleware.py ainda nao materializado.\n"
            "Dockerfile.frontend ausente no workspace.\n",
            encoding="utf-8",
        )
        result = check_runtime_topology_claims(root)
        assert result.status == "FAIL"
        assert "repo:" in result.details[0]


class TestModuleRegistryCoherence:
    """CHECK 5: Detectar inconsistências entre MODULE_REGISTRY e src/."""

    def test_passes_when_implemented_module_has_all_artifacts(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        result = check_module_registry_coherence(root)
        assert result.status == "PASS"

    def test_fails_when_implemented_module_lacks_migrations(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        # Remover migrations do módulo training que está como 'implemented'
        import shutil
        shutil.rmtree(root / "src" / "training" / "migrations")
        result = check_module_registry_coherence(root)
        assert result.status == "FAIL"
        assert any("training" in d for d in result.details)

    def test_fails_when_implemented_module_lacks_tests(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        import shutil
        shutil.rmtree(root / "src" / "training" / "tests")
        result = check_module_registry_coherence(root)
        assert result.status == "FAIL"

    def test_fails_when_implementation_ready_module_has_full_code(self, tmp_path):
        """
        Módulo marcado como 'implementation_ready' mas com api.py + migrations/ + tests/
        deveria ser 'implemented'.
        """
        root = _build_minimal_repo(tmp_path)
        # Mudar status para implementation_ready
        registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
        reg = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        reg["modules"]["training"]["status"] = "implementation_ready"
        registry_path.write_text(yaml.dump(reg, allow_unicode=True), encoding="utf-8")

        result = check_module_registry_coherence(root)
        assert result.status == "FAIL"
        assert any("implementation_ready" in d or "implemented" in d for d in result.details)

    def test_passes_when_scaffold_module_has_no_code(self, tmp_path):
        """Módulo scaffold sem código é válido."""
        root = _build_minimal_repo(tmp_path)
        registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
        reg = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        # Adicionar módulo novo sem código
        reg["modules"]["new_module"] = {
            "status": "scaffold",
            "owner": "test",
            "expected_surfaces": [],
        }
        registry_path.write_text(yaml.dump(reg, allow_unicode=True), encoding="utf-8")

        result = check_module_registry_coherence(root)
        assert result.status == "PASS"


class TestHealthEndpointClaim:
    """CHECK 6: Detectar ausência de /health não documentada."""

    def test_passes_when_health_absent_and_documented_as_absent(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        result = check_health_endpoint_claim(root)
        assert result.status == "PASS"

    def test_skips_when_health_route_exists(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        (root / "config" / "urls.py").write_text(
            "urlpatterns = [\n    path('health', health_view),\n    path('api/', api.urls),\n]\n",
            encoding="utf-8",
        )
        result = check_health_endpoint_claim(root)
        assert result.status == "SKIP"

    def test_fails_when_runtime_doc_does_not_declare_health_absent(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        # RUNTIME_CURRENT_STATE.md sem mencionar ausência de /health
        (root / "docs" / "_canon" / "RUNTIME_CURRENT_STATE.md").write_text(
            "---\ndoc_type: canon\nstate_semantics: current-state\n---\n"
            "# Runtime Atual\n"
            "| PostgreSQL local | materializado | postgres:12 |\n"
            "| `frontend/` | **ausente** | não existe |\n"
            "Sem menção ao /health.\n",
            encoding="utf-8",
        )
        result = check_health_endpoint_claim(root)
        assert result.status == "FAIL"

    def test_skips_when_urls_missing(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        (root / "config" / "urls.py").unlink()
        result = check_health_endpoint_claim(root)
        assert result.status == "SKIP"


# ── Teste de output JSON ──────────────────────────────────────────────────────

class TestJsonOutput:
    """O checker deve emitir JSON válido com --json."""

    def test_json_output_structure(self, tmp_path):
        root = _build_minimal_repo(tmp_path)
        report = run_all_checks(root)

        # Simular serialização JSON
        output = {
            "status": report.status,
            "total_pass": report.total_pass,
            "total_fail": report.total_fail,
            "total_skip": report.total_skip,
            "total_error": report.total_error,
            "checks": [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                }
                for r in report.checks
            ],
        }

        # Deve ser serializável
        serialized = json.dumps(output)
        parsed = json.loads(serialized)

        assert parsed["status"] in ("PASS", "FAIL", "ERROR")
        assert isinstance(parsed["checks"], list)
        for check in parsed["checks"]:
            assert "name" in check
            assert "status" in check
            assert check["status"] in ("PASS", "FAIL", "SKIP", "ERROR")
