"""Script para promover 6 flows em TRAINING_USER_FLOWS.md"""
import re

path = 'docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md'
content = open(path, encoding='utf-8').read()

# === 1. Tabela sumário ===
changes_table = [
    ('FLOW-TRAIN-004', 'PARCIAL'),
    ('FLOW-TRAIN-005', 'PARCIAL'),
    ('FLOW-TRAIN-006', 'PARCIAL'),
    ('FLOW-TRAIN-007', 'PARCIAL'),
    ('FLOW-TRAIN-012', 'BLOQUEADO'),
    ('FLOW-TRAIN-013', 'PARCIAL'),
]
for flow_id, old_status in changes_table:
    pattern = rf'(\| {re.escape(flow_id)} \|[^\n]+){re.escape(old_status)}(\|[^\n]*)'
    new_content, n = re.subn(pattern, r'\1EVIDENCIADO\2', content)
    if n:
        content = new_content
        print(f'OK tabela: {flow_id} {old_status}->EVIDENCIADO')
    else:
        print(f'WARN: tabela {flow_id} nao encontrado')

# === 2. Nota L142 ===
old_note = '`FLOW-TRAIN-012` está `BLOQUEADO`: routers de export existem, mas estão **desabilitados** no agregador atual'
new_note = '`FLOW-TRAIN-012` estava `BLOQUEADO`: routers de export existem, **habilitados** após AR_179+AR_180 (evidenciado)'
if old_note in content:
    content = content.replace(old_note, new_note, 1)
    print('OK: nota BLOQUEADO L142 atualizada')
else:
    print('SKIP: nota L142 nao encontrada')

# === 3. YAML estado_asis + notas ===
flow_map = {
    'FLOW-TRAIN-004': ('PARCIAL', 'AR_176 (hb seal 2026-02-28)', 'docs/hbtrack/evidence/AR_176/executor_main.log'),
    'FLOW-TRAIN-005': ('PARCIAL', 'AR_171 (hb seal 2026-02-28)', 'docs/hbtrack/evidence/AR_171/executor_main.log'),
    'FLOW-TRAIN-006': ('PARCIAL', 'AR_187 (hb seal 2026-03-01)', 'docs/hbtrack/evidence/AR_187/executor_main.log'),
    'FLOW-TRAIN-007': ('PARCIAL', 'AR_177 + AR_178 (hb seal 2026-02-28)', 'docs/hbtrack/evidence/AR_177/executor_main.log, docs/hbtrack/evidence/AR_178/executor_main.log'),
    'FLOW-TRAIN-012': ('BLOQUEADO', 'AR_179 + AR_180 (hb seal 2026-02-28)', 'docs/hbtrack/evidence/AR_179/executor_main.log, docs/hbtrack/evidence/AR_180/executor_main.log'),
    'FLOW-TRAIN-013': ('PARCIAL', 'AR_181 + AR_182 (hb seal 2026-03-01)', 'docs/hbtrack/evidence/AR_181/executor_main.log, docs/hbtrack/evidence/AR_182/executor_main.log'),
}

for flow_id, (old_st, ar_ref, paths) in flow_map.items():
    # Change estado_asis in yaml block
    pattern_yaml = rf'(id: {re.escape(flow_id)}\n(?:[^\n]*\n){{1,3}}estado_asis: ){re.escape(old_st)}'
    m = re.search(pattern_yaml, content)
    if m:
        content = content[:m.start()] + m.group(1) + 'EVIDENCIADO' + content[m.end():]
        print(f'OK yaml: {flow_id} estado_asis {old_st}->EVIDENCIADO')
    else:
        print(f'WARN yaml: {flow_id} padrao nao encontrado')

    # Insert traceability note after yaml block closing ```
    note = f'> Promovido por Kanban+evidência: {ar_ref}, paths: {paths}'
    if note not in content:
        sec_pos = content.find(f'## {flow_id}')
        if sec_pos != -1:
            yaml_end = content.find('\n```\n\n', sec_pos)
            if yaml_end != -1:
                insert_pos = yaml_end + len('\n```\n\n')
                content = content[:insert_pos] + note + '\n\n' + content[insert_pos:]
                print(f'OK nota: {flow_id} inserida')
            else:
                print(f'WARN: fechamento yaml nao encontrado para {flow_id}')
        else:
            print(f'WARN: secao {flow_id} nao encontrada')
    else:
        print(f'SKIP: nota {flow_id} ja existe')

open(path, 'w', encoding='utf-8').write(content)
print('DONE: TRAINING_USER_FLOWS.md salvo')
