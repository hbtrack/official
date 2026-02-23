# AR_035 — Criar scripts/run/hb_watch.py — sentinela de estado do fluxo

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.1.0

## Descrição
ARQUIVO ALVO: scripts/run/hb_watch.py (CRIAR)

### Problema
Não existe mecanismo automático que notifique qual agente deve assumir quando o status de uma AR muda. O Arquiteto, Executor e Testador dependem de checagem manual do _INDEX.md. O hb_watch.py preenche esta lacuna com polling do _INDEX.md e notificações no terminal.

### Implementação

O Executor DEVE criar scripts/run/hb_watch.py com o seguinte conteúdo EXATO:

```python
#!/usr/bin/env python3
"""
hb_watch.py — Sentinela de estado do fluxo HB Track (v1.0.0)

Monitoriza docs/hbtrack/ars/_INDEX.md e notifica qual agente deve assumir
baseado nos statuses canônicos do Dev Flow v1.1.0.

Uso:
    python scripts/run/hb_watch.py            # modo contínuo (polling 5s)
    python scripts/run/hb_watch.py --once     # 1 ciclo e sai (smoke test)
    python scripts/run/hb_watch.py --check    # valida ambiente (exit 0=OK)

Implementação: AR_034
"""
import sys
import time
import pathlib

# ========== CONFIG (alinhado ao hb_cli.py v1.1.0) ==========
INDEX_PATH = pathlib.Path("docs/hbtrack/ars/_INDEX.md")
LOCK_FILE = pathlib.Path(".hb_lock")
POLL_INTERVAL = 5  # segundos

# Statuses canônicos (Dev Flow v1.1.0)
EXECUTOR_TRIGGERS = ["DRAFT", "🔴 REJEITADO", "❌ FALHA"]
TESTER_TRIGGERS = ["\u2705 SUCESSO"]  # ✅ SUCESSO
BLOCKED_STATUSES = ["BLOQUEADO_INFRA", "\u23f8\ufe0f"]
TERMINAL_STATUSES = ["VERIFICADO", "SUPERSEDED"]


def is_locked() -> bool:
    """Verifica se hb_cli está com HBLock ativo."""
    return LOCK_FILE.exists()


def read_index() -> list:
    """Lê _INDEX.md e extrai ARs com id, título e status."""
    if not INDEX_PATH.exists():
        return []
    ars = []
    for line in INDEX_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| AR_"):
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 3:
            ars.append({"id": parts[0], "title": parts[1][:55], "status": parts[2]})
    return ars


def classify(ars: list) -> dict:
    """Classifica ARs por agente responsável."""
    result = {"executor": [], "tester": [], "blocked": [], "in_progress": [], "done": []}
    for ar in ars:
        s = ar["status"]
        if any(t in s for t in EXECUTOR_TRIGGERS):
            result["executor"].append(ar)
        elif any(t in s for t in TESTER_TRIGGERS):
            result["tester"].append(ar)
        elif any(t in s for t in BLOCKED_STATUSES):
            result["blocked"].append(ar)
        elif "EM_EXECUCAO" in s or "EM EXECUCAO" in s:
            result["in_progress"].append(ar)
        else:
            result["done"].append(ar)
    return result


def report(classified: dict) -> None:
    """Imprime o estado atual do fluxo."""
    ex = classified["executor"]
    te = classified["tester"]
    bl = classified["blocked"]
    ip = classified["in_progress"]

    if ex:
        print(f"\n\U0001f680 [EXECUTOR] {len(ex)} AR(s) aguardando implementação:")
        for ar in ex:
            print(f"   {ar['id']} [{ar['status']}] — {ar['title']}")

    if te:
        print(f"\n\U0001f52c [TESTADOR] {len(te)} AR(s) prontas para hb verify:")
        for ar in te:
            print(f"   {ar['id']} [{ar['status']}] — {ar['title']}")

    if bl:
        print(f"\n\u23f8\ufe0f  [BLOQUEADO] {len(bl)} AR(s) requerem atenção humana:")
        for ar in bl:
            print(f"   {ar['id']} [{ar['status']}] — {ar['title']}")

    if ip:
        print(f"\n\U0001f6e0\ufe0f  [EM PROGRESSO] {len(ip)} AR(s) com Executor ativo:")
        for ar in ip:
            print(f"   {ar['id']} [{ar['status']}] — {ar['title']}")

    if not ex and not te and not bl:
        done = len(classified["done"])
        print(f"\u2705 Fluxo limpo — {done} ARs concluídas. Nada pendente.")


def check_mode() -> int:
    """Modo --check: valida ambiente e retorna exit 0=OK, 1=FAIL."""
    print("HB Watch — CHECK MODE")
    errors = []

    if not INDEX_PATH.exists():
        errors.append(f"INDEX_PATH nao encontrado: {INDEX_PATH}")

    ars = read_index()
    classified = classify(ars)

    print(f"INDEX: {INDEX_PATH} ({'OK' if INDEX_PATH.exists() else 'MISSING'})")
    print(f"ARs: {len(ars)} total | Executor: {len(classified['executor'])} | Testador: {len(classified['tester'])} | Bloqueadas: {len(classified['blocked'])}")
    print(f"LOCK: {'ATIVO' if is_locked() else 'livre'}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1

    print("PASS: ambiente OK")
    return 0


def main() -> None:
    args = sys.argv[1:]

    if "--check" in args:
        sys.exit(check_mode())

    once = "--once" in args

    print("\U0001f440 HB Watch v1.0.0 — monitorando transições de estado do fluxo.")
    print(f"   INDEX : {INDEX_PATH}")
    print(f"   Poll  : {POLL_INTERVAL}s | HBLock: {LOCK_FILE}")
    if once:
        print("   Modo  : --once (1 ciclo e sai)")
    else:
        print("   Ctrl+C para sair.")
    print()

    last_snapshot = ""
    try:
        while True:
            if is_locked():
                print(f"\U0001f512 [{time.strftime('%H:%M:%S')}] HBLock ativo — aguardando...")
            else:
                ars = read_index()
                classified = classify(ars)
                snapshot = str(classified["executor"]) + str(classified["tester"]) + str(classified["blocked"])
                if snapshot != last_snapshot:
                    print(f"\n{'=' * 60}")
                    print(f"\U0001f504 [{time.strftime('%H:%M:%S')}] Estado do fluxo:")
                    report(classified)
                    last_snapshot = snapshot
            if once:
                break
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n\n\U0001f44b HB Watch encerrado.")


if __name__ == "__main__":
    main()
```

