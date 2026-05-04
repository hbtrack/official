"""Testes de regressão para governança do pipeline."""

from __future__ import annotations

import datetime
import json
from pathlib import Path

from scripts.contracts.validate import validate_contracts as gates


def _write_structured_handoff(
    root: Path,
    *,
    date_value: str,
    branch: str = "main",
    next_action: str = "Executar o próximo bloco validado do roadmap.",
) -> None:
    handoff = root / "SESSION_HANDOFF.md"
    handoff.write_text(
        f"""---
data_ultima_sessao: {date_value}
branch_ativo: {branch}
ci_status: PASS
modulo_foco: governance
fase_roadmap: 1
task_id: phase-1
resultado: PENDENTE
proxima_acao_permitida: {next_action}
bloqueios_ativos: []
---
# SESSION HANDOFF — HB TRACK

## Estado Geral
**Data:** {date_value} | **Branch:** {branch} | **CI:** PASS

## O que foi feito
- item

## Próxima ação permitida
- {next_action}

## Bloqueios ativos
- Nenhum.
""",
        encoding="utf-8",
    )


def test_handoff_coherence_detects_stale_date(tmp_path):
    contracts_dir = tmp_path / "contracts" / "schemas" / "shared"
    contracts_dir.mkdir(parents=True)
    schema_src = Path("contracts/schemas/shared/session_handoff.schema.json")
    (contracts_dir / "session_handoff.schema.json").write_text(
        schema_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    _write_structured_handoff(tmp_path, date_value="2020-01-01")

    result = gates._g_handoff_coherence(tmp_path)

    assert result["status"] == "FAIL"
    assert any("BLOCKED_HANDOFF_INCOMPLETE" in str(item) for item in result.get("violations", []))


def test_handoff_coherence_rejects_missing_next_action(tmp_path):
    contracts_dir = tmp_path / "contracts" / "schemas" / "shared"
    contracts_dir.mkdir(parents=True)
    schema_src = Path("contracts/schemas/shared/session_handoff.schema.json")
    (contracts_dir / "session_handoff.schema.json").write_text(
        schema_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    handoff = tmp_path / "SESSION_HANDOFF.md"
    handoff.write_text(
        f"""---
data_ultima_sessao: {datetime.date.today().isoformat()}
branch_ativo: main
ci_status: PASS
modulo_foco: governance
fase_roadmap: 1
task_id: phase-1
resultado: PENDENTE
bloqueios_ativos: []
---
# SESSION HANDOFF — HB TRACK

## Estado Geral
**Data:** {datetime.date.today().isoformat()} | **Branch:** main | **CI:** PASS

## O que foi feito
- item

## Próxima ação permitida
- item

## Bloqueios ativos
- Nenhum.
""",
        encoding="utf-8",
    )

    result = gates._g_handoff_coherence(tmp_path)

    assert result["status"] == "FAIL"
    assert any("proxima_acao_permitida" in str(item) for item in result.get("violations", []))


def test_module_status_coherence_blocks_with_adversarial_fail(tmp_path):
    canon = tmp_path / "docs" / "_canon"
    canon.mkdir(parents=True)
    (canon / "MODULE_REGISTRY.yaml").write_text(
        "modules:\n  training:\n    status: implementation_ready\n    expected_surfaces: []\n",
        encoding="utf-8",
    )
    adv_dir = tmp_path / "_reports" / "adversarial"
    adv_dir.mkdir(parents=True)
    (adv_dir / "training.adversarial.json").write_text(
        json.dumps({"module": "training", "overall_status": "FAIL", "risks": []}),
        encoding="utf-8",
    )

    result = gates._g_module_status_coherence(tmp_path)

    assert result["status"] == "FAIL"
    assert result["blocking_code"] == "BLOCKED_REGISTRY_MISMATCH"


def test_ui_alignment_detects_missing_operationid(tmp_path):
    oa_dir = tmp_path / "contracts" / "openapi"
    oa_dir.mkdir(parents=True)
    (oa_dir / "openapi.yaml").write_text("operationId: existingOperation\n", encoding="utf-8")
    ui_dir = tmp_path / "docs" / "hbtrack" / "modulos" / "training"
    ui_dir.mkdir(parents=True)
    (ui_dir / "UI_CONTRACT_TRAINING.md").write_text(
        "Use `getNonExistentOperationXyz` to fetch data.\n",
        encoding="utf-8",
    )

    result = gates._g14_ui_doc_validation(tmp_path)

    assert result["status"] == "FAIL"
    assert any("getNonExistentOperationXyz" in str(item) for item in result.get("violations", []))


def test_frontend_contract_gate_skips_without_frontend_workspace(tmp_path):
    result = gates._g_frontend_contract(tmp_path)

    assert result["status"] == "SKIP_NOT_APPLICABLE"


def test_frontend_contract_gate_detects_missing_visual_contracts(tmp_path):
    canon = tmp_path / "docs" / "_canon"
    canon.mkdir(parents=True)
    (canon / "FRONTEND_CONTRACT.md").write_text(
        "docs/_canon/UX_BRAND_CONTRACT.md\n",
        encoding="utf-8",
    )
    frontend = tmp_path / "frontend"
    (frontend / "src" / "shared" / "layouts").mkdir(parents=True)
    (frontend / "src" / "features" / "auth").mkdir(parents=True)
    (frontend / "src" / "api").mkdir(parents=True)
    (frontend / "package.json").write_text(json.dumps({"scripts": {}}), encoding="utf-8")
    (frontend / "src" / "api" / "schema.d.ts").write_text("// generated\n", encoding="utf-8")
    (frontend / "src" / "App.tsx").write_text("export default function App() { return null }\n", encoding="utf-8")
    (frontend / "index.html").write_text("<html></html>\n", encoding="utf-8")

    result = gates._g_frontend_contract(tmp_path)

    assert result["status"] == "FAIL"
    assert result["blocking_code"] == "BLOCKED_MISSING_CANON_ARTIFACT"
    assert any("UX_SHELL_CONTRACT.md" in str(item) for item in result.get("violations", []))


def test_frontend_contract_gate_passes_for_compliant_workspace(tmp_path):
    canon = tmp_path / "docs" / "_canon"
    canon.mkdir(parents=True)
    for name in (
        "UX_BRAND_CONTRACT.md",
        "UX_SHELL_CONTRACT.md",
        "AUTH_EXPERIENCE_CONTRACT.md",
        "NAVIGATION_VISIBILITY_CONTRACT.md",
    ):
        (canon / name).write_text("# canon\n", encoding="utf-8")
    (canon / "FRONTEND_CONTRACT.md").write_text(
        "\n".join(
            [
                "docs/_canon/UX_BRAND_CONTRACT.md",
                "docs/_canon/UX_SHELL_CONTRACT.md",
                "docs/_canon/AUTH_EXPERIENCE_CONTRACT.md",
                "docs/_canon/NAVIGATION_VISIBILITY_CONTRACT.md",
            ]
        ),
        encoding="utf-8",
    )

    images = tmp_path / "generated" / "images"
    images.mkdir(parents=True)
    for name in (
        "logo.svg",
        "logo-dark.svg",
        "logo-icon.svg",
        "logo-icon-dark.svg",
        "auth-logo.svg",
        "auth-logo-dark.svg",
        "hbicon.ico",
    ):
        (images / name).write_text("asset\n", encoding="utf-8")

    frontend = tmp_path / "frontend"
    (frontend / "src" / "api" / "hooks").mkdir(parents=True)
    (frontend / "src" / "shared" / "layouts").mkdir(parents=True)
    (frontend / "src" / "features" / "auth" / "pages").mkdir(parents=True)
    (tmp_path / "contracts" / "openapi" / "paths").mkdir(parents=True)
    (tmp_path / "contracts" / "schemas" / "users").mkdir(parents=True)
    (tmp_path / "contracts" / "openapi" / "components" / "schemas" / "users").mkdir(parents=True)
    (tmp_path / ".env.example").write_text(
        "\n".join(
            [
                "FRONTEND_URL=https://app.hbtrack.local",
                "RESEND_API_KEY=CHANGE_ME",
                "RESEND_FROM_EMAIL=suporte@handballtrack.app",
                "RESEND_FROM_NAME=Handball Track",
                "CLOUDINARY_URL=cloudinary://CHANGE_ME",
                "CLOUDINARY_CLOUD_NAME=hbtrack",
                "CLOUDINARY_UPLOAD_PRESET=hb_profile_photo",
                "CLOUDINARY_ASSET=https://res.cloudinary.com/hbtrack/image/upload/t_profile_avatar/sample",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "contracts" / "openapi" / "paths" / "identity_access.yaml").write_text(
        """
        /auth/login:
          post:
            operationId: authLogin
        /auth/forgot-password:
          post:
            operationId: authForgotPassword
        /auth/reset-password:
          post:
            operationId: authResetPassword
        /auth/new-password:
          post:
            operationId: authNewPassword
        /auth/confirm-reset:
          post:
            operationId: authConfirmReset
        """,
        encoding="utf-8",
    )
    (canon / "FEATURE_REGISTRY.yaml").write_text(
        """
        features:
          - id: FT-900
            module: identity_access
            name: Conta e Acesso
            description: Forgot password, reset password, new password, confirm reset.
        """,
        encoding="utf-8",
    )
    (tmp_path / "contracts" / "schemas" / "users" / "user_profile.schema.json").write_text(
        json.dumps(
            {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "displayName": {"type": "string"},
                    "avatarUrl": {"type": "string"},
                },
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "contracts" / "openapi" / "components" / "schemas" / "users" / "user_profile.yaml").write_text(
        "type: object\nproperties:\n  avatarUrl:\n    type: string\n",
        encoding="utf-8",
    )
    (frontend / "package.json").write_text(
        json.dumps({"scripts": {"api:generate": "openapi-typescript ../contracts/openapi/openapi.yaml -o src/api/schema.d.ts"}}),
        encoding="utf-8",
    )
    (frontend / "src" / "api" / "schema.d.ts").write_text("// generated\n", encoding="utf-8")
    (frontend / "src" / "api" / "client.ts").write_text("export const apiClient = {}\n", encoding="utf-8")
    (frontend / "src" / "api" / "hooks" / "useAuth.ts").write_text(
        "export function useAuth() { return null }\n",
        encoding="utf-8",
    )
    (frontend / "src" / "App.tsx").write_text(
        """
        export default function App() {
          const groups = [
            'Início',
            'Organização',
            'Planejamento Técnico',
            'Jogo e Competição',
            'Performance e Saúde',
            'Administração',
          ];
          const activeModules = ['Dashboard', 'Teams', 'Seasons', 'Training', 'Users', 'Conta e Acesso'];
          const disabledModules = [
            'Competitions',
            'Matches',
            'Scout',
            'Video',
            'Wellness',
            'Medical',
            'Exercises',
            'Analytics',
            'Reports',
            'AI Ingestion',
            'Audit',
          ];
          const topBarCapabilities = ['Notificações', 'Command palette', 'Breadcrumbs', 'User menu'];
          const rollout = 'disabled coming soon';
          const routes = ['/forgot-password', '/reset-password', '/confirm-reset'];
          return null;
        }
        """,
        encoding="utf-8",
    )
    (frontend / "src" / "shared" / "layouts" / "AppShell.tsx").write_text(
        """
        export function AppShell() {
          const breadcrumbs = true;
          const commandPalette = true;
          const notifications = true;
          const userMenu = true;
          const avatar = true;
          const initials = 'HB';
          const allowedRoles = ['admin'];
          const activeTeam = 'u18';
          const teamSwitcher = true;
          const activeSeason = '2026';
          const collapsed = false;
          const overlay = true;
          const badge = 'coming soon';
          const onKeyDown = (event: { key: string }) => event.key === 'Escape';
          return (
            <div>
              <aside>generated/images/logo.svg generated/images/logo-dark.svg generated/images/logo-icon.svg generated/images/logo-icon-dark.svg</aside>
              <header>breadcrumbs command palette notificações avatar user menu sair rounded-full</header>
              <main>{allowedRoles}{activeTeam}{teamSwitcher}{activeSeason}{collapsed}{overlay}{badge}{initials}</main>
            </div>
          );
        }
        """,
        encoding="utf-8",
    )
    (frontend / "src" / "features" / "auth" / "pages" / "LoginPage.tsx").write_text(
        """
        export function LoginPage() {
          const showPassword = true;
          const isAuthenticated = false;
          const isPending = false;
          const error = '';
          const email = 'coach@hbtrack.app';
          const password = 'secret';
          const navigate = (path: string) => path;
          if (isAuthenticated) navigate('/');
          return (
            <div>
              generated/images/auth-logo.svg
              generated/images/auth-logo-dark.svg
              Esqueceu a senha?
              Eye EyeOff
              Dados que decidem jogos
              credenciais invalidas
              Entrando
              reset solicitado com sucesso
              token inválido/expirado
              senha redefinida com sucesso
              <button disabled={!email || !password || isPending}>Entrar</button>
            </div>
          );
        }
        """,
        encoding="utf-8",
    )
    (frontend / "src" / "index.css").write_text(
        """
        :root {
          --font-base: Inter;
          --font-display: Manrope;
          --font-mono: JetBrains Mono;
          --brand-500: #123456;
          --gray-500: #222222;
          --success-500: #00aa55;
          --error-500: #cc0033;
          --warning-500: #ffaa00;
          --orange-500: #ff6600;
          --court: #e5f7ff;
          --goal-area: #d8efff;
          --shot-success: #008844;
          --shot-miss: #cc3300;
          --save: #2255ff;
          --turnover: #663300;
          --load-deficit: #ffaa00;
          --load-optimal: #00aa55;
          --load-excess: #cc0033;
        }
        .dark\\:app-shell {}
        @media (prefers-color-scheme: dark) {}
        """,
        encoding="utf-8",
    )
    (frontend / "index.html").write_text(
        '<link rel="icon" href="/generated/images/hbicon.ico" />\n',
        encoding="utf-8",
    )

    result = gates._g_frontend_contract(tmp_path)

    assert result["status"] == "PASS"


def test_frontend_contract_gate_detects_missing_runtime_readiness(tmp_path):
    canon = tmp_path / "docs" / "_canon"
    canon.mkdir(parents=True)
    for name in (
        "UX_BRAND_CONTRACT.md",
        "UX_SHELL_CONTRACT.md",
        "AUTH_EXPERIENCE_CONTRACT.md",
        "NAVIGATION_VISIBILITY_CONTRACT.md",
    ):
        (canon / name).write_text("# canon\n", encoding="utf-8")
    (canon / "FRONTEND_CONTRACT.md").write_text(
        "\n".join(
            [
                "docs/_canon/UX_BRAND_CONTRACT.md",
                "docs/_canon/UX_SHELL_CONTRACT.md",
                "docs/_canon/AUTH_EXPERIENCE_CONTRACT.md",
                "docs/_canon/NAVIGATION_VISIBILITY_CONTRACT.md",
            ]
        ),
        encoding="utf-8",
    )

    images = tmp_path / "generated" / "images"
    images.mkdir(parents=True)
    for name in (
        "logo.svg",
        "logo-dark.svg",
        "logo-icon.svg",
        "logo-icon-dark.svg",
        "auth-logo.svg",
        "auth-logo-dark.svg",
        "hbicon.ico",
    ):
        (images / name).write_text("asset\n", encoding="utf-8")

    frontend = tmp_path / "frontend"
    (frontend / "src" / "api" / "hooks").mkdir(parents=True)
    (frontend / "src" / "shared" / "layouts").mkdir(parents=True)
    (frontend / "src" / "features" / "auth" / "pages").mkdir(parents=True)
    (frontend / "package.json").write_text(json.dumps({"scripts": {"api:generate": "npm run api:generate"}}), encoding="utf-8")
    (frontend / "src" / "api" / "schema.d.ts").write_text("// generated\n", encoding="utf-8")
    (frontend / "src" / "App.tsx").write_text("export default function App() { return null }\n", encoding="utf-8")
    (frontend / "src" / "shared" / "layouts" / "AppShell.tsx").write_text(
        "<aside></aside><header></header><main></main> generated/images/logo.svg Escape\n",
        encoding="utf-8",
    )
    (frontend / "src" / "features" / "auth" / "pages" / "LoginPage.tsx").write_text(
        "generated/images/auth-logo.svg generated/images/auth-logo-dark.svg Dados que decidem jogos Esqueceu a senha?\n",
        encoding="utf-8",
    )
    (frontend / "src" / "index.css").write_text("Inter Manrope JetBrains Mono brand- gray- success- error- warning- orange- court dark:\n", encoding="utf-8")
    (frontend / "index.html").write_text('<link rel="icon" href="/generated/images/hbicon.ico" />\n', encoding="utf-8")

    result = gates._g_frontend_contract(tmp_path)

    assert result["status"] == "FAIL"
    messages = " ".join(item["message"] for item in result.get("violations", []))
    assert "Resend" in messages or "FRONTEND_URL" in messages
    assert "identity_access" in messages


def test_waiver_engine_accepts_valid_waiver(tmp_path, monkeypatch):
    baseline_dir = tmp_path / "contracts" / "openapi" / "baseline"
    baseline_dir.mkdir(parents=True)
    (baseline_dir / "openapi_baseline.json").write_text(
        json.dumps(
            {
                "openapi": "3.1.0",
                "paths": {
                    "/sessions": {
                        "get": {
                            "operationId": "listSessions",
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    openapi_dir = tmp_path / "contracts" / "openapi"
    (openapi_dir / "openapi.yaml").write_text("openapi: 3.1.0\npaths: {}\n", encoding="utf-8")

    waivers_dir = tmp_path / "contracts" / "_waivers"
    waivers_dir.mkdir(parents=True)
    expiry = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).isoformat()
    (waivers_dir / "test_waiver.json").write_text(
        json.dumps(
            {
                "gate_id": "CONTRACT_BREAKING_CHANGE_GATE",
                "expires_at_utc": expiry,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.delenv("CI", raising=False)
    original_which = gates.shutil.which
    monkeypatch.setattr(
        gates.shutil,
        "which",
        lambda name: None if name == "oasdiff" else original_which(name),
    )

    result = gates._g9_contract_breaking_change(tmp_path)

    assert result["status"] == "PASS"
    assert "waiver ativo" in result["summary"].lower()


def test_shadow_authority_detects_docs_guias_without_disclaimer(tmp_path):
    guias = tmp_path / "docs" / "guias"
    guias.mkdir(parents=True)
    (guias / "BAD_GUIDE.md").write_text(
        "# Guia\n> SSOT para decisões futuras.\n",
        encoding="utf-8",
    )

    result = gates._g2k_shadow_authority(tmp_path)

    assert result["status"] == "FAIL"
    assert any("docs/guias/BAD_GUIDE.md" in str(item) for item in result.get("violations", []))


def test_canon_does_not_delegate_to_guias_or_missing_environment_doc():
    system_scope = Path("docs/_canon/SYSTEM_SCOPE.md").read_text(encoding="utf-8")
    global_invariants = Path("docs/_canon/GLOBAL_INVARIANTS.md").read_text(encoding="utf-8")
    architecture = Path("docs/_canon/ARCHITECTURE.md").read_text(encoding="utf-8")

    assert "docs/guias/IDENTITY_RBAC.md" not in system_scope
    assert "docs/guias/MVP_SCOPE.md" not in global_invariants
    assert "docs/_canon/contratos/Ambiente.md" not in architecture


def test_non_sovereign_roots_have_readme_disclaimers():
    assert Path("docs/guias/README.md").exists()
    assert Path("_reports/README.md").exists()


# ---------------------------------------------------------------------------
# Testes de regressão: OPENAPI_ROOT_STRUCTURE_GATE respeita waiver ativo
# ---------------------------------------------------------------------------

def _setup_openapi_root(tmp_path: Path) -> None:
    """Cria estrutura mínima para que _g5_openapi_root_structure não retorne skip."""
    openapi_dir = tmp_path / "contracts" / "openapi"
    openapi_dir.mkdir(parents=True)
    (openapi_dir / "openapi.yaml").write_text("openapi: 3.1.0\npaths: {}\n", encoding="utf-8")


def _write_waiver(tmp_path: Path, expires_at_utc: str) -> None:
    waivers_dir = tmp_path / "contracts" / "_waivers"
    waivers_dir.mkdir(parents=True)
    (waivers_dir / "OPENAPI_ROOT_STRUCTURE_GATE_test.json").write_text(
        json.dumps({
            "gate_id": "OPENAPI_ROOT_STRUCTURE_GATE",
            "scope": "system",
            "module": None,
            "expires_at_utc": expires_at_utc,
        }),
        encoding="utf-8",
    )


def test_openapi_root_waiver_absent_keeps_gate_failing(tmp_path, monkeypatch):
    """Sem waiver → lint falha → gate deve retornar FAIL."""
    _setup_openapi_root(tmp_path)
    monkeypatch.setattr(gates, "_try_node_cli", lambda *a, **kw: (1, "Error: lint failed", ""))

    result = gates._g5_openapi_root_structure(tmp_path)

    assert result["status"] == "FAIL"


def test_openapi_root_waiver_active_converts_redocly_failure_to_pass(tmp_path, monkeypatch):
    """Waiver ativo (expiry futuro) → lint falha → gate deve retornar PASS."""
    _setup_openapi_root(tmp_path)
    future = (
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_waiver(tmp_path, future)
    monkeypatch.setattr(gates, "_try_node_cli", lambda *a, **kw: (1, "Error: lint failed", ""))

    result = gates._g5_openapi_root_structure(tmp_path)

    assert result["status"] == "PASS"
    assert "waiver" in result["summary"].lower()


def test_openapi_root_waiver_expired_keeps_gate_failing(tmp_path, monkeypatch):
    """Waiver expirado → lint falha → gate deve retornar FAIL."""
    _setup_openapi_root(tmp_path)
    past = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_waiver(tmp_path, past)
    monkeypatch.setattr(gates, "_try_node_cli", lambda *a, **kw: (1, "Error: lint failed", ""))

    result = gates._g5_openapi_root_structure(tmp_path)

    assert result["status"] == "FAIL"
