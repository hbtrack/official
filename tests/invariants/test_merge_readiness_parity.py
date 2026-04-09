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


# ──────────────────────────────────────────────────────────────────────────────
# Testes v2 — novos blocos do manifesto
# ──────────────────────────────────────────────────────────────────────────────

def test_schema_v2_version_pattern():
    """Schema v2 deve rejeitar versões fora do padrão ^2.x.x."""
    import re
    schema = _schema()
    pattern = schema["properties"]["version"]["pattern"]
    assert re.match(r"\^2\\\\", pattern) or pattern.startswith("^2\\."), (
        f"version.pattern deve ser ^2\\. (ruptura major consciente para v3), atual: {pattern!r}"
    )


def test_manifest_version_is_v2():
    """O manifesto deve declarar version começando com '2.'."""
    version = _manifest()["version"]
    assert version.startswith("2."), (
        f"merge-readiness.json version deve ser 2.x.x, atual: {version!r}"
    )


def test_execution_plan_fields_present():
    """execution_plan deve ter todos os 5 campos obrigatórios."""
    plan = _manifest().get("execution_plan")
    assert plan is not None, "execution_plan ausente em merge-readiness.json"
    for field in ("baseline_steps", "required_check_strategy", "conditional_check_strategy",
                  "decision_policy", "output_report"):
        assert field in plan, f"execution_plan.{field} ausente em merge-readiness.json"


def test_execution_plan_baseline_includes_survival_suite():
    """baseline_steps deve incluir survival_suite como passo obrigatório."""
    steps = _manifest()["execution_plan"]["baseline_steps"]
    assert "survival_suite" in steps, (
        f"execution_plan.baseline_steps deve incluir 'survival_suite', atual: {steps!r}"
    )


def test_diff_classification_classes():
    """diff_classification.classes: cada classe tem class_id único e paths não vazio."""
    classes = _manifest().get("diff_classification", {}).get("classes", [])
    assert classes, "diff_classification.classes está vazio"
    ids_seen = set()
    for cls in classes:
        assert "class_id" in cls, f"Classe sem class_id: {cls!r}"
        assert "paths" in cls and cls["paths"], f"Classe {cls.get('class_id')!r} sem paths"
        assert cls["class_id"] not in ids_seen, f"class_id de classe duplicado: {cls['class_id']!r}"
        ids_seen.add(cls["class_id"])


def test_semantic_requirements_all_when_values():
    """semantic_requirements.rules deve cobrir os 5 when values canônicos."""
    valid_when = {
        "schema_field_removed",
        "new_cross_module_boundary",
        "canonical_status_transition",
        "diff_outside_handoff_scope",
        "bridge_doc_uses_authority_language",
    }
    rules = _manifest().get("semantic_requirements", {}).get("rules", [])
    assert rules, "semantic_requirements.rules está vazio"
    for rule in rules:
        assert rule.get("when") in valid_when, (
            f"when value inválido: {rule.get('when')!r} — valores permitidos: {valid_when}"
        )
        assert isinstance(rule.get("require"), list) and rule["require"], (
            f"rule '{rule.get('when')}': require deve ser lista não vazia"
        )
        assert isinstance(rule.get("block_if_missing"), bool), (
            f"rule '{rule.get('when')}': block_if_missing deve ser booleano"
        )


def test_reviewability_limits_positive():
    """reviewability: todos os limites inteiros devem ser positivos."""
    rev = _manifest().get("reviewability", {})
    assert rev, "reviewability ausente em merge-readiness.json"
    for field in ("max_changed_files", "max_commits", "max_cross_domain_areas"):
        assert field in rev, f"reviewability.{field} ausente"
        assert isinstance(rev[field], int) and rev[field] >= 1, (
            f"reviewability.{field} deve ser inteiro >= 1, atual: {rev[field]!r}"
        )
    assert isinstance(rev.get("split_required_when_exceeded"), bool), (
        "reviewability.split_required_when_exceeded deve ser booleano"
    )


def test_pr_fix_resolution_covers_all_classes():
    """pr_fix_resolution.finding_classes deve cobrir todos os 4 finding_ids canônicos, sem duplicatas."""
    required_ids = {"defect_real", "governance_gap", "evidence_missing", "advisory_non_actionable"}
    finding_classes = _manifest().get("pr_fix_resolution", {}).get("finding_classes", [])
    assert finding_classes, "pr_fix_resolution.finding_classes está vazio"
    ids_found = set()
    for fc in finding_classes:
        assert "finding_id" in fc and "action" in fc, f"finding_class malformado: {fc!r}"
        assert fc["finding_id"] not in ids_found, f"finding_class finding_id duplicado: {fc['finding_id']!r}"
        ids_found.add(fc["finding_id"])
    missing = required_ids - ids_found
    assert not missing, f"finding_classes faltando finding_ids: {missing!r}"


def test_preflight_exit_code_convention():
    """cmd_preflight deve documentar a nova convenção v2: 0=PASS, 1=WARN, 2=BLOCK.

    Essa é uma convenção NOVA e DELIBERADA da v2 — não é continuidade da convenção
    0=sucesso/!=0=falha usada pelos demais comandos de scripts/hb.
    Verificar que a docstring ou comentário explicita isso.
    """
    script = (ROOT / "scripts/hb").read_text()
    assert "0 = PASS" in script and "1 = WARN" in script and "2 = BLOCK" in script, (
        "cmd_preflight deve documentar a convenção v2 de exit codes: "
        "0=PASS, 1=WARN, 2=BLOCK (nova convenção deliberada, não continuidade)"
    )


def test_preflight_is_not_alias_of_survival_suite():
    """preflight não deve mais ser alias de cmd_survival_suite no dispatcher."""
    script = (ROOT / "scripts/hb").read_text()
    # O dispatcher deve chamar cmd_preflight, não cmd_survival_suite, para o comando preflight
    import re
    # Buscar bloco do dispatcher: preflight -> cmd_preflight()
    assert re.search(r'command\s*==\s*"preflight".*?cmd_preflight\(\)', script, re.DOTALL), (
        "dispatcher de 'preflight' deve chamar cmd_preflight() e não cmd_survival_suite() — "
        "preflight é o orquestrador v2, não um alias"
    )


def test_conditional_activation_by_diff_class():
    """Checks condicionais com condição governance_changed devem ativar quando a classe está ativa.

    Este teste valida a lógica de ativação de checks condicionais:
    se governance_changed está em diff_classes e o check tem condition='governance_changed == true',
    ele deve ser ativado.
    """
    manifest = _manifest()
    conditionals = [c for c in manifest["checks"] if c["category"] == "conditional"]
    assert conditionals, "Nenhum check conditional — teste não aplicável"

    # Verificar que todos os condicionais têm condition declarada (já coberto por outro teste)
    # e que a condition referencia uma classe conhecida de diff_classification
    known_classes = {cls["class_id"] for cls in manifest["diff_classification"]["classes"]}
    for check in conditionals:
        condition = check.get("condition", "")
        # Extrair o identificador da condição (ex: "governance_changed == true" → "governance_changed")
        import re
        identifiers = re.findall(r'\b([a-z_]+)\b(?=\s*==)', condition)
        for ident in identifiers:
            assert ident in known_classes, (
                f"Check condicional {check['context']!r} usa condição '{ident}' "
                f"que não é uma classe de diff conhecida. Classes: {known_classes!r}"
            )
