#!/usr/bin/env python3
"""Atualiza _reports/dispatch/architect.todo com estado pós-cleanup batch."""
import pathlib

p = pathlib.Path('_reports/dispatch/architect.todo')
txt = p.read_text(encoding='utf-8')

# Preservar header + secoes TESTADOR x ARQUITETO (até a última linha da secao AR_003)
ar003_end_marker = "| AR_003 | ✅ VERIFICADO (via AR_123) |\n| AR_056–063 | 💤 STUBs sem plano — próxima sessão |\n```"

if ar003_end_marker not in txt:
    print("WARN: marker not found, appending instead")
    new_content = txt.rstrip() + "\n\n"
else:
    # Keep everything up to and including the AR_003 entry section end
    cut_idx = txt.index(ar003_end_marker) + len(ar003_end_marker)
    new_content = txt[:cut_idx] + "\n\n"

# Append updated sections
new_content += """---

## ✅ RESOLVIDO (sessão cleanup batch): AR_005, AR_014, AR_015, AR_024, AR_033, AR_101, AR_102, AR_103

Todas seladas como ✅ VERIFICADO (commit c71d154).

| AR | Hash Verify | Motivo |
|---|---|---|
| AR_005 | c17e182c19318e87 | router match_events SchoutEventCreate + awaits corretos |
| AR_014 | 4d2e095d2ead54d0 | rename Hb Track - Frontend confirmado (filesystem) |
| AR_015 | 2b086aeba34858e5 | zero refs 'Fronted' em scripts/ e docs/_canon/ |
| AR_024 | edb86baf8552defa | docs v1.1.0+ verificados (Dev Flow, Hb CLI Spec, Testador Contract) |
| AR_033 | b87f7c7fd0901ee3 | _INDEX.md sincronizado — fix rglob + path correto (99 ARs) |
| AR_101 | 21a30994f5d40975 | governance ARs estrutura verificada |
| AR_102 | bb4d2e915745147e | competitions ARs estrutura verificada |
| AR_103 | 4a50c611a582011d | drafts ARs estrutura verificada |

## ✅ RESOLVIDO: AR_002.5_C, AR_007, AR_016, AR_020, AR_023, AR_031 — SUPERSEDED

Marcadas ⛔ SUPERSEDED: conteúdo obsoleto/absorvido por protocolo v1.3.0.


**SEÇÃO ARQUITETO x EXECUTOR**
SOLICITAÇÕES DO ARQUITETO PARA O EXECUTOR:

## Estado Atual — Nenhuma tarefa pendente para o Executor

Todas as ARs com status problemático foram resolvidas.

**NÃO re-executar:** AR_003, AR_005, AR_014, AR_015, AR_024, AR_033, AR_037–043, AR_068, AR_071, AR_101–103, AR_110–123 ✅ VERIFICADO.

**ARs 056–063 (STUBs)**: NÃO executar — aguardar planos do Arquiteto.


**SEÇÃO ARQUITETO x TESTADOR**
SOLICITAÇÕES DO ARQUITETO PARA O TESTADOR:

## INFO CONTEXTO — Estado Corrente (pós-cleanup batch completo)

| AR | Status |
|---|---|
| AR_003, AR_005, AR_014, AR_015, AR_024, AR_033 | ✅ VERIFICADO |
| AR_037, AR_039, AR_041, AR_042, AR_043 | ✅ VERIFICADO |
| AR_004, AR_109, AR_111, AR_112 | ✅ VERIFICADO |
| AR_068, AR_071, AR_110 | ✅ VERIFICADO |
| AR_101, AR_102, AR_103 | ✅ VERIFICADO |
| AR_113–123 | ✅ VERIFICADO |
| AR_120, AR_121, AR_122 | ✅ VERIFICADO |
| AR_007, AR_016, AR_020, AR_023, AR_031, AR_002.5_C | ⛔ SUPERSEDED |
| AR_056–063 | 💤 STUBs sem plano — próxima sessão |
"""

p.write_text(new_content, encoding='utf-8')
print(f"OK: architect.todo atualizado ({len(new_content)} chars)")
