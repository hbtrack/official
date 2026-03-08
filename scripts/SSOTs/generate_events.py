import os
import re
import sys
import yaml
import json
import jsonschema
from pathlib import Path

def parse_markdown_to_dict(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {
        "module": re.search(r"Módulo: <(.*?)>|Módulo: (.*?)\n", content).group(2).strip() or "unknown",
        "version": re.search(r"Versão: v(.*?) |Versão: (.*?)\n", content).group(2).strip() or "0.1.0",
        "status": "draft_normativo", # Default do template
        "aggregate_root": {
            "type": re.search(r"Aggregate root principal do módulo:\n\n`(.*?)`", content).group(1),
            "id_type": "uuid" # Padrão do sistema
        },
        "event_store": {
            "required_fields": ["event_id", "event_type", "event_version", "aggregate_type", "aggregate_id", "occurred_at", "actor_user_id", "payload"]
        },
        "events": []
    }

    # Regex para capturar os blocos de eventos ### EVT-
    event_blocks = re.findall(r"### EVT-.*? --- (.*?)\n(.*?)(?=\n### EVT-|## 4\) Regras)", content, re.DOTALL)

    for name, block in event_blocks:
        event = {
            "name": name.strip(),
            "event_version": 1,
            "aggregate_type": re.search(r"Aggregate:\n`(.*?)`", block).group(1),
            "trigger": re.search(r"Trigger:\n`(.*?)`", block).group(1),
            "description": re.search(r"Descrição:\n(.*?)\n", block).group(1).strip(),
            "emission_mode": "sync" if "síncrona" in re.search(r"Emissão:\n- (.*?)\n", block).group(1) else "async",
            "transactional": "não pode ser emitido em caso de rollback" in block,
            "payload": {"required": {}, "optional": {}},
            "relations": {"contracts": [], "flows": [], "invariants": []},
            "consumers": []
        }

        # Parsing de Payload
        req_payload = re.search(r"Payload mínimo:\n(.*?)\n\n", block, re.DOTALL)
        if req_payload:
            for line in req_payload.group(1).split('\n'):
                m = re.match(r"- `(.*?)`: `(.*?)`", line.strip())
                if m: event["payload"]["required"][m.group(1)] = m.group(2)

        # Parsing de Consumers
        consumers = re.search(r"Consumidores previstos:\n(.*?)(?=\n\n|$)", block, re.DOTALL)
        if consumers:
            event["consumers"] = [c.strip("- ").strip() for c in consumers.group(1).split('\n') if c.strip()]

        data["events"].append(event)

    return data

def main():
    # Caminhos Fixos do Pipeline
    INPUT_TEMPLATE = Path("docs/_templates/specs/runtime/EVENTS_MODULE.template.md")
    SCHEMA_PATH = Path("docs/_templates/specs/validation/EVENTS_MODULE.schema.json")
    
    if not INPUT_TEMPLATE.exists():
        print(f"❌ Erro: Template não encontrado em {INPUT_TEMPLATE}")
        sys.exit(1)

    # 1. Parsing
    print(f"🔄 Lendo spec Markdown...")
    try:
        event_data = parse_markdown_to_dict(INPUT_TEMPLATE)
    except Exception as e:
        print(f"❌ Erro no parsing do Markdown: {e}")
        sys.exit(1)

    # 2. Validação contra Schema
    print(f"⚖️ Validando contra JSON Schema...")
    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)

    try:
        jsonschema.validate(instance=event_data, schema=schema)
        print("✅ Validação PASS")
    except jsonschema.exceptions.ValidationError as err:
        print(f"🛑 FAILED: Erro de validação na Spec:\n{err.message}")
        sys.exit(1)

    # 3. Geração do YAML
    module_name = event_data["module"].upper()
    output_dir = Path(f"docs/hbtrack/modulos/{module_name.lower()}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"EVENTS_{module_name}.yaml"

    with open(output_file, 'w', encoding='utf-8') as yf:
        yaml.dump(event_data, yf, sort_keys=False, allow_unicode=True)

    print(f"🚀 Sucesso! YAML gerado em: {output_file}")

if __name__ == "__main__":
    main()