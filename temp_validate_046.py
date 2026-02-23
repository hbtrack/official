import pathlib,sys,os

critical=['scripts/run/hb_cli.py','docs/hbtrack/_INDEX.md','scripts','docs','Hb Track - Backend','Hb Track - Frontend','.gitignore']
missing=[f for f in critical if not pathlib.Path(f).exists()]
assert not missing,f'FAIL critical missing: {missing}' 

temp=['gemini.md','preparar_contexto.py','testador_final_report.py','complete_ar_reports.py','rebuild_index_real.py','mark_blocked_ars.py','insert_vps_policy.py','check_ar_status.py','consolidar_docs.py','temp_validate_ar002.py','test_gate_f.py','tmp_plan.json','validate_ar_translation.py','report_ar002.bat','run_report_ar002.ps1','arquivos_consolidados.txt','docs_consolidado.txt','_audit_output.txt','protocolo de correção.txt','tarefa_atual.md','Hb Track KANBAN.md','temp_report_032.py','temp_report_033.py','temp_report_038.py','temp_report_039.py','temp_report_040.py','temp_report_041.py','temp_report_042.py','temp_report_043.py','temp_report_044.py','fix_moves_044.py','fix_moves_045.py','validation_ar036.log']
present=[f for f in temp if pathlib.Path(f).exists()]
assert not present,f'FAIL temp still exist: {present}' 

evidence=pathlib.Path('docs/hbtrack/evidence/AR_046_removed_files.log')
assert evidence.exists(),f'FAIL no evidence log' 

gi=pathlib.Path('.gitignore').read_text(encoding='utf-8')
assert '.hb_guard' in gi and '.hb_tmp_tests' in gi,'FAIL .gitignore missing temp dirs'

print('PASS: Limpeza segura OK — arquivos mortos removidos, críticos preservados')
