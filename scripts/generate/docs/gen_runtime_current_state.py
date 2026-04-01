#!/usr/bin/env python3
"""
Generate docs/_canon/RUNTIME_CURRENT_STATE.md from the real repository state.

Usage:
  python scripts/generate/docs/gen_runtime_current_state.py --write
  python scripts/generate/docs/gen_runtime_current_state.py --check

Exit codes:
  0 = OK
  2 = Drift detected in --check mode
  3 = Harness / parsing error
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


EXIT_OK = 0
EXIT_DRIFT = 2
EXIT_ERROR = 3

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = REPO_ROOT / "docs" / "_canon" / "RUNTIME_CURRENT_STATE.md"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _load_module_registry(root: Path) -> dict[str, dict[str, Any]]:
    if yaml is None:
        raise RuntimeError("PyYAML não está instalado.")
    path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    modules = data.get("modules") or {}
    if not isinstance(modules, dict):
        raise RuntimeError("MODULE_REGISTRY.yaml inválido: chave `modules` ausente ou malformada.")
    return {str(module): entry for module, entry in modules.items() if isinstance(entry, dict)}


def _count_router_mounts(urls_text: str) -> int:
    return len(re.findall(r"api\.add_router\s*\(", urls_text))


def _has_health_route(urls_text: str) -> bool:
    return bool(
        re.search(r"""(path|url)\s*\(\s*['"/]health""", urls_text)
        or re.search(r"""['"/]health['"/]""", urls_text)
    )


def _postgres_image_tag(compose_text: str) -> str:
    match = re.search(r"image:\s*postgres:([^\s]+)", compose_text)
    return match.group(1) if match else "unknown"


def _has_redis_service(compose_text: str) -> bool:
    return bool(re.search(r"^\s*redis:\s*$", compose_text, flags=re.MULTILINE))


def _module_row(root: Path, module: str, status: str) -> str:
    src = root / "src" / module
    api = "✓" if (src / "api.py").exists() else "✗"
    migrations = "✓" if (src / "migrations").exists() else "✗"
    tests = "✓" if (src / "tests").exists() else "✗"
    return f"| `{module}` | `{status}` | {api} | {migrations} | {tests} |"


def generate_runtime_current_state(root: Path) -> str:
    modules = _load_module_registry(root)
    module_names = sorted(modules)

    settings_path = root / "config" / "settings.py"
    urls_path = root / "config" / "urls.py"
    compose_path = root / "infra" / "docker-compose.yml"

    settings_text = _read_text(settings_path)
    urls_text = _read_text(urls_path)
    compose_text = _read_text(compose_path)

    postgres_tag = _postgres_image_tag(compose_text)
    redis_service = _has_redis_service(compose_text)
    health_route = _has_health_route(urls_text)
    router_count = _count_router_mounts(urls_text)

    has_databases = "DATABASES" in settings_text
    has_channel_layers = "CHANNEL_LAYERS" in settings_text
    has_celery_config = (root / "config" / "celery.py").exists()
    tasks_count = len(list((root / "src").glob("*/tasks.py"))) if (root / "src").exists() else 0
    consumers_count = len(list((root / "src").glob("*/consumers.py"))) if (root / "src").exists() else 0

    openapi_paths = len(list((root / "contracts" / "openapi" / "paths").glob("*.yaml")))
    schema_dirs = sorted(
        path.name for path in (root / "contracts" / "schemas").iterdir() if path.is_dir()
    ) if (root / "contracts" / "schemas").exists() else []
    domain_schema_dirs = sorted(name for name in schema_dirs if name in modules)
    shared_schema_dirs = sorted(name for name in schema_dirs if name not in modules)
    async_channels = len(list((root / "contracts" / "asyncapi" / "channels").glob("*.yaml"))) if (root / "contracts" / "asyncapi" / "channels").exists() else 0
    workflows = len(list((root / "contracts" / "workflows").rglob("*.arazzo.yaml"))) if (root / "contracts" / "workflows").exists() else 0
    state_models = len(list((root / "docs" / "hbtrack" / "modulos").glob("*/STATE_MODEL_*.md"))) if (root / "docs" / "hbtrack" / "modulos").exists() else 0
    ui_contracts = len(list((root / "docs" / "hbtrack" / "modulos").glob("*/UI_CONTRACT_*.md"))) if (root / "docs" / "hbtrack" / "modulos").exists() else 0

    frontend_dir = root / "frontend"
    frontend_exists = frontend_dir.exists()
    frontend_package = (frontend_dir / "package.json").exists()
    frontend_src = (frontend_dir / "src").exists()
    frontend_schema_types = len(list(frontend_dir.rglob("schema.d.ts"))) if frontend_exists else 0

    dockerfile_root = (root / "Dockerfile").exists()
    compose_prod = (root / "infra" / "docker-compose.prod.yml").exists()
    nginx_conf = (root / "infra" / "nginx" / "nginx.conf").exists()
    rollback_script = (root / "infra" / "scripts" / "rollback.sh").exists()

    pipeline_gate_tests = len(list((root / "tests" / "pipeline_gates").glob("test_*.py"))) if (root / "tests" / "pipeline_gates").exists() else 0
    unit_test_dirs = len(list((root / "src").glob("*/tests/unit"))) if (root / "src").exists() else 0
    integration_test_dirs = len(list((root / "src").glob("*/tests/integration"))) if (root / "src").exists() else 0

    module_rows = "\n".join(
        _module_row(root, module, str(modules[module].get("status", "unknown")))
        for module in module_names
    )

    return f"""---
doc_type: canon
version: "2.0.0"
last_reviewed: "auto-generated"
status: active
state_semantics: current-state
generator: "scripts/generate/docs/gen_runtime_current_state.py"
manual_edits: forbidden
---

# Runtime Atual — HB Track

> **Gerado automaticamente** a partir do estado real do workspace.
> **Não editar manualmente**. Atualize o sistema real e rode `python3 scripts/generate/docs/gen_runtime_current_state.py --write`.

## 0. Objetivo e limite de autoridade

Este documento registra apenas **fatos materializados no repositório atual**.
Ele não promove target-state, não substitui ADRs e não inventa roadmap.

Fontes executáveis observadas por este gerador:

- `src/`
- `config/`
- `infra/`
- `frontend/`
- `contracts/`
- `tests/`
- `docs/_canon/MODULE_REGISTRY.yaml`

## 1. Snapshot Executivo

| Item | Estado atual | Evidência |
|------|--------------|-----------|
| Backend Django/Ninja | materializado | `config/settings.py`, `config/urls.py`, `manage.py` |
| Routers HTTP montados | `{router_count}` routers | `config/urls.py` |
| Módulos backend canônicos | `{len(module_names)}/{len(module_names)}` materializados | `src/<module>/api.py`, `migrations/`, `tests/` |
| PostgreSQL dev | materializado (`postgres:{postgres_tag}`) | `infra/docker-compose.yml` |
| Redis dev | {"materializado" if redis_service else "ausente"} | `infra/docker-compose.yml` |
| Celery runtime | {"materializado" if has_celery_config else "ausente"} ({tasks_count} `tasks.py`) | `config/celery.py`, `src/*/tasks.py` |
| Channels/WebSocket config | {"materializado" if has_channel_layers else "ausente"} ({consumers_count} `consumers.py`) | `config/settings.py`, `src/*/consumers.py` |
| Endpoint `GET /health` | {"materializado" if health_route else "ausente"} | `config/urls.py` |
| Frontend | {"materializado" if frontend_exists else "ausente"} | `frontend/`, `frontend/package.json`, `frontend/src/` |
| Deploy assets | {"materializado" if dockerfile_root and compose_prod and nginx_conf else "parcial"} | `Dockerfile`, `infra/docker-compose.prod.yml`, `infra/nginx/nginx.conf` |

## 2. Backend e Runtime

| Item | Estado | Evidência |
|------|--------|-----------|
| `DATABASES` em Django settings | {"configurado" if has_databases else "ausente"} | `config/settings.py` |
| `CHANNEL_LAYERS` | {"configurado" if has_channel_layers else "ausente"} | `config/settings.py` |
| Celery app | {"configurado" if has_celery_config else "ausente"} | `config/celery.py` |
| Módulos com `tasks.py` | `{tasks_count}` | `src/*/tasks.py` |
| Módulos com `consumers.py` | `{consumers_count}` | `src/*/consumers.py` |
| Health check HTTP | {"presente" if health_route else "ausente"} | `config/urls.py` |

## 3. Módulos Canônicos

| Módulo | Status no registry | API | Migrations | Tests |
|--------|--------------------|-----|------------|-------|
{module_rows}

## 4. Contratos e Superfícies

| Artefato | Cobertura atual | Evidência |
|----------|-----------------|-----------|
| OpenAPI paths por módulo | `{openapi_paths}/{len(module_names)}` | `contracts/openapi/paths/` |
| JSON Schema por módulo de domínio | `{len(domain_schema_dirs)}/{len(module_names)}` | `contracts/schemas/<module>/` |
| JSON Schema compartilhado | `{len(shared_schema_dirs)}` diretórios | `contracts/schemas/shared/` |
| AsyncAPI channels | `{async_channels}` arquivos | `contracts/asyncapi/channels/` |
| Arazzo workflows | `{workflows}` arquivos | `contracts/workflows/` |
| State model docs | `{state_models}` arquivos | `docs/hbtrack/modulos/*/STATE_MODEL_*.md` |
| UI contract docs | `{ui_contracts}` arquivos | `docs/hbtrack/modulos/*/UI_CONTRACT_*.md` |

## 5. Frontend e Deploy

| Item | Estado | Evidência |
|------|--------|-----------|
| Diretório `frontend/` | {"presente" if frontend_exists else "ausente"} | `frontend/` |
| `frontend/package.json` | {"presente" if frontend_package else "ausente"} | `frontend/package.json` |
| `frontend/src/` | {"presente" if frontend_src else "ausente"} | `frontend/src/` |
| Tipos `schema.d.ts` | `{frontend_schema_types}` arquivo(s) | `frontend/**/schema.d.ts` |
| `Dockerfile` raiz | {"presente" if dockerfile_root else "ausente"} | `Dockerfile` |
| `infra/docker-compose.prod.yml` | {"presente" if compose_prod else "ausente"} | `infra/docker-compose.prod.yml` |
| `infra/nginx/nginx.conf` | {"presente" if nginx_conf else "ausente"} | `infra/nginx/nginx.conf` |
| Rollback script | {"presente" if rollback_script else "ausente"} | `infra/scripts/rollback.sh` |

## 6. Testes e Governança

| Item | Estado | Evidência |
|------|--------|-----------|
| Diretórios `tests/unit` por módulo | `{unit_test_dirs}/{len(module_names)}` | `src/*/tests/unit/` |
| Diretórios `tests/integration` por módulo | `{integration_test_dirs}/{len(module_names)}` | `src/*/tests/integration/` |
| Arquivos em `tests/pipeline_gates/` | `{pipeline_gate_tests}` | `tests/pipeline_gates/` |
| Validador de drift arquitetural | presente | `scripts/audit/check_architecture_docs.py` |
| Validador principal de contratos | presente | `scripts/contracts/validate/validate_contracts.py` |

## 7. Regras de uso

- Este documento é derivado; qualquer edição manual deve ser tratada como drift.
- Divergência entre este arquivo e o workspace atual deve falhar via `gen_runtime_current_state.py --check`.
- ADRs e docs de arquitetura continuam normativos para target-state e decisões; este arquivo cobre somente estado materializado.
"""


def _normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate docs/_canon/RUNTIME_CURRENT_STATE.md from the real repository state.")
    parser.add_argument("--check", action="store_true", help="Validate drift only.")
    parser.add_argument("--write", action="store_true", help="Write the generated file.")
    args = parser.parse_args()

    if yaml is None:
        print("[ERROR] PyYAML não está instalado.", file=sys.stderr)
        return EXIT_ERROR

    if not args.check and not args.write:
        print("[ERROR] Use --check ou --write.", file=sys.stderr)
        return EXIT_ERROR

    try:
        generated = _normalize(generate_runtime_current_state(REPO_ROOT))
    except Exception as exc:
        print(f"[ERROR] Falha ao gerar RUNTIME_CURRENT_STATE.md: {exc}", file=sys.stderr)
        return EXIT_ERROR

    current = _normalize(_read_text(OUTPUT_PATH)) if OUTPUT_PATH.exists() else None

    if args.check:
        if current == generated:
            print("[OK] RUNTIME_CURRENT_STATE.md está sincronizado.")
            return EXIT_OK
        print("[FAIL] RUNTIME_CURRENT_STATE.md está desatualizado. Rode com --write.", file=sys.stderr)
        return EXIT_DRIFT

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(generated, encoding="utf-8")
    print(f"[OK] Arquivo gerado: {OUTPUT_PATH}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
