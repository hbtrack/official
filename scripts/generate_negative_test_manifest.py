#!/usr/bin/env python3
"""
Gera _reports/implementation_flow/negative_test_manifest.json a partir da
execução dos test files de negative enforcement (issue #108).

Cada teste pytest é mapeado para um item em `rules_tested[]`. O verdict do item
é PROTECTED se o teste passou (gate detectou a violação injetada) e UNPROTECTED
caso contrário. O verdict global é PASS se coverage_ratio >= 0.80 e nenhum
UNPROTECTED.

O manifesto é validado contra contracts/schemas/shared/negative_test_manifest.schema.json
antes de ser escrito.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
from xml.etree import ElementTree as ET

import jsonschema

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TESTS = [
    "tests/pipeline_gates/test_openapi_policy_ruleset_gate_negative.py",
    "tests/pipeline_gates/test_asyncapi_validation_gate_negative.py",
    "tests/pipeline_gates/test_agent_governance_negative_enforcement.py",
]
SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "shared" / "negative_test_manifest.schema.json"
OUTPUT_PATH = REPO_ROOT / "_reports" / "implementation_flow" / "negative_test_manifest.json"
PR_URL_PLACEHOLDER = "https://github.com/hbtrack/official/pull/0"
COVERAGE_THRESHOLD = 0.80


# Mapeamento test_name → (rule_id, rule_source, prohibited_behavior).
# rule_source aponta o arquivo SSOT que define a regra.
TEST_RULE_MAP: dict[str, tuple[str, str, str]] = {
    # OpenAPI ruleset
    "test_fail_when_openapi_version_violated": (
        "hbtrack-openapi-version",
        ".spectral.yaml",
        "openapi version diferente de 3.1.x",
    ),
    "test_fail_when_operation_id_missing": (
        "hbtrack-operation-id-required",
        ".spectral.yaml",
        "operação HTTP sem operationId",
    ),
    "test_fail_when_tag_description_missing": (
        "hbtrack-tag-description",
        ".spectral.yaml",
        "tag declarada sem description",
    ),
    "test_fail_when_uri_versioning_present": (
        "hbtrack-no-uri-versioning",
        ".spectral.yaml",
        "versão na URI (ex.: /v1/)",
    ),
    "test_fail_when_info_title_missing": (
        "hbtrack-info-title",
        ".spectral.yaml",
        "info.title ausente",
    ),
    "test_fail_when_info_version_missing": (
        "hbtrack-info-version",
        ".spectral.yaml",
        "info.version ausente",
    ),
    "test_fail_when_servers_missing": (
        "hbtrack-servers-defined",
        ".spectral.yaml",
        "servers ausente ou vazio",
    ),
    "test_fail_when_problem_schema_undeclared": (
        "hbtrack-problem-schema-declared",
        ".spectral.yaml",
        "components.schemas.problem ausente (RFC 7807)",
    ),
    # AsyncAPI
    "test_fail_when_asyncapi_version_field_missing": (
        "asyncapi-version-field-required",
        "asyncapi-cli (validate)",
        "campo top-level 'asyncapi' ausente",
    ),
    "test_fail_when_asyncapi_version_unsupported": (
        "asyncapi-version-supported",
        "asyncapi-cli (validate)",
        "versão AsyncAPI inexistente / não suportada",
    ),
    "test_fail_when_asyncapi_info_title_missing": (
        "asyncapi-info-title-required",
        "asyncapi-cli (validate)",
        "info.title ausente em AsyncAPI",
    ),
    "test_fail_when_asyncapi_info_version_missing": (
        "asyncapi-info-version-required",
        "asyncapi-cli (validate)",
        "info.version ausente em AsyncAPI",
    ),
    "test_fail_when_yaml_is_malformed": (
        "asyncapi-yaml-syntactically-valid",
        "asyncapi-cli (validate)",
        "YAML sintaticamente inválido",
    ),
    "test_fail_when_channels_field_missing": (
        "asyncapi-channels-required",
        "asyncapi-cli (validate)",
        "channels ausente em AsyncAPI 2.x",
    ),
    # Agent governance
    "test_fail_when_required_copilot_agent_missing": (
        "agent-copilot-required-files",
        "tests/pipeline_gates/test_platform_agent_exposure.py",
        "arquivo de agente Copilot esperado ausente",
    ),
    "test_fail_when_agent_frontmatter_name_mismatches": (
        "agent-frontmatter-name-matches-file",
        "tests/pipeline_gates/test_platform_agent_exposure.py",
        "frontmatter.name divergente do arquivo do agente",
    ),
    "test_fail_when_implementer_missing_runtime_task_type": (
        "agent-implementer-runtime-task-type-declared",
        "tests/pipeline_gates/test_platform_agent_exposure.py",
        "hb-implementer sem referência a implementation_execution",
    ),
    "test_fail_when_handtracker_presented_as_runtime_executor": (
        "agent-handtracker-not-runtime-executor",
        "tests/pipeline_gates/test_platform_agent_exposure.py",
        "HandTracker apresentado como executor runtime",
    ),
    "test_fail_when_claude_md_missing_external_tester_role": (
        "bridge-claude-declares-external-tester-role",
        "CLAUDE.md",
        "CLAUDE.md sem declaração de tester externo final",
    ),
    "test_fail_when_codex_missing_no_equivalent_clause": (
        "bridge-codex-declares-no-equivalent-ui",
        ".codex",
        ".codex sem declaração de não-equivalência de UI a Copilot",
    ),
    "test_fail_when_execution_plan_doc_deleted": (
        "bridge-execution-plan-doc-required",
        ".dev/AGENT_PLATFORM_EXPOSURE_EXECUTION_PLAN.md",
        "doc dedicado de exposição por plataforma ausente",
    ),
}


def _run_pytest(junit_xml: pathlib.Path) -> int:
    """Roda pytest sobre os 3 test files, gravando JUnit XML."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *TESTS,
        f"--junitxml={junit_xml}",
        "-q",
        "--no-header",
        "-p",
        "no:cacheprovider",
    ]
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode not in (0, 1):  # 0=all pass, 1=some failed
        sys.stderr.write(f"pytest exit code inesperado: {proc.returncode}\n")
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
    return proc.returncode


