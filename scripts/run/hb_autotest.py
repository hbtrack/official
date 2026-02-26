#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HB Track — Auto-Testador Daemon (AR-First)
Arquivo: scripts/run/hb_autotest.py
Versão: 1.1.0
Protocolo: v1.3.0+
Contrato: docs/_canon/contratos/Testador Contract.md

Papel: Testador autônomo — substitui a necessidade de humano atuando como API
entre Executor e Testador. Executa hb verify + hb seal automaticamente quando
as condições do protocolo são atendidas.

Uso:
  python scripts/run/hb_autotest.py [--loop N] [--once] [--dry-run]

Flags:
  --loop N    Intervalo em segundos entre polls (default: 5)
  --once      Executar uma vez e sair (sem loop contínuo)
  --dry-run   Apenas reportar o que faria, sem executar

Fluxo autônomo implementado (v1.1.0 AR-First):
  1. Varre docs/hbtrack/ars/**/AR_*.md e lê **Status**: diretamente (sem _INDEX.md)
  2. Verifica se evidence do Executor existe E está staged (git diff --cached)
  3. Verifica que não existe TESTADOR_REPORT staged (evitar reprocessar)
  4. Executa: python hb_cli.py verify <id>
  5. Após SUCESSO: git add TESTADOR_REPORT + AR atualizada
  6. Executa: python hb_cli.py seal <id> "<reason>"
  7. Após VERIFICADO: git add AR selada

Regras Anti-Alucinação (AH-1..AH-12 do Testador Contract):
  - Este daemon NÃO modifica código — apenas executa hb verify e hb seal.
  - hb verify realiza triple-run independente (3x) com behavior_hash.
  - Este daemon NÃO confia no output do Executor — hb verify re-executa.
  - AH_DIVERGENCE, FLAKY_OUTPUT e TRIPLE_FAIL geram 🔴 REJEITADO automático.

v1.1.0 — AR-First Pipeline:
  - _INDEX.md NÃO é mais fonte de verdade para detecção de ARs
  - Elegibilidade decidida por: Status na AR + evidence existe + evidence staged
"""

import os
import sys
import re
import json
import subprocess
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ========== CONFIGURAÇÃO ==========
POLL_INTERVAL_DEFAULT = 5  # segundos
INDEX_PATH = 'docs/hbtrack/_INDEX.md'  # Cache only — NOT used for detection
AR_DIR = 'docs/hbtrack/ars'
TESTADOR_DIR = '_reports/testador'
EV_DIR = 'docs/hbtrack/evidence'
DISPATCH_DIR = '_reports/dispatch'
LOG_PREFIX = '🤖 [AutoTestador]'

# Configurar stdout UTF-8 (Windows)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


# ========== UTILS ==========

def get_repo_root() -> Path:
    """Retorna root do repo (hb_autotest.py está em scripts/run/)."""
    return Path(__file__).resolve().parent.parent.parent


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"{LOG_PREFIX} [{ts}] {msg}", flush=True)


def log_error(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"❌ [AutoTestador] [{ts}] {msg}", file=sys.stderr, flush=True)


def run_cmd(cmd: list, cwd: Path) -> tuple:
    """Executa comando e retorna (exit_code, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        cwd=str(cwd)
    )
    return result.returncode, result.stdout, result.stderr


def get_staged_files(repo_root: Path) -> set:
    """Retorna conjunto de arquivos staged (git diff --cached)."""
    _, stdout, _ = run_cmd(['git', 'diff', '--cached', '--name-only'], repo_root)
    return set(f.strip().replace('\\', '/') for f in stdout.splitlines() if f.strip())


def git_add(repo_root: Path, path: str, dry_run: bool = False) -> bool:
    """Executa git add para o path especificado."""
    if dry_run:
        log(f"  [DRY-RUN] git add {path}")
        return True
    ec, _, err = run_cmd(['git', 'add', path], repo_root)
    if ec != 0:
        log_error(f"  git add falhou ({ec}): {err.strip()[:200]}")
        return False
    return True


# ========== AR-FIRST DETECTION (v1.1.0) ==========

