"""Stage exact artifacts for AR_068 and ARs 113-119 batch commit."""
import subprocess
import pathlib

# Helper
def add(path):
    r = subprocess.run(['git', 'add', path], capture_output=True, text=True)
    if r.returncode == 0:
        print(f'  staged: {path}')
    else:
        print(f'  WARN: {path} — {r.stderr.strip()}')

# 1. Evidence directories (8)
for ar_id in ['068', '113', '114', '115', '116', '117', '118', '119']:
    add(f'docs/hbtrack/evidence/AR_{ar_id}/executor_main.log')

# 2. Fix ARs (8 files)
features_dir = pathlib.Path('docs/hbtrack/ars/features')
fix_ids = ['068', '113', '114', '115', '116', '117', '118', '119']
for ar_id in fix_ids:
    files = list(features_dir.glob(f'AR_{ar_id}*.md'))
    for f in files:
        add(str(f))

# 3. Legacy ARs (7 files)
legacy = [
    'docs/hbtrack/ars/governance/AR_032_hb_cli_spec.md_sync_v1.0.8_\u2192_v1.1.0_gate_p3.5,_hbl.md',
    'docs/hbtrack/ars/governance/AR_034_governan\u00e7a_plans_-_gate_json-to-ar_obrigat\u00f3rio.md',
    'docs/hbtrack/ars/governance/AR_035_criar_scripts_run_hb_watch.py_-_sentinela_de_estad.md',
    'docs/hbtrack/ars/competitions/AR_038_migration_0057_drop_uk_competition_standings_team_.md',
    'docs/hbtrack/ars/competitions/AR_040_migration_0058_comp-db-006_add_3_check_constraints.md',
    'docs/hbtrack/ars/drafts/AR_044_git_mv_docs__canon_planos__\u2192_governance_,_competit.md',
    'docs/hbtrack/ars/drafts/AR_045_git_mv_docs_hbtrack_ars__\u2192_governance_,_competitio.md',
]
for path in legacy:
    # Find exact file via glob to handle potential name truncation
    p = pathlib.Path(path)
    if p.exists():
        add(str(p))
    else:
        # Try glob
        candidates = list(p.parent.glob(p.name[:20] + '*'))
        if candidates:
            add(str(candidates[0]))
        else:
            print(f'  NOT FOUND: {path}')

# 4. Temp validate scripts
for fname in [
    'temp/validate_ar068.py',
    'temp/validate_ar113.py',
    'temp/validate_ar114.py',
    'temp/validate_ar115.py',
    'temp/validate_ar116.py',
    'temp/validate_ar117.py',
    'temp/validate_ar118.py',
    'temp/validate_ar119.py',
    'temp/update_fix_ars.py',
]:
    add(fname)

# 5. Index file
add('docs/_INDEX.yaml')

print('Staging complete.')
