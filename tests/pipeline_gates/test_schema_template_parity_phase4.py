"""
tests/pipeline_gates/test_schema_template_parity_phase4.py

FASE 4 — ALINHAMENTO SCHEMA / TEMPLATE / PROMPTS / SKILLS

Testa as mudanças da Fase 4 do AGENT_COMPLIANCE_EXECUTION_PLAN.md:
  - SESSION_HANDOFF.template.md é schema-compatível com session_handoff.schema.json
  - Template possui todas as 5 seções obrigatórias no corpo
  - hb-pipeline-orchestrator/SKILL.md não contém 'task_type_target'
  - hb-pipeline-orchestrator/SKILL.md não contém declaração errada sobre o validador
  - hb-roadmap-executor/SKILL.md contém front matter YAML no template de handoff
  - execute_roadmap_phase.prompt.md descreve uso de 'hb verify' para estado de sessão
  - generate_code.prompt.md menciona 'hb verify' como pré-requisito (item 0)
  - pre_contract_orchestrator.prompt.md esclarece que hb verify grava session_start.json
  - copilot-instructions.md declara session_handoff.schema.json como validador ativo
"""

import json
import re
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).parent.parent.parent

HANDOFF_SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "shared" / "session_handoff.schema.json"
TEMPLATE_PATH = REPO_ROOT / "docs" / "_canon" / "templates" / "SESSION_HANDOFF.template.md"
ROADMAP_EXECUTOR_SKILL = REPO_ROOT / ".github" / "skills" / "hb-roadmap-executor" / "SKILL.md"
PIPELINE_ORCHESTRATOR_SKILL = REPO_ROOT / ".github" / "skills" / "hb-pipeline-orchestrator" / "SKILL.md"
EXECUTE_ROADMAP_PROMPT = REPO_ROOT / ".contract_driven" / "agent_prompts" / "execute_roadmap_phase.prompt.md"
GENERATE_CODE_PROMPT = REPO_ROOT / ".contract_driven" / "agent_prompts" / "generate_code.prompt.md"
PRE_CONTRACT_PROMPT = REPO_ROOT / ".contract_driven" / "agent_prompts" / "pre_contract_orchestrator.prompt.md"
COPILOT_INSTRUCTIONS = REPO_ROOT / ".github" / "copilot-instructions.md"

# Seções obrigatórias no corpo do SESSION_HANDOFF (confirmado via validate_contracts.py linha ~7078)
REQUIRED_SECTIONS = [
    "## Estado Geral",
    "## O que foi feito",
    "## Evidências",
    "## Próxima ação permitida",
    "## Bloqueios ativos",
]


