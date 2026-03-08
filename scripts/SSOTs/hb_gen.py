import yaml
import os
import sys
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# Configurações de Caminhos
TEMPLATE_DIR = Path("scripts/generate/templates")
MODULES_BASE_DIR = Path("app/modules")
SPECS_DIR = Path("docs/hbtrack/modulos")

# Mapeamento de Tipos (DSL -> Python)
TYPE_MAP = {
    "uuid": "UUID",
    "string": "str",
    "int": "int",
    "float": "float",
    "datetime": "datetime",
    "bool": "bool"
}

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_code(spec_type, module_name):
    """
    spec_type: 'commands', 'events' ou 'projections'
    module_name: nome do módulo (ex: 'training')
    """
    spec_file = SPECS_DIR / module_name / f"{spec_type.upper()}_{module_name.upper()}.yaml"
    
    if not spec_file.exists():
        print(f"⚠️  Aviso: Spec {spec_file} não encontrada. Ignorando...")
        return

    print(f"⚙️  Gerando {spec_type} para o módulo: {module_name.upper()}...")
    
    spec_data = load_yaml(spec_file)
    
    # Configurar Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    
    # Filtro personalizado para converter tipos da Spec para Python
    def py_type(value):
        return TYPE_MAP.get(value.lower(), value)
    env.filters['py_type'] = py_type

    # Selecionar template e destino
    template_map = {
        "commands": ("commands.jt2", f"app/modules/{module_name}/commands.py"),
        "events": ("events.jt2", f"app/modules/{module_name}/events/generated_events.py"),
        "projections": ("projections.jt2", f"app/modules/{module_name}/projections/stubs.py")
    }

    template_name, output_rel_path = template_map[spec_type]
    template = env.get_template(template_name)
    
    # Renderizar
    output_code = template.render(
        module=module_name,
        **spec_data
    )

    # Guardar ficheiro
    output_path = Path(output_rel_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_code)
    
    print(f"✅ Sucesso: {output_path} atualizado.")

def main():
    if len(sys.argv) < 2:
        print("Uso: python hb-gen.py <module_name>")
        sys.exit(1)

    target_module = sys.argv[1].lower()

    # Executa a geração para os três pilares
    generate_code("commands", target_module)
    generate_code("events", target_module)
    # generate_code("projections", target_module) # Ativar quando o template estiver pronto

if __name__ == "__main__":
    main()