NÃO modificar nenhum outro arquivo. NÃO adicionar dependências externas.

## Critérios de Aceite
1) scripts/run/hb_watch.py existe. 2) INDEX_PATH = 'docs/hbtrack/ars/_INDEX.md'. 3) LOCK_FILE = '.hb_lock'. 4) Contém modo --check que sai com exit 0 quando INDEX_PATH existe. 5) Contém modo --once. 6) EXECUTOR_TRIGGERS inclui 'DRAFT', 'REJEITADO', 'FALHA'. 7) TESTER_TRIGGERS inclui 'SUCESSO'. 8) NÃO usa statuses inválidos 'PENDENTE' ou 'EM TESTE'. 9) --check retorna 'PASS' quando ambiente OK. 10) Script é Python puro (stdlib only).

## Validation Command (Contrato)
```
python -c "import subprocess,sys,pathlib; src=pathlib.Path('scripts/run/hb_watch.py'); assert src.exists(),'FAIL: script nao existe'; content=src.read_text(encoding='utf-8'); assert 'docs/hbtrack/ars/_INDEX.md' in content,'FAIL: INDEX_PATH errado'; assert 'hb_lock' in content or 'LOCK_FILE' in content,'FAIL: sem HBLock'; assert 'DRAFT' in content,'FAIL: EXECUTOR_TRIGGERS sem DRAFT'; assert 'SUCESSO' in content,'FAIL: TESTER_TRIGGERS sem SUCESSO'; assert '--check' in content,'FAIL: sem modo check'; assert 'PENDENTE' not in content,'FAIL: status invalido PENDENTE presente'; r=subprocess.run([sys.executable,str(src),'--check'],capture_output=True,text=True,timeout=15); assert r.returncode==0,f'FAIL: --check exit={r.returncode} err={r.stderr[:80]}'; assert 'PASS' in r.stdout,f'FAIL: PASS nao em stdout: {r.stdout[:100]}'; print('PASS: hb_watch.py OK — --check exit 0, paths corretos, statuses canonicos')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_035_hb_watch_sentinela_fluxo.log`

## Notas do Arquiteto
TESTES DETERMINÍSTICOS (Manual Deterministico):

GATE-WATCH-001: Script existe e passa --check
  cmd: python scripts/run/hb_watch.py --check
  PASS: exit 0, stdout contém 'PASS: ambiente OK'
  FAIL: exit != 0 ou 'FAIL:' no stdout

GATE-WATCH-002: INDEX_PATH correto (source inspection)
  cmd: python -c "import pathlib; c=pathlib.Path('scripts/run/hb_watch.py').read_text(encoding='utf-8'); assert 'docs/hbtrack/ars/_INDEX.md' in c; print('PASS')"
  PASS: 'PASS'
  FAIL: AssertionError

GATE-WATCH-003: Statuses inválidos ausentes
  cmd: python -c "import pathlib; c=pathlib.Path('scripts/run/hb_watch.py').read_text(encoding='utf-8'); assert 'PENDENTE' not in c and 'EM TESTE' not in c,'FAIL: statuses invalidos'; print('PASS')"
  PASS: 'PASS'
  FAIL: 'FAIL: statuses invalidos'

