#!/usr/bin/env python3
"""
PreToolUse Hook — HB Track Backend Gate
Bloqueia escrita em src/{module}/ se o módulo não estiver em
implementation_ready ou acima no MODULE_REGISTRY.yaml.
Usa apenas stdlib (sem dependências externas).
"""
import json
import re
import sys
from pathlib import Path

ALLOWED_STATUSES = {
    "implementation_ready",
    "implemented",
    "staging_validated",
    "released",
}
WRITE_TOOLS = {
    "editFiles",
    "replace_string_in_file",
    "multi_replace_string_in_file",
    "write_file",
    "create_file",
}
WORKSPACE = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = WORKSPACE / "docs/_canon/MODULE_REGISTRY.yaml"
ROADMAP_EXEMPT_PREFIXES = ("src/shared/",)
ROADMAP_EXEMPT_BASENAMES = {"tasks.py", "consumers.py", "middleware.py"}
INTERNAL_BLOCK_CODE = "BLOCKED_BACKEND_GATE_INTERNAL"


def get_module_status(module: str):
    """Extrai status do módulo direto do YAML via regex (sem PyYAML)."""
    try:
        text = REGISTRY_PATH.read_text()
        # Bloco do módulo: "  video:\n    status: \"draft_contract\""
        pattern = rf"(?m)^\s+{re.escape(module)}:\s*\n(?:.*\n)*?.*?status:\s*[\"']?(\w+)[\"']?"
        match = re.search(pattern, text)
        return match.group(1) if match else None
    except Exception:
        return None


def extract_file_path(tool_input: dict) -> str:
    """Extrai o caminho do arquivo do input do tool, independente do formato."""
    path = (
        tool_input.get("filePath")
        or tool_input.get("path")
        or ""
    )
    if not path:
        # multi_replace_string_in_file usa lista de replacements
        replacements = tool_input.get("replacements", [])
        if replacements and isinstance(replacements, list):
            path = replacements[0].get("filePath", "")
    return path or ""


def deny(reason: str):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(2)


def deny_internal(reason: str):
    deny(f"{INTERNAL_BLOCK_CODE}\n{reason}")


def main():
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            deny_internal("Evento do hook vazio ou ausente.")

        event = json.loads(raw)
        tool_name = event.get("toolName", "")

        if tool_name not in WRITE_TOOLS:
            sys.exit(0)

        file_path = extract_file_path(event.get("toolInput", {})).replace("\\", "/")
        if not file_path:
            sys.exit(0)

        if any(file_path.startswith(prefix) for prefix in ROADMAP_EXEMPT_PREFIXES):
            sys.exit(0)

        if Path(file_path).name in ROADMAP_EXEMPT_BASENAMES and file_path.startswith("src/"):
            sys.exit(0)

        # Só fiscaliza escritas em src/{module}/
        match = re.search(r"src/([^/]+)/", file_path)
        if not match:
            sys.exit(0)

        module = match.group(1)
        status = get_module_status(module)

        if status is None:
            deny(
                f"BLOCKED_MISSING_MODULE\n"
                f"Módulo '{module}' não existe em MODULE_REGISTRY.yaml.\n"
                f"Nenhum código backend pode ser criado para módulos não catalogados."
            )

        if status not in ALLOWED_STATUSES:
            deny(
                f"BLOCKED_REQUIRED_ARTIFACT_MISSING\n"
                f"Módulo '{module}' está em '{status}'.\n"
                f"Código backend exige status 'implementation_ready' ou superior.\n\n"
                f"Sequência obrigatória antes de gerar código:\n"
                f"  1. Se draft_contract → promover para validated_contract (pipeline PASS)\n"
                f"  2. readiness_promotion → implementation_ready\n"
                f"  3. adversarial_analysis → ADVERSARIAL_ANALYSIS_GATE=PASS\n"
                f"  4. Somente então: generate_code / evolução backend controlada\n\n"
                f"Comando para iniciar: python3 scripts/hb verify --task-type readiness_promotion --module {module}"
            )

        # Status OK — permite
        sys.exit(0)

    except json.JSONDecodeError as exc:
        deny_internal(f"Evento do hook inválido (JSON): {exc.msg}")
    except Exception as e:
        deny_internal(f"Erro interno no backend gate: {e}")


if __name__ == "__main__":
    main()
