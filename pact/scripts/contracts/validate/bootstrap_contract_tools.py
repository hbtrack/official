"""
HB Track — bootstrap_contract_tools.py

Bootstrap de Sanidade: garante que as ferramentas de validação de contratos estejam
disponíveis antes de qualquer claim de conformidade.

Filosofia:
- "In God we trust; all others must bring data." (W. Edwards Deming)
- O que não é provado pelo compilador, não existe.
- Infraestrutura É Política (Infrastructure as Policy).

Este script:
1. Verifica a presença de Node.js, npm, Go
2. Verifica/instala Redocly CLI, Spectral CLI, oasdiff
3. Valida versões mínimas
4. Gera relatório machine-readable de status das ferramentas
5. Exit codes determinísticos:
   - 0: Todas as ferramentas disponíveis e validadas
   - 1: Ferramentas ausentes mas instalação possível
   - 2: Ferramentas críticas ausentes e instalação falhou
   - 3: Sistema não suporta instalação automática

Blocking codes:
  ERROR_INFRA_NODEJS_MISSING
  ERROR_INFRA_NPM_MISSING
  ERROR_INFRA_GO_MISSING
  ERROR_INFRA_REDOCLY_MISSING
  ERROR_INFRA_SPECTRAL_MISSING
  ERROR_INFRA_OASDIFF_MISSING
  ERROR_INFRA_AUTO_INSTALL_FAILED
"""

from __future__ import annotations

import json
import pathlib
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from typing import Literal


@dataclass
class ToolStatus:
    """Status de uma ferramenta de validação."""
    tool_name: str
    available: bool
    version: str | None
    path: str | None
    install_command: str | None
    blocking_code: str | None
    message: str


@dataclass
class BootstrapReport:
    """Relatório machine-readable do bootstrap."""
    timestamp_utc: str
    system: str
    python_version: str
    status: Literal["READY", "PARTIAL", "BLOCKED"]
    exit_code: int
    tools: list[ToolStatus]
    critical_missing: list[str]
    auto_install_attempted: bool
    auto_install_success: bool
    summary: str


def _run_command(cmd: list[str], check: bool = False, timeout: int = 30) -> tuple[int, str, str]:
    """Executa comando e retorna (returncode, stdout, stderr)."""
    try:
        # No Windows, usa shell=True para herdar PATH completo do PowerShell
        use_shell = platform.system() == "Windows"
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check,
            shell=use_shell,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"Comando não encontrado: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return -2, "", f"Timeout executando: {' '.join(cmd)}"
    except Exception as e:
        return -3, "", str(e)


def _check_nodejs() -> ToolStatus:
    """Verifica Node.js."""
    rc, stdout, stderr = _run_command(["node", "--version"])
    if rc == 0:
        version = stdout.strip()
        path_result = shutil.which("node")
        return ToolStatus(
            tool_name="node",
            available=True,
            version=version,
            path=path_result,
            install_command=None,
            blocking_code=None,
            message=f"Node.js {version} disponível."
        )
    
    install_msg = (
        "Windows: baixe em https://nodejs.org/\n"
        "Linux: sudo apt install nodejs npm (Debian/Ubuntu) ou yum install nodejs npm (RHEL/CentOS)\n"
        "macOS: brew install node"
    )
    return ToolStatus(
        tool_name="node",
        available=False,
        version=None,
        path=None,
        install_command=install_msg,
        blocking_code="ERROR_INFRA_NODEJS_MISSING",
        message="Node.js não encontrado. Instalação manual necessária."
    )


def _check_npm() -> ToolStatus:
    """Verifica npm."""
    rc, stdout, stderr = _run_command(["npm", "--version"])
    if rc == 0:
        version = stdout.strip()
        path_result = shutil.which("npm")
        return ToolStatus(
            tool_name="npm",
            available=True,
            version=version,
            path=path_result,
            install_command=None,
            blocking_code=None,
            message=f"npm {version} disponível."
        )
    
    return ToolStatus(
        tool_name="npm",
        available=False,
        version=None,
        path=None,
        install_command="Instalado com Node.js (https://nodejs.org/)",
        blocking_code="ERROR_INFRA_NPM_MISSING",
        message="npm não encontrado. Instalação manual necessária."
    )


