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
    CHECK 3: Nenhum artefato current-state reivindica frontend ativo se frontend/ não existe.
    """
    frontend_dir = root / "frontend"
    if frontend_dir.exists():
        return CheckResult(
            name="no_frontend_claim_in_current_state",
            status="SKIP",
            message="frontend/ existe no workspace — check não aplicável.",
        )

    # frontend/ não existe: verificar que RUNTIME_CURRENT_STATE.md declara ausência
    runtime_doc_path = root / "docs" / "_canon" / "RUNTIME_CURRENT_STATE.md"
    violations: List[str] = []

    if runtime_doc_path.exists():
        runtime_text = _read_text_safe(runtime_doc_path)
        # Deve declarar ausência do frontend de forma explícita
        # Verificação: "frontend/" aparece na tabela de itens ausentes
        if "ausente" not in runtime_text.lower() and "frontend/" in runtime_text:
            # Verificação mais específica: a linha com frontend/ deve conter "ausente"
            for line in runtime_text.splitlines():
                if "frontend/" in line.lower() and "ausente" not in line.lower():
                    violations.append(f"RUNTIME_CURRENT_STATE.md: linha suspeita — '{line.strip()}'")

    # Verificar outros arquivos current-state que NÃO devem afirmar frontend como presente
    # Exclusões: linhas de cabeçalho (#), linhas de seção, linhas que descrevem ausência
    _NEGATIVE_WORDS = (
        "ausente", "não existe", "inexiste", "target", "aprovado",
        "não possui", "sem ", "nenhum", "nenhuma", "ainda não",
        "não materializado", "absent", "inexistent",
    )

    for doc_name in CURRENT_STATE_DOCS:
        doc_path = root / "docs" / "_canon" / doc_name
        if not doc_path.exists():
            continue
        text = _read_text_safe(doc_path)
        fm = _extract_frontmatter(text)
        if not fm or fm.get("state_semantics") != "current-state":
            continue
        for line in text.splitlines():
            stripped = line.strip()
            # Ignorar cabeçalhos de seção e linhas vazias
            if stripped.startswith("#") or not stripped:
                continue
            lower = stripped.lower()
            # Procurar apenas afirmações positivas de que frontend existe
            # Padrão: célula de tabela com ✓, ou "frontend materializado", ou "frontend/ existe"
            has_positive_claim = (
                ("frontend" in lower and "✓" in stripped) or
                re.search(r"frontend[/\s]+(?:materializado|existe|implementado|present)", lower)
            )
            if has_positive_claim:
                if not any(w in lower for w in _NEGATIVE_WORDS):
                    violations.append(f"{doc_name}: '{stripped}'")

    if violations:
        return CheckResult(
            name="no_frontend_claim_in_current_state",
            status="FAIL",
            message=f"frontend/ não existe, mas {len(violations)} claim(s) suspeita(s) encontrada(s).",
            details=violations,
        )

    return CheckResult(
        name="no_frontend_claim_in_current_state",
        status="PASS",
        message="frontend/ ausente e nenhum artefato current-state afirma sua existência.",
    )


def check_no_async_runtime_claims(root: Path) -> CheckResult:
    """
    CHECK 4: Nenhum artefato current-state reivindica Celery/Channels/WebSocket como runtime
    se não há código correspondente (config/celery.py ou src/*/tasks.py).
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

    if async_runtime_exists:
        return CheckResult(
            name="no_async_runtime_claims",
            status="SKIP",
            message="Runtime assíncrono detectado no código — check não aplicável.",
            details=[
                f"config/celery.py exists: {has_celery_config}",
                f"src/*/tasks.py count: {len(tasks_files)}",
                f"CHANNEL_LAYERS in settings: {has_channels}",
            ],
        )

    # Async runtime não existe: verificar docs current-state
    violations: List[str] = []

    # Palavras que indicam ausência / negação em Português
    _NEG = (
        "ausente", "não existe", "inexiste", "target", "[target",
        "aprovado", "absent", "sem ", "nenhum", "nenhuma",
        "ainda não", "não materializado", "não está", "nao define",
        "nao substitui", "não substitui", "não define",
    )

    for doc_name in CURRENT_STATE_DOCS:
        doc_path = root / "docs" / "_canon" / doc_name
        if not doc_path.exists():
            continue
        text = _read_text_safe(doc_path)
        fm = _extract_frontmatter(text)
        if not fm or fm.get("state_semantics") != "current-state":
            continue

        for line in text.splitlines():
            stripped = line.strip()
            # Ignorar cabeçalhos de seção e linhas vazias
            if stripped.startswith("#") or not stripped:
                continue
            lower = stripped.lower()

            # Procurar apenas afirmações POSITIVAS de que Celery/Channels está em execução:
            # Ex: ✓ em tabela com celery, ou "celery configurado", "channel_layers ativo"
            has_celery_claim = bool(
                ("celery" in lower and "✓" in stripped) or
                re.search(r"celery\s+(?:configurado|executando|rodando|ativo|running|installed|enabled)", lower) or
                re.search(r"CELERY_BROKER_URL\s*=", stripped)
            )
            has_channels_claim = bool(
                "CHANNEL_LAYERS" in stripped and "=" in stripped and
                not any(w in lower for w in _NEG)
            )

            if has_celery_claim or has_channels_claim:
                if not any(w in lower for w in _NEG):
                    violations.append(f"{doc_name}: '{stripped}'")

    if violations:
        return CheckResult(
            name="no_async_runtime_claims",
            status="FAIL",
            message=(
                f"Celery/Channels não estão no runtime, mas {len(violations)} "
                "claim(s) suspeita(s) encontrada(s) em artefatos current-state."
            ),
            details=violations,
        )

    return CheckResult(
        name="no_async_runtime_claims",
        status="PASS",
        message=(
            "Celery/Channels/WebSocket ausentes do código e nenhum artefato "
            "current-state afirma sua existência como runtime ativo."
        ),
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
        has_api = (module_src / "api.py").exists() if has_src else False
        has_migrations = (module_src / "migrations").exists() if has_src else False
        has_tests = (module_src / "tests").exists() if has_src else False

        if status in implemented_statuses:
            # Deve ter api.py, migrations/ e tests/
            missing = []
            if not has_src:
                missing.append("src/<module>/")
            elif not has_api:
                missing.append("src/<module>/api.py")
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
                    "src/<module>/api.py + migrations/ + tests/ — deveria ser 'implemented' ou superior."
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
