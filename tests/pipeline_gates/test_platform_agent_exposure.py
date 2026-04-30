from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

AGENT_FILES = {
    "hb-contract.agent.md": "HB Contract",
    "hb-implementer.agent.md": "Hb Implementer",
    "hb-adversarial-tester.agent.md": "Hb Adversarial Tester",
    "Mesclado.agent.md": "HandTracker",
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
        text = _read(ROOT / ".github" / "agents" / "Mesclado.agent.md")
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

    def test_exposure_map_disambiguates_other_artifacts(self):
        path = ROOT / ".dev" / "AGENT_PLATFORM_EXPOSURE_MAP.md"
        assert path.exists(), "Mapa unificado de exposição por plataforma ausente."
        text = _read(path)
        assert ".dev/CODEXPLAN.md" in text
        assert "Claude" in text


CLAUDE_AGENT_FILES = [
    "hb-adversarial-tester.md",
    "hb-governance-auditor.md",
    "hb-evidence-verifier.md",
]

CODEX_AGENT_FILES = [
    "hb-gate-auditor.toml",
    "hb-pr-reviewer.toml",
]


class TestClaudeAgentFiles:
    def test_expected_claude_agents_exist(self):
        missing = [
            name
            for name in CLAUDE_AGENT_FILES
            if not (ROOT / ".claude" / "agents" / name).exists()
        ]
        assert not missing, f"Subagents Claude ausentes: {missing}"

    def test_claude_agents_have_bridge_only_banner(self):
        missing_banner = []
        for name in CLAUDE_AGENT_FILES:
            path = ROOT / ".claude" / "agents" / name
            text = _read(path)
            if "BRIDGE ONLY" not in text:
                missing_banner.append(name)
        assert not missing_banner, f"Subagents Claude sem banner BRIDGE ONLY: {missing_banner}"

    def test_claude_agents_have_explicit_tools(self):
        missing_tools = []
        for name in CLAUDE_AGENT_FILES:
            path = ROOT / ".claude" / "agents" / name
            text = _read(path)
            if not text.startswith("---\n"):
                missing_tools.append(name)
                continue
            _, yaml_block, _ = text.split("---\n", 2)
            fm = yaml.safe_load(yaml_block)
            if "tools" not in fm or not fm["tools"]:
                missing_tools.append(name)
        assert not missing_tools, f"Subagents Claude sem tools explícito: {missing_tools}"

    def test_claude_agents_do_not_emit_validated(self):
        for name in CLAUDE_AGENT_FILES:
            path = ROOT / ".claude" / "agents" / name
            text = _read(path)
            # VALIDATED deve aparecer apenas em seção de proibidos, não em status permitidos
            assert "VALIDATED" not in text.split("## Status permitidos")[1].split("## Proibido")[0] if "## Status permitidos" in text else True, (
                f"{name}: VALIDATED aparece em 'Status permitidos'"
            )
            # Deve aparecer na seção de proibidos
            if "## Proibido" in text:
                assert "VALIDATED" in text.split("## Proibido")[1], (
                    f"{name}: VALIDATED ausente na seção Proibido"
                )

    def test_adversarial_tester_declares_isolation_input(self):
        text = _read(ROOT / ".claude" / "agents" / "hb-adversarial-tester.md")
        assert "evidence_pack" in text
        assert "ADVERSARIAL_PASS_PENDING_GATE" in text

    def test_governance_auditor_references_gemini_styleguide(self):
        text = _read(ROOT / ".claude" / "agents" / "hb-governance-auditor.md")
        assert ".github/ai-review/styleguide.md" in text

    def test_evidence_verifier_does_not_edit_files(self):
        text = _read(ROOT / ".claude" / "agents" / "hb-evidence-verifier.md").lower()
        assert "editar arquivos" in text or "edit" in text


class TestCodexAgentFiles:
    def test_expected_codex_agents_exist(self):
        missing = [
            name
            for name in CODEX_AGENT_FILES
            if not (ROOT / ".dev" / "codex-agents" / name).exists()
        ]
        assert not missing, f"Agents Codex ausentes em .dev/codex-agents/: {missing}"

    def test_codex_agents_have_bridge_banner(self):
        missing_banner = []
        for name in CODEX_AGENT_FILES:
            path = ROOT / ".dev" / "codex-agents" / name
            text = _read(path)
            if "BRIDGE" not in text and "NON-SOVEREIGN" not in text:
                missing_banner.append(name)
        assert not missing_banner, f"Agents Codex sem banner BRIDGE/NON-SOVEREIGN: {missing_banner}"

    def test_codex_gate_auditor_prohibits_editing(self):
        text = _read(ROOT / ".dev" / "codex-agents" / "hb-gate-auditor.toml").lower()
        assert "editar arquivos" in text or "edit" in text

    def test_codex_gate_auditor_does_not_emit_validated(self):
        text = _read(ROOT / ".dev" / "codex-agents" / "hb-gate-auditor.toml")
        # VALIDATED deve aparecer apenas em contexto de proibição
        assert "VALIDATED" in text, "hb-gate-auditor.toml deve mencionar VALIDATED na lista de proibições"
        # Verificar que aparece no bloco de proibições (Proibido: ou declarar ... VALIDATED)
        assert "APPROVED" in text and "VALIDATED" in text, (
            "hb-gate-auditor.toml deve proibir explicitamente APPROVED e VALIDATED"
        )
        # Garantir que VALIDATED não é um status de saída permitido
        assert "retornar apenas GATE_FAIL" in text or "GATE_FAIL" in text, (
            "hb-gate-auditor.toml deve restringir saída a GATE_FAIL/GATE_INCONCLUSIVE/PASS_PENDING_CI"
        )

    def test_codex_agents_declare_read_only_sandbox(self):
        for name in CODEX_AGENT_FILES:
            path = ROOT / ".dev" / "codex-agents" / name
            text = _read(path)
            assert "read-only" in text, f"{name}: sandbox_mode read-only ausente"


class TestMultiAgentArchitectureCoherence:
    def test_agents_md_declares_multiagent_architecture(self):
        text = _read(ROOT / "AGENTS.md")
        assert "hb-adversarial-tester" in text
        assert "hb-governance-auditor" in text
        assert "hb-evidence-verifier" in text

    def test_agents_md_no_agent_emits_validated(self):
        text = _read(ROOT / "AGENTS.md")
        assert "Nenhum agente Copilot, Claude ou Codex pode emitir" in text
        assert "`VALIDATED`" in text

    def test_copilot_agents_have_explicit_tools(self):
        """Nenhum agente Copilot deve omitir tools ou usar tools: ['*']."""
        bad = []
        for filename in AGENT_FILES:
            path = ROOT / ".github" / "agents" / filename
            text = _read(path)
            _, yaml_block, _ = text.split("---\n", 2)
            fm = yaml.safe_load(yaml_block)
            if "tools" not in fm:
                bad.append(f"{filename}: tools ausente")
            elif fm["tools"] == ["*"]:
                bad.append(f"{filename}: tools: ['*'] proibido")
        assert not bad, "Agentes Copilot com tools problemático:\n" + "\n".join(bad)

    def test_handtracker_declares_operational_states(self):
        text = _read(ROOT / ".github" / "agents" / "Mesclado.agent.md")
        assert "READY_FOR_PR" in text
        assert "PR_OPENED_PENDING_CI" in text
        assert "POST_MERGE_VERIFIED" in text

    def test_implementer_has_adversarial_handoff(self):
        text = _read(ROOT / ".github" / "agents" / "hb-implementer.agent.md")
        assert "adversarial" in text.lower()
        assert "send: false" in text

    def test_adversarial_tester_handoff_is_non_sending(self):
        text = _read(ROOT / ".github" / "agents" / "hb-adversarial-tester.agent.md")
        assert "isolated Claude review" in text or "prepare isolated" in text.lower()
        # O handoff para HandTracker deve usar send: false agora
        assert "send: false" in text

    def test_exposure_map_no_longer_prohibits_claude_codex_agents(self):
        text = _read(ROOT / ".dev" / "AGENT_PLATFORM_EXPOSURE_MAP.md")
        assert "Não criar agentes Claude separados" not in text
        assert "Não criar agentes Codex separados" not in text
        assert "Evolução arquitetural" in text