GATE-WATCH-004: Modo --once (1 ciclo, sai limpo)
  cmd: python scripts/run/hb_watch.py --once
  PASS: exit 0, imprime estado atual
  FAIL: exit != 0 ou loop infinito (timeout)

NOTA DE TRIPLE-RUN: --check não tem side-effects (read-only) → stdout_hash idêntico nos 3 runs → triple_consistency=OK garantido.

## Riscos
- O validation_command roda '--check' com timeout=15s — se o script importar módulos lentos, pode dar timeout
- EXECUTOR_TRIGGERS usa strings literais com emoji — cuidado com encoding ao copiar do JSON para o .py
- O modo --once faz 1 ciclo e quebra o loop — útil para smoke test mas não para monitorização contínua
- Se INDEX_PATH não existir, --check retorna exit 1 com 'FAIL:' — Executor DEVE garantir que existe antes de validar
- NÃO adicionar dependências externas (watchdog, inotify etc.) — apenas stdlib (pathlib, sys, time)

## Análise de Impacto
**Executor**: Roo (💻 Code Mode)
**Data**: 2026-02-22

**Escopo da Implementação**:
1. **Substituir scripts/run/hb_watch.py**: Implementação completa conforme AR-035, incluindo suporte a:
   - Polling de 5s do `_INDEX.md`.
   - Modos `--check` e `--once`.
   - Classificação multi-agente (Executor, Testador, Bloqueado, In Progress, Done).
   - Detecção de `HBLock` (`.hb_lock`).
2. **Upgrade v1.1.0 (Status NEEDS REVIEW)**: Integrada a lógica de `🔍 NEEDS REVIEW` conforme nota de atualização da AR.
   - Constante `REVIEW_TRIGGERS` adicionada.
   - Categoria `review` incluída na classificação e report.

**Impacto**:
- Visibilidade total: Agentes agora sabem imediatamente quando há tarefas para sua função.
- Robustez: O modo `--check` permite validar a integridade do ambiente de monitoramento.
- Conformidade: Alinhado ao Dev Flow v1.1.0.

**Conclusão**: O script legado (protótipo) foi substituído pela versão de produção v1.1.0.

---
## Adição v1.1.0 — Status NEEDS REVIEW (2026-02-21)

**Contexto**: Adicionado novo status `🔍 NEEDS REVIEW` ao hb_watch.py para suportar ARs que aguardam revisão humana intermediária (entre `✅ SUCESSO` e `✅ VERIFICADO`).

**Mudanças em hb_watch.py**:
- Nova constante: `REVIEW_TRIGGERS = ["NEEDS REVIEW", "🔍 NEEDS REVIEW"]`
- Nova categoria na `classify()`: `"review": []`
- Prioridade na classificação: depois de TESTER_TRIGGERS, antes de BLOCKED_STATUSES
- Novo bloco no `report()`: `🔍 [NEEDS REVIEW] N AR(s) aguardando revisão humana.`
- Snapshot atualizado para incluir `classified["review"]`
- Versão do script bumpeada para v1.1.0

**Documentação atualizada**:
- `docs/_canon/contratos/Dev Flow.md` §9.R-AR-4 — NEEDS_REVIEW adicionado à lista de status válidos
- `docs/_canon/contratos/Dev Flow.md` §11.3 — linha na tabela semáforo (Humano | Revisar manualmente)
- `docs/_canon/specs/Hb cli Spec.md` §11 — NEEDS_REVIEW listado com descrição
- `docs/_canon/specs/Hb cli Spec.md` §14 changelog — entrada v1.1.1

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import subprocess,sys,pathlib; src=pathlib.Path('scripts/run/hb_watch.py'); assert src.exists(),'FAIL: script nao existe'; content=src.read_text(encoding='utf-8'); assert 'docs/hbtrack/ars/_INDEX.md' in content,'FAIL: INDEX_PATH errado'; assert 'hb_lock' in content or 'LOCK_FILE' in content,'FAIL: sem HBLock'; assert 'DRAFT' in content,'FAIL: EXECUTOR_TRIGGERS sem DRAFT'; assert 'SUCESSO' in content,'FAIL: TESTER_TRIGGERS sem SUCESSO'; assert '--check' in content,'FAIL: sem modo check'; assert 'PENDENTE' not in content,'FAIL: status invalido PENDENTE presente'; r=subprocess.run([sys.executable,str(src),'--check'],capture_output=True,text=True,timeout=15); assert r.returncode==0,f'FAIL: --check exit={r.returncode} err={r.stderr[:80]}'; assert 'PASS' in r.stdout,f'FAIL: PASS nao em stdout: {r.stdout[:100]}'; print('PASS: hb_watch.py OK — --check exit 0, paths corretos, statuses canonicos')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_035_hb_watch_sentinela_fluxo.log`
**Python Version**: 3.11.9