def find_ars_ready_for_verify(repo_root: Path) -> list:
    """
    v1.1.0 AR-First: Encontra ARs elegíveis para verify lendo ARs diretamente.

    Critérios de elegibilidade (TODOS devem ser atendidos):
    1. Status na AR é 🏗️ EM_EXECUCAO (ou ✅ SUCESSO para retrocompat)
    2. Evidence do Executor EXISTE no disco: docs/hbtrack/evidence/AR_<id>/executor_main.log
    3. Evidence está STAGED: presente em git diff --cached --name-only
    4. NÃO existe TESTADOR_REPORT staged para esse AR (evitar reprocessar)

    Retorna: [{"id": "055", "ar_full": "AR_055", "title": "...", "status": "..."}]

    NÃO depende de _INDEX.md — lê cada AR.md diretamente.
    """
    ar_dir = repo_root / AR_DIR
    if not ar_dir.exists():
        return []

    staged = get_staged_files(repo_root)
    eligible = []

    for ar_file in sorted(ar_dir.rglob("AR_*.md")):
        # Extrair ID numérico
        id_match = re.search(r"AR_(\d+)", ar_file.name)
        if not id_match:
            continue
        ar_id = id_match.group(1)

        try:
            content = ar_file.read_text(encoding="utf-8")
        except Exception:
            continue

        # Critério 1: Status deve indicar que Executor terminou
        status_match = re.search(r'\*\*Status\*\*:\s*(.+)', content)
        status = status_match.group(1).strip() if status_match else ""

        if not ('🏗️' in status or 'EM_EXECUCAO' in status or '✅ SUCESSO' in status):
            continue

        # Critério 2: Evidence do Executor deve existir no disco
        evidence_path = f"{EV_DIR}/AR_{ar_id}/executor_main.log"
        evidence_file = repo_root / evidence_path
        if not evidence_file.exists():
            continue

        # Critério 3: Evidence deve estar staged
        evidence_norm = evidence_path.replace('\\', '/')
        if evidence_norm not in staged:
            continue

        # Critério 4: Não deve existir TESTADOR_REPORT staged (evitar reprocessar)
        testador_prefix = f"{TESTADOR_DIR}/AR_{ar_id}_"
        has_testador_staged = any(testador_prefix in f for f in staged)
        if has_testador_staged:
            continue

        # Extrair título
        title_match = re.search(r"^#\s+AR_\d+[^:\n]*[:\s]+(.+)", content, re.MULTILINE)
        title = title_match.group(1).strip()[:50] if title_match else ar_file.stem[:50]

        eligible.append({
            "id": ar_id,
            "ar_full": f"AR_{ar_id}",
            "title": title,
            "status": status,
        })

    return eligible


def parse_index(repo_root: Path) -> list:
    """DEPRECATED (v1.1.0): Mantida para referência. Use find_ars_ready_for_verify().
    Lê _INDEX.md e retorna lista de ARs em 🏗️ EM_EXECUCAO."""
    index_path = repo_root / INDEX_PATH
    if not index_path.exists():
        return []
    ars = []
    pattern = re.compile(r'\|\s*(AR_([\w.]+))\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|')
    for line in index_path.read_text(encoding='utf-8').splitlines():
        m = pattern.search(line)
        if not m:
            continue
        ar_full = m.group(1).strip()
        ar_num = m.group(2).strip()
        title = m.group(3).strip()
        status = m.group(4).strip()
        if ar_num == "ID":
            continue
        if '🏗️' in status or 'EM_EXECUCAO' in status:
            id_match = re.match(r'^(\d+)', ar_num)
            if id_match:
                ars.append({
                    "id": id_match.group(1),
                    "ar_full": ar_full,
                    "title": title[:50],
                    "status": status,
                })
    return ars


# ========== AR FILE HELPERS ==========

def find_ar_file(repo_root: Path, ar_id: str) -> Path | None:
    """Localiza arquivo AR_<id>_*.md."""
    matches = list((repo_root / AR_DIR).rglob(f"AR_{ar_id}_*.md"))
    return matches[0] if matches else None


def read_ar_status(repo_root: Path, ar_id: str) -> str | None:
    """Lê status atual da AR direto do arquivo."""
    ar_file = find_ar_file(repo_root, ar_id)
    if not ar_file:
        return None
    content = ar_file.read_text(encoding='utf-8')
    # Match: **Status**: <value>
    m = re.search(r'\*\*Status\*\*:\s*(.+)', content)
    if m:
        return m.group(1).strip()
    return None


