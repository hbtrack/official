# AR_053 — hb_watch.py — Windows UTF-8 stdout fix + contract sync

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
DOIS BUGS EM hb_watch.py v1.1.0:

--- BUG 1: UnicodeEncodeError no Windows ---
hb_watch.py falha com UnicodeEncodeError ao imprimir '👀 HB Watch v1.1.0...' (main():145).
O stdout padrão no Windows usa codec cp1252, que não suporta emoji. Erro exato:

  UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f440' in position 0

FIX 1 (padrão canônico — hb_cli.py:31-32):
  Inserir após a última linha de import (após 'import pathlib'), antes do bloco '# CONFIG':

    # Windows UTF-8 fix (idem hb_cli.py:31-32)
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

--- BUG 2: INDEX_PATH aponta para índice LEGADO ---
hb_watch.py:20 define:
  INDEX_PATH = pathlib.Path("docs/hbtrack/ars/_INDEX.md")

Esse arquivo é o índice LEGADO (formato antigo) que usa status 'DRAFT' — violando
DEV FLOW §11.3 / R-AR-4, que define 🔲 PENDENTE como status inicial do semáforo.

O índice CANÔNICO (escrito por hb_cli.py rebuild_ar_index(), DEV FLOW §2.2) é:
  docs/hbtrack/_INDEX.md  (usa 🔲 PENDENTE conforme contrato)

FIX 2:
  Alterar linha 20 de:
    INDEX_PATH = pathlib.Path("docs/hbtrack/ars/_INDEX.md")
  Para:
    INDEX_PATH = pathlib.Path("docs/hbtrack/_INDEX.md")

--- TERCIÁRIO — CONTRACT SYNC ---
  infra_003_hb_watch.json documenta v1.0.0 mas a implementação é v1.1.0.
  Divergências identificadas (6): version, bucket review, PEND trigger, TESTE trigger,
  snapshot scope, AR reference (AR_034 vs AR_035).
  O Executor deve atualizar as notes de infra_003_hb_watch.json.

## Critérios de Aceite
1. grep 'sys.stdout.reconfigure' scripts/run/hb_watch.py retorna 1 match.
2. grep 'docs/hbtrack/_INDEX.md' scripts/run/hb_watch.py retorna 1 match (SEM 'ars/' no path).
3. python scripts/run/hb_watch.py --check exits 0 sem UnicodeEncodeError.
4. python scripts/run/hb_watch.py --once exits 0 (output contém 'HB Watch' sem crash).
5. infra_003_hb_watch.json atualizado com nota de divergências.

## Validation Command (Contrato)
```
python scripts/run/hb_watch.py --check > nul 2>&1 && echo WATCH_OK
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_053_hb_watch_unicode_fix.log`

## Notas do Arquiteto
FIX 1 (stdout — após 'import pathlib', antes de '# ========== CONFIG'):

  # Windows UTF-8 fix (idem hb_cli.py:31-32)
  if sys.platform == "win32":
      sys.stdout.reconfigure(encoding="utf-8")

FIX 2 (INDEX_PATH — linha 20 do arquivo):
  ANTES: INDEX_PATH = pathlib.Path("docs/hbtrack/ars/_INDEX.md")
  DEPOIS: INDEX_PATH = pathlib.Path("docs/hbtrack/_INDEX.md")

Após o Fix 2, hb_watch lerá o índice canônico com status 🔲 PENDENTE (não DRAFT).
O docs/hbtrack/ars/_INDEX.md (legado) deve ser mantido em disco — não deletar.
O fix de stdout é idempotente em Linux/macOS (sys.platform != 'win32' → ignorado).

## Riscos
- sys.stdout.reconfigure() só existe a partir do Python 3.7 — OK pois projeto usa Python 3.11.9.
- Fix 2: o docs/hbtrack/_INDEX.md pode ter statuses diferentes do docs/hbtrack/ars/_INDEX.md — o hb_watch passará a mostrar os statuses reais (🔲 PENDENTE, ✅ SUCESSO etc.) em vez de DRAFT.
- hb_watch EXECUTOR_TRIGGERS inclui 'DRAFT' como trigger — após Fix 2, ARs com status DRAFT não existem mais no índice canônico, portanto esse trigger não disparará. Isso é comportamento correto.
- infra_003_hb_watch.json: atualizar apenas campos informativos — NÃO quebrar estrutura JSON.

## Análise de Impacto
**Executor**: Claude Sonnet 4.6 (Modo Executor)
**Data**: 2026-02-22

**Escopo da Implementação**:
1. **FIX 1** (`scripts/run/hb_watch.py`): Inserir bloco `if sys.platform == "win32": sys.stdout.reconfigure(encoding="utf-8")` após `import pathlib`, antes de `# ========== CONFIG`. Padrão idêntico ao `hb_cli.py:31-32`.
2. **FIX 2** (`scripts/run/hb_watch.py`): Alterar `INDEX_PATH` linha 20 de `"docs/hbtrack/ars/_INDEX.md"` para `"docs/hbtrack/_INDEX.md"` (índice canônico).
3. **CONTRACT SYNC** (`docs/_canon/planos/infra/infra_003_hb_watch.json`): Adicionar nota de divergências de versão.

**Impacto**:
- `hb_watch.py` passa a funcionar no Windows sem crash
- Pipeline de monitoramento restaurado
- hb_watch lê ARs com status correto (🔲 PENDENTE, não DRAFT)

---
## Carimbo de Execução
_(Gerado por hb report)_


> 📋 Kanban routing: Executor: Output não-determinístico: hashes divergem nos 3 runs (exit 0 em todos, mas stdout_hash diferente)

### Verificacao Testador em b2e7523
**Status Testador**: ⚠️ PENDENTE
**Consistency**: UNKNOWN
**Triple-Run**: FLAKY_OUTPUT (3x)
**Exit Testador**: 2 | **Exit Executor**: None
**TESTADOR_REPORT**: `_reports/testador/AR_053_b2e7523/result.json`

### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python scripts/run/hb_watch.py --check > nul 2>&1 && echo WATCH_OK`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_053_hb_watch_unicode_fix.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_053_b2e7523/result.json`

### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_053_b2e7523/result.json`
