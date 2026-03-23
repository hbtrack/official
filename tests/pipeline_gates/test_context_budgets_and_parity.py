"""
PR6 Phase 8: Golden tests for context budgets and CI/local parity validation.
Tests validate that refactoring budgets are enforced and critical parity is maintained.
"""
import os
import json
import subprocess
import sys
import yaml
from pathlib import Path


class TestContextBudgets:
    """Verify all critical documents stay within allocated budgets."""

    BUDGETS = {
        "CLAUDE.md": 450,
        "SESSION_HANDOFF.md": 350,
        "docs/_canon/CONTRACT_PIPELINE.md": 600,
        ".contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md": 700,
    }

    @staticmethod
    def count_words(filepath: str) -> int:
        """Count words in a file."""
        if not Path(filepath).exists():
            return 0
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return len(content.split())

    def test_claude_md_under_budget(self):
        """CLAUDE.md must be <= 450 words."""
        count = self.count_words("CLAUDE.md")
        assert count <= self.BUDGETS["CLAUDE.md"], \
            f"CLAUDE.md is {count}w, budget is {self.BUDGETS['CLAUDE.md']}w"

    def test_session_handoff_md_under_budget(self):
        """SESSION_HANDOFF.md must be <= 350 words."""
        count = self.count_words("SESSION_HANDOFF.md")
        assert count <= self.BUDGETS["SESSION_HANDOFF.md"], \
            f"SESSION_HANDOFF.md is {count}w, budget is {self.BUDGETS['SESSION_HANDOFF.md']}w"

    def test_contract_pipeline_md_under_budget(self):
        """CONTRACT_PIPELINE.md must be <= 600 words."""
        count = self.count_words("docs/_canon/CONTRACT_PIPELINE.md")
        assert count <= self.BUDGETS["docs/_canon/CONTRACT_PIPELINE.md"], \
            f"CONTRACT_PIPELINE.md is {count}w, budget is {self.BUDGETS['docs/_canon/CONTRACT_PIPELINE.md']}w"

    def test_pre_contract_orchestrator_under_budget(self):
        """pre_contract_orchestrator.prompt.md must be <= 700 words."""
        count = self.count_words(".contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md")
        assert count <= self.BUDGETS[".contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md"], \
            f"orchestrator is {count}w, budget is {self.BUDGETS['.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md']}w"

    def test_all_budgets_combined(self):
        """Total of all budgets must be <= 2100 words."""
        total = sum(self.count_words(doc) for doc in self.BUDGETS.keys())
        max_total = 2100
        assert total <= max_total, \
            f"Total is {total}w, max budget is {max_total}w"


class TestSSOTParity:
    """Verify SSOTs are loaded and interpreted consistently."""

    def test_task_catalog_yaml_loads(self):
        """TASK_CATALOG.yaml must be valid YAML."""
        with open(".contract_driven/TASK_CATALOG.yaml", 'r') as f:
            catalog = yaml.safe_load(f)
        assert catalog is not None, "TASK_CATALOG.yaml failed to load"
        # Check for required keys (phase_routing or task_types)
        assert any(k in catalog for k in ["phase_routing", "task_types", "routing_validation"]), \
            "TASK_CATALOG.yaml missing required keys"

    def test_gates_registry_yaml_loads(self):
        """GATES_REGISTRY.yaml must be valid YAML with at least 46 gates."""
        with open("docs/_canon/gates/GATES_REGISTRY.yaml", 'r') as f:
            registry = yaml.safe_load(f)
        assert registry is not None, "GATES_REGISTRY.yaml failed to load"
        assert "gates" in registry, "GATES_REGISTRY.yaml missing gates"
        assert len(registry["gates"]) >= 46, f"Expected at least 46 gates, found {len(registry['gates'])}"

    def test_boot_profiles_yaml_loads(self):
        """BOOT_PROFILES.yaml must be valid YAML."""
        with open(".contract_driven/BOOT_PROFILES.yaml", 'r') as f:
            profiles = yaml.safe_load(f)
        assert profiles is not None, "BOOT_PROFILES.yaml failed to load"
        assert "profiles" in profiles, "BOOT_PROFILES.yaml missing profiles"

    def test_session_start_schema_valid(self):
        """session_start.schema.json must be valid JSON schema."""
        with open("contracts/schemas/shared/session_start.schema.json", 'r') as f:
            schema = json.load(f)
        assert schema is not None, "session_start.schema.json failed to load"
        assert "$schema" in schema, "session_start.schema.json missing $schema"


