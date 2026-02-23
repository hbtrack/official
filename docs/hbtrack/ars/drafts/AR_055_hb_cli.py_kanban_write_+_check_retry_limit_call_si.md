# AR_055 — hb_cli.py: Kanban write + check_retry_limit call site (dois dead-codes do claude.md)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
DOIS DEAD-CODES confirmados em hb_cli.py (origem: claude.md especificado hoje):

--- FIX 1: check_retry_limit() DEAD CODE ---
check_retry_limit() está DEFINIDA (linha 133) mas NUNCA CHAMADA. Sem call site, o gate de retry é inoperante.

O GATE_RETRY_LIMIT_GATE em GATES_REGISTRY.yaml define: 'hb plan exits 0 (check_retry_limit passes)' — portanto o call site CANÔNICO é em cmd_plan(), no loop de tasks, antes de materializar cada AR.

LOCAL DO FIX: em cmd_plan(), dentro do loop 'for task in tasks:', após validar o task e antes de escrever o arquivo AR no disco. O dict 'task' já tem 'retry_count' e 'id' (campos do plan JSON schema).

IMPLEMENTAÇÃO FIX 1:
  No loop de tasks em cmd_plan() (aproximadamente após linha 616, onde ar_dir é definido):
    check_retry_limit(task)  # GATE AR_035: bloqueia se retry_count >= MAX_RETRY_THRESHOLD
  
  O task dict tem: {'id': '001', 'retry_count': 0, 'title': '...', ...}
  check_retry_limit já lê task.get('retry_count', 0) e task.get('id') — compatível.

--- FIX 2: update_kanban_and_status() NÃO ESCREVE NO KANBAN ---
update_kanban_and_status() (linha 840-850) só retorna AR content atualizado e IMPRIME roteamento. NUNCA escreve em docs/hbtrack/Hb Track Kanban.md.

IMPLEMENTAÇÃO FIX 2:
  Adicionar constante: KANBAN_PATH = 'docs/hbtrack/Hb Track Kanban.md'
  
  Expandir update_kanban_and_status() para aceitar ar_id (parâmetro opcional):
    def update_kanban_and_status(ar_content, new_status, reason=None, ar_id=None):
        ar_updated = re.sub(r'\*\*Status\*\*:.*', f'**Status**: {new_status}', ar_content, count=1)
        if reason:
            ar_updated += f'\n> 📋 Kanban routing: {reason}\n'
        # Kanban write (SAFE — se arquivo não existir, skip silencioso)
        if ar_id:
            _write_kanban(ar_id, new_status, reason)
        return ar_updated
  
  Nova função _write_kanban(ar_id, new_status, reason=None):
    - Path: repo_root / KANBAN_PATH
    - Se não existir: print warning e return (não quebrar fluxo)
    - Ler conteúdo
    - Mapear new_status → nome da coluna:
        '✅ VERIFICADO' → '✅ Concluído'
        '🔍 NEEDS REVIEW' → 'Backlog' ou 'Revisão'
        '⚠️ PENDENTE' → 'Em Execução'
        '⏸️ BLOQUEADO_INFRA' → 'Bloqueado'
    - Se linha com 'AR_{ar_id}' encontrada: mover para coluna correta
    - Se não encontrada: APPEND na coluna correta como '- AR_{ar_id}'
    - Escrever arquivo (dentro do HBLock já ativo no caller)
    - try/except: se falhar, print warning, NÃO re-raise (não quebrar fluxo principal)
  
  Adaptar callers em finalize_verification() (~linha 873, 881, 889, 897) para passar ar_id:
    update_kanban_and_status(ar_content, novo_status, ar_id=ar_id)

ORDEM DE EXECUÇÃO: FIX 1 primeiro (mais simples), depois FIX 2.

## Critérios de Aceite
1. grep -c 'check_retry_limit(' scripts/run/hb_cli.py retorna >= 2 (1 def + >= 1 call site).
2. grep 'Hb Track Kanban\|KANBAN_PATH' scripts/run/hb_cli.py retorna >= 1 match.
3. python scripts/run/hb_cli.py version exits 0 (sem syntax error).
4. python -c "content=open('scripts/run/hb_cli.py',encoding='utf-8').read(); calls=content.count('check_retry_limit('); assert calls >= 2, f'FAIL: only {calls} occurrences of check_retry_limit( (need >= 2)'; assert 'Hb Track Kanban' in content or 'KANBAN_PATH' in content, 'FAIL: Kanban path missing'; print('PASS: both dead-codes fixed')" exits 0.

## Validation Command (Contrato)
```
python -c "content=open('scripts/run/hb_cli.py',encoding='utf-8').read(); calls=content.count('check_retry_limit('); assert calls >= 2, f'FAIL check_retry_limit: {calls} occurrences (need >= 2: 1 def + 1 call)'; assert 'Hb Track Kanban' in content or 'KANBAN_PATH' in content, 'FAIL: Kanban path missing'; print('PASS: check_retry_limit called + Kanban write present')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_055_hb_cli_kanban_write.log`

## Notas do Arquiteto
SAFE CONTRACT para FIX 2 (Kanban write):
  - Idempotente (rodar 2x não duplica card)
  - SAFE (se Kanban não existir, skip com warning — nunca sys.exit)
  - Atomic (dentro do HBLock já existente no caller)
  - try/except no _write_kanban completo — falha silenciosa com log

Para FIX 1 (check_retry_limit call site):
  - Inserir DENTRO do loop de tasks, ANTES do write do arquivo AR
  - Se cmd_plan for chamado com --skip-existing, o task pode não ser materializado — OK, o gate ainda é útil (previne --force em AR com muitas tentativas)
  - Se retry_count não estiver no task dict (campo opcional), check_retry_limit usa default 0 — sem problema

Após esta AR, hb plan bloqueará automaticamente ARs com retry_count >= 3, e hb verify atualizará o Kanban.

## Riscos
- hb_cli.py é arquivo crítico — qualquer syntax error quebra TODO o fluxo. Rodar 'python scripts/run/hb_cli.py version' após CADA edit para validar.
- O loop de tasks em cmd_plan() pode ter múltiplos pontos de iteração — verificar linha exata com 'grep -n for.*task.*tasks scripts/run/hb_cli.py'.
- O Kanban pode ter seções com nomes variados — _write_kanban deve ser tolerante (substring match, não exact match).
- finalize_verification tem 4 callers de update_kanban_and_status — atualizar TODOS para passar ar_id.
- check_retry_limit em --dry-run: verificar se o dry-run mode deve também bloquear (sim — dry-run valida, não deve fingir que retry_count é OK).

## Análise de Impacto
**Executor**: Claude Sonnet 4.6 (Modo Executor)
**Data**: 2026-02-22

**Escopo**:
1. FIX 1: Adicionar chamada  no loop de tasks em , antes de materializar cada AR no disco.
2. FIX 2: Adicionar constante , função  e expandir  para escrever no arquivo .
3. Adaptar 4 callers de  em  para passar .

**Impacto**: gate de retry ativo, Kanban atualizado automaticamente após verify.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "content=open('scripts/run/hb_cli.py',encoding='utf-8').read(); calls=content.count('check_retry_limit('); assert calls >= 2, f'FAIL check_retry_limit: {calls} occurrences (need >= 2: 1 def + 1 call)'; assert 'Hb Track Kanban' in content or 'KANBAN_PATH' in content, 'FAIL: Kanban path missing'; print('PASS: check_retry_limit called + Kanban write present')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_055_hb_cli_kanban_write.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_055_b2e7523/result.json`

### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_055_b2e7523/result.json`