def get_testador_report_path(repo_root: Path, ar_id: str) -> str | None:
    """Extrai caminho do TESTADOR_REPORT da AR (após hb verify)."""
    ar_file = find_ar_file(repo_root, ar_id)
    if not ar_file:
        return None
    content = ar_file.read_text(encoding='utf-8')
    reports = re.findall(r'\*\*TESTADOR_REPORT\*\*:\s*` (.+?)`', content)
    return reports[-1].strip() if reports else None


def get_evidence_rel_path(ar_id: str) -> str:
    """Retorna path relativo canônico do evidence do Executor."""
    return f"{EV_DIR}/AR_{ar_id}/executor_main.log"


# ========== COMANDOS HB ==========

def run_hb_verify(repo_root: Path, ar_id: str, dry_run: bool = False) -> tuple:
    """Executa python hb_cli.py verify <id>."""
    cmd = [sys.executable, str(repo_root / 'scripts/run/hb_cli.py'), 'verify', ar_id]
    if dry_run:
        log(f"  [DRY-RUN] {' '.join(cmd)}")
        return 0, "DRY-RUN: SUCESSO simulado", ""
    return run_cmd(cmd, repo_root)


def run_hb_seal(repo_root: Path, ar_id: str, reason: str, dry_run: bool = False) -> tuple:
    """Executa python hb_cli.py seal <id> "<reason>"."""
    cmd = [sys.executable, str(repo_root / 'scripts/run/hb_cli.py'), 'seal', ar_id, reason]
    if dry_run:
        log(f"  [DRY-RUN] {' '.join(cmd)}")
        return 0, "DRY-RUN: VERIFICADO simulado", ""
    return run_cmd(cmd, repo_root)


def auto_commit_if_enabled(repo_root: Path, ar_id: str, title: str, dry_run: bool = False) -> bool:
    """
    Auto-commit opt-in: commit staged files após hb seal bem-sucedido.
    
    Critérios:
    - HB_AUTO_COMMIT=1 (opt-in explícito)
    - Todos staged files devem estar na allowlist estrita da AR
    - Mensagem padronizada com metadata
    
    Retorna True se commit foi executado (ou simulado em dry-run), False caso contrário.
    """
    auto_commit_enabled = os.environ.get('HB_AUTO_COMMIT', '0') == '1'
    
    if not auto_commit_enabled:
        log(f"AR_{ar_id}: auto-commit DESABILITADO (HB_AUTO_COMMIT != 1)")
        return False
    
    log(f"AR_{ar_id}: auto-commit HABILITADO — validando staged files...")
    
    # Allowlist estrita por AR
    allowlist = [
        f'docs/hbtrack/evidence/AR_{ar_id}/',
        f'docs/hbtrack/ars/',  # AR file pode estar em subdir (governance/, features/, etc.)
        f'_reports/testador/AR_{ar_id}/',
        'docs/hbtrack/_INDEX.md'
    ]
    
    staged = get_staged_files(repo_root)
    
    if not staged:
        log_error(f"AR_{ar_id}: NENHUM arquivo staged — abortando auto-commit")
        return False
    
    # Validate allowlist
    violators = []
    for file_path in staged:
        is_allowed = any(file_path.startswith(prefix) or file_path == prefix 
                        for prefix in allowlist)
        if not is_allowed:
            violators.append(file_path)
    
    if violators:
        log_error(f"AR_{ar_id}: ALLOWLIST VIOLATION — arquivos fora da allowlist detectados:")
        for v in violators:
            log_error(f"  ❌ {v}")
        log_error(f"  Allowlist: {allowlist}")
        log_error(f"  ABORTANDO auto-commit por segurança")
        return False
    
    # Build commit message
    protocol_version = os.environ.get('HB_PROTOCOL_VERSION', '1.2.0')
    evidence_path = f"docs/hbtrack/evidence/AR_{ar_id}/executor_main.log"
    report_path = f"_reports/testador/AR_{ar_id}/TESTADOR_REPORT.md"
    
    commit_msg = (
        f"feat(ar_{ar_id}): {title} [VERIFICADO]\n\n"
        f"Evidence: {evidence_path}\n"
        f"Report: {report_path}\n"
        f"Protocol: {protocol_version}\n"
        f"Agent: hb_autotest v1.0.0 (auto-commit)\n"
    )
    
    if dry_run:
        log(f"  [DRY-RUN] git commit -m \"{commit_msg[:80]}...\"")
        log(f"  Staged files ({len(staged)}): {', '.join(list(staged)[:3])}")
        return True
    
    # Execute commit
    cmd = ['git', 'commit', '-m', commit_msg]
    ec, stdout, stderr = run_cmd(cmd, repo_root)
    
    if ec != 0:
        log_error(f"AR_{ar_id}: git commit FALHOU (exit={ec})")
        log_error(f"  stderr: {stderr[:500]}")
        return False
    
    log(f"✅ AR_{ar_id}: AUTO-COMMIT executado com sucesso")
    for line in stdout.splitlines()[:3]:
        log(f"  commit> {line.strip()}")
    
    return True