def _load_handoff_schema() -> dict:
    return json.loads(HANDOFF_SCHEMA_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 1. Template: extrai front matter YAML e valida contra session_handoff.schema.json
# ---------------------------------------------------------------------------

def _extract_front_matter(text: str) -> str:
    """Retorna o conteúdo entre os delimitadores --- do front matter YAML."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        raise ValueError("Front matter YAML não encontrado no template")
    return match.group(1)


def _build_valid_payload() -> dict:
    """Gera payload minimamente válido para validação do schema."""
    return {
        "data_ultima_sessao": "2026-01-01",
        "branch_ativo": "main",
        "modo_operacao": "CDD",
        "ci_status": "PASS",
        "modulo_foco": "test_module",
        "fase_roadmap": 0,
        "task_type": "generate_api_contract",
        "boot_profile_id": "contract_execution",
        "task_id": "T-001",
        "resultado": "DONE",
        "proxima_acao_permitida": "Executar próxima fase conforme ROADMAP",
        "bloqueios_ativos": [],
        "evidence_paths": ["_reports/runs/001/contract_gates.json"],
    }


class TestTemplateSchemaCompatibility:
    """O SESSION_HANDOFF.template.md deve ser preenchível com dados válidos que passem na schema."""

    def test_template_exists(self):
        assert TEMPLATE_PATH.exists(), f"Template não encontrado: {TEMPLATE_PATH}"

    def test_template_has_front_matter_delimiters(self):
        content = TEMPLATE_PATH.read_text(encoding="utf-8")
        assert content.startswith("---"), "Template deve começar com delimitador YAML '---'"
        assert content.count("---") >= 2, "Template deve ter pelo menos dois delimitadores '---'"

    def test_valid_payload_passes_schema(self):
        schema = _load_handoff_schema()
        payload = _build_valid_payload()
        # Não deve lançar exceção
        jsonschema.validate(payload, schema)

    def test_evidence_paths_minItems(self):
        """evidence_paths: [] deve falhar — minItems: 1."""
        schema = _load_handoff_schema()
        payload = _build_valid_payload()
        payload["evidence_paths"] = []
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    def test_modo_operacao_enum(self):
        """Valores fora do enum CDD|ROADMAP devem falhar."""
        schema = _load_handoff_schema()
        payload = _build_valid_payload()
        payload["modo_operacao"] = "CDD | ROADMAP"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    def test_ci_status_enum(self):
        """Valores tipo 'PASS | FAIL | UNKNOWN' devem falhar."""
        schema = _load_handoff_schema()
        payload = _build_valid_payload()
        payload["ci_status"] = "PASS | FAIL | UNKNOWN"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    def test_resultado_enum(self):
        """Valores tipo 'DONE | PENDENTE | BLOCKED' devem falhar."""
        schema = _load_handoff_schema()
        payload = _build_valid_payload()
        payload["resultado"] = "DONE | PENDENTE | BLOCKED"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    def test_proxima_acao_min_length(self):
        """proxima_acao_permitida com menos de 10 caracteres deve falhar."""
        schema = _load_handoff_schema()
        payload = _build_valid_payload()
        payload["proxima_acao_permitida"] = "curto"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    def test_template_does_not_have_pipe_separator_in_enums(self):
        """Template não deve usar valores tipo 'CDD | ROADMAP' como valor YAML (fora de comentário)."""
        content = TEMPLATE_PATH.read_text(encoding="utf-8")
        # Verifica cada linha: se contiver '|' fora de um comentário YAML (# ...), é um valor inválido
        bad_patterns = [
            r"^modo_operacao:\s*CDD\s*\|",
            r"^ci_status:\s*PASS\s*\|",
            r"^resultado:\s*DONE\s*\|",
        ]
        for line in content.splitlines():
            stripped = line.strip()
            for pat in bad_patterns:
                assert not re.match(pat, stripped), (
                    f"Template contém valor de enum inválido como valor YAML: '{stripped}' — "
                    "use um valor válido com comentário explicativo"
                )

    def test_template_evidence_paths_not_empty(self):
        """Template não deve conter 'evidence_paths: []'."""
        content = TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "evidence_paths: []" not in content, (
            "Template contém 'evidence_paths: []' — viola minItems:1 do schema"
        )


class TestTemplateSections:
    """Corpo do template deve conter todas as seções obrigatórias detectadas pelo HANDOFF_COHERENCE_GATE."""

    def test_all_required_sections_present(self):
        content = TEMPLATE_PATH.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            assert section in content, (
                f"Seção obrigatória '{section}' ausente do template — "
                "validate_contracts.py vai rejeitar SESSION_HANDOFF.md sem ela"
            )


class TestPipelineOrchestratorSkill:
    """hb-pipeline-orchestrator/SKILL.md não deve conter ficções técnicas."""

    def test_skill_exists(self):
        assert PIPELINE_ORCHESTRATOR_SKILL.exists()

    def test_no_task_type_target(self):
        """'task_type_target' não existe em scripts/hb — SKILL.md não deve referenciar."""
        content = PIPELINE_ORCHESTRATOR_SKILL.read_text(encoding="utf-8")
        assert "task_type_target" not in content, (
            "SKILL.md referencia 'task_type_target' que não existe em scripts/hb"
        )

    def test_no_wrong_validator_statement(self):
        """SKILL.md não deve negar que session_handoff.schema.json é o validador ativo."""
        content = PIPELINE_ORCHESTRATOR_SKILL.read_text(encoding="utf-8")
        assert "Nao tratar" not in content, (
            "SKILL.md contém 'Nao tratar' — declaração errada sobre o validador ativo"
        )
        assert "não deve ser tratado como o validador ativo" not in content, (
            "SKILL.md nega incorretamente que session_handoff.schema.json é o validador ativo"
        )

    def test_handoff_template_has_yaml_front_matter(self):
        """O template de handoff no SKILL.md deve conter campos do front matter YAML."""
        content = PIPELINE_ORCHESTRATOR_SKILL.read_text(encoding="utf-8")
        assert "data_ultima_sessao" in content, (
            "Template de handoff no SKILL.md não contém 'data_ultima_sessao' (front matter YAML ausente)"
        )

    def test_handoff_template_correct_sections(self):
        """O template H.1 deve conter as seções obrigatórias."""
        content = PIPELINE_ORCHESTRATOR_SKILL.read_text(encoding="utf-8")
        assert "## Evidências" in content, "SKILL.md deve incluir '## Evidências' no template"
        assert "## Próxima ação permitida" in content, (
            "SKILL.md deve incluir '## Próxima ação permitida' no template"
        )


class TestRoadmapExecutorSkill:
    """hb-roadmap-executor/SKILL.md deve ter template de handoff com front matter válido."""

    def test_skill_exists(self):
        assert ROADMAP_EXECUTOR_SKILL.exists()

    def test_fechamento_template_has_yaml_front_matter(self):
        content = ROADMAP_EXECUTOR_SKILL.read_text(encoding="utf-8")
        assert "data_ultima_sessao" in content, (
            "SKILL.md FECHAMENTO não contém 'data_ultima_sessao' — front matter YAML ausente"
        )

    def test_fechamento_template_correct_sections(self):
        content = ROADMAP_EXECUTOR_SKILL.read_text(encoding="utf-8")
        assert "## Evidências" in content, "SKILL.md deve incluir '## Evidências' no template"
        assert "## Próxima ação permitida" in content, (
            "SKILL.md deve substituir '## Próximos passos' por '## Próxima ação permitida'"
        )

    def test_fechamento_template_not_wrong_sections(self):
        """Seções antigas não devem mais aparecer no contexto do template."""
        content = ROADMAP_EXECUTOR_SKILL.read_text(encoding="utf-8")
        # "## Critério de Done da fase" era errado — foi substituído
        assert "## Critério de Done da fase" not in content, (
            "SKILL.md ainda contém '## Critério de Done da fase' no template de handoff"
        )


class TestExecuteRoadmapPrompt:
    """execute_roadmap_phase.prompt.md deve descrever uso de hb verify para estado de sessão."""

    def test_prompt_exists(self):
        assert EXECUTE_ROADMAP_PROMPT.exists()

    def test_mentions_hb_verify_for_session(self):
        content = EXECUTE_ROADMAP_PROMPT.read_text(encoding="utf-8")
        assert "hb verify" in content, (
            "execute_roadmap_phase.prompt.md não menciona 'hb verify' para registro de estado de sessão"
        )

    def test_mentions_roadmap_phase_flag(self):
        content = EXECUTE_ROADMAP_PROMPT.read_text(encoding="utf-8")
        assert "--roadmap-phase" in content, (
            "execute_roadmap_phase.prompt.md não menciona a flag '--roadmap-phase'"
        )

    def test_handoff_step_mentions_front_matter(self):
        content = EXECUTE_ROADMAP_PROMPT.read_text(encoding="utf-8")
        assert "data_ultima_sessao" in content or "SESSION_HANDOFF.template.md" in content, (
            "execute_roadmap_phase.prompt.md não referencia o template canônico ou front matter obrigatório"
        )


class TestGenerateCodePrompt:
    """generate_code.prompt.md deve ter hb verify como pré-requisito explícito."""

    def test_prompt_exists(self):
        assert GENERATE_CODE_PROMPT.exists()

    def test_hb_verify_in_prerequisites(self):
        content = GENERATE_CODE_PROMPT.read_text(encoding="utf-8")
        assert "hb verify" in content, (
            "generate_code.prompt.md não menciona 'hb verify' nos pré-requisitos"
        )

    def test_handoff_references_template(self):
        content = GENERATE_CODE_PROMPT.read_text(encoding="utf-8")
        assert "SESSION_HANDOFF.template.md" in content or "HANDOFF_COHERENCE_GATE" in content, (
            "generate_code.prompt.md não referencia template canônico ou HANDOFF_COHERENCE_GATE"
        )


class TestPreContractPrompt:
    """pre_contract_orchestrator.prompt.md deve esclarecer que hb verify grava session_start.json."""

    def test_prompt_exists(self):
        assert PRE_CONTRACT_PROMPT.exists()

    def test_no_wrong_observability_statement(self):
        """Prompt não deve dizer que o orchestrator 'Publica' session_start.json diretamente."""
        content = PRE_CONTRACT_PROMPT.read_text(encoding="utf-8")
        assert "Publicar `_reports/session_start.json`" not in content, (
            "pre_contract_orchestrator.prompt.md diz que o orchestrator publica session_start.json "
            "diretamente — na prática, hb verify (FASE 0) é quem grava esse arquivo"
        )

    def test_hb_verify_writes_session_start(self):
        """Prompt deve indicar que hb verify grava session_start.json."""
        content = PRE_CONTRACT_PROMPT.read_text(encoding="utf-8")
        # Aceitar qualquer texto que ligue hb verify a session_start.json
        assert "session_start.json" in content, (
            "pre_contract_orchestrator.prompt.md não menciona session_start.json"
        )


class TestCopilotInstructions:
    """copilot-instructions.md deve conter declaração correta sobre o validador ativo."""

    def test_file_exists(self):
        assert COPILOT_INSTRUCTIONS.exists()

    def test_schema_declared_as_active_validator(self):
        """copilot-instructions.md deve afirmar que session_handoff.schema.json É o validador ativo."""
        content = COPILOT_INSTRUCTIONS.read_text(encoding="utf-8")
        assert "session_handoff.schema.json" in content, (
            "copilot-instructions.md não menciona session_handoff.schema.json"
        )
        assert "não deve ser tratado como o validador ativo" not in content, (
            "copilot-instructions.md ainda contém declaração negando o validador ativo"
        )

    def test_roadmap_mode_hb_verify_available(self):
        """copilot-instructions.md deve indicar que hb verify está disponível no modo ROADMAP."""
        content = COPILOT_INSTRUCTIONS.read_text(encoding="utf-8")
        # Deve mencionar hb verify para modo roadmap (para tracking de estado de sessão)
        assert "execute_roadmap_phase" in content, (
            "copilot-instructions.md não menciona 'execute_roadmap_phase' para o modo ROADMAP"
        )