def _check_go() -> ToolStatus:
    """Verifica Go."""
    rc, stdout, stderr = _run_command(["go", "version"])
    if rc == 0:
        version = stdout.strip()
        path_result = shutil.which("go")
        return ToolStatus(
            tool_name="go",
            available=True,
            version=version,
            path=path_result,
            install_command=None,
            blocking_code=None,
            message=f"Go disponível: {version}."
        )
    
    install_msg = (
        "Windows: baixe em https://go.dev/dl/\n"
        "Linux: sudo apt install golang-go (Debian/Ubuntu)\n"
        "macOS: brew install go"
    )
    return ToolStatus(
        tool_name="go",
        available=False,
        version=None,
        path=None,
        install_command=install_msg,
        blocking_code="ERROR_INFRA_GO_MISSING",
        message="Go não encontrado. Instalação manual necessária para oasdiff."
    )


def _check_redocly(npm_available: bool) -> ToolStatus:
    """Verifica Redocly CLI."""
    rc, stdout, stderr = _run_command(["redocly", "--version"])
    if rc == 0:
        version = stdout.strip()
        path_result = shutil.which("redocly")
        return ToolStatus(
            tool_name="redocly",
            available=True,
            version=version,
            path=path_result,
            install_command=None,
            blocking_code=None,
            message=f"Redocly CLI {version} disponível."
        )
    
    install_cmd = "npm install -g @redocly/cli" if npm_available else "npm não disponível"
    return ToolStatus(
        tool_name="redocly",
        available=False,
        version=None,
        path=None,
        install_command=install_cmd,
        blocking_code="ERROR_INFRA_REDOCLY_MISSING",
        message="Redocly CLI não encontrado."
    )


def _check_spectral(npm_available: bool) -> ToolStatus:
    """Verifica Spectral CLI."""
    rc, stdout, stderr = _run_command(["spectral", "--version"])
    if rc == 0:
        version = stdout.strip()
        path_result = shutil.which("spectral")
        return ToolStatus(
            tool_name="spectral",
            available=True,
            version=version,
            path=path_result,
            install_command=None,
            blocking_code=None,
            message=f"Spectral CLI {version} disponível."
        )
    
    install_cmd = "npm install -g @stoplight/spectral-cli" if npm_available else "npm não disponível"
    return ToolStatus(
        tool_name="spectral",
        available=False,
        version=None,
        path=None,
        install_command=install_cmd,
        blocking_code="ERROR_INFRA_SPECTRAL_MISSING",
        message="Spectral CLI não encontrado."
    )


def _check_oasdiff(go_available: bool) -> ToolStatus:
    """Verifica oasdiff."""
    # Tenta comando help (não existe comando version no oasdiff)
    rc, stdout, stderr = _run_command(["oasdiff", "--help"])
    if rc == 0 or "Usage:" in stdout or "Usage:" in stderr:
        # oasdiff está disponível
        output = stdout + stderr
        # Extrai versão se disponível, ou usa "installed"
        version_line = [ln for ln in output.splitlines() if "version" in ln.lower()]
        version = version_line[0].strip() if version_line else "installed"
        path_result = shutil.which("oasdiff")
        
        # No Windows, pode estar em GOPATH/bin sem estar no shutil.which
        if not path_result and platform.system() == "Windows":
            gopath_rc, gopath_out, _ = _run_command(["go", "env", "GOPATH"])
            if gopath_rc == 0:
                gopath = gopath_out.strip()
                oasdiff_path = pathlib.Path(gopath) / "bin" / "oasdiff.exe"
                if oasdiff_path.exists():
                    path_result = str(oasdiff_path)
        
        return ToolStatus(
            tool_name="oasdiff",
            available=True,
            version=version,
            path=path_result,
            install_command=None,
            blocking_code=None,
            message=f"oasdiff disponível: {version}."
        )
    
    install_cmd = "go install github.com/oasdiff/oasdiff@latest" if go_available else "Go não disponível"
    return ToolStatus(
        tool_name="oasdiff",
        available=False,
        version=None,
        path=None,
        install_command=install_cmd,
        blocking_code="ERROR_INFRA_OASDIFF_MISSING",
        message="oasdiff não encontrado."
    )