# ========== LOOP PRINCIPAL ==========

def process_ar(repo_root: Path, ar_info: dict, processed: set, dry_run: bool) -> None:
    """
    Processa uma AR em EM_EXECUCAO.
    Ciclo: verify → seal → done.
    """
    ar_id = ar_info["id"]
    title = ar_info["title"]
    ev_rel = get_evidence_rel_path(ar_id)

    # Verificar se evidence está staged
    staged = get_staged_files(repo_root)
    if ev_rel not in staged:
        # Evidence não staged — Executor ainda não terminou
        return

    verify_key = (ar_id, 'verify')
    if verify_key in processed:
        # Já tentamos verify nesta sessão — aguardar mudança de estado
        return

    log(f"AR_{ar_id} [{title}]: evidence staged → iniciando hb verify...")

    # Executar hb verify
    ec, stdout, stderr = run_hb_verify(repo_root, ar_id, dry_run)

    output_lines = (stdout + "\n" + stderr).strip().splitlines()
    for line in output_lines[:10]:  # mostrar primeiras 10 linhas
        if line.strip():
            log(f"  verify> {line.rstrip()}")

    processed.add(verify_key)

    if ec != 0:
        log_error(f"AR_{ar_id}: hb verify FALHOU (exit={ec}) — AR marcada como 🔴 REJEITADO")
        log(f"  Executor deve corrigir e re-stage a evidence.")
        # Registrar falha no dispatch
        _write_dispatch_note(repo_root, ar_id, "REJEITADO", stderr or stdout, dry_run)
        return

    # Sucesso! Agora stage TESTADOR_REPORT + AR + _INDEX
    log(f"AR_{ar_id}: hb verify ✅ SUCESSO — staging artefatos...")

    # 1. TESTADOR_REPORT (diretório completo)
    report_path = get_testador_report_path(repo_root, ar_id)
    if report_path:
        report_dir = str(Path(report_path).parent)
        git_add(repo_root, report_dir, dry_run)
        log(f"  staged: {report_dir}")
    else:
        log_error(f"AR_{ar_id}: TESTADOR_REPORT não encontrado na AR — seal pode falhar")

    # 2. AR atualizada (com ✅ SUCESSO stamp)
    ar_file = find_ar_file(repo_root, ar_id)
    if ar_file:
        ar_rel = str(ar_file.relative_to(repo_root)).replace('\\', '/')
        git_add(repo_root, ar_rel, dry_run)
        log(f"  staged: {ar_rel}")

    # v1.1.0: _INDEX.md NÃO é mais staged pelo autotest (AR-First pipeline)
    # Index é cache opcional — será reconstruído por hb seal ou hb index

    # Aguardar git settle
    if not dry_run:
        time.sleep(0.5)

    # Executar hb seal
    seal_reason = (
        "auto-seal: triple_consistency=OK, executor_exit=0, "
        "temporal_check=PASS — hb_autotest daemon v1.0.0"
    )
    log(f"AR_{ar_id}: rodando hb seal...")
    seal_ec, seal_out, seal_err = run_hb_seal(repo_root, ar_id, seal_reason, dry_run)

    seal_output = (seal_out + "\n" + seal_err).strip()
    for line in seal_output.splitlines()[:5]:
        if line.strip():
            log(f"  seal> {line.rstrip()}")

    if seal_ec != 0:
        log_error(f"AR_{ar_id}: hb seal FALHOU (exit={seal_ec})")
        log(f"  Verificar pré-condições: evidence staged, TESTADOR_REPORT staged, status ✅ SUCESSO")
        return

    # Seal OK — stage AR selada
    log(f"AR_{ar_id}: ✅ VERIFICADO — staging artefatos finais...")
    if ar_file:
        ar_rel = str(ar_file.relative_to(repo_root)).replace('\\', '/')
        git_add(repo_root, ar_rel, dry_run)
    # v1.1.0: NÃO stage _INDEX.md — AR-First pipeline

    log(f"✅ AR_{ar_id} [{title}]: VERIFICADO e staged — pronto para commit")
    
    # Auto-commit opt-in (se HB_AUTO_COMMIT=1)
    auto_commit_if_enabled(repo_root, ar_id, title, dry_run)
    
    _write_dispatch_note(repo_root, ar_id, "VERIFICADO", "auto-seal OK", dry_run)


