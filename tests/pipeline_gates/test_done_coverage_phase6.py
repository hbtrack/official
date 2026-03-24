"""
tests/pipeline_gates/test_done_coverage_phase6.py

FASE 6 — FECHAMENTO DE DONE: FEATURE COVERAGE E RASTREABILIDADE

Testa as mudanças da Fase 6 do AGENT_COMPLIANCE_EXECUTION_PLAN.md:
  - MODULE_REGISTRY.yaml com regra incondicional para status implemented
  - FEATURE_REGISTRY.yaml com cobertura de todos os 17 módulos implemented
  - FEATURE_COVERAGE_GATE implementado em validate_contracts.py
  - FEATURE_COVERAGE_GATE registrado em GATES_REGISTRY.yaml
  - session_start.schema.json sem contagem de gates hardcoded ("44 gates")
  - stage2_exit_code e stage3_exit_code persistidos pelo scripts/hb
"""

import json
import pathlib
import tempfile

import pytest
import yaml

import scripts.contracts.validate.validate_contracts as _vc

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
MODULE_REGISTRY_PATH = REPO_ROOT / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
FEATURE_REGISTRY_PATH = REPO_ROOT / "docs" / "_canon" / "FEATURE_REGISTRY.yaml"
GATES_REGISTRY_PATH = REPO_ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml"
SESSION_SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "shared" / "session_start.schema.json"
VALIDATE_SCRIPT = REPO_ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py"
HB_SCRIPT = REPO_ROOT / "scripts" / "hb"


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _load_yaml(path: pathlib.Path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_json(path: pathlib.Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ──────────────────────────────────────────────────────────────────────────────
# 1. MODULE_REGISTRY.yaml — regra incondicional
# ──────────────────────────────────────────────────────────────────────────────

class TestModuleRegistryUnconditionalRule:
    """Valida que a semântica de 'implemented' é incondicional."""

    def test_implemented_semantics_does_not_contain_conditional_phrase(self):
        """A semântica de 'implemented' não deve conter 'Quando o módulo existir no FEATURE_REGISTRY'."""
        data = _load_yaml(MODULE_REGISTRY_PATH)
        implemented_text = data["policy"]["status_semantics"]["implemented"]
        assert "Quando o módulo existir no FEATURE_REGISTRY" not in implemented_text, (
            "MODULE_REGISTRY.yaml ainda contém a regra CONDICIONAL para 'implemented'. "
            "Deve ser incondicional: todo módulo implemented precisa ter feature no FEATURE_REGISTRY."
        )

    def test_implemented_semantics_mentions_feature_registry(self):
        """A semântica deve referenciar FEATURE_REGISTRY.yaml explicitamente."""
        data = _load_yaml(MODULE_REGISTRY_PATH)
        implemented_text = data["policy"]["status_semantics"]["implemented"]
        assert "FEATURE_REGISTRY" in implemented_text, (
            "MODULE_REGISTRY.yaml não menciona FEATURE_REGISTRY no texto de 'implemented'."
        )

    def test_implemented_semantics_is_unconditional(self):
        """A semântica deve conter 'Todo módulo' (incondicional)."""
        data = _load_yaml(MODULE_REGISTRY_PATH)
        implemented_text = data["policy"]["status_semantics"]["implemented"]
        assert "Todo módulo" in implemented_text, (
            "MODULE_REGISTRY.yaml não usa linguagem incondicional para a regra de feature coverage."
        )


# ──────────────────────────────────────────────────────────────────────────────
# 2. FEATURE_REGISTRY.yaml — cobertura de todos os 17 módulos
# ──────────────────────────────────────────────────────────────────────────────

class TestFeatureRegistryCoverage:
    """Valida que todos os módulos implemented têm ao menos uma feature implemented."""

    @pytest.fixture(scope="class")
    def module_registry(self):
        return _load_yaml(MODULE_REGISTRY_PATH)

    @pytest.fixture(scope="class")
    def feature_registry(self):
        return _load_yaml(FEATURE_REGISTRY_PATH)

    def test_feature_registry_has_features_key(self, feature_registry):
        assert isinstance(feature_registry.get("features"), list), (
            "FEATURE_REGISTRY.yaml não possui chave 'features' como lista."
        )

    def test_all_implemented_modules_have_at_least_one_feature(self, module_registry, feature_registry):
        """Cada módulo com status=implemented deve ter >=1 feature implemented."""
        modules = module_registry.get("modules", {})
        implemented_modules = [
            m for m, entry in modules.items()
            if isinstance(entry, dict) and entry.get("status") == "implemented"
        ]
        features = feature_registry.get("features", [])
        features_by_module = {}
        for ft in features:
            if not isinstance(ft, dict):
                continue
            mod = ft.get("module")
            status = ft.get("status")
            if isinstance(mod, str) and status == "implemented":
                features_by_module.setdefault(mod, []).append(ft.get("id", "?"))

        uncovered = [m for m in implemented_modules if not features_by_module.get(m)]
        assert not uncovered, (
            f"Módulos implemented sem feature implemented no FEATURE_REGISTRY: {uncovered}"
        )

    def test_feature_registry_has_43_or_more_features(self, feature_registry):
        """FEATURE_REGISTRY deve ter ao menos 43 features (FT-001 a FT-043)."""
        features = feature_registry.get("features", [])
        assert len(features) >= 43, (
            f"FEATURE_REGISTRY tem apenas {len(features)} features; esperado >= 43 (FT-001 a FT-043)."
        )

    def test_ft_032_through_ft_043_exist(self, feature_registry):
        """FT-032 a FT-043 (novos módulos) devem estar presentes."""
        features = feature_registry.get("features", [])
        ids = {ft.get("id") for ft in features if isinstance(ft, dict)}
        for i in range(32, 44):
            fid = f"FT-{i:03d}"
            assert fid in ids, f"Feature {fid} ausente no FEATURE_REGISTRY."

    def test_new_features_have_status_implemented(self, feature_registry):
        """FT-032 a FT-043 devem ter status=implemented."""
        features = feature_registry.get("features", [])
        by_id = {ft.get("id"): ft for ft in features if isinstance(ft, dict)}
        for i in range(32, 44):
            fid = f"FT-{i:03d}"
            ft = by_id.get(fid)
            assert ft is not None, f"Feature {fid} ausente."
            assert ft.get("status") == "implemented", (
                f"Feature {fid} não tem status=implemented (tem: {ft.get('status')})."
            )

    def test_new_features_have_required_fields(self, feature_registry):
        """FT-032 a FT-043 devem ter id, name, module, description, endpoints, status, contracts."""
        features = feature_registry.get("features", [])
        by_id = {ft.get("id"): ft for ft in features if isinstance(ft, dict)}
        required_keys = {"id", "name", "module", "status", "endpoints", "contracts"}
        for i in range(32, 44):
            fid = f"FT-{i:03d}"
            ft = by_id.get(fid, {})
            missing = required_keys - set(ft.keys())
            assert not missing, f"Feature {fid} ausente de campos: {missing}."

    def test_new_features_cover_correct_modules(self, feature_registry):
        """FT-032 a FT-043 devem cobrir os 12 módulos sem cobertura anterior."""
        expected_modules = {
            "wellness", "medical", "competitions", "matches", "scout",
            "exercises", "analytics", "reports", "ai_ingestion", "audit",
            "notifications", "video",
        }
        features = feature_registry.get("features", [])
        by_id = {ft.get("id"): ft for ft in features if isinstance(ft, dict)}
        covered = set()
        for i in range(32, 44):
            fid = f"FT-{i:03d}"
            ft = by_id.get(fid)
            if ft and isinstance(ft.get("module"), str):
                covered.add(ft["module"])
        missing_coverage = expected_modules - covered
        assert not missing_coverage, (
            f"Módulos sem feature em FT-032 a FT-043: {missing_coverage}"
        )


# ──────────────────────────────────────────────────────────────────────────────
# 3. session_start.schema.json — sem contagem de gates hardcoded
# ──────────────────────────────────────────────────────────────────────────────

class TestSessionStartSchemaNoHardcodedCount:
    """Valida que session_start.schema.json não contém texto stale com contagem de gates."""

    def test_no_44_gates_string_in_schema(self):
        """Schema não deve conter '44 gates' (stale count)."""
        text = SESSION_SCHEMA_PATH.read_text(encoding="utf-8")
        assert "44 gates" not in text, (
            "session_start.schema.json ainda contém '44 gates' (texto stale). "
            "Remover contagem hardcoded da description de stage3_exit_code."
        )

    def test_stage3_exit_code_description_has_no_gate_count(self):
        """Description de stage3_exit_code não deve mencionar número de gates."""
        import re
        schema = _load_json(SESSION_SCHEMA_PATH)
        props = schema.get("properties", {})
        stage3 = props.get("stage3_exit_code", {})
        description = stage3.get("description", "")
        # Verificar que não há padrão "NN gates" (número seguido de "gates")
        assert not re.search(r"\d+\s+gates", description), (
            f"stage3_exit_code.description contém contagem de gates hardcoded: '{description}'"
        )

    def test_generated_schema_also_no_44_gates(self):
        """O schema gerado em generated/ também não deve conter '44 gates'."""
        generated = REPO_ROOT / "generated" / "contracts" / "schemas" / "shared" / "session_start.schema.json"
        if not generated.exists():
            pytest.skip("Schema gerado não encontrado — ok em CI sem geração.")
        text = generated.read_text(encoding="utf-8")
        assert "44 gates" not in text, (
            "generated/contracts/schemas/shared/session_start.schema.json ainda contém '44 gates'."
        )


# ──────────────────────────────────────────────────────────────────────────────
# 4. FEATURE_COVERAGE_GATE — existência e registro
# ──────────────────────────────────────────────────────────────────────────────

class TestFeatureCoverageGateExistence:
    """Valida que FEATURE_COVERAGE_GATE existe no código e no registry."""

    def test_gate_function_exists_in_validate_contracts(self):
        """Função _g_feature_coverage deve existir em validate_contracts.py."""
        text = VALIDATE_SCRIPT.read_text(encoding="utf-8")
        assert "_g_feature_coverage" in text, (
            "Função _g_feature_coverage não encontrada em validate_contracts.py."
        )

    def test_gate_id_in_validate_contracts(self):
        """Gate FEATURE_COVERAGE_GATE deve estar no gate_plan de run_pipeline."""
        text = VALIDATE_SCRIPT.read_text(encoding="utf-8")
        assert '"FEATURE_COVERAGE_GATE"' in text, (
            "FEATURE_COVERAGE_GATE não está no gate_plan de validate_contracts.py."
        )

    def test_blocked_feature_coverage_missing_constant_exists(self):
        """Constante BLOCKED_FEATURE_COVERAGE_MISSING deve existir."""
        text = VALIDATE_SCRIPT.read_text(encoding="utf-8")
        assert "BLOCKED_FEATURE_COVERAGE_MISSING" in text, (
            "Constante BLOCKED_FEATURE_COVERAGE_MISSING ausente em validate_contracts.py."
        )

    def test_gate_registered_in_gates_registry(self):
        """FEATURE_COVERAGE_GATE deve estar registrado em GATES_REGISTRY.yaml."""
        data = _load_yaml(GATES_REGISTRY_PATH)
        gate_ids = {g.get("gate_id") for g in data.get("gates", []) if isinstance(g, dict)}
        assert "FEATURE_COVERAGE_GATE" in gate_ids, (
            "FEATURE_COVERAGE_GATE ausente em docs/_canon/gates/GATES_REGISTRY.yaml."
        )

    def test_gate_in_registry_is_blocking(self):
        """FEATURE_COVERAGE_GATE deve ser blocking=true no GATES_REGISTRY."""
        data = _load_yaml(GATES_REGISTRY_PATH)
        for gate in data.get("gates", []):
            if gate.get("gate_id") == "FEATURE_COVERAGE_GATE":
                assert gate.get("blocking") is True, (
                    "FEATURE_COVERAGE_GATE deve ser blocking=true."
                )
                return
        pytest.fail("FEATURE_COVERAGE_GATE não encontrado no GATES_REGISTRY.")

    def test_gate_in_registry_has_blocking_code(self):
        """FEATURE_COVERAGE_GATE deve ter BLOCKED_FEATURE_COVERAGE_MISSING nos blocking_codes."""
        data = _load_yaml(GATES_REGISTRY_PATH)
        for gate in data.get("gates", []):
            if gate.get("gate_id") == "FEATURE_COVERAGE_GATE":
                codes = gate.get("blocking_codes", [])
                assert "BLOCKED_FEATURE_COVERAGE_MISSING" in codes, (
                    "FEATURE_COVERAGE_GATE não lista BLOCKED_FEATURE_COVERAGE_MISSING."
                )
                return
        pytest.fail("FEATURE_COVERAGE_GATE não encontrado no GATES_REGISTRY.")


# ──────────────────────────────────────────────────────────────────────────────
# 5. FEATURE_COVERAGE_GATE — testes funcionais com fixture temporária
# ──────────────────────────────────────────────────────────────────────────────

class TestFeatureCoverageGateFunctional:
    """Testa o comportamento do FEATURE_COVERAGE_GATE com dados sintéticos."""

    @pytest.fixture(scope="class")
    def validate_module(self):
        return _vc

    def _make_module_registry(self, tmp: pathlib.Path, modules: dict) -> None:
        """Cria um MODULE_REGISTRY.yaml mínimo em tmp."""
        (tmp / "docs" / "_canon").mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.2.0",
            "policy": {"status_semantics": {"implemented": "Incondicional."}},
            "modules": modules,
        }
        with open(tmp / "docs" / "_canon" / "MODULE_REGISTRY.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data, f)

    def _make_feature_registry(self, tmp: pathlib.Path, features: list) -> None:
        """Cria um FEATURE_REGISTRY.yaml mínimo em tmp."""
        (tmp / "docs" / "_canon").mkdir(parents=True, exist_ok=True)
        data = {"version": "1.0.0", "features": features}
        with open(tmp / "docs" / "_canon" / "FEATURE_REGISTRY.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data, f)

    def test_pass_when_all_implemented_modules_have_feature(self, validate_module):
        """Gate deve retornar PASS quando todos os módulos implemented têm feature."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            self._make_module_registry(tmp, {
                "training": {"status": "implemented"},
                "users": {"status": "implemented"},
            })
            self._make_feature_registry(tmp, [
                {"id": "FT-001", "name": "T1", "module": "training", "status": "implemented"},
                {"id": "FT-002", "name": "U1", "module": "users", "status": "implemented"},
            ])
            result = validate_module._g_feature_coverage(tmp)
            assert result["status"] == "PASS", (
                f"Gate deveria ser PASS. Violations: {result.get('violations')}"
            )

    def test_fail_when_implemented_module_has_no_features(self, validate_module):
        """Gate deve retornar FAIL quando módulo implemented não tem feature."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            self._make_module_registry(tmp, {
                "training": {"status": "implemented"},
                "wellness": {"status": "implemented"},  # sem feature
            })
            self._make_feature_registry(tmp, [
                {"id": "FT-001", "name": "T1", "module": "training", "status": "implemented"},
                # wellness tem feature mas em status "planned", não "implemented"
                {"id": "FT-100", "name": "W1", "module": "wellness", "status": "planned"},
            ])
            result = validate_module._g_feature_coverage(tmp)
            assert result["status"] == "FAIL", (
                "Gate deveria ser FAIL para módulo implemented sem feature implemented."
            )
            assert result.get("blocking") is True
            codes = [v.get("blocking_code") for v in result.get("violations", [])]
            assert "BLOCKED_FEATURE_COVERAGE_MISSING" in codes

    def test_skip_when_module_registry_absent(self, validate_module):
        """Gate deve ser SKIP_NOT_APPLICABLE quando MODULE_REGISTRY ausente."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            self._make_feature_registry(tmp, [])
            result = validate_module._g_feature_coverage(tmp)
            assert result["status"] == "SKIP_NOT_APPLICABLE"

    def test_skip_when_feature_registry_absent(self, validate_module):
        """Gate deve ser SKIP_NOT_APPLICABLE quando FEATURE_REGISTRY ausente."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            self._make_module_registry(tmp, {"training": {"status": "implemented"}})
            result = validate_module._g_feature_coverage(tmp)
            assert result["status"] == "SKIP_NOT_APPLICABLE"

    def test_pass_when_no_implemented_modules(self, validate_module):
        """Gate deve retornar PASS quando não há módulos implemented."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            self._make_module_registry(tmp, {
                "training": {"status": "draft_contract"},
            })
            self._make_feature_registry(tmp, [])
            result = validate_module._g_feature_coverage(tmp)
            assert result["status"] == "PASS"

    def test_pass_for_real_repo(self, validate_module):
        """Gate deve PASS no repositório real (todos os 17 módulos têm feature)."""
        result = validate_module._g_feature_coverage(REPO_ROOT)
        assert result["status"] == "PASS", (
            f"FEATURE_COVERAGE_GATE falhou no repo real. Violations: {result.get('violations')}"
        )


# ──────────────────────────────────────────────────────────────────────────────
# 6. stage2_exit_code e stage3_exit_code — persistência no scripts/hb
# ──────────────────────────────────────────────────────────────────────────────

class TestExitCodePersistence:
    """Valida que scripts/hb persiste os exit codes de fase corretamente."""

    def test_cmd_artifact_persists_stage2_exit_code(self):
        """cmd_artifact deve atribuir stage2_exit_code à sessão."""
        text = HB_SCRIPT.read_text(encoding="utf-8")
        assert 'self.session["stage2_exit_code"] = result.returncode' in text, (
            "scripts/hb não persiste stage2_exit_code em cmd_artifact."
        )

    def test_cmd_stage3_persists_stage3_exit_code(self):
        """cmd_stage3 deve atribuir stage3_exit_code à sessão."""
        text = HB_SCRIPT.read_text(encoding="utf-8")
        assert 'self.session["stage3_exit_code"] = result.returncode' in text, (
            "scripts/hb não persiste stage3_exit_code em cmd_stage3."
        )

    def test_session_schema_has_stage2_exit_code_property(self):
        """session_start.schema.json deve ter propriedade stage2_exit_code."""
        schema = _load_json(SESSION_SCHEMA_PATH)
        props = schema.get("properties", {})
        assert "stage2_exit_code" in props, (
            "session_start.schema.json não define propriedade stage2_exit_code."
        )

    def test_session_schema_has_stage3_exit_code_property(self):
        """session_start.schema.json deve ter propriedade stage3_exit_code."""
        schema = _load_json(SESSION_SCHEMA_PATH)
        props = schema.get("properties", {})
        assert "stage3_exit_code" in props, (
            "session_start.schema.json não define propriedade stage3_exit_code."
        )
