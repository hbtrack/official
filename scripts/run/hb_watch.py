#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_repo_root() -> Path:
    # hb_watch.py em scripts/run/ -> repo_root é 3 níveis acima
    return Path(__file__).resolve().parent.parent.parent


REPO_ROOT = get_repo_root()

INDEX_PATH = REPO_ROOT / "docs/hbtrack/_INDEX.md"
AR_ROOT = REPO_ROOT / "docs/hbtrack/ars"
EVIDENCE_ROOT = REPO_ROOT / "docs/hbtrack/evidence"
LOCK_FILE = REPO_ROOT / ".hb_lock"

DISPATCH_DIR = REPO_ROOT / "_reports/dispatch"
DISPATCH_EXECUTOR = DISPATCH_DIR / "executor.todo"
DISPATCH_TESTADOR = DISPATCH_DIR / "testador.todo"
DISPATCH_HUMANO = DISPATCH_DIR / "humano.todo"

POLL_SECONDS = 5
MIN_AR_SIZE_BYTES = 200

# Status strings (v1.2.0)
S_PENDENTE = "🔲 PENDENTE"
S_SUCESSO = "✅ SUCESSO"
S_REJEITADO = "🔴 REJEITADO"
S_VERIFICADO = "✅ VERIFICADO"
S_BLOQUEADO_INFRA = "⏸️ BLOQUEADO_INFRA"