def _write_dispatch_note(repo_root: Path, ar_id: str, status: str, reason: str, dry_run: bool) -> None:
    """Escreve nota de dispatch para o Arquiteto/Executor saberem o resultado."""
    if dry_run:
        return
    dispatch_dir = repo_root / DISPATCH_DIR
    dispatch_dir.mkdir(parents=True, exist_ok=True)
    note_file = dispatch_dir / f"testador_result_{ar_id}.json"
    note = {
        "ar_id": ar_id,
        "status": status,
        "reason": reason,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "agent": "hb_autotest",
    }
    note_file.write_text(json.dumps(note, indent=2, ensure_ascii=False), encoding='utf-8')


def main_loop(poll_interval: int, once: bool, dry_run: bool) -> None:
    """Loop principal do daemon."""
    repo_root = get_repo_root()
    processed: set = set()  # (ar_id, action) — evita re-processamento na mesma sessão

    if dry_run:
        log("MODO DRY-RUN ativo — nenhuma ação real será executada")
    log(f"Iniciado. Repo: {repo_root}")
    log(f"Poll interval: {poll_interval}s | Loop: {'não' if once else 'sim'}")
    log("v1.1.0 AR-First: Varrendo ARs diretamente (sem _INDEX.md)...")
    log("Critérios: Status EM_EXECUCAO + evidence existe + evidence staged + sem testador_report staged")
    log("-" * 60)

    while True:
        # v1.1.0: detecção AR-First — lê ARs diretamente
        em_execucao = find_ars_ready_for_verify(repo_root)

        if em_execucao:
            log(f"ARs elegíveis para verify: {[a['id'] for a in em_execucao]}")
            for ar_info in em_execucao:
                try:
                    process_ar(repo_root, ar_info, processed, dry_run)
                except Exception as e:
                    log_error(f"AR_{ar_info['id']}: erro inesperado: {e}")
        else:
            # Limpar processed quando não há mais ARs elegíveis (novo ciclo)
            if processed:
                log("Nenhuma AR elegível para verify — resetando estado interno.")
                processed.clear()

        if once:
            break

        time.sleep(poll_interval)


# ========== ENTRY POINT ==========

def main() -> None:
    parser = argparse.ArgumentParser(
        description="HB Track Auto-Testador Daemon (Protocol v1.2.0+)"
    )
    parser.add_argument(
        "--loop", type=int, default=POLL_INTERVAL_DEFAULT,
        help=f"Intervalo entre polls em segundos (default: {POLL_INTERVAL_DEFAULT})"
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Executar uma vez e sair (sem loop contínuo)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Apenas reportar ações sem executar (diagnóstico)"
    )
    args = parser.parse_args()

    try:
        main_loop(
            poll_interval=args.loop,
            once=args.once,
            dry_run=args.dry_run,
        )
    except KeyboardInterrupt:
        log("Daemon encerrado pelo usuário (Ctrl+C).")


if __name__ == "__main__":
    main()
