"""
tests/pipeline_gates/test_done_legacy_phase7.py

FASE 7 — REMOÇÃO DE LEGADO E ISOLAMENTO DE SHADOW AUTHORITY

Testa as mudanças da Fase 7 do AGENT_COMPLIANCE_EXECUTION_PLAN.md:
  - SHADOW_AUTHORITY_GATE expandido para cobrir markdowns de raiz
  - Markdowns de raiz não-soberanos têm banner NON-SOVEREIGN ou DERIVED
  - boot_resolution_report.json marcado com "_legacy": true
  - scripts/hbtrack_lint/__init__.py contém aviso LEGACY/legado/deprecated
  - LEGACY_CRITICAL_PATH_GATE implementado e registrado
  - Caminhos críticos não referenciam hbtrack_lint
  - Referência legada anotada em CONTRACT_FILESYSTEM_REFERENCE.md
"""

import json
import pathlib
import re
import tempfile

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
VALIDATE_SCRIPT = REPO_ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py"
GATES_REGISTRY = REPO_ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml"
BOOT_REPORT = REPO_ROOT / "_reports" / "evidence" / "boot_resolution_report.json"
HBTRACK_LINT_INIT = REPO_ROOT / "scripts" / "hbtrack_lint" / "__init__.py"
CONTRACT_FS_REF = REPO_ROOT / ".contract_driven" / "CONTRACT_FILESYSTEM_REFERENCE.md"

# Markdowns NON-SOVEREIGN — podem estar na raiz ou em _archive/ (após limpeza de legado)
def _resolve_md(name: str) -> pathlib.Path:
    archive = REPO_ROOT / "_archive" / name
    if archive.exists():
        return archive
    return REPO_ROOT / name


ROOT_DERIVED_MARKDOWNS = [
    _resolve_md("DEVCONT.md"),
    _resolve_md("compilance.md"),
    _resolve_md("ADVERSARIAL.md"),
    _resolve_md("ANALISEARQUITETURA.md"),
]

# Padrões de disclaimer não-soberano aceitos
DISCLAIMER_PATTERNS = [
    re.compile(r"NON-SOVEREIGN", re.IGNORECASE),
    re.compile(r"n[aã]o[- ]soberan", re.IGNORECASE),
    re.compile(r"ARTEFATO DERIVADO", re.IGNORECASE),
    re.compile(r"BRIDGE ONLY", re.IGNORECASE),
    re.compile(r"derived.*non.sovereign", re.IGNORECASE),
]