def _try_auto_install(tool: ToolStatus, runtime_env: dict) -> tuple[bool, str]:
    """
    Tenta instalação automática se possível.
    Retorna (sucesso, mensagem).
    """
    if tool.available or not tool.install_command:
        return True, "Já disponível ou sem comando de instalação."
    
    # Bloqueia instalação automática se não temos npm/go
    if tool.tool_name in ["redocly", "spectral"] and not runtime_env.get("npm_available"):
        return False, "npm não disponível para instalação."
    
    if tool.tool_name == "oasdiff" and not runtime_env.get("go_available"):
        return False, "Go não disponível para instalação."
    
    # Executa instalação
    if tool.tool_name == "redocly":
        print(f"→ Instalando {tool.tool_name}...")
        rc, stdout, stderr = _run_command(["npm", "install", "-g", "@redocly/cli"], timeout=120)
        if rc == 0:
            return True, "Instalação concluída."
        return False, f"Instalação falhou: {stderr}"
    
    if tool.tool_name == "spectral":
        print(f"→ Instalando {tool.tool_name}...")
        rc, stdout, stderr = _run_command(["npm", "install", "-g", "@stoplight/spectral-cli"], timeout=120)
        if rc == 0:
            return True, "Instalação concluída."
        return False, f"Instalação falhou: {stderr}"
    
    if tool.tool_name == "oasdiff":
        print(f"→ Instalando {tool.tool_name}...")
        # Path correto mudou de tufin/oasdiff para oasdiff/oasdiff
        rc, stdout, stderr = _run_command(["go", "install", "github.com/oasdiff/oasdiff@latest"], timeout=120)
        if rc == 0:
            # oasdiff é instalado em $GOPATH/bin, pode não estar no PATH
            gopath_rc, gopath_out, _ = _run_command(["go", "env", "GOPATH"])
            if gopath_rc == 0:
                gopath = gopath_out.strip()
                oasdiff_path = pathlib.Path(gopath) / "bin" / "oasdiff"
                if platform.system() == "Windows":
                    oasdiff_path = pathlib.Path(gopath) / "bin" / "oasdiff.exe"
                if oasdiff_path.exists():
                    return True, f"Instalação concluída em {oasdiff_path}. Adicione $GOPATH/bin ao PATH."
            return True, "Instalação concluída (verifique $GOPATH/bin no PATH)."
        return False, f"Instalação falhou: {stderr}"
    
    return False, "Ferramenta não suporta instalação automática."


