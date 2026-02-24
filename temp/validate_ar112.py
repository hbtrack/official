import pathlib, re
ar071 = pathlib.Path('docs/hbtrack/ars/governance/AR_071_add_auto-commit_opt-in_to_hb_autotest_strict_allow.md').read_text(encoding='utf-8')
ar004 = pathlib.Path('docs/hbtrack/ars/features/AR_004_matcheventservice.create()_\u2014_orm_correto,_roster,_.md').read_text(encoding='utf-8')
stamps_071 = re.findall(r'### Verificacao Testador em [a-f0-9]{7}', ar071)
stamps_004 = re.findall(r'### Verificacao Testador em [a-f0-9]{7}', ar004)
assert len(stamps_071) == 1, f'AR_071 deve ter exatamente 1 carimbo Testador (tem {len(stamps_071)})'
assert len(stamps_004) == 1, f'AR_004 deve ter exatamente 1 carimbo Testador (tem {len(stamps_004)})'
assert '\U0001f534 REJEITADO' not in ar071, 'AR_071 ainda contém REJEITADO'
assert '\U0001f50d NEEDS REVIEW' not in ar004, 'AR_004 ainda contém NEEDS REVIEW'
assert '\u2705 SUCESSO' in ar071, 'AR_071 deve ter SUCESSO'
assert '\u2705 SUCESSO' in ar004, 'AR_004 deve ter SUCESSO'
print('PASS: AR_071 e AR_004 limpos (apenas 1 carimbo Testador SUCESSO cada)')