def run_cmd(args: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run(
        args,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    return p.returncode, p.stdout, p.stderr


def workspace_lock_present() -> bool:
    return LOCK_FILE.exists()


def read_index_stable() -> Optional[str]:
    """
    Lê _INDEX.md apenas se estiver estável (mtime/size não mudam durante leitura).
    Evita ler durante rebuild parcial.
    """
    if not INDEX_PATH.exists():
        return None

    s1 = INDEX_PATH.stat()
    try:
        txt = INDEX_PATH.read_text(encoding="utf-8")
    except Exception:
        return None
    s2 = INDEX_PATH.stat()

    if s1.st_mtime != s2.st_mtime or s1.st_size != s2.st_size:
        return None  # instável, tentar no próximo ciclo

    # Sanidade mínima: tabela do index existe
    if "| ID |" not in txt or "| Status |" not in txt:
        return None

    return txt


def parse_index_rows(index_text: str) -> List[Dict[str, str]]:
    """
    Parseia linhas da tabela:
    | AR_001 | Título | Status | Evidence |
    Retorna [{ar_id, status, evidence}]
    """
    rows: List[Dict[str, str]] = []
    for line in index_text.splitlines():
        line = line.strip()
        if not line.startswith("| AR_"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 4:
            continue
        ar_id, _, status, evidence = parts[0], parts[1], parts[2], parts[3]
        m = re.match(r"AR_([0-9]{3})$", ar_id)
        if not m:
            continue
        rows.append({"id": m.group(1), "status": status, "evidence": evidence})
    return rows


def find_ar_file(ar_id: str) -> Optional[Path]:
    matches = list(AR_ROOT.rglob(f"AR_{ar_id}_*.md"))
    if not matches:
        return None
    if len(matches) > 1:
        # INTEGRITY GATE: duplicatas são erro, não ambiguidade silenciosa
        raise RuntimeError(
            f"INTEGRITY_ERROR: AR_{ar_id} exists in multiple locations: "
            + ", ".join(str(p) for p in sorted(matches))
        )
    return matches[0]


def ar_is_integrity_ok(ar_path: Path, ar_id: str) -> bool:
    try:
        if ar_path.stat().st_size < MIN_AR_SIZE_BYTES:
            return False
        txt = ar_path.read_text(encoding="utf-8")
    except Exception:
        return False
    if not txt.startswith(f"# AR_{ar_id}"):
        return False
    if "**Status**:" not in txt:
        return False
    return True


def expected_evidence_path(ar_id: str) -> Path:
    return EVIDENCE_ROOT / f"AR_{ar_id}" / "executor_main.log"


def parse_evidence_min(ev_path: Path) -> Dict[str, str]:
    """
    Extrai campos mínimos do evidence canônico.
    """
    out = {"exit_code": "", "timestamp_utc": "", "behavior_hash": ""}
    try:
        txt = ev_path.read_text(encoding="utf-8")
    except Exception:
        return out

    m = re.search(r"Exit Code:\s*(\d+)", txt)
    if m:
        out["exit_code"] = m.group(1).strip()

    m = re.search(r"Timestamp UTC:\s*(.+)", txt)
    if m:
        out["timestamp_utc"] = m.group(1).strip()

    m = re.search(r"Behavior Hash.*:\s*([0-9a-fA-F]{64})", txt)
    if m:
        out["behavior_hash"] = m.group(1).strip()

    return out


def staged_files_set() -> set:
    rc, out, _ = run_cmd(["git", "diff", "--cached", "--name-only"])
    if rc != 0:
        return set()
    return {p.strip().replace("\\", "/") for p in out.splitlines() if p.strip()}


def extract_testador_report_from_ar(ar_text: str) -> Optional[str]:
    reports = re.findall(r"\*\*TESTADOR_REPORT\*\*:\s*`(.+?)`", ar_text)
    if not reports:
        return None
    return reports[-1].strip().replace("\\", "/")


def dispatch_write(path: Path, payload: Dict) -> None:
    DISPATCH_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    print("HB Watcher v1.2.0-aligned ativo. Monitorando _INDEX e pré-condições (AR/Evidence/Stage).")
    last_state = ""

    while True:
        if workspace_lock_present():
            time.sleep(POLL_SECONDS)
            continue

        idx = read_index_stable()
        if not idx:
            time.sleep(POLL_SECONDS)
            continue

        rows = parse_index_rows(idx)
        staged = staged_files_set()

        executor_ready: List[str] = []
        testador_ready: List[str] = []
        humano_ready: List[str] = []
        warnings: List[str] = []

        for r in rows:
            ar_id = r["id"]
            status = r["status"]

            ar_path = find_ar_file(ar_id)
            if not ar_path:
                continue
            if not ar_is_integrity_ok(ar_path, ar_id):
                continue

            ar_txt = ar_path.read_text(encoding="utf-8", errors="replace")
            ev_path = expected_evidence_path(ar_id)
            ev_rel = ev_path.as_posix()

            # Trigger Executor
            if S_PENDENTE in status:
                executor_ready.append(ar_id)
                continue

            # Trigger Testador (baseado em evidence canônico exit 0)
            if ev_path.exists() and (S_SUCESSO not in status) and (S_REJEITADO not in status) and (S_VERIFICADO not in status):
                ev = parse_evidence_min(ev_path)
                if ev["exit_code"] == "0" and ev["timestamp_utc"] and ev["behavior_hash"]:
                    # opcional: exigir evidence staged para evitar “status fantasma”
                    if ev_rel not in staged:
                        warnings.append(f"AR_{ar_id}: evidence canônico existe mas não está STAGED: {ev_rel}")
                    else:
                        testador_ready.append(ar_id)

            # Trigger Humano (seal) — somente quando ✅ SUCESSO + report exists + staged
            if S_SUCESSO in status and S_VERIFICADO not in status:
                rep = extract_testador_report_from_ar(ar_txt)
                if not rep:
                    warnings.append(f"AR_{ar_id}: status ✅ SUCESSO mas AR não declara TESTADOR_REPORT.")
                    continue
                rep_abs = REPO_ROOT / rep
                if not rep_abs.exists():
                    warnings.append(f"AR_{ar_id}: TESTADOR_REPORT declarado mas arquivo não existe: {rep}")
                    continue
                if rep not in staged:
                    warnings.append(f"AR_{ar_id}: TESTADOR_REPORT existe mas não está STAGED: {rep}")
                    continue
                if ev_rel not in staged:
                    warnings.append(f"AR_{ar_id}: evidence canônico não está STAGED: {ev_rel}")
                    continue
                humano_ready.append(ar_id)

        snapshot = json.dumps({
            "executor_ready": executor_ready,
            "testador_ready": testador_ready,
            "humano_ready": humano_ready,
            "warnings": warnings
        }, sort_keys=True)

        if snapshot != last_state:
            dispatch_write(DISPATCH_EXECUTOR, {"trigger": "EXECUTOR", "ar_ids": executor_ready, "warnings": warnings})
            dispatch_write(DISPATCH_TESTADOR, {"trigger": "TESTADOR", "ar_ids": testador_ready, "warnings": warnings})
            dispatch_write(DISPATCH_HUMANO, {"trigger": "HUMANO_SEAL", "ar_ids": humano_ready, "warnings": warnings})

            # stdout ainda útil, mas agora não é o único canal
            if executor_ready:
                print(f"\n[TRIGGER EXECUTOR] {executor_ready}")
            if testador_ready:
                print(f"\n[TRIGGER TESTADOR] {testador_ready}")
            if humano_ready:
                print(f"\n[TRIGGER HUMANO: SEAL] {humano_ready}")
            for w in warnings:
                print(f"⚠️  {w}")

            last_state = snapshot

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()