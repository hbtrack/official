#!/usr/bin/env python3
"""
check_architecture_docs.py — Validador de Drift Arquitetural

Compara claims em documentação arquitetural contra evidências reais no repositório.
Impede que a documentação volte a divergir silenciosamente do sistema.

Exit codes:
  0: PASS — sem divergências detectadas
  1: FAIL — uma ou mais verificações falharam
  2: ERROR — erro ao executar o checker (arquivo ausente, YAML inválido, etc.)

Checks executados:
  1. Unicidade de adr_id entre todos os arquivos ADR
  2. Versão do PostgreSQL consistente entre docs e infra
  3. Nenhum artefato current-state reivindica frontend ativo se `frontend/` não existe
  4. Nenhum artefato current-state reivindica Celery/Channels/WebSocket como runtime
     se não houver código correspondente
  5. Coerência de MODULE_REGISTRY.yaml com src/<module>/, migrations/ e tests/
  6. Ausência de rota /health documentada como operacional se não constar em config/urls.py

Uso:
  python3 scripts/audit/check_architecture_docs.py [--json] [--root <path>]

Exemplos:
  python3 scripts/audit/check_architecture_docs.py
  python3 scripts/audit/check_architecture_docs.py --json
  python3 scripts/audit/check_architecture_docs.py --root /path/to/repo
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None


# ── Constantes ────────────────────────────────────────────────────────────────

CANONICAL_MODULES = {
    "users", "seasons", "teams", "training", "wellness", "medical",
    "competitions", "matches", "scout", "exercises", "analytics",
    "reports", "ai_ingestion", "identity_access", "audit", "notifications",
    "video",
}

# Padrões que NÃO devem aparecer em documentos de current-state como runtime ativo
ASYNC_RUNTIME_PATTERNS = {
    "celery": re.compile(r"\bcelery\b", re.IGNORECASE),
    "channels": re.compile(r"\bdjango.channels\b|\bchannels\b.*websocket|CHANNEL_LAYERS", re.IGNORECASE),
    "websocket_runtime": re.compile(r"\bAsyncWebsocketConsumer\b|CHANNEL_LAYERS\s*=", re.IGNORECASE),
    "tasks_py": re.compile(r"\btasks\.py\b.*runtime|runtime.*\btasks\.py\b", re.IGNORECASE),
}

# Documentos de estado atual (state_semantics: current-state)
CURRENT_STATE_DOCS = {
    "CODE_ARCHITECTURE.md",
    "C4_COMPONENTS_BACKEND.md",
    "RUNTIME_CURRENT_STATE.md",
}
FACTUALITY_DOCS = CURRENT_STATE_DOCS | {
    "ARCHITECTURE.md",
    "C4_CONTAINERS.md",
}

# Versão de PostgreSQL esperada no docker-compose de dev vs target-state
POSTGRES_TARGET_VERSION = "16"

# ── Estruturas de dados ───────────────────────────────────────────────────────

@dataclass
class CheckResult:
    name: str
    status: str  # PASS | FAIL | SKIP | ERROR
    message: str
    details: List[str] = field(default_factory=list)


@dataclass
class ArchDriftReport:
    status: str  # PASS | FAIL | ERROR
    checks: List[CheckResult] = field(default_factory=list)
    total_pass: int = 0
    total_fail: int = 0
    total_skip: int = 0
    total_error: int = 0


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_yaml(path: Path) -> Optional[Any]:
    """Carrega YAML com tratamento de erro; retorna None em caso de falha."""
    if yaml is None:
        raise RuntimeError("pyyaml não está instalado. Execute: pip install pyyaml")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Não foi possível carregar {path}: {exc}") from exc


def _extract_frontmatter(text: str) -> Optional[Dict]:
    """Extrai frontmatter YAML delimitado por --- do início do arquivo."""
    if yaml is None:
        return None
    if not text.startswith("---"):
        return None
    # Encontra o segundo ---
    end = text.find("\n---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(text[3:end])
    except Exception:
        return None


def _read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _iter_doc_lines(root: Path, *, doc_names: set[str]) -> List[tuple[str, int, str, str]]:
    rows: List[tuple[str, int, str, str]] = []
    for doc_name in sorted(doc_names):
        doc_path = root / "docs" / "_canon" / doc_name
        if not doc_path.exists():
            continue
        text = _read_text_safe(doc_path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            rows.append((doc_name, line_no, stripped, stripped.lower()))
    return rows


def _fmt_doc_line(doc_name: str, line_no: int, stripped: str) -> str:
    return f"{doc_name}:{line_no}: '{stripped}'"


NEGATION_TERMS = (
    "ausente",
    "não existe",
    "nao existe",
    "inexiste",
    "target-state",
    "target state",
    "target",
    "aprovado",
    "ainda não",
    "ainda nao",
    "não materializado",
    "nao materializado",
    "não operacional",
    "nao operacional",
    "não implementado",
    "nao implementado",
    "sem ",
    "nenhum",
    "nenhuma",
)


def _contains_any(text: str, values: tuple[str, ...]) -> bool:
    return any(value in text for value in values)


def _doc_evidence_line(doc_name: str, line_no: int, stripped: str, repo_evidence: str) -> str:
    return f"{_fmt_doc_line(doc_name, line_no, stripped)} | repo: {repo_evidence}"


# ── Checks ────────────────────────────────────────────────────────────────────

def check_adr_id_uniqueness(root: Path) -> CheckResult:
    """
    CHECK 1: Unicidade de adr_id entre todos os arquivos ADR.
    Garante que duas ADRs nunca compartilhem o mesmo ID.
    """
    decisions_dir = root / "docs" / "_canon" / "decisions"
    if not decisions_dir.exists():
        return CheckResult(
            name="adr_id_uniqueness",
            status="ERROR",
            message="Diretório docs/_canon/decisions/ não encontrado.",
        )

    adr_files = sorted(decisions_dir.glob("ADR-*.md"))
    if not adr_files:
        return CheckResult(
            name="adr_id_uniqueness",
            status="SKIP",
            message="Nenhum arquivo ADR encontrado.",
        )

    seen: Dict[str, List[str]] = {}  # adr_id → lista de arquivos com esse ID

    for adr_file in adr_files:
        text = _read_text_safe(adr_file)
        fm = _extract_frontmatter(text)

        if fm and isinstance(fm, dict) and "adr_id" in fm:
            adr_id = str(fm["adr_id"]).strip()
        else:
            # Fallback: tentar extrair do nome do arquivo (ADR-NNN-*)
            m = re.match(r"ADR-(\d+)-", adr_file.name)
            if m:
                adr_id = f"ADR-{m.group(1)}"
            else:
                continue

        if adr_id not in seen:
            seen[adr_id] = []
        seen[adr_id].append(adr_file.name)

    duplicates = {k: v for k, v in seen.items() if len(v) > 1}

    if duplicates:
        details = [f"{adr_id}: {', '.join(files)}" for adr_id, files in sorted(duplicates.items())]
        return CheckResult(
            name="adr_id_uniqueness",
            status="FAIL",
            message=f"{len(duplicates)} adr_id(s) duplicado(s) detectado(s).",
            details=details,
        )

    return CheckResult(
        name="adr_id_uniqueness",
        status="PASS",
        message=f"{len(seen)} ADRs verificadas — todos os IDs são únicos.",
    )


def check_postgres_version_consistency(root: Path) -> CheckResult:
    """
    CHECK 2: Consistência da versão do PostgreSQL entre docker-compose e RUNTIME_CURRENT_STATE.md.
    RUNTIME_CURRENT_STATE.md deve documentar a versão real do compose, não o target-state.
    """
    compose_path = root / "infra" / "docker-compose.yml"
    runtime_doc_path = root / "docs" / "_canon" / "RUNTIME_CURRENT_STATE.md"

    if not compose_path.exists():
        return CheckResult(
            name="postgres_version_consistency",
            status="SKIP",
            message="infra/docker-compose.yml não encontrado — check ignorado.",
        )

    compose_text = _read_text_safe(compose_path)
    # Extrai versão do postgres no compose, ex: postgres:12, postgres:16
    pg_match = re.search(r"image:\s*postgres:([\w.]+)", compose_text)
    if not pg_match:
        return CheckResult(
            name="postgres_version_consistency",
            status="SKIP",
            message="Versão do PostgreSQL não detectada no docker-compose.yml.",
        )
    compose_pg_version = pg_match.group(1)

    # RUNTIME_CURRENT_STATE.md deve mencionar a versão real do compose
    if not runtime_doc_path.exists():
        return CheckResult(
            name="postgres_version_consistency",
            status="SKIP",
            message="RUNTIME_CURRENT_STATE.md não encontrado — check parcial.",
        )

    runtime_text = _read_text_safe(runtime_doc_path)

    # A versão real do compose deve estar presente no documento de current-state
    if f"postgres:{compose_pg_version}" not in runtime_text:
        return CheckResult(
            name="postgres_version_consistency",
            status="FAIL",
            message=(
                f"RUNTIME_CURRENT_STATE.md não documenta a versão real do compose "
                f"(postgres:{compose_pg_version}). Verifique se o documento reflete "
                "o estado atual do infra/docker-compose.yml."
            ),
            details=[
                f"Versão no compose: postgres:{compose_pg_version}",
                f"Procurado em: docs/_canon/RUNTIME_CURRENT_STATE.md",
            ],
        )

    # Verificação adicional: ARCHITECTURE.md deve declarar a versão do compose como delta,
    # não como estado atual. Se ARCHITECTURE.md afirma PostgreSQL 16 sem marcar como target,
    # é um sinal de drift. (Soft check — não falha, apenas alerta se compose != target doc sem delta note)
    if compose_pg_version != POSTGRES_TARGET_VERSION:
        arch_path = root / "docs" / "_canon" / "ARCHITECTURE.md"
        arch_text = _read_text_safe(arch_path) if arch_path.exists() else ""
        # ARCHITECTURE.md deve mencionar o delta explicitamente
        if "postgres:12" not in arch_text and f"postgres:{compose_pg_version}" not in arch_text:
            return CheckResult(
                name="postgres_version_consistency",
                status="FAIL",
                message=(
                    f"ARCHITECTURE.md não documenta o delta de versão do PostgreSQL "
                    f"(compose usa {compose_pg_version}, target-state é {POSTGRES_TARGET_VERSION})."
                ),
                details=[
                    f"Versão no compose: postgres:{compose_pg_version}",
                    f"Target-state aprovado: PostgreSQL {POSTGRES_TARGET_VERSION}",
                    "ARCHITECTURE.md deve explicitar esse delta em §5 ou equivalente.",
                ],
            )

    return CheckResult(
        name="postgres_version_consistency",
        status="PASS",
        message=(
            f"PostgreSQL consistente: compose usa postgres:{compose_pg_version}, "
            "RUNTIME_CURRENT_STATE.md documenta corretamente."
        ),
    )


def check_no_frontend_claim_in_current_state(root: Path) -> CheckResult:
    """
    CHECK 3: Claims de frontend não podem divergir do workspace.
    - Se `frontend/` não existe, docs factuais não podem afirmar presença.
    - Se `frontend/` existe, docs factuais não podem afirmar ausência.
    """
    frontend_dir = root / "frontend"
    positive_claims: List[str] = []
    negative_claims: List[str] = []
    explicit_absence_in_current_state = False
    repo_evidence = "frontend/ existe" if frontend_dir.exists() else "frontend/ ausente"

    for doc_name, line_no, stripped, lower in _iter_doc_lines(root, doc_names=FACTUALITY_DOCS):
        if "frontend" not in lower:
            continue
        has_positive_claim = bool(
            ("✓" in stripped and "frontend" in lower)
            or re.search(r"frontend[/`\s]+(?:materializado|existe|implementado|present)", lower)
            or re.search(r"toolchain\s+react/vite", lower)
        )
        has_negative_claim = bool(
            re.search(r"frontend[/`\s]+.*(?:ausente|nao existe|não existe|inexiste|nao materializado|não materializado)", lower)
            or re.search(r"(?:ausente|nao existe|não existe|inexiste|nao materializado|não materializado).*(frontend|spa)", lower)
        )
        if has_positive_claim and not _contains_any(lower, NEGATION_TERMS):
            positive_claims.append(_doc_evidence_line(doc_name, line_no, stripped, repo_evidence))
        if has_negative_claim:
            negative_claims.append(_doc_evidence_line(doc_name, line_no, stripped, repo_evidence))
            if doc_name in CURRENT_STATE_DOCS:
                explicit_absence_in_current_state = True

    if frontend_dir.exists():
        if negative_claims:
            return CheckResult(
                name="no_frontend_claim_in_current_state",
                status="FAIL",
                message=(
                    f"frontend/ existe no workspace, mas {len(negative_claims)} claim(s) "
                    "documental(is) ainda afirmam ausência."
                ),
                details=negative_claims,
            )
        return CheckResult(
            name="no_frontend_claim_in_current_state",
            status="PASS",
            message="frontend/ materializado e nenhum artefato factual afirma sua ausência.",
        )

    if positive_claims:
        return CheckResult(
            name="no_frontend_claim_in_current_state",
            status="FAIL",
            message=f"frontend/ não existe, mas {len(positive_claims)} claim(s) suspeita(s) encontrada(s).",
            details=positive_claims,
        )

    if not explicit_absence_in_current_state:
        return CheckResult(
            name="no_frontend_claim_in_current_state",
            status="FAIL",
            message="frontend/ não existe e nenhum artefato current-state declara sua ausência explicitamente.",
            details=["Adicionar uma linha factual em RUNTIME_CURRENT_STATE.md ou doc current-state equivalente."],
        )

    return CheckResult(
        name="no_frontend_claim_in_current_state",
        status="PASS",
        message="frontend/ ausente e nenhum artefato current-state afirma sua existência.",
    )


def check_no_async_runtime_claims(root: Path) -> CheckResult:
    """
    CHECK 4: Claims sobre Celery/Channels/WebSocket devem refletir o código real.
    """
    # Verificar evidências de Celery no código
    celery_config = root / "config" / "celery.py"
    has_celery_config = celery_config.exists()

    tasks_files = list((root / "src").glob("*/tasks.py")) if (root / "src").exists() else []
    has_tasks = len(tasks_files) > 0

    # Verificar Channel Layers no settings
    settings_path = root / "config" / "settings.py"
    settings_text = _read_text_safe(settings_path) if settings_path.exists() else ""
    has_channels = "CHANNEL_LAYERS" in settings_text

    async_runtime_exists = has_celery_config or has_tasks or has_channels
    positive_claims: List[str] = []
    negative_claims: List[str] = []
    repo_evidence_parts = []
    if has_celery_config:
        repo_evidence_parts.append("config/celery.py existe")
    if has_tasks:
        repo_evidence_parts.append(f"{len(tasks_files)} arquivo(s) src/*/tasks.py")
    if has_channels:
        repo_evidence_parts.append("CHANNEL_LAYERS configurado")
    repo_evidence = ", ".join(repo_evidence_parts) if repo_evidence_parts else "runtime assíncrono ausente"

    for doc_name, line_no, stripped, lower in _iter_doc_lines(root, doc_names=FACTUALITY_DOCS):
        if not any(token in lower for token in ("celery", "channel_layers", "channels", "websocket", "tasks.py")):
            continue

        has_positive_claim = bool(
            ("celery" in lower and "✓" in stripped)
            or re.search(r"celery\s+(?:configurado|executando|rodando|ativo|running|installed|enabled)", lower)
            or re.search(r"channel_layers", lower)
            or re.search(r"websocket", lower)
        )
        has_negative_claim = bool(
            re.search(r"(?:nao existe|não existe|ausente).*(config/celery\.py|tasks\.py|channels|channel_layers|websocket)", lower)
            or re.search(r"(config/celery\.py|tasks\.py|channels|channel_layers|websocket).*(?:nao existe|não existe|ausente)", lower)
            or re.search(r"(celery|channels|websocket).*(?:ainda nao materializado|ainda não materializado|nao materializado|não materializado)", lower)
            or re.search(r"(config/celery\.py|tasks\.py|channel_layers).*(?:ainda nao|ainda não|nao materializado|não materializado)", lower)
            or re.search(r"(celery|channels|websocket).*(?:target-state aprovado|nao arquitetura de codigo atual|não arquitetura de código atual)", lower)
        )
        if has_negative_claim and _contains_any(lower, ("não podem", "nao podem", "não devem", "nao devem")):
            has_negative_claim = False

        if has_positive_claim and not _contains_any(lower, NEGATION_TERMS):
            positive_claims.append(_doc_evidence_line(doc_name, line_no, stripped, repo_evidence))
        if has_negative_claim:
            negative_claims.append(_doc_evidence_line(doc_name, line_no, stripped, repo_evidence))

    if async_runtime_exists:
        if negative_claims:
            return CheckResult(
                name="no_async_runtime_claims",
                status="FAIL",
                message=(
                    "Runtime assíncrono existe no código, mas artefatos factuais ainda "
                    f"carregam {len(negative_claims)} claim(s) de ausência/target-state."
                ),
                details=negative_claims,
            )
        return CheckResult(
            name="no_async_runtime_claims",
            status="PASS",
            message="Runtime assíncrono detectado no código e nenhum artefato factual afirma sua ausência.",
            details=[
                f"config/celery.py exists: {has_celery_config}",
                f"src/*/tasks.py count: {len(tasks_files)}",
                f"CHANNEL_LAYERS in settings: {has_channels}",
            ],
        )

    if positive_claims:
        return CheckResult(
            name="no_async_runtime_claims",
            status="FAIL",
            message=(
                f"Celery/Channels não estão no runtime, mas {len(positive_claims)} "
                "claim(s) suspeita(s) encontrada(s) em artefatos factuais."
            ),
            details=positive_claims,
        )

    return CheckResult(
        name="no_async_runtime_claims",
        status="PASS",
        message=(
            "Celery/Channels/WebSocket ausentes do código e nenhum artefato "
            "current-state afirma sua existência como runtime ativo."
        ),
    )


def check_runtime_topology_claims(root: Path) -> CheckResult:
    """
    CHECK 5: Claims de topologia/runtime deployável devem refletir artefatos reais.
    Cobertura mínima:
      - config/asgi.py
      - src/notifications/middleware.py
      - Dockerfile.frontend
      - infra/docker-compose*.yml
    """
    signals = {
        "asgi_runtime": {
            "present": (root / "config" / "asgi.py").exists(),
            "terms": ("config/asgi.py", "protocoltyperouter", "asgi", "websocket"),
            "positive": (
                r"config/asgi\.py",
                r"protocoltyperouter",
                r"asgi runtime",
            ),
            "negative": (
                r"config/asgi\.py.*(?:ausente|nao existe|não existe|nao materializado|não materializado)",
                r"(?:ausente|nao existe|não existe|nao materializado|não materializado).*(?:config/asgi\.py|asgi)",
                r"(?:asgi|websocket).*(?:target-state aprovado|nao operacional|não operacional)",
            ),
            "repo_evidence": "config/asgi.py existe",
        },
        "websocket_auth_middleware": {
            "present": (root / "src" / "notifications" / "middleware.py").exists(),
            "terms": ("tokenauthmiddleware", "notifications/middleware.py", "middleware websocket"),
            "positive": (
                r"tokenauthmiddleware",
                r"notifications/middleware\.py",
                r"middleware websocket",
            ),
            "negative": (
                r"notifications/middleware\.py.*(?:ausente|nao existe|não existe|nao materializado|não materializado)",
                r"tokenauthmiddleware.*(?:ausente|nao existe|não existe|nao materializado|não materializado)",
                r"(?:middleware websocket|auth middleware).*(?:target-state aprovado|nao operacional|não operacional)",
            ),
            "repo_evidence": "src/notifications/middleware.py existe",
        },
        "frontend_deploy": {
            "present": (root / "Dockerfile.frontend").exists() and any((root / "infra").glob("docker-compose*.yml")),
            "terms": ("dockerfile.frontend", "nginx-spa", "frontend deploy", "frontend spa"),
            "positive": (
                r"dockerfile\.frontend",
                r"nginx-spa",
                r"frontend deploy",
                r"frontend spa",
            ),
            "negative": (
                r"dockerfile\.frontend.*(?:ausente|nao existe|não existe|nao materializado|não materializado)",
                r"(?:ausente|nao existe|não existe|nao materializado|não materializado).*(?:dockerfile\.frontend|frontend deploy|frontend spa)",
                r"(?:frontend deploy|dockerfile\.frontend).*(?:target-state aprovado|nao operacional|não operacional)",
            ),
            "repo_evidence": "Dockerfile.frontend + infra/docker-compose*.yml existem",
        },
    }

    positive_claims: List[str] = []
    negative_claims: List[str] = []
    doc_rows = _iter_doc_lines(root, doc_names=FACTUALITY_DOCS)

    for signal in signals.values():
        for doc_name, line_no, stripped, lower in doc_rows:
            if not any(term in lower for term in signal["terms"]):
                continue
            if any(re.search(pattern, lower) for pattern in signal["negative"]):
                negative_claims.append(
                    _doc_evidence_line(doc_name, line_no, stripped, signal["repo_evidence"])
                )
            elif any(re.search(pattern, lower) for pattern in signal["positive"]) and not _contains_any(lower, NEGATION_TERMS):
                positive_claims.append(
                    _doc_evidence_line(doc_name, line_no, stripped, signal["repo_evidence"])
                )

    if any(signal["present"] for signal in signals.values()) and negative_claims:
        return CheckResult(
            name="runtime_topology_claims",
            status="FAIL",
            message=(
                "Artefatos de topologia/runtime já existem no repo, mas a documentação factual "
                f"ainda contém {len(negative_claims)} claim(s) negativa(s)."
            ),
            details=negative_claims,
        )

    absent_signals = [signal for signal in signals.values() if not signal["present"]]
    if absent_signals and positive_claims:
        return CheckResult(
            name="runtime_topology_claims",
            status="FAIL",
            message=(
                "A documentação factual afirma topologia/runtime deployável sem evidência suficiente "
                "no repositório."
            ),
            details=positive_claims,
        )

    return CheckResult(
        name="runtime_topology_claims",
        status="PASS",
        message="Claims de topologia/runtime estão coerentes com os artefatos reais do repositório.",
    )


def check_module_registry_coherence(root: Path) -> CheckResult:
    """
    CHECK 5: Coerência de MODULE_REGISTRY.yaml com src/<module>/, migrations/ e tests/.
    Módulos marcados como 'implemented' devem ter código, migrations e testes presentes.
    Módulos com código, migrations e testes devem estar marcados como 'implemented' ou superior.
    """
    registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
    src_path = root / "src"

    if not registry_path.exists():
        return CheckResult(
            name="module_registry_coherence",
            status="ERROR",
            message="docs/_canon/MODULE_REGISTRY.yaml não encontrado.",
        )
    if not src_path.exists():
        return CheckResult(
            name="module_registry_coherence",
            status="ERROR",
            message="src/ não encontrado.",
        )

    registry = _load_yaml(registry_path)
    modules_data = registry.get("modules", {})
    status_order = registry.get("policy", {}).get("status_order", [])

    # Status que implicam "código deve existir"
    implemented_statuses = {"implemented", "staging_validated", "released"}
    # Status que implicam "código pode não existir ainda"
    pre_impl_statuses = {"scaffold", "draft_contract", "validated_contract", "implementation_ready"}

    violations: List[str] = []
    details: List[str] = []

    for module, data in modules_data.items():
        status = data.get("status", "scaffold")
        module_src = src_path / module
        has_src = module_src.exists()
        has_api = (
            (module_src / "api.py").exists() or (module_src / "api" / "__init__.py").exists()
        ) if has_src else False
        has_migrations = (module_src / "migrations").exists() if has_src else False
        has_tests = (module_src / "tests").exists() if has_src else False

        if status in implemented_statuses:
            # Deve ter api.py, migrations/ e tests/
            missing = []
            if not has_src:
                missing.append("src/<module>/")
            elif not has_api:
                missing.append("src/<module>/api.py (or api/)")
            if not has_migrations:
                missing.append("src/<module>/migrations/")
            if not has_tests:
                missing.append("src/<module>/tests/")

            if missing:
                violations.append(module)
                details.append(
                    f"FAIL [{module}] status='{status}' mas ausente: {', '.join(missing)}"
                )
        elif status in pre_impl_statuses:
            # Se tem código completo (api + migrations + tests), deveria estar como 'implemented'
            if has_src and has_api and has_migrations and has_tests:
                violations.append(module)
                details.append(
                    f"FAIL [{module}] status='{status}' mas possui "
                    "src/<module>/api.py (or api/) + migrations/ + tests/ — deveria ser 'implemented' ou superior."
                )

    if violations:
        return CheckResult(
            name="module_registry_coherence",
            status="FAIL",
            message=f"{len(violations)} módulo(s) com status inconsistente no MODULE_REGISTRY.yaml.",
            details=details,
        )

    return CheckResult(
        name="module_registry_coherence",
        status="PASS",
        message=(
            f"{len(modules_data)} módulos verificados — "
            "STATUS em MODULE_REGISTRY.yaml coerente com src/<module>/."
        ),
    )


def check_health_endpoint_claim(root: Path) -> CheckResult:
    """
    CHECK 6: Ausência de /health documentada como operacional se não constar em config/urls.py.
    RUNTIME_CURRENT_STATE.md deve declarar /health como ausente se não existe.
    """
    urls_path = root / "config" / "urls.py"
    runtime_doc_path = root / "docs" / "_canon" / "RUNTIME_CURRENT_STATE.md"

    if not urls_path.exists():
        return CheckResult(
            name="health_endpoint_claim",
            status="SKIP",
            message="config/urls.py não encontrado — check ignorado.",
        )

    urls_text = _read_text_safe(urls_path)
    # Verificar se /health existe como rota registrada
    has_health_route = bool(
        re.search(r"""(path|url)\s*\(\s*['"/]health""", urls_text) or
        re.search(r"""['"/]health['"/]""", urls_text)
    )

    if has_health_route:
        return CheckResult(
            name="health_endpoint_claim",
            status="SKIP",
            message="GET /health encontrado em config/urls.py — check não aplicável.",
        )

    # /health não existe: verificar que RUNTIME_CURRENT_STATE.md declara ausência
    if not runtime_doc_path.exists():
        return CheckResult(
            name="health_endpoint_claim",
            status="SKIP",
            message="RUNTIME_CURRENT_STATE.md não encontrado — check parcial.",
        )

    runtime_text = _read_text_safe(runtime_doc_path)

    # Deve existir uma linha mencionando /health como ausente
    health_mentioned_as_absent = False
    for line in runtime_text.splitlines():
        lower = line.lower()
        if "/health" in lower and "ausente" in lower:
            health_mentioned_as_absent = True
            break

    if not health_mentioned_as_absent:
        # Verificação mais ampla: /health aparece mas não está marcado como ausente?
        if "/health" in runtime_text:
            # Checar se aparece sem "ausente"
            for line in runtime_text.splitlines():
                if "/health" in line and "ausente" not in line.lower() and "target" not in line.lower():
                    return CheckResult(
                        name="health_endpoint_claim",
                        status="FAIL",
                        message=(
                            "GET /health não existe em config/urls.py, mas RUNTIME_CURRENT_STATE.md "
                            "não declara claramente sua ausência."
                        ),
                        details=[
                            f"Linha suspeita: '{line.strip()}'",
                            "RUNTIME_CURRENT_STATE.md deve marcar /health como 'ausente'.",
                        ],
                    )
        # Se /health não mencionado em RUNTIME_CURRENT_STATE.md, é gap de documentação (soft fail)
        return CheckResult(
            name="health_endpoint_claim",
            status="FAIL",
            message=(
                "GET /health não existe em config/urls.py e "
                "RUNTIME_CURRENT_STATE.md não documenta sua ausência explicitamente."
            ),
            details=[
                "Adicionar linha em RUNTIME_CURRENT_STATE.md mencionando ausência de /health.",
            ],
        )

    return CheckResult(
        name="health_endpoint_claim",
        status="PASS",
        message="GET /health ausente do código e documentado como ausente em RUNTIME_CURRENT_STATE.md.",
    )


# ── Runner principal ──────────────────────────────────────────────────────────

def run_all_checks(root: Path) -> ArchDriftReport:
    """Executa todos os checks de drift arquitetural."""
    report = ArchDriftReport(status="PASS")

    checks_to_run = [
        check_adr_id_uniqueness,
        check_postgres_version_consistency,
        check_no_frontend_claim_in_current_state,
        check_no_async_runtime_claims,
        check_runtime_topology_claims,
        check_module_registry_coherence,
        check_health_endpoint_claim,
    ]

    for check_fn in checks_to_run:
        try:
            result = check_fn(root)
        except Exception as exc:
            result = CheckResult(
                name=check_fn.__name__.replace("check_", ""),
                status="ERROR",
                message=f"Erro inesperado ao executar check: {exc}",
            )

        report.checks.append(result)

        if result.status == "PASS":
            report.total_pass += 1
        elif result.status == "FAIL":
            report.total_fail += 1
            report.status = "FAIL"
        elif result.status == "SKIP":
            report.total_skip += 1
        elif result.status == "ERROR":
            report.total_error += 1
            report.status = "FAIL"

    return report


def _print_report(report: ArchDriftReport) -> None:
    """Imprime relatório legível para humanos."""
    icons = {"PASS": "✓", "FAIL": "✗", "SKIP": "—", "ERROR": "!"}

    print("\n═══════════════════════════════════════════════════════")
    print("  Architecture Drift Checker — HB Track")
    print("═══════════════════════════════════════════════════════\n")

    for r in report.checks:
        icon = icons.get(r.status, "?")
        print(f"  [{icon}] {r.status:5s}  {r.name}")
        print(f"         {r.message}")
        for d in r.details:
            print(f"           → {d}")
        print()

    print("───────────────────────────────────────────────────────")
    print(
        f"  PASS: {report.total_pass}  "
        f"FAIL: {report.total_fail}  "
        f"SKIP: {report.total_skip}  "
        f"ERROR: {report.total_error}"
    )
    print(f"\n  STATUS FINAL: {report.status}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida drift entre documentação arquitetural e repositório real."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emitir saída em JSON ao invés de texto legível.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Raiz do repositório (padrão: detecta automaticamente).",
    )
    args = parser.parse_args()

    # Detectar raiz do repositório
    if args.root:
        root = Path(args.root).resolve()
    else:
        # Subir até encontrar pyproject.toml ou manage.py
        candidate = Path(__file__).resolve()
        for _ in range(6):
            candidate = candidate.parent
            if (candidate / "manage.py").exists() or (candidate / "pyproject.toml").exists():
                root = candidate
                break
        else:
            root = Path.cwd()

    if not root.exists():
        print(f"ERROR: Diretório raiz não encontrado: {root}", file=sys.stderr)
        return 2

    if yaml is None:
        print("ERROR: pyyaml não está instalado. Execute: pip install pyyaml", file=sys.stderr)
        return 2

    report = run_all_checks(root)

    if args.json:
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
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        _print_report(report)

    return 0 if report.status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