def _parse_junit(junit_xml: pathlib.Path) -> list[dict]:
    """Extrai resultados por teste do JUnit XML."""
    results: list[dict] = []
    tree = ET.parse(junit_xml)
    for testcase in tree.iter("testcase"):
        name = testcase.get("name") or ""
        classname = testcase.get("classname") or ""
        failed = any(child.tag in ("failure", "error") for child in testcase)
        skipped = any(child.tag == "skipped" for child in testcase)
        results.append({
            "name": name,
            "classname": classname,
            "passed": not failed and not skipped,
            "failed": failed,
            "skipped": skipped,
        })
    return results


def _build_rules_tested(results: list[dict]) -> list[dict]:
    items: list[dict] = []
    for r in results:
        name = r["name"]
        if name not in TEST_RULE_MAP:
            # Baselines (test_baseline_*) e outros — ignorar
            continue
        rule_id, rule_source, prohibited = TEST_RULE_MAP[name]
        if r["skipped"]:
            verdict = "UNPROTECTED"
            actual = "SKIPPED — toolchain ausente, regra não pôde ser verificada"
        elif r["passed"]:
            verdict = "PROTECTED"
            actual = "FAIL (gate detectou a violação injetada — comportamento esperado)"
        else:
            verdict = "UNPROTECTED"
            actual = "PASS ou erro inesperado (gate NÃO detectou a violação injetada)"
        items.append({
            "rule_id": rule_id,
            "rule_source": rule_source,
            "prohibited_behavior": prohibited,
            "test_command": (
                f"python3 -m pytest {r['classname'].replace('.', '/')}.py::{name}"
            ),
            "expected_result": "FAIL (gate retorna status FAIL ou AssertionError)",
            "actual_result": actual,
            "verdict": verdict,
        })
    return items


def _resolve_pr_url(arg_pr_url: str | None) -> str:
    if arg_pr_url:
        return arg_pr_url
    state_path = REPO_ROOT / "_reports" / "implementation_flow" / "current_state.json"
    if state_path.exists():
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
            url = data.get("pr_url")
            if url and url.startswith("http"):
                return url
        except (json.JSONDecodeError, OSError):
            pass
    return PR_URL_PLACEHOLDER


def _resolve_decision_ids() -> list[str]:
    """Lê decision_ids do current_state.json se disponível; senão lista vazia."""
    state_path = REPO_ROOT / "_reports" / "implementation_flow" / "current_state.json"
    if not state_path.exists():
        return []
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        ids = data.get("decision_ids_affected", [])
        return [s for s in ids if isinstance(s, str) and s]
    except (json.JSONDecodeError, OSError):
        return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr-url", default=None, help="URL do PR remoto (opcional)")
    parser.add_argument(
        "--junit-out",
        default=str(REPO_ROOT / "_reports" / "implementation_flow" / "negative_tests.junit.xml"),
        help="Caminho do JUnit XML intermediário",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="Caminho do manifesto de saída",
    )
    parser.add_argument(
        "--skip-pytest",
        action="store_true",
        help="Não roda pytest; usa --junit-out existente",
    )
    args = parser.parse_args()

    junit_xml = pathlib.Path(args.junit_out)
    output_path = pathlib.Path(args.output)
    junit_xml.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not args.skip_pytest:
        _run_pytest(junit_xml)

    if not junit_xml.exists():
        sys.stderr.write(f"JUnit XML não encontrado em {junit_xml}\n")
        return 2

    results = _parse_junit(junit_xml)
    rules = _build_rules_tested(results)
    if not rules:
        sys.stderr.write(
            "Nenhuma regra mapeada nos testes — atualize TEST_RULE_MAP em "
            f"{__file__} se adicionou testes novos.\n"
        )
        return 2

    protected = sum(1 for r in rules if r["verdict"] == "PROTECTED")
    coverage_ratio = round(protected / len(rules), 4)
    has_unprotected = any(r["verdict"] == "UNPROTECTED" for r in rules)
    if coverage_ratio >= COVERAGE_THRESHOLD and not has_unprotected:
        verdict = "PASS"
    elif coverage_ratio > 0 and has_unprotected:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    manifest = {
        "schema_version": "1.0.0",
        "pr_url": _resolve_pr_url(args.pr_url),
        "decision_ids_tested": _resolve_decision_ids(),
        "rules_tested": rules,
        "coverage_ratio": coverage_ratio,
        "verdict": verdict,
    }

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(manifest, schema)

    output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sys.stdout.write(
        f"manifest: {output_path.relative_to(REPO_ROOT)} | "
        f"verdict={verdict} | coverage_ratio={coverage_ratio} | "
        f"rules={len(rules)} (PROTECTED={protected}, "
        f"UNPROTECTED={len(rules) - protected})\n"
    )
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
