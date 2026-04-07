"""
Testes anti-regressão — FASE 0 do AGENT_COMPLIANCE_EXECUTION_PLAN.md

Garante que:
1. Bridge docs tenham banner BRIDGE ONLY — NON-SOVEREIGN e não contenham
   linguagem de override normativo.
2. Artefatos derivados (root markdowns analíticos) tenham banner NON-SOVEREIGN.
3. A cadeia de precedência esteja declarada de forma idêntica em
   CONTRACT_SYSTEM_RULES.md e AGENT_INSTRUCTIONS.md.
4. Nenhum bridge doc declare schema, gate ou política canônica sem banner.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ── Constantes ────────────────────────────────────────────────────────────────

BRIDGE_DOCS: list[Path] = [
    ROOT / ".github" / "copilot-instructions.md",
    ROOT / "CLAUDE.md",
    ROOT / ".github" / "skills" / "hb-pipeline-orchestrator" / "SKILL.md",
    ROOT / ".github" / "skills" / "hb-roadmap-executor" / "SKILL.md",
]

DERIVED_DOCS: list[Path] = [
    ROOT / "DEVCONT.md",
    ROOT / "compilance.md",
    ROOT / "ADVERSARIAL.md",
    ROOT / "ANALISEARQUITETURA.md",
]

BRIDGE_BANNER_PATTERN = re.compile(r"BRIDGE ONLY[^-\n]*NON-SOVEREIGN", re.IGNORECASE)
DERIVED_BANNER_PATTERN = re.compile(r"NON-SOVEREIGN", re.IGNORECASE)

# Palavras que indicam que o arquivo tenta se comportar como autoridade soberana
# sem ter o banner adequado
SOVEREIGN_CLAIM_PATTERNS = [
    re.compile(r"\bSSO[T]\b"),                   # SSOT
    re.compile(r"\bsource of truth\b", re.IGNORECASE),
    re.compile(r"\bfonte soberana\b", re.IGNORECASE),
    re.compile(r"\bautoritativo\b", re.IGNORECASE),
    re.compile(r"\bcanônico\b", re.IGNORECASE),
]

# Padrões que indicam tentativa de override de schema/gate/política em bridge doc
OVERRIDE_PATTERNS = [
    re.compile(r"override.*schema", re.IGNORECASE),
    re.compile(r"override.*gate", re.IGNORECASE),
    re.compile(r"override.*polic", re.IGNORECASE),
    re.compile(r"BLOCKED_.*=\s*\w"),  # redefine bloqueios como código
]

# Texto canônico da cadeia de precedência (deve ser idêntico nos dois artefatos)
PRECEDENCE_CHAIN_SIGNATURE = (
    "enforcement executável"
    # a ordem exata não precisa ser testada char-a-char, mas a presença de todos
    # os 6 níveis é obrigatória
)
PRECEDENCE_LEVELS = [
    "enforcement executável",
    "schemas ativos",
    "canon",
    "bridge docs",
    "artefatos derivados",
    "legado",
]


# ── Testes: bridge docs ───────────────────────────────────────────────────────

class TestBridgeDocBanners:
    """Bridge docs devem ter o banner BRIDGE ONLY — NON-SOVEREIGN."""

    def test_copilot_instructions_has_bridge_banner(self):
        path = ROOT / ".github" / "copilot-instructions.md"
        assert path.exists(), f"Arquivo ausente: {path}"
        text = path.read_text(encoding="utf-8")
        assert BRIDGE_BANNER_PATTERN.search(text), (
            f"{path.name} não contém banner BRIDGE ONLY — NON-SOVEREIGN. "
            "Adicione o aviso no topo conforme AGENT_COMPLIANCE_EXECUTION_PLAN.md §Fase 0."
        )

    def test_claude_md_has_bridge_banner(self):
        path = ROOT / "CLAUDE.md"
        assert path.exists(), f"Arquivo ausente: {path}"
        text = path.read_text(encoding="utf-8")
        assert BRIDGE_BANNER_PATTERN.search(text), (
            f"{path.name} não contém banner BRIDGE ONLY — NON-SOVEREIGN."
        )

    def test_pipeline_orchestrator_skill_has_bridge_banner(self):
        path = ROOT / ".github" / "skills" / "hb-pipeline-orchestrator" / "SKILL.md"
        assert path.exists(), f"Arquivo ausente: {path}"
        text = path.read_text(encoding="utf-8")
        assert BRIDGE_BANNER_PATTERN.search(text), (
            f"{path.name} não contém banner BRIDGE ONLY — NON-SOVEREIGN."
        )

    def test_roadmap_executor_skill_has_bridge_banner(self):
        path = ROOT / ".github" / "skills" / "hb-roadmap-executor" / "SKILL.md"
        assert path.exists(), f"Arquivo ausente: {path}"
        text = path.read_text(encoding="utf-8")
        assert BRIDGE_BANNER_PATTERN.search(text), (
            f"{path.name} não contém banner BRIDGE ONLY — NON-SOVEREIGN."
        )

    def test_all_bridge_docs_have_banner(self):
        """Teste abrangente: qualquer novo bridge doc também deve ter o banner."""
        missing = [
            str(p.relative_to(ROOT))
            for p in BRIDGE_DOCS
            if p.exists() and not BRIDGE_BANNER_PATTERN.search(p.read_text(encoding="utf-8"))
        ]
        assert not missing, (
            "Bridge docs sem banner NON-SOVEREIGN:\n" + "\n".join(f"  - {m}" for m in missing)
        )


# ── Testes: artefatos derivados ───────────────────────────────────────────────

class TestDerivedDocBanners:
    """Artefatos derivados (root markdowns analíticos) devem ter banner NON-SOVEREIGN."""

    def test_devcont_has_non_sovereign_banner(self):
        path = ROOT / "_archive" / "DEVCONT.md"
        if not path.exists():
            path = ROOT / "DEVCONT.md"
        assert path.exists()
        assert DERIVED_BANNER_PATTERN.search(path.read_text(encoding="utf-8")), (
            "DEVCONT.md não contém banner NON-SOVEREIGN."
        )

    def test_compilance_has_non_sovereign_banner(self):
        path = ROOT / "_archive" / "compilance.md"
        if not path.exists():
            path = ROOT / "compilance.md"
        assert path.exists()
        assert DERIVED_BANNER_PATTERN.search(path.read_text(encoding="utf-8")), (
            "compilance.md não contém banner NON-SOVEREIGN."
        )

    def test_adversarial_has_non_sovereign_banner(self):
        path = ROOT / "_archive" / "ADVERSARIAL.md"
        if not path.exists():
            path = ROOT / "ADVERSARIAL.md"
        assert path.exists()
        assert DERIVED_BANNER_PATTERN.search(path.read_text(encoding="utf-8")), (
            "ADVERSARIAL.md não contém banner NON-SOVEREIGN."
        )

    def test_analisearquitetura_has_non_sovereign_banner(self):
        path = ROOT / "_archive" / "ANALISEARQUITETURA.md"
        if not path.exists():
            path = ROOT / "ANALISEARQUITETURA.md"
        assert path.exists()
        assert DERIVED_BANNER_PATTERN.search(path.read_text(encoding="utf-8")), (
            "ANALISEARQUITETURA.md não contém banner NON-SOVEREIGN."
        )

    def test_all_derived_docs_have_banner(self):
        missing = [
            str(p.relative_to(ROOT))
            for p in DERIVED_DOCS
            if p.exists() and not DERIVED_BANNER_PATTERN.search(p.read_text(encoding="utf-8"))
        ]
        assert not missing, (
            "Artefatos derivados sem banner NON-SOVEREIGN:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )


# ── Testes: cadeia de precedência idêntica ────────────────────────────────────

class TestPrecedenceChainConsistency:
    """
    A cadeia de precedência deve estar declarada de forma idêntica em:
    - .contract_driven/CONTRACT_SYSTEM_RULES.md
    - docs/_canon/AGENT_INSTRUCTIONS.md
    """

    def _check_has_all_precedence_levels(self, text: str, source: str) -> None:
        missing = [lvl for lvl in PRECEDENCE_LEVELS if lvl not in text]
        assert not missing, (
            f"{source} está faltando os seguintes níveis de precedência:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )

    def test_contract_system_rules_has_precedence_chain(self):
        path = ROOT / ".contract_driven" / "CONTRACT_SYSTEM_RULES.md"
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        self._check_has_all_precedence_levels(text, "CONTRACT_SYSTEM_RULES.md")

    def test_agent_instructions_has_precedence_chain(self):
        path = ROOT / "docs" / "_canon" / "AGENT_INSTRUCTIONS.md"
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        self._check_has_all_precedence_levels(text, "AGENT_INSTRUCTIONS.md")

    def test_both_sources_declare_same_levels(self):
        """Os mesmos 6 níveis devem aparecer nos dois artefatos."""
        rules = (ROOT / ".contract_driven" / "CONTRACT_SYSTEM_RULES.md").read_text(encoding="utf-8")
        agent = (ROOT / "docs" / "_canon" / "AGENT_INSTRUCTIONS.md").read_text(encoding="utf-8")

        rules_missing_in_agent = [lvl for lvl in PRECEDENCE_LEVELS if lvl in rules and lvl not in agent]
        agent_missing_in_rules = [lvl for lvl in PRECEDENCE_LEVELS if lvl in agent and lvl not in rules]

        assert not rules_missing_in_agent, (
            "Níveis em CONTRACT_SYSTEM_RULES.md ausentes em AGENT_INSTRUCTIONS.md:\n"
            + "\n".join(f"  - {l}" for l in rules_missing_in_agent)
        )
        assert not agent_missing_in_rules, (
            "Níveis em AGENT_INSTRUCTIONS.md ausentes em CONTRACT_SYSTEM_RULES.md:\n"
            + "\n".join(f"  - {l}" for l in agent_missing_in_rules)
        )


# ── Testes: bridge docs não contêm override normativo ────────────────────────

class TestBridgeDocsNoOverride:
    """
    Bridge docs não podem conter linguagem que redefina schemas, gates ou políticas.
    Se usarem linguagem soberana (SSOT, canônico, etc.) precisam ter o banner.
    """

    def test_bridge_docs_no_schema_gate_policy_override(self):
        """
        Nenhum bridge doc pode conter padrões que sugiram redefinição de
        schema, gate ou política canônica.
        """
        violations = []
        for path in BRIDGE_DOCS:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            for pattern in OVERRIDE_PATTERNS:
                match = pattern.search(text)
                if match:
                    violations.append(
                        f"{path.relative_to(ROOT)}: padrão '{pattern.pattern}' "
                        f"encontrado — possível override normativo"
                    )
        assert not violations, (
            "Bridge docs com possível override normativo:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )

    def test_new_root_md_files_without_banner_are_flagged(self):
        """
        Qualquer markdown na raiz com tom normativo forte (SSOT, canônico, etc.)
        deve ter banner NON-SOVEREIGN.
        Escaneia apenas arquivos na raiz (não recursivo).
        """
        # Arquivos explicitamente excluídos (têm papel especial ou são README)
        EXEMPT = {
            "README.md",
            "ROADMAP.md",
            "SESSION_HANDOFF.md",
            "SESSION_HANDOFF.md.backup",
            "AGENT_COMPLIANCE_EXECUTION_PLAN.md",  # novo plano, sem banner ainda
            "plano1.md",  # rascunho de planejamento humano, sem ton normativo operacional
        }
        # Exceções para arquivos que têm SESSION em nome (múltiplos handoffs)
        violations = []
        for md_file in ROOT.glob("*.md"):
            if md_file.name in EXEMPT:
                continue
            if md_file.name.startswith("SESSION_HANDOFF"):
                continue
            text = md_file.read_text(encoding="utf-8")
            # Verifica se usa linguagem soberana sem ter banner de não-soberania
            has_sovereign_claim = any(p.search(text) for p in SOVEREIGN_CLAIM_PATTERNS)
            has_banner = DERIVED_BANNER_PATTERN.search(text) or BRIDGE_BANNER_PATTERN.search(text)
            if has_sovereign_claim and not has_banner:
                violations.append(str(md_file.relative_to(ROOT)))

        assert not violations, (
            "Markdowns de raiz com linguagem normativa mas sem banner NON-SOVEREIGN:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )
