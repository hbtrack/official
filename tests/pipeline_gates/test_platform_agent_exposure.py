from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

AGENT_FILES = {
    "hb-contract.agent.md": "HB Contract",
    "hb-implementer.agent.md": "Hb Implementer",
    "hb-adversarial-tester.agent.md": "Hb Adversarial Tester",
    "hb-mesclado.agent.md": "Hb Merger",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _frontmatter(path: Path) -> dict:
    text = _read(path)
    if not text.startswith("---\n"):
        raise AssertionError(f"{path} não começa com frontmatter YAML")
    _, yaml_block, _ = text.split("---\n", 2)
    return yaml.safe_load(yaml_block)


class TestCopilotAgentFiles:
    def test_expected_copilot_agents_exist(self):
        missing = [
            name
            for name in AGENT_FILES
            if not (ROOT / ".github" / "agents" / name).exists()
        ]
        assert not missing, f"Agentes esperados do Copilot ausentes: {missing}"

    def test_copilot_agent_names_match_frontmatter(self):
        mismatches = []
        for filename, expected_name in AGENT_FILES.items():
            path = ROOT / ".github" / "agents" / filename
            frontmatter = _frontmatter(path)
            if frontmatter.get("name") != expected_name:
                mismatches.append(
                    f"{filename}: esperado '{expected_name}', encontrado '{frontmatter.get('name')}'"
                )
        assert not mismatches, "Frontmatter name divergente:\n" + "\n".join(mismatches)

    def test_implementer_references_runtime_task_type(self):
        text = _read(ROOT / ".github" / "agents" / "hb-implementer.agent.md")
        assert "implementation_execution" in text
        assert "Claude" in text

    def test_adversarial_tester_references_runtime_task_type(self):
        text = _read(ROOT / ".github" / "agents" / "hb-adversarial-tester.agent.md")
        assert "adversarial_test_execution" in text
        assert "Claude" in text

    def test_handtracker_is_not_presented_as_runtime_executor(self):
        text = _read(ROOT / ".github" / "agents" / "hb-mesclado.agent.md")
        assert "implementation_execution" not in text
        assert "adversarial_test_execution" not in text
        assert "merges, PRs e CI".lower() in text.lower()


class TestPlatformExposureDocs:
    def test_claude_declares_no_equivalent_agent_ui(self):
        text = _read(ROOT / "CLAUDE.md")
        assert ".github/agents/*.agent.md" in text
        assert "não existe mecanismo equivalente" in text.lower()

    def test_codex_declares_no_equivalent_agent_ui(self):
        text = _read(ROOT / ".codex")
        assert ".github/agents/*.agent.md" in text
        assert "não existe mecanismo equivalente" in text.lower()

    def test_claude_declares_external_tester_role(self):
        text = _read(ROOT / "CLAUDE.md").lower()
        assert "tester externo final" in text
        assert "pacote estruturado de evidências" in text
        assert "não é autoridade final" in text

    def test_codex_declares_no_special_final_review_role(self):
        text = _read(ROOT / ".codex").lower()
        assert "não ganha agente separado" in text
        assert "não por ui dedicada" in text or "não por ui" in text

    def test_agents_inventory_matches_platform_story(self):
        text = _read(ROOT / "AGENTS.md").lower()
        assert ".github/agents/*.agent.md" in text
        assert "claude é a camada recomendada de revisão adversarial externa" in text
        assert "codex mantém paridade operacional documentada" in text

    def test_exposure_map_matches_platform_story(self):
        text = _read(ROOT / ".dev" / "AGENT_PLATFORM_EXPOSURE_MAP.md").lower()
        assert "claude é a camada recomendada de revisão adversarial externa" in text
        assert "codex mantém paridade operacional documentada" in text
        assert "copilot / hb implementer" in text
        assert "claude (tester externo com pacote estruturado)" in text

    def test_execution_plan_exists_and_disambiguates_other_artifacts(self):
        path = ROOT / ".dev" / "AGENT_PLATFORM_EXPOSURE_EXECUTION_PLAN.md"
        assert path.exists(), "Plano dedicado de exposição por plataforma ausente."
        text = _read(path)
        assert ".dev/CODEXPLAN.md" in text
        assert ".dev/AGENT_PLATFORM_EXPOSURE_MAP.md" in text
        assert "Claude" in text