def run_bootstrap(
    auto_install: bool = False,
    output_file: pathlib.Path | None = None,
) -> BootstrapReport:
    """
    Executa o bootstrap de sanidade das ferramentas de contrato.
    
    Args:
        auto_install: Se True, tenta instalar ferramentas ausentes automaticamente.
        output_file: Caminho para salvar relatório JSON.
    
    Returns:
        BootstrapReport com status detalhado.
    """
    print("=== HB Track: Bootstrap de Sanidade — Contract Tools ===\n")
    
    # 1. Verifica runtimes base (Node.js, npm, Go)
    print("→ Verificando runtimes base...")
    node_status = _check_nodejs()
    npm_status = _check_npm()
    go_status = _check_go()
    
    runtime_env = {
        "npm_available": npm_status.available,
        "go_available": go_status.available,
    }
    
    # 2. Verifica ferramentas de validação
    print("→ Verificando ferramentas de validação...")
    redocly_status = _check_redocly(runtime_env["npm_available"])
    spectral_status = _check_spectral(runtime_env["npm_available"])
    oasdiff_status = _check_oasdiff(runtime_env["go_available"])
    
    tools = [
        node_status,
        npm_status,
        go_status,
        redocly_status,
        spectral_status,
        oasdiff_status,
    ]
    
    # 3. Identifica ferramentas críticas ausentes
    critical_tools = ["node", "npm", "redocly", "spectral", "oasdiff"]
    critical_missing = [t.tool_name for t in tools if t.tool_name in critical_tools and not t.available]
    
    # 4. Tentativa de instalação automática (se habilitada)
    auto_install_attempted = False
    auto_install_success = True
    
    if auto_install and critical_missing:
        print("\n→ Tentando instalação automática das ferramentas ausentes...")
        auto_install_attempted = True
        
        # Re-verifica após tentativa de instalação
        for i, tool in enumerate(tools):
            if not tool.available and tool.tool_name in ["redocly", "spectral", "oasdiff"]:
                success, msg = _try_auto_install(tool, runtime_env)
                if not success:
                    auto_install_success = False
                    print(f"  ✗ {tool.tool_name}: {msg}")
                else:
                    print(f"  ✓ {tool.tool_name}: {msg}")
                    # Re-verifica disponibilidade
                    if tool.tool_name == "redocly":
                        tools[i] = _check_redocly(runtime_env["npm_available"])
                    elif tool.tool_name == "spectral":
                        tools[i] = _check_spectral(runtime_env["npm_available"])
                    elif tool.tool_name == "oasdiff":
                        tools[i] = _check_oasdiff(runtime_env["go_available"])
        
        # Re-calcula ferramentas ausentes
        critical_missing = [t.tool_name for t in tools if t.tool_name in critical_tools and not t.available]
    
    # 5. Determina status final
    if not critical_missing:
        status = "READY"
        exit_code = 0
        summary = "✓ Todas as ferramentas críticas disponíveis. Sistema pronto para validação de contratos."
    elif not node_status.available or not npm_status.available:
        status = "BLOCKED"
        exit_code = 3
        summary = f"✗ Node.js/npm ausentes. Instalação manual necessária. Ferramentas faltando: {', '.join(critical_missing)}"
    elif critical_missing:
        status = "PARTIAL"
        exit_code = 1 if not auto_install_attempted else 2
        summary = f"⚠ Ferramentas ausentes: {', '.join(critical_missing)}. Instalação necessária."
    else:
        status = "READY"
        exit_code = 0
        summary = "✓ Sistema pronto."
    
    # 6. Gera relatório
    report = BootstrapReport(
        timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        system=platform.system(),
        python_version=platform.python_version(),
        status=status,
        exit_code=exit_code,
        tools=tools,
        critical_missing=critical_missing,
        auto_install_attempted=auto_install_attempted,
        auto_install_success=auto_install_success,
        summary=summary,
    )
    
    # 7. Salva relatório se solicitado
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, indent=2, default=str)
        print(f"\n→ Relatório salvo em: {output_file}")
    
    # 8. Exibe resumo
    print("\n" + "=" * 60)
    print(f"Status: {status}")
    print(f"Exit Code: {exit_code}")
    print(f"\n{summary}")
    print("=" * 60)
    
    if critical_missing:
        print("\n⚠ FERRAMENTAS AUSENTES:")
        for tool_name in critical_missing:
            tool = next(t for t in tools if t.tool_name == tool_name)
            print(f"\n  • {tool.tool_name}")
            print(f"    Blocking Code: {tool.blocking_code}")
            if tool.install_command:
                print(f"    Instalação: {tool.install_command}")
    
    return report


def main():
    """Entry point CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Bootstrap de Sanidade: valida presença de ferramentas de validação de contratos."
    )
    parser.add_argument(
        "--auto-install",
        action="store_true",
        help="Tenta instalar ferramentas ausentes automaticamente.",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("_reports") / "contract_gates" / "bootstrap.json",
        help="Caminho para salvar relatório JSON (padrão: _reports/contract_gates/bootstrap.json).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Exibe apenas o JSON do relatório (suprime logs).",
    )
    
    args = parser.parse_args()
    
    if args.json:
        # Modo silencioso: redireciona print para stderr temporariamente
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            report = run_bootstrap(auto_install=args.auto_install, output_file=args.output)
        
        print(json.dumps(asdict(report), indent=2, default=str))
    else:
        report = run_bootstrap(auto_install=args.auto_install, output_file=args.output)
    
    sys.exit(report.exit_code)


if __name__ == "__main__":
    main()
