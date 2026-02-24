import re

with open('_reports/dispatch/architect.todo', 'r', encoding='utf-8') as f:
    content = f.read()

old_start = '## \U0001f534 NOVO REJEITADO: AR_003 \u2014 AH_DIVERGENCE (Windows cmd-safe)'
old_end = '4. Fazer `hb report 003` com exit_code=0.'

new_section = """## \u2705 RESOLVIDO: AR_003 + AR_123 \u2014 Verificadas e Seladas

AR_123 criada pelo Arquiteto (plano `fix_ar003_validation_cmd_windows_shell.json`), executada pelo Executor (commits fe8ca5a, fb72af5) e verificada pelo Testador.

| AR | Hash Verify | Status |
|---|---|---|
| AR_123 | 7149b8f31933aa3d | \u2705 VERIFICADO |
| AR_003 | 7149b8f31933aa3d | \u2705 VERIFICADO |

Novo `validation_command` (cmd-safe): `python docs/hbtrack/evidence/AR_003/validate_ar003.py`
Triple-run: exit=0, stdout "PASS: Schemas Pydantic canonicos OK", hash consistente 3x."""

start_idx = content.find(old_start)
end_idx = content.find(old_end)
if start_idx == -1 or end_idx == -1:
    # Try finding without the exact emoji
    start_idx = content.find('NOVO REJEITADO: AR_003')
    idx_begin = content.rfind('\n##', 0, start_idx)
    end_idx = content.find(old_end)
    print(f"Fallback: idx_begin={idx_begin}, end_idx={end_idx}")
    if idx_begin >= 0 and end_idx >= 0:
        end_idx += len(old_end)
        content = content[:idx_begin+1] + new_section + content[end_idx:]
        with open('_reports/dispatch/architect.todo', 'w', encoding='utf-8') as f:
            f.write(content)
        print("OK: replaced via fallback")
    else:
        print(f"FAILED: could not locate section")
else:
    end_idx += len(old_end)
    content = content[:start_idx] + new_section + content[end_idx:]
    with open('_reports/dispatch/architect.todo', 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK: replaced section")

# Also update the Executor and Testador sections
with open('_reports/dispatch/architect.todo', 'r', encoding='utf-8') as f:
    content = f.read()

# Update Executor section
old_exec = """## Batch Atual \u2014 Estado Atualizado

| Prioridade | AR | Status |
|---|---|---|
| \U0001f534 URGENTE | AR_003 (via AR_123) | \U0001f7f2 PENDENTE \u2014 plano fix_ar003_validation_cmd_windows_shell.json |
| \u2705 | AR_068 | \u2705 VERIFICADO |
| \u2705 | AR_113\u2013119 | \u2705 VERIFICADO (todos 7) |

**ARs j\u00e1 conclu\u00eddas (N\u00c3O re-executar):** AR_120, AR_121, AR_122, AR_068, AR_113\u2013119 \u2705 VERIFICADO; AR_110, AR_071 \u2705 VERIFICADO (colateral).

**ARs 056\u2013063 (STUBs)**: NAO executar \u2014 aguardar planos pr\u00f3prios do Arquiteto."""

new_exec = """## Batch Atual \u2014 Estado Atualizado (ALL DONE)

Todos os batches desta sess\u00e3o est\u00e3o \u2705 VERIFICADO.

**ARs j\u00e1 conclu\u00eddas (N\u00c3O re-executar):**
AR_003, AR_123, AR_068, AR_113\u2013119, AR_120, AR_121, AR_122, AR_110, AR_071 \u2014 todos \u2705 VERIFICADO.

**ARs 056\u2013063 (STUBs)**: N\u00c3O executar \u2014 aguardar planos pr\u00f3prios do Arquiteto."""

idx = content.find('## Batch Atual')
if idx >= 0:
    print(f"Found 'Batch Atual' at idx {idx}")

content = content.replace(old_exec, new_exec)

# Update Testador section
old_test = """\u2014 \U0001f7f2 AGUARDANDO VERIFY ap\u00f3s Executor completar AR_123

Ap\u00f3s Executor completar AR_123, fazer `hb verify 003`.
- Novo `validation_command`: `python docs/hbtrack/evidence/AR_003/validate_ar003.py`
- Deve retornar exit 0, stdout "PASS: Schemas Pydantic canonicos OK", hash consistente 3x."""

new_test = """\u2014 \u2705 AR_003 VERIFICADO (hash 7149b8f31933aa3d, triple-run OK)"""

# simpler replacement
content = content.replace(
    '\U0001f7f2 AGUARDANDO VERIFY ap\u00f3s Executor completar AR_123',
    '\u2705 AR_003 VERIFICADO (hash 7149b8f31933aa3d, triple-run OK)'
)

# Also update INFO CONTEXTO table
old_info = "| AR_003 | \U0001f534 REJEITADO \u2192 AR_123 plano criado |"
new_info = "| AR_003 | \u2705 VERIFICADO (via AR_123) |"
content = content.replace(old_info, new_info)

old_info2 = "| AR_056\u2013063 | \U0001f4a4 STUBs sem plano \u2014 pr\u00f3xima sess\u00e3o |"
new_info2 = "| AR_056\u2013063 | \U0001f4a4 STUBs sem plano \u2014 pr\u00f3xima sess\u00e3o |"
# no change needed for that one

with open('_reports/dispatch/architect.todo', 'w', encoding='utf-8') as f:
    f.write(content)

print("architect.todo updated successfully")
