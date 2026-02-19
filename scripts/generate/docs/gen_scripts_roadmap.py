#!/usr/bin/env python3
# HB_SCRIPT_KIND=GENERATE
# HB_SCRIPT_SCOPE=generate/docs
# HB_SCRIPT_SIDE_EFFECTS=FS_READ,FS_WRITE
# HB_SCRIPT_IDEMPOTENT=YES
# HB_SCRIPT_ENTRYPOINT=python scripts/generate/docs/gen_scripts_roadmap.py
# HB_SCRIPT_OUTPUTS=docs/hbtrack/_generated/scripts_roadmap.md
# HB_SCRIPT_INPUTS=scripts/scripts_roadmap.yaml
# HB_SCRIPT_RISK=LOW

import argparse
import sys
import hashlib
from pathlib import Path
import yaml

# Resolução dinâmica de caminhos a partir da localização do script (scripts/generate/docs/)
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
YAML_PATH = REPO_ROOT / "scripts" / "scripts_roadmap.yaml"
MD_PATH = REPO_ROOT / "docs" / "hbtrack" / "_generated" / "scripts_roadmap.md"

def load_ssot(yaml_path: Path) -> dict:
    """Carrega o arquivo YAML (SSOT)."""
    if not yaml_path.exists():
        print(f"ERRO: SSOT não encontrado em {yaml_path}")
        sys.exit(3) # HARNESS_ERROR
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_markdown(data: dict) -> str:
    """Renderiza o conteúdo do dicionário para uma string Markdown determinística."""
    md = []
    
    # Meta
    meta = data.get('meta', {})
    md.append(f"# {meta.get('title', 'Scripts Inventory')}\n")
    if 'description' in meta:
        desc_lines = meta['description'].strip().split('\n')
        for line in desc_lines:
            md.append(f"> {line}")
        md.append("\n")

    # Convenções
    conventions = data.get('conventions', {})
    if conventions:
        md.append("## Convenções do projeto\n")
        md.append("| Convenção | Valor |")
        md.append("|-----------|-------|")
        for key, value in conventions.items():
            formatted_key = key.replace('_', ' ').capitalize()
            # Formatação específica para Python runtime conforme o original
            if key == 'python_runtime':
                md.append(f"| **{formatted_key}** | {value} |")
            else:
                md.append(f"| {formatted_key} | {value} |")
        md.append("\n---\n")

    # Inventário
    inventory = data.get('inventory', [])
    for section in inventory:
        md.append(f"## {section.get('section')}\n")
        if 'description' in section and section['description']:
            md.append(f"{section['description']}\n")
        
        # Subseções
        for subsec in section.get('subsections', []):
            md.append(f"### {subsec.get('title')}\n")
            
            files = subsec.get('files', [])
            if not files:
                continue
            
            # Cabeçalho dinâmico da tabela baseado nas chaves presentes
            has_se = any(f.get('side_effects') for f in files)
            has_inputs = any(f.get('inputs') for f in files)
            has_outputs = any(f.get('outputs') for f in files)
            has_prereqs = any(f.get('prerequisites') for f in files)
            
            headers = ["Arquivo", "Descrição"]
            if has_se: headers.append("Side-effects")
            if has_inputs: headers.append("Entradas")
            if has_outputs: headers.append("Saídas/Evidência")
            if has_prereqs: headers.append("Pré-requisitos")
            
            md.append("| " + " | ".join(headers) + " |")
            md.append("|" + "|".join(["---" for _ in headers]) + "|")
            
            for file in files:
                row = [f"`{file.get('name')}`", file.get('description', '—')]
                if has_se: row.append(file.get('side_effects', '—') or '—')
                if has_inputs: row.append(file.get('inputs', '—') or '—')
                if has_outputs: row.append(file.get('outputs', '—') or '—')
                if has_prereqs: row.append(file.get('prerequisites', '—') or '—')
                md.append("| " + " | ".join(row) + " |")
            md.append("\n")

    return "\n".join(md).strip() + "\n"

def get_hash(content: str) -> str:
    """Gera hash SHA256 do conteúdo para verificação de integridade."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Gerador determinístico do inventário de scripts (SSOT -> MD).")
    parser.add_argument("--check", action="store_true", help="Apenas verifica se o MD atual corresponde ao SSOT. Não escreve no disco.")
    args = parser.parse_args()

    data = load_ssot(YAML_PATH)
    generated_md = generate_markdown(data)
    generated_hash = get_hash(generated_md)

    if args.check:
        if not MD_PATH.exists():
            print(f"FAIL: Arquivo derivado não encontrado em {MD_PATH}.")
            sys.exit(2) # VIOLATION/DRIFT
        
        current_md = MD_PATH.read_text(encoding='utf-8')
        current_hash = get_hash(current_md)
        
        if current_hash != generated_hash:
            print(f"FAIL: Drift detectado no arquivo {MD_PATH.name}.")
            print(f"Hash esperado (SSOT): {generated_hash}")
            print(f"Hash atual (Disco):  {current_hash}")
            print("VIOLATION: O arquivo foi editado manualmente ou está desatualizado. Execute o script sem a flag --check para regenerar.")
            sys.exit(2) # VIOLATION/DRIFT
        else:
            print(f"OK: Integridade validada. {MD_PATH.name} está perfeitamente sincronizado com o SSOT.")
            sys.exit(0) # OK
    else:
        # Garante que o diretório de destino exista
        MD_PATH.parent.mkdir(parents=True, exist_ok=True)
        MD_PATH.write_text(generated_md, encoding='utf-8')
        print(f"SUCCESS: Artefato derivado gerado em {MD_PATH}")
        sys.exit(0)

if __name__ == "__main__":
    main()