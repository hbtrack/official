"""
Negative enforcement tests for agent governance (issue #108).

Cada teste constrói uma cópia mínima do repositório em tmp_path,
viola UMA regra de agent governance (estrutura de .github/agents/, frontmatter,
bridge docs CLAUDE.md/.codex), e asserta que a asserção do gate existente
DISPARA AssertionError sob essa violação.

A estratégia de monkeypatch sobre `ROOT` do módulo testado prova que a regra
captura a violação — sem precisar reimplementar a lógica.
"""
from __future__ import annotations

import importlib
import pathlib
import shutil

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Fixture builder
# ---------------------------------------------------------------------------

AGENT_FILES = (
    "hb-contract.agent.md",
    "hb-implementer.agent.md",
    "hb-adversarial-tester.agent.md",
    "Mesclado.agent.md",
)

BRIDGE_DOCS = ("CLAUDE.md", ".codex", "AGENTS.md")
DEV_DOCS = (
    ".dev/AGENT_PLATFORM_EXPOSURE_MAP.md",
    ".dev/AGENT_PLATFORM_EXPOSURE_EXECUTION_PLAN.md",
)


def _seed_fake_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """Copia para tmp_path o conjunto mínimo de arquivos que o teste original lê."""
    agents_src = REPO_ROOT / ".github" / "agents"
    agents_dst = tmp_path / ".github" / "agents"
    agents_dst.mkdir(parents=True, exist_ok=True)
    for name in AGENT_FILES:
        src = agents_src / name
        if src.exists():
            shutil.copy2(src, agents_dst / name)
    for rel in BRIDGE_DOCS:
        src = REPO_ROOT / rel
        if src.exists():
            (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, tmp_path / rel)
    for rel in DEV_DOCS:
        src = REPO_ROOT / rel
        dst = tmp_path / rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    return tmp_path


@pytest.fixture
def fake_repo(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch):
    """Constrói repo fake em tmp_path e aponta o módulo real para ele via monkeypatch."""
    _seed_fake_repo(tmp_path)
    exposure_test = importlib.import_module(
        "tests.pipeline_gates.test_platform_agent_exposure"
    )
    monkeypatch.setattr(exposure_test, "ROOT", tmp_path)
    return tmp_path, exposure_test


# ---------------------------------------------------------------------------
# Sanidade: fixture não-violada deve passar nos testes existentes
# ---------------------------------------------------------------------------

def test_baseline_unmutated_repo_passes_existing_gate(fake_repo) -> None:
    _, exposure_test = fake_repo
    instance = exposure_test.TestCopilotAgentFiles()
    instance.test_expected_copilot_agents_exist()
    instance.test_copilot_agent_names_match_frontmatter()


# ---------------------------------------------------------------------------
# Negativos: cada um viola UMA regra
# ---------------------------------------------------------------------------

def test_fail_when_required_copilot_agent_missing(fake_repo) -> None:
    """Remove hb-contract.agent.md → test_expected_copilot_agents_exist deve falhar."""
    tmp_path, exposure_test = fake_repo
    (tmp_path / ".github" / "agents" / "hb-contract.agent.md").unlink()
    instance = exposure_test.TestCopilotAgentFiles()
    with pytest.raises(AssertionError, match="hb-contract.agent.md"):
        instance.test_expected_copilot_agents_exist()


def test_fail_when_agent_frontmatter_name_mismatches(fake_repo) -> None:
    """Renomeia o campo `name` no frontmatter de hb-contract → asserção falha."""
    tmp_path, exposure_test = fake_repo
    target = tmp_path / ".github" / "agents" / "hb-contract.agent.md"
    text = target.read_text(encoding="utf-8")
    mutated = text.replace("name: HB Contract", "name: Wrong Name")
    assert mutated != text, "fixture inválida — string esperada não encontrada"
    target.write_text(mutated, encoding="utf-8")
    instance = exposure_test.TestCopilotAgentFiles()
    with pytest.raises(AssertionError, match="hb-contract"):
        instance.test_copilot_agent_names_match_frontmatter()


def test_fail_when_implementer_missing_runtime_task_type(fake_repo) -> None:
    """Remove referência a `implementation_execution` → asserção falha."""
    tmp_path, exposure_test = fake_repo
    target = tmp_path / ".github" / "agents" / "hb-implementer.agent.md"
    text = target.read_text(encoding="utf-8")
    mutated = text.replace("implementation_execution", "garbage_task_type")
    assert mutated != text, "fixture inválida — string esperada não encontrada"
    target.write_text(mutated, encoding="utf-8")
    instance = exposure_test.TestCopilotAgentFiles()
    with pytest.raises(AssertionError):
        instance.test_implementer_references_runtime_task_type()


def test_fail_when_handtracker_presented_as_runtime_executor(fake_repo) -> None:
    """Adiciona task_type runtime ao Mesclado.agent.md → asserção falha."""
    tmp_path, exposure_test = fake_repo
    target = tmp_path / ".github" / "agents" / "Mesclado.agent.md"
    text = target.read_text(encoding="utf-8")
    mutated = text + "\n\nimplementation_execution\n"
    target.write_text(mutated, encoding="utf-8")
    instance = exposure_test.TestCopilotAgentFiles()
    with pytest.raises(AssertionError):
        instance.test_handtracker_is_not_presented_as_runtime_executor()


def test_fail_when_claude_md_missing_external_tester_role(fake_repo) -> None:
    """Remove menção a 'tester externo final' em CLAUDE.md → asserção falha."""
    tmp_path, exposure_test = fake_repo
    target = tmp_path / "CLAUDE.md"
    text = target.read_text(encoding="utf-8")
    mutated = text.replace("tester externo final", "REMOVED")
    assert mutated != text, "fixture inválida — string esperada não encontrada"
    target.write_text(mutated, encoding="utf-8")
    instance = exposure_test.TestPlatformExposureDocs()
    with pytest.raises(AssertionError):
        instance.test_claude_declares_external_tester_role()


def test_fail_when_codex_missing_no_equivalent_clause(fake_repo) -> None:
    """Remove menção a '.github/agents/*.agent.md' em .codex → asserção falha."""
    tmp_path, exposure_test = fake_repo
    target = tmp_path / ".codex"
    text = target.read_text(encoding="utf-8")
    mutated = text.replace(".github/agents/*.agent.md", "REMOVED")
    assert mutated != text, "fixture inválida — string esperada não encontrada"
    target.write_text(mutated, encoding="utf-8")
    instance = exposure_test.TestPlatformExposureDocs()
    with pytest.raises(AssertionError):
        instance.test_codex_declares_no_equivalent_agent_ui()


def test_fail_when_execution_plan_doc_deleted(fake_repo) -> None:
    """Remove .dev/AGENT_PLATFORM_EXPOSURE_EXECUTION_PLAN.md → asserção falha."""
    tmp_path, exposure_test = fake_repo
    target = tmp_path / ".dev" / "AGENT_PLATFORM_EXPOSURE_EXECUTION_PLAN.md"
    target.unlink()
    instance = exposure_test.TestPlatformExposureDocs()
    with pytest.raises(AssertionError):
        instance.test_execution_plan_exists_and_disambiguates_other_artifacts()
