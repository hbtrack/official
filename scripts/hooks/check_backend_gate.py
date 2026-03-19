#!/usr/bin/env python3
"""
PreToolUse Hook — HB Track Backend Gate
Bloqueia escrita em backend/apps/{module}/ se o módulo não estiver em
validated_contract ou implementation_ready no MODULE_REGISTRY.yaml.
Usa apenas stdlib (sem dependências externas).
"""
import json
import re
import sys
from pathlib import Path

ALLOWED_STATUSES = {"validated_contract", "implementation_ready"}
WRITE_TOOLS = {
    "editFiles",
    "replace_string_in_file",
    "multi_replace_string_in_file",
    "write_file",
    "create_file",
}
WORKSPACE = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = WORKSPACE / "docs/_canon/MODULE_REGISTRY.yaml"


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


def main():
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            sys.exit(0)

        event = json.loads(raw)
        tool_name = event.get("toolName", "")

        if tool_name not in WRITE_TOOLS:
            sys.exit(0)

        file_path = extract_file_path(event.get("toolInput", {}))
        if not file_path:
            sys.exit(0)

        # Só fiscaliza escritas em backend/apps/{module}/
        match = re.search(r"backend/apps/([^/]+)/", file_path)
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
                f"Código backend exige status 'validated_contract' ou 'implementation_ready'.\n\n"
                f"Sequência obrigatória antes de gerar código:\n"
                f"  1. Se draft_contract → promover para validated_contract (pipeline PASS)\n"
                f"  2. readiness_promotion → implementation_ready\n"
                f"  3. adversarial_analysis → ADVERSARIAL_ANALYSIS_GATE=PASS\n"
                f"  4. Somente então: generate_code\n\n"
                f"Comando para iniciar: python3 scripts/hb verify --task-type readiness_promotion --module {module}"
            )

        # Status OK — permite
        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)  # Não bloqueia em erro de parse
    except Exception as e:
        print(f"check_backend_gate warning: {e}", file=sys.stderr)
        sys.exit(0)  # Fail-open: não quebra o agente em erros do hook


if __name__ == "__main__":
    main()
