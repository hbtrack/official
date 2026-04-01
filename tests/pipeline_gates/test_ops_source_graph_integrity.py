from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
OPS_ROOT = ROOT / "docs" / "_canon" / "graph" / "ops"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_ops_graph_files_exist_and_are_active():
    expected = {
        "environment_catalog.yaml": "OPS_ENVIRONMENT_CATALOG",
        "secrets_catalog.yaml": "OPS_SECRETS_CATALOG",
        "service_topology.yaml": "OPS_SERVICE_TOPOLOGY",
        "deploy_contract.yaml": "OPS_DEPLOY_CONTRACT",
        "runtime_endpoints.yaml": "OPS_RUNTIME_ENDPOINTS",
        "github_actions_catalog.yaml": "OPS_GITHUB_ACTIONS_CATALOG",
    }

    for filename, artifact in expected.items():
        path = OPS_ROOT / filename
        assert path.exists(), f"{filename} deve existir"
        payload = _load_yaml(path)
        assert payload["artifact"] == artifact
        assert payload["status"] == "active"


def test_environment_catalog_covers_required_envs_and_variables():
    payload = _load_yaml(OPS_ROOT / "environment_catalog.yaml")
    assert set(payload["environments"].keys()) == {"development", "staging", "production"}

    variable_names = {entry["name"] for entry in payload["variables"]}
    assert {
        "SECRET_KEY",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
        "DB_TEST_NAME",
        "REDIS_URL",
        "CELERY_BROKER_URL",
        "CORS_ALLOWED_ORIGINS",
        "LOG_LEVEL",
        "DATABASE_URL",
    } <= variable_names

    assert payload["environments"]["staging"]["deploy_dir"] == "/opt/hbtrack/staging"
    assert payload["environments"]["production"]["deploy_dir"] == "/opt/hbtrack/production"


def test_secrets_catalog_covers_github_secrets_and_runtime_contracts():
    payload = _load_yaml(OPS_ROOT / "secrets_catalog.yaml")
    secret_names = {entry["name"] for entry in payload["github_actions"]["secrets"]}
    variable_names = {entry["name"] for entry in payload["github_actions"]["variables"]}
    runtime_secret_names = {entry["name"] for entry in payload["runtime_secrets"]}

    assert {
        "GITHUB_TOKEN",
        "VPS_HOST_STAGING",
        "VPS_HOST_PRODUCTION",
        "VPS_USER",
        "VPS_SSH_KEY",
        "PACT_BROKER_TOKEN",
        "JWT_PRIVATE_KEY",
        "JWT_PUBLIC_KEY",
        "POSTGRES_PASSWORD",
        "CLOUDINARY_URL",
    } <= secret_names
    assert {"STAGING_URL", "PRODUCTION_URL"} <= variable_names
    assert {
        "SECRET_KEY",
        "DB_PASSWORD",
        "POSTGRES_PASSWORD",
        "JWT_PRIVATE_KEY",
        "JWT_PUBLIC_KEY",
        "CLOUDINARY_URL",
        "RESEND_API_KEY",
        "GEMINI_API_KEY",
    } <= runtime_secret_names


def test_service_topology_covers_required_services():
    payload = _load_yaml(OPS_ROOT / "service_topology.yaml")
    services = payload["services"]

    assert {"api", "postgres", "redis", "worker", "beat", "nginx", "pact_broker"} <= set(services.keys())
    assert services["worker"]["compose_service"] == "celery_worker"
    assert services["beat"]["compose_service"] == "celery_beat"
    assert services["pact_broker"]["deployment_type"] == "external_same_vps"


def test_deploy_contract_covers_prechecks_health_rollback_and_evidence():
    payload = _load_yaml(OPS_ROOT / "deploy_contract.yaml")

    assert payload["pre_checks"]
    assert set(payload["health_checks"].keys()) == {"staging", "production"}
    assert payload["rollback"]["script_ref"] == "infra/scripts/rollback.sh"
    assert "approve" in payload["promotion_flow"]
    assert payload["evidence"]["required_refs"]


def test_runtime_endpoints_cover_health_openapi_and_pact_broker():
    payload = _load_yaml(OPS_ROOT / "runtime_endpoints.yaml")
    endpoints = {entry["name"]: entry for entry in payload["endpoints"]}

    assert {"health", "openapi_schema", "api_docs", "pact_broker"} <= set(endpoints.keys())
    assert endpoints["health"]["implementation_ref"] == "config/urls.py#health_check"
    assert endpoints["openapi_schema"]["path"] == "/api/openapi.json"
    assert endpoints["api_docs"]["path"] == "/api/docs"
    assert endpoints["pact_broker"]["urls"]["staging"] == "http://<VPS_IP>:9292"


def test_github_actions_catalog_matches_deploy_workflow_contract():
    payload = _load_yaml(OPS_ROOT / "github_actions_catalog.yaml")
    workflow = payload["workflows"]["deploy_pipeline"]
    job_ids = {job["id"] for job in workflow["jobs"]}

    assert workflow["workflow_ref"] == ".github/workflows/deploy.yml"
    assert {"staging", "production"} == set(workflow["github_environments"])
    assert {
        "validate",
        "test",
        "build",
        "deploy-staging",
        "contract-conformance",
        "approve",
        "deploy-production",
    } <= job_ids


def test_ops_graph_is_registered_in_usage_authority_and_sync_manifests():
    usage_manifest = _load_yaml(ROOT / "docs" / "_canon" / "DOC_USAGE_MANIFEST.yaml")
    source_graph = _load_yaml(ROOT / "docs" / "_canon" / "SOURCE_AUTHORITY_GRAPH.yaml")
    sync_manifest = _load_yaml(ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml")

    ops_usage = next(entry for entry in usage_manifest["entries"] if entry["rule_id"] == "CANON_OPS_GRAPH_IR")
    covered = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.glob(ops_usage["path_globs"][0])
        if path.is_file()
    }
    assert covered == {
        "docs/_canon/graph/ops/environment_catalog.yaml",
        "docs/_canon/graph/ops/secrets_catalog.yaml",
        "docs/_canon/graph/ops/service_topology.yaml",
        "docs/_canon/graph/ops/deploy_contract.yaml",
        "docs/_canon/graph/ops/runtime_endpoints.yaml",
        "docs/_canon/graph/ops/github_actions_catalog.yaml",
    }

    ops_concept = source_graph["concepts"]["operational_runtime_contracts"]
    assert ops_concept["owner_source"] == "docs/_canon/graph/ops/"

    ops_sync = next(rule for rule in sync_manifest["rules"] if rule["rule_id"] == "OPS_SOURCE_GRAPH_SYNC")
    assert ops_sync["source_master"] == "docs/_canon/graph/ops/"
    assert "docs/_canon/DEPLOY_PIPELINE.md" in ops_sync["blocking_consumers"]


def test_canon_docs_reference_ops_graph():
    for rel in (
        "docs/_canon/DEPLOY_PIPELINE.md",
        "docs/_canon/VPS_SETUP.md",
        "docs/_canon/OPERATIONS.md",
        "docs/_canon/decisions/ADR-012-secrets-policy.md",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "docs/_canon/graph/ops/" in text