def _has_disclaimer(path: pathlib.Path) -> bool:
    """Retorna True se as primeiras 10 linhas do arquivo contêm um disclaimer não-soberano."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        top = "\n".join(content.splitlines()[:10])
        return any(p.search(top) for p in DISCLAIMER_PATTERNS)
    except Exception:
        return False


import scripts.contracts.validate.validate_contracts as _vc


# ──────────────────────────────────────────────────────────────────────────────
# 1. Markdowns de raiz — banners NON-SOVEREIGN
# ──────────────────────────────────────────────────────────────────────────────

class TestRootMarkdownsNonSovereign:
    """Valida que os 4 markdowns de raiz têm disclaimer non-sovereign explícito."""

    @pytest.mark.parametrize("md_path", ROOT_DERIVED_MARKDOWNS)
    def test_markdown_has_non_sovereign_banner(self, md_path):
        """Arquivo deve existir e ter banner NON-SOVEREIGN ou DERIVED nas primeiras 10 linhas."""
        assert md_path.exists(), f"{md_path.name} não encontrado na raiz."
        assert _has_disclaimer(md_path), (
            f"{md_path.name} não tem banner NON-SOVEREIGN/DERIVED nas primeiras 10 linhas. "
            "Adicionar: '> ⚠️ **ARTEFATO DERIVADO — NON-SOVEREIGN**'"
        )

    def test_no_new_root_md_without_disclaimer(self):
        """Qualquer markdown de raiz NÃO-operacional com linguagem de autoridade deve ter disclaimer."""
        import scripts.contracts.validate.validate_contracts as _vc_mod
        authority_patterns = [
            re.compile(r"\bssot\b", re.IGNORECASE),
            re.compile(r"fonte soberana", re.IGNORECASE),
            re.compile(r"source of truth", re.IGNORECASE),
            re.compile(r"fonte prim[aá]ria", re.IGNORECASE),
        ]
        # Exclui os mesmos prefixos que o gate exclui
        skip_prefixes = getattr(_vc_mod, "_ROOT_OPERATIONAL_SKIP_PREFIXES", ())
        sovereign_prefixes = getattr(_vc_mod, "_ROOT_SOVEREIGN_PREFIXES", ())
        violators = []
        for md in sorted(REPO_ROOT.glob("*.md")):
            rel = str(md.relative_to(REPO_ROOT))
            if any(rel.startswith(pfx) for pfx in sovereign_prefixes):
                continue
            if any(md.name.startswith(pfx) or md.name.lower().startswith(pfx.lower()) for pfx in skip_prefixes):
                continue
            try:
                text = md.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if not any(p.search(text) for p in authority_patterns):
                continue
            if _has_disclaimer(md):
                continue
            violators.append(md.name)
        assert not violators, (
            f"Markdowns de raiz com linguagem de autoridade e sem disclaimer: {violators}"
        )


# ──────────────────────────────────────────────────────────────────────────────
# 2. SHADOW_AUTHORITY_GATE — expansão para raiz
# ──────────────────────────────────────────────────────────────────────────────

class TestShadowAuthorityGateExpanded:
    """Valida a expansão do SHADOW_AUTHORITY_GATE para markdowns de raiz."""

    def test_root_sovereign_prefixes_constant_exists(self):
        """Constante _ROOT_SOVEREIGN_PREFIXES deve existir em validate_contracts.py."""
        text = VALIDATE_SCRIPT.read_text(encoding="utf-8")
        assert "_ROOT_SOVEREIGN_PREFIXES" in text, (
            "_ROOT_SOVEREIGN_PREFIXES não encontrado em validate_contracts.py. "
            "A expansão do SHADOW_AUTHORITY_GATE depende desta constante."
        )

    def test_shadow_authority_scans_root_markdowns(self):
        """_g2k_shadow_authority deve fazer glob de *.md na raiz."""
        text = VALIDATE_SCRIPT.read_text(encoding="utf-8")
        assert 'root.glob("*.md")' in text or "root.glob('*.md')" in text, (
            "_g2k_shadow_authority não faz glob de *.md na raiz do repositório."
        )

    def test_shadow_authority_passes_on_repo_root(self):
        """SHADOW_AUTHORITY_GATE deve PASS no repo atual (todos os markdowns têm disclaimer)."""
        result = _vc._g2k_shadow_authority(REPO_ROOT)
        status = result.get("status")
        violations = result.get("violations", [])
        assert status in ("PASS", "SKIP_NOT_APPLICABLE"), (
            f"SHADOW_AUTHORITY_GATE falhou. Status: {status}. Violations: {violations}"
        )

    def test_shadow_authority_fails_root_markdown_without_disclaimer(self):
        """Gate deve FAIL para arquivo de raiz com SSOT-claim sem disclaimer."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            # Cria um markdown de raiz com linguagem de autoridade e SEM disclaimer
            bad_md = tmp / "BAD_DOC.md"
            bad_md.write_text("# Docs\nEste documento é o SSOT para autenticação.", encoding="utf-8")
            result = _vc._g2k_shadow_authority(tmp)
            # Verifica que o gate detectou a violação
            assert result.get("status") == "FAIL", (
                f"Gate devia ser FAIL para markdown de raiz com SSOT sem disclaimer. Got: {result.get('status')}"
            )
            artifacts = [v.get("artifact", "") for v in result.get("violations", [])]
            assert any("BAD_DOC.md" in a for a in artifacts), (
                f"Violação não aponta para BAD_DOC.md. Violations: {artifacts}"
            )

    def test_shadow_authority_passes_root_markdown_with_disclaimer(self):
        """Gate deve PASS para arquivo de raiz com SSOT-claim MAS com disclaimer NON-SOVEREIGN."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            # Cria um markdown de raiz com linguagem de autoridade E disclaimer
            good_md = tmp / "GOOD_DOC.md"
            good_md.write_text(
                "> ⚠️ **ARTEFATO DERIVADO — NON-SOVEREIGN**\n\n"
                "Este documento referencia o SSOT mas não é o SSOT.",
                encoding="utf-8",
            )
            result = _vc._g2k_shadow_authority(tmp)
            violations = [
                v for v in result.get("violations", [])
                if "GOOD_DOC.md" in v.get("artifact", "")
            ]
            assert not violations, (
                f"Gate falhou para markdown com disclaimer válido. Violations: {violations}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 3. boot_resolution_report.json — marcado como legado
# ──────────────────────────────────────────────────────────────────────────────

class TestBootReportLegacyMarker:
    """Valida que boot_resolution_report.json está marcado como legado."""

    def test_boot_report_exists(self):
        assert BOOT_REPORT.exists(), "_reports/evidence/boot_resolution_report.json não encontrado."

    def test_boot_report_has_legacy_true(self):
        """_reports/evidence/boot_resolution_report.json deve ter '_legacy': true."""
        data = json.loads(BOOT_REPORT.read_text(encoding="utf-8"))
        assert data.get("_legacy") is True, (
            "boot_resolution_report.json não tem '_legacy': true. "
            "Marcar como legado para impedir reintrodução no fluxo ativo."
        )

    def test_boot_report_has_legacy_notice(self):
        """boot_resolution_report.json deve ter uma nota explicando o status de legado."""
        data = json.loads(BOOT_REPORT.read_text(encoding="utf-8"))
        notice = data.get("_legacy_notice", "")
        assert isinstance(notice, str) and len(notice) > 20, (
            "boot_resolution_report.json não tem '_legacy_notice' com descrição adequada."
        )

    def test_contract_filesystem_reference_annotates_legacy(self):
        """CONTRACT_FILESYSTEM_REFERENCE.md deve indicar que boot_resolution_report.json é LEGADO."""
        text = CONTRACT_FS_REF.read_text(encoding="utf-8")
        # Verifica que a referência ao arquivo está anotada com LEGADO ou similar
        assert re.search(r"boot_resolution_report\.json.*LEGADO", text), (
            "CONTRACT_FILESYSTEM_REFERENCE.md não anota boot_resolution_report.json como LEGADO."
        )


# ──────────────────────────────────────────────────────────────────────────────
# 4. scripts/hbtrack_lint/ — marcado como legado
# ──────────────────────────────────────────────────────────────────────────────

class TestHbtrackLintLegacyMarker:
    """Valida que scripts/hbtrack_lint/ está marcado como legado."""

    def test_hbtrack_lint_init_exists(self):
        assert HBTRACK_LINT_INIT.exists(), "scripts/hbtrack_lint/__init__.py não encontrado."

    def test_hbtrack_lint_init_has_legacy_warning(self):
        """scripts/hbtrack_lint/__init__.py deve conter aviso LEGACY/legado/deprecated."""
        text = HBTRACK_LINT_INIT.read_text(encoding="utf-8")
        assert re.search(r"LEGACY|legado|deprecated", text, re.IGNORECASE), (
            "scripts/hbtrack_lint/__init__.py não contém aviso LEGACY/legado/deprecated. "
            "Marcar explicitamente para documentar o status."
        )

    def test_critical_path_hb_does_not_reference_hbtrack_lint(self):
        """scripts/hb não deve referenciar hbtrack_lint."""
        hb = REPO_ROOT / "scripts" / "hb"
        if not hb.exists():
            pytest.skip("scripts/hb não encontrado.")
        text = hb.read_text(encoding="utf-8", errors="replace")
        assert "hbtrack_lint" not in text, (
            "scripts/hb referencia hbtrack_lint (caminho crítico). Remover referência."
        )

    def test_critical_path_validate_contracts_does_not_import_hbtrack_lint(self):
        """validate_contracts.py não deve ter 'import hbtrack_lint' nem 'from hbtrack_lint import'."""
        import re as _re
        text = VALIDATE_SCRIPT.read_text(encoding="utf-8", errors="replace")
        # O gate menciona a string "hbtrack_lint" como PATH (ex.: root/"scripts"/"hbtrack_lint"),
        # mas NÃO deve ter um import do módulo hbtrack_lint.
        assert not _re.search(r"(?:import|from)\s+hbtrack_lint", text), (
            "validate_contracts.py contém um import de hbtrack_lint (caminho crítico). "
            "Remover import para isolar o legado."
        )


# ──────────────────────────────────────────────────────────────────────────────
# 5. LEGACY_CRITICAL_PATH_GATE — existência e registro
# ──────────────────────────────────────────────────────────────────────────────

class TestLegacyCriticalPathGateExistence:
    """Valida que LEGACY_CRITICAL_PATH_GATE existe no código e no registry."""

    def test_gate_function_exists_in_validate_contracts(self):
        """Função _g_legacy_isolation deve existir em validate_contracts.py."""
        text = VALIDATE_SCRIPT.read_text(encoding="utf-8")
        assert "_g_legacy_isolation" in text, (
            "Função _g_legacy_isolation não encontrada em validate_contracts.py."
        )

    def test_gate_id_in_validate_contracts(self):
        """LEGACY_CRITICAL_PATH_GATE deve estar no gate_plan."""
        text = VALIDATE_SCRIPT.read_text(encoding="utf-8")
        assert '"LEGACY_CRITICAL_PATH_GATE"' in text, (
            "LEGACY_CRITICAL_PATH_GATE não está no gate_plan de validate_contracts.py."
        )

    def test_blocked_legacy_constant_exists(self):
        """Constante BLOCKED_LEGACY_IN_CRITICAL_PATH deve existir."""
        text = VALIDATE_SCRIPT.read_text(encoding="utf-8")
        assert "BLOCKED_LEGACY_IN_CRITICAL_PATH" in text, (
            "Constante BLOCKED_LEGACY_IN_CRITICAL_PATH ausente em validate_contracts.py."
        )

    def test_blocked_legacy_in_known_blocking_codes(self):
        """BLOCKED_LEGACY_IN_CRITICAL_PATH deve estar em _KNOWN_BLOCKING_CODES."""
        assert hasattr(_vc, "BLOCKED_LEGACY_IN_CRITICAL_PATH")
        assert _vc.BLOCKED_LEGACY_IN_CRITICAL_PATH in _vc._KNOWN_BLOCKING_CODES

    def test_gate_registered_in_gates_registry(self):
        """LEGACY_CRITICAL_PATH_GATE deve estar no GATES_REGISTRY.yaml."""
        data = yaml.safe_load(GATES_REGISTRY.read_text(encoding="utf-8"))
        gate_ids = {g.get("gate_id") for g in data.get("gates", [])}
        assert "LEGACY_CRITICAL_PATH_GATE" in gate_ids, (
            "LEGACY_CRITICAL_PATH_GATE ausente em GATES_REGISTRY.yaml."
        )

    def test_gate_in_registry_is_blocking(self):
        """LEGACY_CRITICAL_PATH_GATE deve ser blocking=true."""
        data = yaml.safe_load(GATES_REGISTRY.read_text(encoding="utf-8"))
        for gate in data.get("gates", []):
            if gate.get("gate_id") == "LEGACY_CRITICAL_PATH_GATE":
                assert gate.get("blocking") is True
                return
        pytest.fail("LEGACY_CRITICAL_PATH_GATE não encontrado no GATES_REGISTRY.")


# ──────────────────────────────────────────────────────────────────────────────
# 6. LEGACY_CRITICAL_PATH_GATE — testes funcionais
# ──────────────────────────────────────────────────────────────────────────────

class TestLegacyCriticalPathGateFunctional:
    """Testa o comportamento do LEGACY_CRITICAL_PATH_GATE com dados sintéticos."""

    def test_gate_passes_on_real_repo(self):
        """Gate deve PASS no repositório atual após as marcações de FASE 7."""
        result = _vc._g_legacy_isolation(REPO_ROOT)
        status = result.get("status")
        violations = result.get("violations", [])
        assert status in ("PASS", "SKIP_NOT_APPLICABLE"), (
            f"LEGACY_CRITICAL_PATH_GATE falhou no repo real. Status: {status}. "
            f"Violations: {violations}"
        )

    def test_gate_fails_when_boot_report_has_no_legacy_marker(self):
        """Gate deve FAIL quando boot_report existe sem '_legacy': true."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            evidence_dir = tmp / "_reports" / "evidence"
            evidence_dir.mkdir(parents=True)
            boot = evidence_dir / "boot_resolution_report.json"
            boot.write_text(
                '{"artifact_id": "HBTRACK_BOOT_RESOLUTION_REPORT", "version": "2.0.0"}',
                encoding="utf-8",
            )
            result = _vc._g_legacy_isolation(tmp)
            assert result.get("status") == "FAIL", (
                "Gate deveria FAIL quando boot_report não tem '_legacy': true."
            )
            codes = [v.get("blocking_code") for v in result.get("violations", [])]
            assert "BLOCKED_LEGACY_IN_CRITICAL_PATH" in codes

    def test_gate_fails_when_hbtrack_lint_has_no_legacy_marker(self):
        """Gate deve FAIL quando hbtrack_lint/__init__.py existe sem aviso LEGACY."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            lint_dir = tmp / "scripts" / "hbtrack_lint"
            lint_dir.mkdir(parents=True)
            init = lint_dir / "__init__.py"
            init.write_text(
                '"""HB Track Lint — pacote de validação."""\n',
                encoding="utf-8",
            )
            result = _vc._g_legacy_isolation(tmp)
            assert result.get("status") == "FAIL", (
                "Gate deveria FAIL quando __init__.py não tem aviso LEGACY."
            )

    def test_gate_skips_when_no_legacy_artifacts(self):
        """Gate deve SKIP quando nenhum artefato legado existe."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            result = _vc._g_legacy_isolation(tmp)
            assert result.get("status") == "SKIP_NOT_APPLICABLE", (
                "Gate deveria SKIP quando nenhum artefato legado monitorado existe."
            )

    def test_gate_passes_when_boot_report_has_legacy_true(self):
        """Gate deve PASS quando boot_report tem '_legacy': true."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            evidence_dir = tmp / "_reports" / "evidence"
            evidence_dir.mkdir(parents=True)
            boot = evidence_dir / "boot_resolution_report.json"
            boot.write_text(
                '{"_legacy": true, "_legacy_notice": "Legado substituido.", "artifact_id": "X"}',
                encoding="utf-8",
            )
            result = _vc._g_legacy_isolation(tmp)
            status = result.get("status")
            assert status in ("PASS", "SKIP_NOT_APPLICABLE"), (
                f"Gate deveria PASS ou SKIP quando boot_report tem _legacy=true. Got: {status}"
            )
