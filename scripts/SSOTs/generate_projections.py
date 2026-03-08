import os
import re
import sys
import yaml
import json
import jsonschema
from pathlib import Path

def parse_projection_md(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extração de Metadados
    module_match = re.search(r"Módulo: <(.*?)>|Módulo: (.*?)\n", content)
    version_match = re.search(r"Versão: v(.*?) |Versão: (.*?)\n", content)
    
    data = {
        "module": (module_match.group(1) or module_match.group(2)).strip().lower() if module_match else "unknown",
        "version": (version_match.group(1) or version_match.group(2)).strip() if version_match else "0.1.0",
        "status": "draft_normativo",
        "projections": []
    }

    # Regex para capturar blocos ### PRJ-
    prj_blocks = re.findall(r"### PRJ-.*? --- (.*?)\n(.*?)(?=\n### PRJ-|## 3\) Regras)", content, re.DOTALL)

    for name, block in prj_blocks:
        projection = {
            "name": name.strip(),
            "description": re.search(r"Objetivo:\n(.*?)\n", block).group(1).strip() if "Objetivo:" in block else "",
            "source_events": [],
            "grain": re.search(r"Grão:\n- (.*?)\n", block).group(1).strip() if "Grão:" in block else "",
            "fields": [],
            "refresh_mode": "async",
            "consistency_model": "eventual",
            "storage_target": "table",
            "rebuild_strategy": {"full_rebuild": True, "incremental": True},
            "consumers": {"endpoints": [], "screens": [], "analytics": []}
        }

        # Parsing Source Events
        events = re.search(r"Source Events:\n(.*?)(?=\n\n|\n[A-Z])", block, re.DOTALL)
        if events:
            projection["source_events"] = [e.strip("- ").strip("`").strip() for e in events.group(1).split('\n') if e.strip()]

        # Parsing Fields
        fields_section = re.search(r"Campos:\n(.*?)(?=\n\n|\n[A-Z])", block, re.DOTALL)
        if fields_section:
            for line in fields_section.group(1).split('\n'):
                m = re.match(r"- `(.*?)`| - (.*?)$", line.strip())
                if m:
                    fname = (m.group(1) or m.group(2)).strip()
                    projection["fields"].append({"name": fname, "type": "unknown"})

        # Parsing Enums Técnicos
        rmode = re.search(r"Refresh Mode:\n`(.*?)`", block)
        if rmode: projection["refresh_mode"] = rmode.group(1).lower()

        cmodel = re.search(r"Consistency Model:\n`(.*?)`", block)
        if cmodel: projection["consistency_model"] = cmodel.group(1).lower()

        target = re.search(r"Storage Target:\n`(.*?)`", block)
        if target: projection["storage_target"] = target.group(1).lower()

        # Rebuild Strategy
        full_rb = re.search(r"full rebuild permitido\? (sim|não)", block)
        if full_rb: projection["rebuild_strategy"]["full_rebuild"] = full_rb.group(1) == "sim"

        # Parsing Consumers
        consumers_list = re.findall(r"- (endpoint|dashboard|tela) `<(.*?)>`|- (endpoint|dashboard|tela) (.*?)$", block)
        for ctype, cval, ctype2, cval2 in consumers_list:
            t = (ctype or ctype2)
            v = (cval or cval2).strip()
            if t == "endpoint": projection["consumers"]["endpoints"].append(v)
            elif t == "dashboard": projection["consumers"]["analytics"].append(v)
            elif t == "tela": projection["consumers"]["screens"].append(v)

        data["projections"].append(projection)

    return data

def main():
    INPUT_TEMPLATE = Path("docs/_templates/specs/runtime/PROJECTIONS_MODULE.template.md")
    SCHEMA_PATH = Path("docs/_templates/specs/validation/PROJECTIONS_MODULE.schema.json")
    
    if not INPUT_TEMPLATE.exists():
        print(f"❌ Erro: Template não encontrado em {INPUT_TEMPLATE}")
        sys.exit(1)

    print(f"🔄 Lendo spec de Projeções...")
    try:
        data = parse_projection_md(INPUT_TEMPLATE)
    except Exception as e:
        print(f"❌ Erro no parsing: {e}")
        sys.exit(1)

    print(f"⚖️ Validando contra JSON Schema...")
    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)

    try:
        jsonschema.validate(instance=data, schema=schema)
        print("✅ Validação PASS")
    except jsonschema.exceptions.ValidationError as err:
        print(f"🛑 FAILED: Erro na spec de Projeções:\n{err.message}")
        sys.exit(1)

    module_name = data["module"].upper()
    output_dir = Path(f"docs/hbtrack/modulos/{module_name.lower()}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"PROJECTIONS_{module_name}.yaml"

    with open(output_file, 'w', encoding='utf-8') as yf:
        yaml.dump(data, yf, sort_keys=False, allow_unicode=True)

    print(f"🚀 YAML de Projeções gerado: {output_file}")

if __name__ == "__main__":
    main()