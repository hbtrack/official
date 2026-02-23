# AR_028 — HBLock: Concurrency Lock Atômico para hb_cli.py (3 Agentes)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
ARQUIVO ALVO: scripts/run/hb_cli.py

### Problema
Quando 3 agentes (Arquiteto/Executor/Testador) operam em paralelo, operações de escrita (hb plan, hb report, hb verify) podem corromper _INDEX.md ou arquivos de AR por corrida de escrita concorrente.

### Implementação (PATCH MÍNIMO)

(L1) CLASSE HBLock — inserir APÓS as constantes e ANTES de # ========== UTILS ==========:

class HBLock:
    """File-based atomic lock para operações de escrita do hb_cli.
    Impede corrida concorrente entre Arquiteto, Executor e Testador.
    Implementação: AR_028.
    """
    LOCK_FILE = '.hb_lock'
    MAX_RETRIES = 10
    MIN_WAIT = 0.1
    MAX_WAIT = 0.5

    def __init__(self):
        self.lock_path = Path(LOCK_FILE) if 'LOCK_FILE' not in dir() else Path(self.LOCK_FILE)
        self.pid = os.getpid()

    def __enter__(self):
        import random as _random
        for attempt in range(self.MAX_RETRIES):
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, 'w') as f:
                    f.write(f'pid={self.pid}\ntimestamp={__import__("time").time()}')
                return self
            except FileExistsError:
                wait = _random.uniform(self.MIN_WAIT, self.MAX_WAIT)
                __import__('time').sleep(wait)
        fail('E_CLI_LOCKED',
             f'Lock file {self.lock_path} retido por outro agente após {self.MAX_RETRIES} tentativas.\n'
             f'Se o processo travou, remova manualmente: {self.lock_path}',
             exit_code=3)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.lock_path.exists():
                self.lock_path.unlink()
        except Exception:
            pass
        return False

(L2) NOVO ERROR CODE — adicionar após E_TRIPLE_FAIL:
E_CLI_LOCKED = 'E_CLI_LOCKED'

(L3) INTEGRAR HBLock nos comandos de escrita:
- cmd_plan: envolver corpo de materialização (após validações, antes de escrita) com `with HBLock():`
- cmd_report: envolver bloco de escrita com `with HBLock():`
- cmd_verify: envolver bloco de escrita com `with HBLock():`

(L4) .gitignore — adicionar '.hb_lock' se não existir.

### Safety
- O lock usa os.O_CREAT | os.O_EXCL — atomicidade garantida pelo SO
- Cleanup em __exit__ via finally — mesmo em crash parcial
- Se SIGKILL matar o processo: lock órfão requer remoção manual (risco aceitável, stale lock detectável por timestamp)
- Backoff aleatório (100-500ms) evita thundering herd

NÃO MODIFICAR lógica de validação existente. APENAS adicionar classe + integrar nos 3 comandos.

## Critérios de Aceite
1) hb_cli.py contém class HBLock com __enter__/__exit__. 2) E_CLI_LOCKED definido. 3) cmd_plan usa 'with HBLock()'. 4) cmd_report usa 'with HBLock()'. 5) cmd_verify usa 'with HBLock()'. 6) .hb_lock está no .gitignore. 7) hb version retorna v1.1.0 (não regride).

## Validation Command (Contrato)
```
python -c "import pathlib,subprocess,sys; hb=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); assert 'class HBLock' in hb,'FAIL no HBLock class'; assert 'E_CLI_LOCKED' in hb,'FAIL no E_CLI_LOCKED'; assert 'with HBLock()' in hb,'FAIL no with HBLock()'; assert hb.count('with HBLock()')>=3,f'FAIL only {hb.count(chr(119)+chr(105)+chr(116)+chr(104)+chr(32)+chr(72)+chr(66)+chr(76)+chr(111)+chr(99)+chr(107))} uses, need >=3'; gi=pathlib.Path('.gitignore'); assert gi.exists() and '.hb_lock' in gi.read_text(encoding='utf-8'),'FAIL .hb_lock not in .gitignore'; v=subprocess.run([sys.executable,'scripts/run/hb_cli.py','version'],capture_output=True,text=True,encoding='utf-8'); assert 'v1.1.0' in v.stdout,f'FAIL version={v.stdout.strip()}'; print('PASS: HBLock concurrency enterprise OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_028_hblock_concurrency_enterprise.log`

## Riscos
- HBLock MUST usar Path() para lock_path — consistente com estilo do arquivo
- fail() já existe no hb_cli.py — HBLock MUST usar fail() para E_CLI_LOCKED, não sys.exit() direto
- Integração nos 3 comandos MUST envolver APENAS o bloco de escrita, não as validações read-only
- SIGKILL deixa lock órfão — aceitável com documentação; stale detectável por timestamp no lock file
- os.O_CREAT | os.O_EXCL é cross-platform (Windows + Linux) — OK para workflow HB Track

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib,subprocess,sys; hb=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); assert 'class HBLock' in hb,'FAIL no HBLock class'; assert 'E_CLI_LOCKED' in hb,'FAIL no E_CLI_LOCKED'; assert 'with HBLock()' in hb,'FAIL no with HBLock()'; assert hb.count('with HBLock()')>=3,f'FAIL only {hb.count(chr(119)+chr(105)+chr(116)+chr(104)+chr(32)+chr(72)+chr(66)+chr(76)+chr(111)+chr(99)+chr(107))} uses, need >=3'; gi=pathlib.Path('.gitignore'); assert gi.exists() and '.hb_lock' in gi.read_text(encoding='utf-8'),'FAIL .hb_lock not in .gitignore'; v=subprocess.run([sys.executable,'scripts/run/hb_cli.py','version'],capture_output=True,text=True,encoding='utf-8'); assert 'v1.1.0' in v.stdout,f'FAIL version={v.stdout.strip()}'; print('PASS: HBLock concurrency enterprise OK')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_028_hblock_concurrency_enterprise.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_028_b2e7523/result.json`

### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_028_b2e7523/result.json`
