import os
import re
import sys
import yaml
import json
import jsonschema
from pathlib import Path

def parse_commands_md(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {
        "module": re.search(r"Módulo: <(.*?)>|Módulo: (.*?)\n", content).group(2).strip().lower(),
        "version": re.search(r"Versão: v(.*?) |Versão: (.*?)\n", content).group(2).strip(),
        "commands": []
    }

    # Procura blocos ### CMD-
    cmd_blocks = re.findall(r"### CMD-.*? --- (.*?)\n(.*?)(?=\n### CMD-|## 4\) Regras)", content, re.DOTALL)

    for name, block in cmd_blocks:
        command = {
            "name": name.strip(),
            "trigger": re.search(r"Trigger:\n`(.*?)`", block).group(1),
            "description": re.search(r"Descrição:\n(.*?)\n", block).group(1).strip(),
            "payload": {},
            "auth_required": True
        }

        # Parsing de Payload do Comando
        payload_section = re.search(r"Payload esperado:\n(.*?)(?=\n\n|$)", block, re.DOTALL)
        if payload_section:
            for line in payload_section.group(1).split('\n'):
                m = re.match(r"- `(.*?)`: `(.*?)`", line.strip())
                if m: command["payload"][m.group(1)] = m.group(2)

        data["commands"].append(command)

    return data

def main():
    INPUT_MD = Path("docs/_templates/specs/runtime/COMMANDS_MODULE.template.md")
    SCHEMA_PATH = Path("docs/_templates/specs/validation/COMMANDS_MODULE.schema.json")
    
    if not INPUT_MD.exists():
        print(f"❌ Erro: Template de comandos não encontrado.")
        sys.exit(1)

    # 1. Parsing e Validação
    command_data = parse_commands_md(INPUT_MD)
    
    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)

    try:
        jsonschema.validate(instance=command_data, schema=schema)
        print("✅ Command Spec Valida")
    except jsonschema.exceptions.ValidationError as err:
        print(f"🛑 FAILED: Erro na spec de Comandos: {err.message}")
        sys.exit(1)

    # 2. Export YAML
    output_file = Path(f"docs/hbtrack/modulos/{command_data['module']}/COMMANDS_{command_data['module'].upper()}.yaml")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as yf:
        yaml.dump(command_data, yf, sort_keys=False, allow_unicode=True)
    
    print(f"🚀 YAML de Comandos gerado em: {output_file}")

if __name__ == "__main__":
    main()