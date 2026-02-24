import json, glob

for ar in ['AR_016', 'AR_020', 'AR_023', 'AR_031']:
    files = glob.glob(f'_reports/testador/{ar}_*/result.json')
    if files:
        d = json.load(open(files[-1], encoding='utf-8'))
        runs = d.get('runs', [])
        sample_stdout = ''
        if runs:
            # try to get actual content from first run
            sample_stdout = str(runs[0])[:200]
        print(f'\n=== {ar} ===')
        print(f'  rejection: {d.get("rejection_reason","-")}')
        print(f'  consistency: {d.get("consistency","-")}')
        print(f'  testador_exit: {d.get("testador_exit_code","-")}')
        print(f'  executor_exit: {d.get("executor_exit_code","-")}')
        print(f'  first_run: {sample_stdout}')
    else:
        print(f'{ar}: no report found')
