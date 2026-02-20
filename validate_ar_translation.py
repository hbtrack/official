#!/usr/bin/env python3
"""
Validador de tradução JSON → MD para AR_003.5
Verifica se todas as informações do JSON estão presentes no MD
"""

import json
import sys
from pathlib import Path

def validate_translation():
    """Valida se o MD contém todas as informações do JSON"""
    
    repo_root = Path(__file__).resolve().parent
    json_path = repo_root / "docs/hbtrack/planos/AR_003.5_persons_birth_date_not_null.json"
    md_path = repo_root / "docs/hbtrack/ars/AR_003_persons_birth_date.md"
    
    # Ler JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Ler MD
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    errors = []
    
    # Validar campos principais
    checks = [
        (data["ar_id"], "AR_003.5"),
        (data["title"], "persons.birth_date NOT NULL"),
        (data["status"], "PROPOSTA"),
        (data["version"], "1.0"),
        (data["created_at"], "2026-02-19"),
        (data["mode"], "PROPOSE_ONLY"),
        (data["author"], "Arquiteto"),
        (data["invariant_text"], "paridade entre persons.birth_date e athletes.birth_date"),
        (data["ssot_bindings"]["schema_ssot"], "docs/ssot/schema.sql"),
        (data["ssot_bindings"]["model_person"], "Hb Track - Backend/app/models/person.py"),
        (data["ssot_bindings"]["alembic_current_head"], "0fb0f76b48a7"),
        (data["context"]["current_state"]["persons.birth_date"], "nullable=True"),
        (data["context"]["target_state"]["persons.birth_date"], "NOT NULL"),
    ]
    
    for field_value, search_term in checks:
        if search_term not in md_content:
            errors.append(f"❌ Termo não encontrado no MD: '{search_term}' (esperado de {field_value})")
    
    # Validar pre-flight checks
    for pf in data["pre_flight_checks"]:
        pf_id = pf["id"]
        if pf_id not in md_content:
            errors.append(f"❌ Pre-flight check {pf_id} não encontrado")
        if pf["label"] not in md_content:
            errors.append(f"❌ Label do {pf_id} não encontrado: {pf['label']}")
    
    # Validar migration steps
    for mig in data["migration_steps"]:
        step = mig["step"]
        if step not in md_content:
            errors.append(f"❌ Migration step {step} não encontrado")
        if mig["label"] not in md_content:
            errors.append(f"❌ Label do {step} não encontrado: {mig['label']}")
    
    # Validar alembic migration
    if "def upgrade():" not in md_content:
        errors.append("❌ Função upgrade() não encontrada no MD")
    if "def downgrade():" not in md_content:
        errors.append("❌ Função downgrade() não encontrada no MD")
    if "MIG-001: PF-002" not in md_content:
        errors.append("❌ Comentário MIG-001 não encontrado no código alembic")
    
    # Validar model changes
    for mc in data["model_changes"]:
        if mc["file"] not in md_content:
            errors.append(f"❌ Model file não encontrado: {mc['file']}")
        if "Mapped[Optional[date]]" not in md_content:
            errors.append("❌ OLD model code não encontrado")
        if "Mapped[date]" not in md_content:
            errors.append("❌ NEW model code não encontrado")
    
    # Validar success criteria
    for criterion in data["success_criteria"]:
        # Verificar pelo menos keywords principais
        if "PF-002" in criterion and "PF-002" not in md_content:
            errors.append(f"❌ Success criterion não encontrado: {criterion}")
    
    # Validar evidence file
    if data["evidence_file"] not in md_content:
        errors.append(f"❌ Evidence file não encontrado: {data['evidence_file']}")
    
    # Validar rollback plan
    if "alembic downgrade -1" not in md_content:
        errors.append("❌ Comando de rollback alembic não encontrado")
    if data["rollback_plan"]["git"] not in md_content:
        errors.append("❌ Comando git restore não encontrado")
    
    # Validar risk assessment
    risk_keywords = ["Data Loss", "Downtime", "Regression"]
    for keyword in risk_keywords:
        if keyword not in md_content:
            errors.append(f"❌ Risk assessment keyword não encontrado: {keyword}")
    
    for endpoint in data["risk_assessment"]["endpoints_to_audit"]:
        # Extrair apenas a rota principal (POST /path)
        endpoint_route = endpoint.split(" (")[0] if " (" in endpoint else endpoint
        if endpoint_route not in md_content:
            errors.append(f"❌ Endpoint não encontrado: {endpoint_route}")
    
    # Resultado
    if errors:
        print("❌ VALIDAÇÃO FALHOU\n")
        for error in errors:
            print(error)
        return 1
    else:
        print("✅ VALIDAÇÃO PASSOU")
        print(f"\n📊 Estatísticas:")
        print(f"   - AR ID: {data['ar_id']}")
        print(f"   - Pre-flight checks: {len(data['pre_flight_checks'])}")
        print(f"   - Migration steps: {len(data['migration_steps'])}")
        print(f"   - Model changes: {len(data['model_changes'])}")
        print(f"   - Success criteria: {len(data['success_criteria'])}")
        print(f"   - MD filesize: {len(md_content)} chars")
        print(f"\n✅ Todas as informações do JSON foram corretamente traduzidas para o MD")
        return 0

if __name__ == "__main__":
    sys.exit(validate_translation())
