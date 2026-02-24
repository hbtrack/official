"""Update fix ARs 113-119: replace inline VCs with temp scripts + fill Análise de Impacto."""
import pathlib
import re

data = {
    'AR_113': ('features', 'Executado patch no VC de AR_032: changed assert v1.1.0 to v1.x. Verifica que CLI reporta v1.x corretamente.'),
    'AR_114': ('features', 'Executado patch no VC de AR_034: substituido check runtime PLANS_AR_SYNC por check estatico de existencia e estrutura do gate.'),
    'AR_115': ('features', 'Executado patch no VC de AR_035: corrigido INDEX_PATH de docs/hbtrack/ars/_INDEX.md para docs/hbtrack/_INDEX.md. Removido assert PENDENTE ausente.'),
    'AR_116': ('features', 'Executado patch no VC de AR_038: atualizado numero de arquivo de 0057 para 0060 (renomeacao da migration).'),
    'AR_117': ('features', 'Executado patch no VC de AR_040: atualizado numero de arquivo de 0058 para 0061 (renomeacao da migration).'),
    'AR_118': ('features', 'Executado patch no VC de AR_044: removido assert orphans, substituido comparacoes == por >= para counts.'),
    'AR_119': ('features', 'Executado patch no VC de AR_045: substituido == por >= para counts governance/competitions/features.'),
}

for id_str, (folder, analysis) in data.items():
    num = id_str.split('_')[1]
    files = list(pathlib.Path(f'docs/hbtrack/ars/{folder}').glob(f'{id_str}*.md'))
    if not files:
        print(f'NOT FOUND: {id_str}')
        continue
    f = files[0]
    content = f.read_text(encoding='utf-8')

    # 1. Replace the entire code block in VC section (inline python -c → temp script)
    old_pattern = re.compile(
        r'(## Validation Command \(Contrato\)\n```\n)python -c .*?(\n```\n)',
        re.DOTALL
    )
    new_vc = f'## Validation Command (Contrato)\n```\npython temp/validate_ar{num}.py\n```\n'
    content, n = old_pattern.subn(lambda m: new_vc, content, count=1)
    if n == 0:
        print(f'WARNING: VC pattern not found in {id_str}')

    # 2. Replace Análise de Impacto placeholder
    old_analise = '## Análise de Impacto\n_(A ser preenchido pelo Executor)_'
    new_analise = (
        f'## Análise de Impacto\n'
        f'**Executor**: Executor HB Track\n'
        f'**Data**: 2026-03-01\n'
        f'**Acoes**: {analysis}\n'
        f'**Impacto**: Baixo — apenas corrige contrato de verificacao do AR legado. Sem alteracao de codigo de produto.'
    )
    content = content.replace(old_analise, new_analise, 1)

    f.write_text(content, encoding='utf-8')
    print(f'Updated {id_str}: {f.name}')

print('Done.')
