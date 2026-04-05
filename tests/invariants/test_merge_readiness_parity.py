"""Invariant tests: merge-readiness.json structure, schema, and workflow consistency."""
import json
import pathlib
import pytest

ROOT = pathlib.Path(__file__).parent.parent.parent


def _manifest():
    return json.loads((ROOT / "merge-readiness.json").read_text())


def _schema():
    return json.loads(
        (ROOT / "contracts/schemas/shared/merge-readiness.schema.json").read_text()
    )


def test_merge_readiness_schema():
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(_manifest(), _schema())


def test_toolchain_schema():
    tc_path = ROOT / "toolchain.json"
    schema_path = ROOT / "contracts/schemas/shared/toolchain.schema.json"
    assert tc_path.exists(), "toolchain.json not found"
    if not schema_path.exists():
        pytest.skip("toolchain schema not found")
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(
        json.loads(tc_path.read_text()), json.loads(schema_path.read_text())
    )


def test_required_checks_have_local_equivalent():
    for check in _manifest()["checks"]:
        if check["category"] == "required":
            assert "local_equivalent" in check, (
                f"required check {check['context']!r} missing local_equivalent"
            )


def test_conditional_checks_have_condition():
    for check in _manifest()["checks"]:
        if check["category"] == "conditional":
            assert "condition" in check, (
                f"conditional check {check['context']!r} missing condition"
            )
            assert "reason" in check, (
                f"conditional check {check['context']!r} missing reason"
            )


def test_all_required_check_workflows_exist():
    for check in _manifest()["checks"]:
        if check["category"] == "required":
            wf = ROOT / ".github/workflows" / check["workflow"]
            assert wf.exists(), (
                f"workflow {check['workflow']!r} for check {check['context']!r} not found"
            )


def test_category_values_are_valid():
    valid = {"required", "informational", "conditional"}
    for check in _manifest()["checks"]:
        assert check["category"] in valid, (
            f"invalid category {check['category']!r} for {check['context']!r}"
        )


def test_hb_validate_is_registered():
    """hb validate deve existir como subcomando — executor canônico para 'Validate Contract Gates'.

    O job remoto roda validate_contracts.py --profile ci.
    hb validate --profile ci é o wrapper canônico equivalente a hb ci para ci / Tests.
    """
    script = (ROOT / "scripts/hb").read_text()
    assert '"validate"' in script and "cmd_validate" in script, (
        "hb validate não está registrado em scripts/hb — divergência com 'Validate Contract Gates' "
        "(merge-readiness.json: local_equivalent = 'python3 scripts/hb validate --profile ci')"
    )


def test_hb_ci_includes_migrate():
    """hb ci --profile pr deve executar migrate antes de pytest para paridade com ci / Tests.

    O job remoto _reusable-ci.yml faz: install → migrate --noinput → pytest.
    Se hb ci não incluir migrate, PASS local pode divergir do PASS remoto.
    """
    script = (ROOT / "scripts/hb").read_text()
    assert '"manage.py", "migrate", "--noinput"' in script, (
        "hb ci não inclui chamada a 'manage.py migrate --noinput' — divergência com job remoto ci / Tests "
        "(_reusable-ci.yml: 'python manage.py migrate --noinput')"
    )


def test_conditional_checks_have_local_equivalent():
    """Todos os checks condicionais devem ter local_equivalent e local_equivalent_kind.

    Checks condicionais têm local_equivalent mapeado para que o agente possa reproduzir
    o check localmente quando governance_changed=true, sem improvisar comando alternativo.
    """
    for check in _manifest()["checks"]:
        if check["category"] == "conditional":
            assert "local_equivalent" in check, (
                f"conditional check {check['context']!r} missing local_equivalent — "
                "adicionar a merge-readiness.json para paridade com PR_FIX lookup"
            )
            assert "local_equivalent_kind" in check, (
                f"conditional check {check['context']!r} missing local_equivalent_kind"
            )


def test_local_equivalent_python_scripts_exist():
    """Scripts Python referenciados em local_equivalent devem existir no repo.

    Um local_equivalent que aponta para script inexistente produz falso PASS local —
    o agente roda o comando, recebe FileNotFoundError e interpreta como falha de teste,
    não como gap de paridade.
    """
    import re
    for check in _manifest()["checks"]:
        le = check.get("local_equivalent", "")
        # Extrair caminhos python3/python -m pytest ... scripts/...
        for match in re.finditer(r"python3?\s+(scripts/\S+\.py)", le):
            script_path = ROOT / match.group(1)
            assert script_path.exists(), (
                f"check {check['context']!r}: script {match.group(1)!r} "
                "referenciado em local_equivalent não existe"
            )


def test_local_equivalent_test_files_exist():
    """Arquivos de teste referenciados em local_equivalent devem existir no repo.

    Um pytest apontando para arquivo inexistente retorna exit 4 (no tests collected),
    que pode ser interpretado incorretamente. Verificar existência em tempo de lint.
    """
    import re
    for check in _manifest()["checks"]:
        le = check.get("local_equivalent", "")
        # Extrair paths de teste: pytest tests/...py ou pytest tests/...py
        for match in re.finditer(r"pytest\s+(tests/\S+\.py)", le):
            test_path = ROOT / match.group(1)
            assert test_path.exists(), (
                f"check {check['context']!r}: test file {match.group(1)!r} "
                "referenciado em local_equivalent não existe"
            )


def test_ci_validate_contracts_uses_hb_wrapper():
    """ci / Validate Contracts deve usar scripts/hb validate, não o script direto.

    O local_equivalent canônico é 'python3 scripts/hb validate --profile precommit'.
    Usar o script diretamente (validate_contracts.py --profile precommit) diverge do
    wrapper, que pode ter lógica adicional de ambiente e relatório.
    """
    checks = {c["context"]: c for c in _manifest()["checks"]}
    ci_validate = checks.get("ci / Validate Contracts")
    assert ci_validate is not None, "'ci / Validate Contracts' não encontrado em merge-readiness.json"
    le = ci_validate.get("local_equivalent", "")
    assert "scripts/hb validate" in le, (
        f"'ci / Validate Contracts' local_equivalent deve usar 'scripts/hb validate', "
        f"atual: {le!r}"
    )
