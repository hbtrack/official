"""Mark AR_007, AR_016, AR_020, AR_023, AR_031 as SUPERSEDED."""
import pathlib
import re

base = pathlib.Path('docs/hbtrack/ars')

superseded_data = {
    '007': 'Smoke test protocolo v1.0.4 obsoleto — absorvido por protocolo v1.3.0',
    '016': 'PRD v2.2 sync concluído; validação .ps1 overfit em regra proibitiva — absorvida pelo protocolo atual',
    '020': 'Dev Flow v1.0.8 check — Dev Flow está em v1.3.0; conteúdo absorvido por ARs de governança subsequentes',
    '023': 'Triple-run em produção desde v1.1.0; Evidence Pack nunca criado — absorvida pelo protocolo atual',
    '031': 'gemini.md removido do repositório; conteúdo de SSOT absorvido por equivalentes atuais',
}

for ar_id, reason in superseded_data.items():
    files = list(base.rglob(f'AR_{ar_id}_*.md'))
    if not files:
        print(f'NOT FOUND: AR_{ar_id}')
        continue
    
    ar_file = files[0]
    content = ar_file.read_text(encoding='utf-8')
    
    # Replace the first **Status**: line
    new_status = f'**Status**: ⛔ SUPERSEDED — {reason}'
    updated = re.sub(r'\*\*Status\*\*: .+', new_status, content, count=1)
    
    if updated == content:
        print(f'AR_{ar_id}: NO CHANGE (status not found or already correct)')
        continue
    
    ar_file.write_text(updated, encoding='utf-8')
    print(f'AR_{ar_id}: ✅ Marked SUPERSEDED — {ar_file.name[:60]}')
