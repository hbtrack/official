"""Script temporario: reescreve ar_train_010a_ssot_path_migration.json com tasks 173+174."""
import json
from pathlib import Path

data = {
    "project": "HB Track",
    "version": "1.2.0",
    "notes": (
        "AR-TRAIN-010A: Migrar referencias docs/_generated/ para docs/ssot/ em 11 arquivos "
        "de testes de invariantes TRAINING. Quebrado em 2 tasks (173+174) por limite write_scope "
        "maxItems=10. ANCORAS: docs/ssot/schema.sql EXISTS (confirmado por gen_docs_ssot.py). "
        "Substituicao puramente mecanica -- zero risco de regressao logica nos testes."
    ),
    "assumptions": [
        "docs/ssot/schema.sql existe e e o arquivo canonico atual (confirmado: regenerado pelo gen_docs_ssot.py)",
        "docs/ssot/openapi.json existe e e o arquivo canonico atual",
        "Todos os 11 arquivos usam o padrao: Path(__file__).parent.parent.parent / 'docs' / '_generated' / '<arquivo>'",
        "Substituicao e mecanica (string replace) sem alteracao de logica de teste",
        "docs/_generated/ NAO deve ser removido nesta AR -- pode ser referenciado por outros modulos"
    ],
    "tasks": [
        {
            "id": "173",
            "title": "Migrar _generated para ssot nos test files TRAINING (lote 1/2)",
            "description": (
                "Substituir '\"_generated\"' por '\"ssot\"' em 6 arquivos de testes TRAINING (Lote 1 de 2).\n"
                "Task 174 cobre os outros 5 arquivos.\n\n"
                "ARQUIVOS DESTE LOTE (executar a partir de Hb Track - Backend/):\n"
                "1. tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py\n"
                "2. tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py\n"
                "3. tests/training/invariants/test_inv_train_021_internal_load_trigger.py\n"
                "4. tests/training/invariants/test_inv_train_028_focus_sum_constraint.py\n"
                "5. tests/training/invariants/test_inv_train_030_attendance_correction_fields.py\n"
                "6. tests/training/invariants/test_inv_train_031_derive_phase_focus.py\n\n"
                "PADRAO DE SUBSTITUICAO:\n"
                "  DE:   / \"docs\" / \"_generated\" / \"schema.sql\"\n"
                "  PARA: / \"docs\" / \"ssot\" / \"schema.sql\"\n"
                "Idem para openapi.json e manifest.json se presentes nos arquivos.\n\n"
                "METODO RECOMENDADO (Python, from Hb Track - Backend/):\n"
                ">>> from pathlib import Path\n"
                ">>> files = [<lista acima>]\n"
                ">>> for f in files:\n"
                "...     p = Path(f); t = p.read_text('utf-8')\n"
                "...     p.write_text(t.replace('\"_generated\"', '\"ssot\"'), 'utf-8')\n\n"
                "NAO modificar arquivos fora da lista."
            ),
            "criteria": (
                "1) Nenhum dos 6 arquivos deste lote contem a string '\"_generated\"' apos a migracao.\n"
                "2) Os arquivos referenciam docs/ssot/schema.sql.\n"
                "3) docs/ssot/schema.sql existe no repositorio."
            ),
            "validation_command": (
                "cd \"Hb Track - Backend\" && "
                "python -c \""
                "import sys; from pathlib import Path; "
                "files=['tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py',"
                "'tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py',"
                "'tests/training/invariants/test_inv_train_021_internal_load_trigger.py',"
                "'tests/training/invariants/test_inv_train_028_focus_sum_constraint.py',"
                "'tests/training/invariants/test_inv_train_030_attendance_correction_fields.py',"
                "'tests/training/invariants/test_inv_train_031_derive_phase_focus.py']; "
                "errs=[f for f in files if '_generated' in Path(f).read_text(encoding='utf-8')]; "
                "sys.exit('FAIL _generated still found: '+str(errs)) if errs else print('PASS lote 1: 6 files migrated')\""
            ),
            "write_scope": [
                "Hb Track - Backend/tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py",
                "Hb Track - Backend/tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py",
                "Hb Track - Backend/tests/training/invariants/test_inv_train_021_internal_load_trigger.py",
                "Hb Track - Backend/tests/training/invariants/test_inv_train_028_focus_sum_constraint.py",
                "Hb Track - Backend/tests/training/invariants/test_inv_train_030_attendance_correction_fields.py",
                "Hb Track - Backend/tests/training/invariants/test_inv_train_031_derive_phase_focus.py"
            ],
            "risks": [
                "Se arquivos tiverem refs a openapi.json ou manifest.json em _generated, migrar no mesmo pass",
                "NAO remover docs/_generated/ -- escopo fora desta AR"
            ],
            "notes": "ANCORA: docs/ssot/schema.sql EXISTS. Task 174 cobre os outros 5 arquivos."
        },
        {
            "id": "174",
            "title": "Migrar _generated para ssot nos test files TRAINING (lote 2/2)",
            "description": (
                "Substituir '\"_generated\"' por '\"ssot\"' em 5 arquivos de testes TRAINING (Lote 2 de 2).\n"
                "Task 173 cobriu os primeiros 6 arquivos.\n\n"
                "ARQUIVOS DESTE LOTE:\n"
                "1. tests/training/invariants/test_inv_train_035_session_templates_unique_name.py\n"
                "2. tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py\n"
                "3. tests/training/invariants/test_inv_train_037_cycle_dates.py\n"
                "4. tests/training/invariants/test_inv_train_072_ai_suggestion_not_order.py\n"
                "5. tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py\n\n"
                "PADRAO DE SUBSTITUICAO:\n"
                "  DE:   / \"docs\" / \"_generated\" / \"schema.sql\"\n"
                "  PARA: / \"docs\" / \"ssot\" / \"schema.sql\"\n\n"
                "NAO modificar arquivos fora da lista. Executor deve completar Task 173 primeiro."
            ),
            "criteria": (
                "1) Nenhum dos 5 arquivos deste lote contem '\"_generated\"' apos a migracao.\n"
                "2) docs/ssot/schema.sql existe no repositorio.\n"
                "3) Combinado com Task 173: ZERO arquivos TRAINING contem refs a _generated."
            ),
            "validation_command": (
                "cd \"Hb Track - Backend\" && "
                "python -c \""
                "import sys; from pathlib import Path; "
                "files=['tests/training/invariants/test_inv_train_035_session_templates_unique_name.py',"
                "'tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py',"
                "'tests/training/invariants/test_inv_train_037_cycle_dates.py',"
                "'tests/training/invariants/test_inv_train_072_ai_suggestion_not_order.py',"
                "'tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py']; "
                "errs=[f for f in files if '_generated' in Path(f).read_text(encoding='utf-8')]; "
                "sys.exit('FAIL _generated still found: '+str(errs)) if errs else print('PASS lote 2: 5 files migrated')\""
            ),
            "write_scope": [
                "Hb Track - Backend/tests/training/invariants/test_inv_train_035_session_templates_unique_name.py",
                "Hb Track - Backend/tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py",
                "Hb Track - Backend/tests/training/invariants/test_inv_train_037_cycle_dates.py",
                "Hb Track - Backend/tests/training/invariants/test_inv_train_072_ai_suggestion_not_order.py",
                "Hb Track - Backend/tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py"
            ],
            "risks": [
                "Se arquivos tiverem refs a openapi.json ou manifest.json em _generated, migrar no mesmo pass",
                "Executor deve rodar Task 173 primeiro"
            ],
            "notes": "ANCORA: docs/ssot/schema.sql EXISTS. Continuacao Task 173. Apos ambas: zero refs _generated em testes TRAINING."
        }
    ]
}

out = Path("docs/_canon/planos/ar_train_010a_ssot_path_migration.json")
out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"OK: wrote {out} ({out.stat().st_size} bytes, {len(data['tasks'])} tasks)")
