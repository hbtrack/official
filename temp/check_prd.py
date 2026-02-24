import pathlib

prd = pathlib.Path('docs/hbtrack/PRD Hb Track.md').read_text(encoding='utf-8')

checks = {
    'v2.2': '2.2' in prd,
    'data_20_02': '20/02/2026' in prd or '20 de fevereiro' in prd,
    'rf009': 'RF-009' in prd,
    'rf014': 'RF-014' in prd,
    'raci_prep': 'Preparador F' in prd,
    'celery': 'Celery' in prd,
    'no_ps1': '.ps1' not in prd,
    'competitions_domain': 'COMP-DB' in prd or 'Domínio Competitions' in prd,
    'passo65': 'Passo 6.5' in prd,
    'v108': 'v1.0.8' in prd,
}

failed = [k for k, v in checks.items() if not v]
passed = [k for k, v in checks.items() if v]
print('FAILED:', failed)
print('PASSED:', passed)
