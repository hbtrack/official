import os
import re
import sys
import yaml
import json
import jsonschema
from pathlib import Path

def parse_errors_markdown(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extração de Metadados
    module_match = re.search(r"Módulo: (.*?)\n", content)
    version_match = re.search(r"Versão: (.*?)\n", content)
    status_match = re.search(r"Status: (.*?)\n", content)

    data = {
        "module": module_match.group(1).strip() if module_match else "UNKNOWN",
        "version": version_match.group(1).strip() if version_match else "0.1.0",
        "status": status_match.group(1).strip() if status_match else "DRAFT_NORMATIVO",
        "errors": []
    }

    # Regex para capturar blocos de erros ### ERR-
    # Captura o Código, e o corpo do bloco
    error_blocks = re.findall(r"### ERR-.*? — (.*?)\n(.*?)(?=\n### ERR-|## 2\) Critérios)", content, re.DOTALL)

    for code_name, block in error_blocks:
        # Parsing de campos internos do bloco
        http_match = re.search(r"HTTP sugerido:\n`(.*?)`", block)
        desc_match = re.search(r"Descrição:\n(.*?)\n", block)
        cmd_match = re.search(r"- comando: `(.*?)`", block)
        inv_match = re.search(r"- invariante: `(.*?)`", block)
        con_match = re.search(r"- contrato: `(.*?)`", block)
        ux_match = re.search(r"Mensagem UX sugerida:\n`(.*?)`", block)

        error_entry = {
            "code": code_name.strip(),
            "http_status": int(http_match.group(1)) if http_match else 422,
            "description": desc_match.group(1).strip() if desc_match else "",
            "origin": {
                "command": cmd_match.group(1).strip() if cmd_match else "N/A",
                "invariant": inv_match.group(1).strip() if inv_match else "N/A",
                "contract": con_match.group(1).strip() if con_match else "N/A"
            },
            "payload": ["code", "message", "details"], # Default conforme template
            "ux_message": ux_match.group(1).strip() if ux_match else ""
        }
        data["errors"].append(error_entry)

    return data

def run_pipeline():
    # Definição de caminhos baseada na estrutura do projeto
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    TEMPLATE_PATH = BASE_DIR / "docs/_templates/specs/runtime"
    SCHEMA_PATH = BASE_DIR / "docs/_templates/specs/validation/ERROS_MODULE.schema.json"
    
    # Busca por arquivos de template que casem com o padrão
    templates = list(TEMPLATE_PATH.glob("ERRORS_*.template.md"))
    
    if not templates:
        print("⚠️ Nenhum template de erro encontrado.")
        return

    # Carregar Schema
    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)

    for template in templates:
        print(f"🔄 Processando: {template.name}")
        
        try:
            # 1. Parse
            error_data = parse_errors_markdown(template)
            
            # 2. Validate
            jsonschema.validate(instance=error_data, schema=schema)
            print(f"✅ Validação PASS para {template.name}")
            
            # 3. Export YAML
            module_name = error_data["module"].lower()
            output_dir = BASE_DIR / f"docs/hbtrack/modulos/{module_name}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"ERROS_{module_name.upper()}.yaml"
            
            with open(output_file, 'w', encoding='utf-8') as yf:
                yaml.dump(error_data, yf, sort_keys=False, allow_unicode=True)
            
            print(f"🚀 YAML gerado: {output_file}")
            
        except Exception as e:
            print(f"🛑 FAILED BUILD: {template.name} violou o contrato ou falhou no parsing.")
            print(f"Erro: {str(e)}")
            sys.exit(1) # Cancela a build

if __name__ == "__main__":
    run_pipeline()