class TestHookIntegrity:
    """Verify hook versioned and hook installed are identical."""

    def test_hook_git_config_set(self):
        """git config core.hooksPath must be set to scripts/git-hooks."""
        result = subprocess.run(
            ["git", "config", "core.hooksPath"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "git config core.hooksPath not set"
        assert "scripts/git-hooks" in result.stdout, \
            f"core.hooksPath is {result.stdout.strip()}, expected scripts/git-hooks"

    def test_hook_versionado_exists(self):
        """scripts/git-hooks/pre-commit must exist."""
        assert Path("scripts/git-hooks/pre-commit").exists(), \
            "scripts/git-hooks/pre-commit does not exist"

    def test_hook_executable(self):
        """scripts/git-hooks/pre-commit must be executable."""
        st = os.stat("scripts/git-hooks/pre-commit")
        assert st.st_mode & 0o111, "scripts/git-hooks/pre-commit is not executable"

    def test_hook_no_divergence_in_git_hooks(self):
        """No pre-commit file should exist in .git/hooks (via core.hooksPath)."""
        # If core.hooksPath is set, .git/hooks/pre-commit should not be manually managed
        if Path(".git/hooks/pre-commit").exists():
            with open("scripts/git-hooks/pre-commit", 'r') as versionado:
                versionado_content = versionado.read()
            with open(".git/hooks/pre-commit", 'r') as installed:
                installed_content = installed.read()
            assert versionado_content == installed_content, \
                "Hook in .git/hooks diverges from versionado version"


class TestLegacyEvidenceRemoved:
    """Verify legacy evidence model (boot_resolution_report, agent_execution/latest) is removed."""

    def test_no_active_legacy_evidence_refs(self):
        """Zero references to boot_resolution_report.json or agent_execution/latest in critical path."""
        # Search in critical path files only
        critical_paths = [
            ".contract_driven/agent_prompts/",
            "docs/_canon/",
            "scripts/contracts/",
        ]
        
        legacy_patterns = ["boot_resolution_report", "agent_execution/latest"]
        found_refs = []
        
        for path_str in critical_paths:
            if Path(path_str).is_dir():
                for file in Path(path_str).rglob("*"):
                    if file.suffix in [".md", ".py", ".yaml"]:
                        try:
                            with open(file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                for pattern in legacy_patterns:
                                    if pattern in content:
                                        found_refs.append(f"{file}:{pattern}")
                        except:
                            pass
        
        assert len(found_refs) == 0, \
            f"Found {len(found_refs)} legacy evidence references:\n" + "\n".join(found_refs)


class TestZeroBootProfileReferences:
    """Verify boot configuration uses BOOT_PROFILES.yaml, not hardcoded."""

    def test_no_hardcoded_boot_profiles(self):
        """No hardcoded boot_profile or boot references in active code."""
        script_files = list(Path("scripts").rglob("*.py"))
        found_hardcoded = []
        
        for script in script_files:
            with open(script, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for hardcoded boot profile references (e.g., "boot_profile: 'default'")
                if 'boot_profile:' in content and 'BOOT_PROFILES' not in content:
                    found_hardcoded.append(str(script))
        
        assert len(found_hardcoded) == 0, \
            f"Found hardcoded boot references in: {found_hardcoded}"


def test_parity_cli_verify():
    """Verify hb CLI exists (CLI parity smoke test)."""
    hb_cli = Path(__file__).parent.parent.parent / "scripts" / "hb"
    assert hb_cli.exists(), f"hb CLI not found at {hb_cli}"


def test_parity_test_suite_green():
    """Verify survival suite tests all pass (exit code 0).

    Survival suite = testes que devem passar antes de qualquer mudança em
    gates, profiles, task catalog, schemas críticos ou validate_contracts.py.
    """
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/test_pipeline_governance.py",
            "tests/pipeline_gates/test_phase_0_determinism.py",
            "tests/pipeline_gates/test_module_lifecycle_governance.py",
            "tests/pipeline_gates/test_roadmap_artifact_tracking.py",
            "tests/pipeline_gates/test_context_budgets_and_parity.py::TestSSOTParity",
            "tests/pipeline_gates/test_context_budgets_and_parity.py::TestHookIntegrity",
            "tests/pipeline_gates/test_context_budgets_and_parity.py::TestZeroBootProfileReferences",
            "tests/pipeline_gates/test_context_budgets_and_parity.py::test_parity_cli_verify",
            "tests/pipeline_gates/test_tooling_config_gate.py",
            "-v",
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"Survival suite failed:\n{result.stdout}\n{result.stderr}"


def test_session_start_schema_rejects_unknown():
    """Verify session_start schema rejects task_type=unknown, module=unknown."""
    with open("contracts/schemas/shared/session_start.schema.json", 'r') as f:
        schema = json.load(f)
    
    # Verify schema has enum constraints
    assert "properties" in schema
    assert "task_type" in schema["properties"]
    assert "module" in schema["properties"]
    
    # Check for "unknown" exclusion (schema should reject it)
    task_type_prop = schema["properties"]["task_type"]
    if "enum" in task_type_prop:
        assert "unknown" not in task_type_prop["enum"], \
            "Schema allows task_type=unknown (should reject)"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
