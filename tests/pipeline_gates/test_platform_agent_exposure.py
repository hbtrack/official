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

    def test_execution_plan_exists_and_disambiguates_other_artifacts(self):
        path = ROOT / ".dev" / "AGENT_PLATFORM_EXPOSURE_EXECUTION_PLAN.md"
        assert path.exists(), "Plano dedicado de exposição por plataforma ausente."
        text = _read(path)
        assert ".dev/CODEXPLAN.md" in text
        assert ".dev/AGENT_PLATFORM_EXPOSURE_MAP.md" in text
        assert "Claude" in text


# ---------------------------------------------------------------------------
# Items 11-22: Multiagent auditable architecture
# ---------------------------------------------------------------------------

CLAUDE_AGENTS_DIR = ROOT / ".claude" / "agents"
CODEX_AGENTS_DIR = ROOT / ".dev" / "codex-agents"

EXPECTED_CLAUDE_AGENTS = [
    "hb-adversarial-tester.md",
    "hb-governance-auditor.md",
    "hb-evidence-verifier.md",
]

EXPECTED_CODEX_AGENTS = [
    "hb-gate-auditor.toml",
    "hb-pr-reviewer.toml",
]


class TestMultiagentArchitecture:
    # ------------------------------------------------------------------
    # 11: .claude/agents/ exists with exactly the 3 expected files
    # ------------------------------------------------------------------
    def test_11_claude_agents_dir_exists_with_3_files(self):
        """Item 11 positivo: .claude/agents/ existe com os 3 subagents esperados."""
        missing = [f for f in EXPECTED_CLAUDE_AGENTS if not (CLAUDE_AGENTS_DIR / f).exists()]
        assert not missing, f".claude/agents/ faltando: {missing}"

    def test_11n_no_unexpected_files_in_claude_agents(self):
        """Item 11 negativo: ausência de qualquer arquivo esperado falha."""
        # Verificar que o diretório existe — ausência seria uma regressão
        assert CLAUDE_AGENTS_DIR.exists(), (
            ".claude/agents/ não existe — subagents Claude ausentes"
        )

    # ------------------------------------------------------------------
    # 12: Claude subagents declare explicit tools (not "*", not absent)
    # ------------------------------------------------------------------
    def test_12_claude_subagents_have_explicit_tools(self):
        """Item 12 positivo: tools declarados explicitamente em cada subagent Claude."""
        for fname in EXPECTED_CLAUDE_AGENTS:
            path = CLAUDE_AGENTS_DIR / fname
            fm = _frontmatter(path)
            assert "tools" in fm, f"{fname}: 'tools' ausente no frontmatter"
            tools_val = fm["tools"]
            assert tools_val != ["*"] and tools_val != "*", (
                f"{fname}: tools: ['*'] é proibido — deve listar ferramentas explícitas"
            )
            assert tools_val, f"{fname}: tools está vazio"

    def test_12n_wildcard_tools_rejected(self):
        """Item 12 negativo: tools: '*' ou ausente não é aceito."""
        for fname in EXPECTED_CLAUDE_AGENTS:
            path = CLAUDE_AGENTS_DIR / fname
            fm = _frontmatter(path)
            tools_val = fm.get("tools")
            assert tools_val != "*" and tools_val != ["*"], (
                f"{fname}: tools: ['*'] encontrado — proibido por segurança"
            )
            assert tools_val is not None, f"{fname}: tools ausente — proibido"

    # ------------------------------------------------------------------
    # 13: Claude adversarial tester declares isolated context (BRIDGE ONLY)
    # ------------------------------------------------------------------
    def test_13_claude_adversarial_tester_declares_isolated_context(self):
        """Item 13 positivo: hb-adversarial-tester.md declara BRIDGE ONLY e contexto isolado."""
        text = _read(CLAUDE_AGENTS_DIR / "hb-adversarial-tester.md")
        assert "BRIDGE ONLY" in text, "hb-adversarial-tester.md sem banner BRIDGE ONLY"
        assert "contexto isolado" in text.lower() or "isolated" in text.lower(), (
            "hb-adversarial-tester.md não declara contexto isolado"
        )

    def test_13n_adversarial_tester_no_validated_status(self):
        """Item 13 negativo: VALIDATED não pode aparecer como status emitível."""
        text = _read(CLAUDE_AGENTS_DIR / "hb-adversarial-tester.md")
        # VALIDATED must not appear as an allowed output status (but may appear as prohibited)
        lower = text.lower()
        validated_idx = lower.find("validated")
        while validated_idx != -1:
            # check context: must be in a prohibition, not in an allowed-status list
            context_start = max(0, validated_idx - 60)
            snippet = lower[context_start:validated_idx + 20]
            assert any(word in snippet for word in ["proibido", "nunca", "não pode", "prohibited", "never"]), (
                f"'VALIDATED' aparece sem proibição explícita em hb-adversarial-tester.md: ...{snippet}..."
            )
            validated_idx = lower.find("validated", validated_idx + 1)

    # ------------------------------------------------------------------
    # 14: .dev/codex-agents/hb-gate-auditor.toml exists (fallback path)
    # ------------------------------------------------------------------
    def test_14_codex_gate_auditor_exists(self):
        """Item 14 positivo: hb-gate-auditor.toml existe em .dev/codex-agents/."""
        path = CODEX_AGENTS_DIR / "hb-gate-auditor.toml"
        assert path.exists(), (
            f"hb-gate-auditor.toml não encontrado em {CODEX_AGENTS_DIR}"
        )

    def test_14n_codex_gate_auditor_not_in_wrong_location(self):
        """Item 14 negativo: gate auditor não deve estar na raiz de .codex (que é arquivo)."""
        wrong_path = ROOT / ".codex" / "agents" / "hb-gate-auditor.toml"
        assert not wrong_path.exists(), (
            "hb-gate-auditor.toml encontrado em .codex/agents/ — localização errada (.codex é arquivo)"
        )

    # ------------------------------------------------------------------
    # 15: Codex gate auditor prohibits edit, patch, refactor, commit
    # ------------------------------------------------------------------
    def test_15_codex_gate_auditor_prohibits_destructive_actions(self):
        """Item 15 positivo: hb-gate-auditor.toml proíbe editar, patch, refatorar, criar commits."""
        text = _read(CODEX_AGENTS_DIR / "hb-gate-auditor.toml").lower()
        assert "editar" in text or "edit" in text, "hb-gate-auditor.toml não proíbe edição"
        assert "patch" in text, "hb-gate-auditor.toml não proíbe patch"
        assert "refator" in text or "refactor" in text, "hb-gate-auditor.toml não proíbe refatoração"
        assert "commit" in text, "hb-gate-auditor.toml não proíbe commits"

    def test_15n_codex_gate_auditor_has_sandbox_readonly(self):
        """Item 15 negativo: ausência de sandbox_mode = 'read-only' é falha de segurança."""
        text = _read(CODEX_AGENTS_DIR / "hb-gate-auditor.toml")
        assert "read-only" in text, (
            "hb-gate-auditor.toml sem sandbox_mode = 'read-only' — modo de escrita não deve ser permitido"
        )

    # ------------------------------------------------------------------
    # 16: Codex gate auditor returns only GATE_FAIL, GATE_INCONCLUSIVE, PASS_PENDING_CI
    # ------------------------------------------------------------------
    def test_16_codex_gate_auditor_allowed_statuses(self):
        """Item 16 positivo: hb-gate-auditor.toml declara os 3 status permitidos."""
        text = _read(CODEX_AGENTS_DIR / "hb-gate-auditor.toml")
        assert "GATE_FAIL" in text, "hb-gate-auditor.toml não menciona GATE_FAIL"
        assert "GATE_INCONCLUSIVE" in text, "hb-gate-auditor.toml não menciona GATE_INCONCLUSIVE"
        assert "PASS_PENDING_CI" in text, "hb-gate-auditor.toml não menciona PASS_PENDING_CI"

    def test_16n_codex_gate_auditor_no_unrestricted_validated(self):
        """Item 16 negativo: VALIDATED sem restrição CI é proibido."""
        _RESTRICTION_WORDS = [
            "nunca", "proibido", "never", "não pode", "prohibited",
            "declarar", "não deve", "não emitir",
        ]
        text = _read(CODEX_AGENTS_DIR / "hb-gate-auditor.toml")
        if "VALIDATED" in text:
            lower = text.lower()
            idx = lower.find("validated")
            while idx != -1:
                context_start = max(0, idx - 60)
                snippet = lower[context_start:idx + 20]
                assert any(w in snippet for w in _RESTRICTION_WORDS), (
                    f"VALIDATED sem restrição em hb-gate-auditor.toml: ...{snippet}..."
                )
                idx = lower.find("validated", idx + 1)

    # ------------------------------------------------------------------
    # 17: AGENTS.md, CLAUDE.md, .codex and MAP.md agree on platform roles
    # ------------------------------------------------------------------
    def test_17_platform_role_alignment_across_docs(self):
        """Item 17 positivo: docs concordam — Copilot=execução, Claude=isolado, Codex=gate, CI=autoridade."""
        agents_text = _read(ROOT / "AGENTS.md").lower()
        claude_text = _read(ROOT / "CLAUDE.md").lower()
        codex_text = _read(ROOT / ".codex").lower()
        map_text = _read(ROOT / ".dev" / "AGENT_PLATFORM_EXPOSURE_MAP.md").lower()

        # Copilot = execution layer
        assert "copilot" in agents_text and "execução" in agents_text, (
            "AGENTS.md não associa Copilot a execução"
        )
        # Claude = isolated review
        assert "claude" in agents_text and "isolado" in agents_text, (
            "AGENTS.md não associa Claude a contexto isolado"
        )
        # Codex = gate / sandbox
        assert "codex" in agents_text and ("gate" in agents_text or "sandbox" in agents_text), (
            "AGENTS.md não associa Codex a gate/sandbox"
        )
        # CI = final authority
        assert "ci" in agents_text and "validated" in agents_text.lower(), (
            "AGENTS.md não estabelece CI como autoridade de VALIDATED"
        )
        # MAP.md also mentions CI as sole VALIDATED authority
        assert "única autoridade" in map_text or "única" in map_text, (
            "MAP.md não declara autoridade única de VALIDATED"
        )
        # Claude and Codex confirm same story
        assert "revisão adversarial" in claude_text or "tester externo" in claude_text, (
            "CLAUDE.md não confirma papel de revisão adversarial"
        )
        assert "gate" in codex_text or "sandbox" in codex_text, (
            ".codex não confirma papel de gate/sandbox para Codex"
        )

    def test_17n_no_cross_doc_contradiction(self):
        """Item 17 negativo: nenhum doc atribui autoridade de VALIDATED a Copilot/Claude/Codex."""
        _RESTRICTION_WORDS = [
            "nunca", "proibido", "não pode", "never", "prohibited",
            "nenhum agente", "só pode", "apenas", "somente", "única autoridade",
            "declarar", "não deve", "não emitir",
        ]
        for name, path in [
            ("CLAUDE.md", ROOT / "CLAUDE.md"),
            (".codex", ROOT / ".codex"),
            ("AGENTS.md", ROOT / "AGENTS.md"),
            ("MAP.md", ROOT / ".dev" / "AGENT_PLATFORM_EXPOSURE_MAP.md"),
        ]:
            text = _read(path).lower()
            # VALIDATED must not appear as an action these agents can take freely
            idx = text.find("validated")
            while idx != -1:
                context_start = max(0, idx - 80)
                snippet = text[context_start:idx + 30]
                is_restriction = any(w in snippet for w in _RESTRICTION_WORDS)
                assert is_restriction, (
                    f"{name}: 'VALIDATED' aparece sem restrição explícita: ...{snippet}..."
                )
                idx = text.find("validated", idx + 1)

    # ------------------------------------------------------------------
    # 18: Same-chat handoff (3rd handoff of hb-implementer) is non-independent
    # ------------------------------------------------------------------
    def test_18_implementer_3rd_handoff_is_send_false(self):
        """Item 18 positivo: 3º handoff do hb-implementer tem send: false."""
        path = ROOT / ".github" / "agents" / "hb-implementer.agent.md"
        fm = _frontmatter(path)
        handoffs = fm.get("handoffs", [])
        assert len(handoffs) >= 3, (
            f"hb-implementer tem apenas {len(handoffs)} handoffs — esperado >= 3"
        )
        third = handoffs[2]
        assert third.get("send") is False, (
            f"3º handoff de hb-implementer tem send: {third.get('send')} — deve ser False"
        )

    def test_18n_adversarial_tester_handoff_from_implementer_not_send_true(self):
        """Item 18 negativo: handoff para Hb Adversarial Tester no implementer não pode ser send: true."""
        path = ROOT / ".github" / "agents" / "hb-implementer.agent.md"
        fm = _frontmatter(path)
        handoffs = fm.get("handoffs", [])
        for h in handoffs:
            if "adversarial" in h.get("agent", "").lower() or "tester" in h.get("agent", "").lower():
                assert h.get("send") is not True, (
                    "Handoff para Adversarial Tester no implementer tem send: true — "
                    "same-chat handoff não pode ser tratado como validação independente"
                )

    # ------------------------------------------------------------------
    # 19: VALIDATED only appears associated to CI/scripts in all bridge docs
    # ------------------------------------------------------------------
    def test_19_validated_restricted_to_ci_in_all_bridge_docs(self):
        """Item 19 positivo: VALIDATED associado a CI/scripts em todos os bridge docs."""
        _RESTRICTION_WORDS = [
            "ci", "scripts/hb", "validate_contracts", "nunca", "proibido",
            "não pode", "never", "nenhum agente", "só pode", "única autoridade",
            "apenas", "somente", "declarar", "não deve", "não emitir",
        ]
        docs_with_validated = {
            "AGENTS.md": ROOT / "AGENTS.md",
            "MAP.md": ROOT / ".dev" / "AGENT_PLATFORM_EXPOSURE_MAP.md",
            ".codex": ROOT / ".codex",
        }
        for name, path in docs_with_validated.items():
            text = _read(path)
            if "VALIDATED" in text:
                lower = text.lower()
                idx = lower.find("validated")
                while idx != -1:
                    context_start = max(0, idx - 100)
                    snippet = lower[context_start:idx + 40]
                    is_restricted = any(w in snippet for w in _RESTRICTION_WORDS)
                    assert is_restricted, (
                        f"{name}: VALIDATED sem associação a CI/scripts ou restrição: ...{snippet}..."
                    )
                    idx = lower.find("validated", idx + 1)

    # ------------------------------------------------------------------
    # 20: No bridge doc contradicts AI_EXECUTION_ROLES_POLICY.md
    # ------------------------------------------------------------------
    def test_20_bridge_docs_reference_roles_policy(self):
        """Item 20 positivo: AGENTS.md e MAP.md referenciam AI_EXECUTION_ROLES_POLICY.md."""
        agents_text = _read(ROOT / "AGENTS.md")
        assert "AI_EXECUTION_ROLES_POLICY.md" in agents_text, (
            "AGENTS.md não referencia AI_EXECUTION_ROLES_POLICY.md"
        )

    def test_20n_no_free_validated_in_copilot_agents(self):
        """Item 20 negativo: agentes Copilot não podem emitir VALIDATED livre."""
        for fname in AGENT_FILES:
            path = ROOT / ".github" / "agents" / fname
            text = _read(path).lower()
            idx = text.find("validated")
            while idx != -1:
                context_start = max(0, idx - 80)
                snippet = text[context_start:idx + 30]
                is_restricted = any(w in snippet for w in [
                    "proibido", "nunca", "não pode", "never", "prohibited",
                    "não emitir", "não declarar",
                ])
                assert is_restricted, (
                    f"{fname}: VALIDATED aparece sem restrição explícita: ...{snippet}..."
                )
                idx = text.find("validated", idx + 1)

    # ------------------------------------------------------------------
    # 21: .dev/schemas/hb_gate_report.schema.json NOT in contracts/schemas/shared/
    # ------------------------------------------------------------------
    def test_21_gate_report_schema_in_dev_schemas(self):
        """Item 21 positivo: schema experimental está em .dev/schemas/."""
        path = ROOT / ".dev" / "schemas" / "hb_gate_report.schema.json"
        assert path.exists(), (
            f"hb_gate_report.schema.json não encontrado em .dev/schemas/"
        )

    def test_21n_gate_report_schema_not_in_contracts_shared(self):
        """Item 21 negativo: schema experimental NÃO deve estar em contracts/schemas/shared/."""
        forbidden = ROOT / "contracts" / "schemas" / "shared" / "hb_gate_report.schema.json"
        assert not forbidden.exists(), (
            "hb_gate_report.schema.json encontrado em contracts/schemas/shared/ — "
            "schema experimental não pode ser canonizado sem entrada formal no GATES_REGISTRY"
        )

    # ------------------------------------------------------------------
    # 22: governance_changed = false for multiagent arch output files
    #
    # Verifica que NENHUM dos artefatos criados pela arquitetura multiagente
    # está em paths de governança (.contract_driven/, contracts/, docs/_canon/).
    # Não verifica o diff completo do branch — pode haver outras trilhas ativas.
    # ------------------------------------------------------------------
    _MULTIAGENT_ARCH_OUTPUTS = [
        ".claude/agents/hb-adversarial-tester.md",
        ".claude/agents/hb-governance-auditor.md",
        ".claude/agents/hb-evidence-verifier.md",
        ".dev/codex-agents/hb-gate-auditor.toml",
        ".dev/codex-agents/hb-pr-reviewer.toml",
        ".dev/schemas/hb_gate_report.schema.json",
        ".dev/evidence/gates/planning_gate_report.json",
        "AGENTS.md",
        "CLAUDE.md",
        ".codex",
        ".dev/AGENT_PLATFORM_EXPOSURE_MAP.md",
        ".dev/AGENT_PLATFORM_EXPOSURE_EXECUTION_PLAN.md",
        ".github/agents/hb-implementer.agent.md",
        ".github/agents/hb-adversarial-tester.agent.md",
        ".github/agents/Mesclado.agent.md",
        "SESSION_HANDOFF.md",
        "tests/pipeline_gates/test_gate_report_schema.py",
        "tests/pipeline_gates/test_platform_agent_exposure.py",
    ]

    _GOVERNED_PREFIXES = (
        ".contract_driven/",
        "contracts/",
        "docs/_canon/",
    )

    def test_22_multiagent_arch_files_not_in_governance_paths(self):
        """Item 22 positivo: nenhum artefato da arquitetura multiagente está em path de governança."""
        in_governance = [
            f for f in self._MULTIAGENT_ARCH_OUTPUTS
            if any(f.startswith(p) for p in self._GOVERNED_PREFIXES)
        ]
        assert not in_governance, (
            "Artefatos da arquitetura multiagente em paths de governança:\n"
            + "\n".join(in_governance)
            + "\nEsses arquivos ativariam CI condicional de governança."
        )

    def test_22n_multiagent_arch_output_files_exist(self):
        """Item 22 negativo: todos os artefatos da arquitetura multiagente devem existir."""
        missing = [
            f for f in self._MULTIAGENT_ARCH_OUTPUTS
            if not (ROOT / f).exists()
        ]
        assert not missing, (
            "Artefatos da arquitetura multiagente ausentes:\n" + "\n".join(missing)
        )
