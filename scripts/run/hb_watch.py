#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HB Track - Sentinela + Dispatcher de Contexto
Arquivo: scripts/run/hb_watch.py
Versao: 1.2.2
Protocolo: v1.2.0+
"""

import os
import re
import json
import subprocess
import time
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path


# Force UTF-8 output on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class Colors:
    HEADER = '[95m'
    BLUE   = '[94m'
    CYAN   = '[96m'
    GREEN  = '[92m'
    YELLOW = '[93m'
    RED    = '[91m'
    END    = '[0m'
    BOLD   = '[1m'


# ========== CONFIGURACAO ==========
INDEX_PATH   = "docs/hbtrack/_INDEX.md"
AR_DIR       = "docs/hbtrack/ars"
DISPATCH_DIR = "_reports/dispatch"
HB_LOCK      = ".hb_lock"  # Lock file: impede execuções concorrentes

TRIGGERS = {
    "architect": ["PROPOSTA", "STUB", "REJEITADO", "NEEDS_REVIEW"],
    "executor":  ["🔲 PENDENTE"],
    "testador":  ["🏗️ EM_EXECUCAO"],
}

def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def is_locked(repo_root: Path) -> bool:
    """Verifica se .hb_lock existe (execução concorrente ativa)."""
    return (repo_root / HB_LOCK).exists()


def get_staged_evidence_files(repo_root: Path) -> list:
    """Retorna lista de evidence files staged via git diff --cached --name-only."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = result.stdout.strip().splitlines()
        return [l for l in lines if "executor_main.log" in l or "doc_gates.log" in l]
    except Exception:
        return []


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_field(content: str, pattern: str) -> str:
    """Extrai campo de texto da AR via regex."""
    m = re.search(pattern, content, re.DOTALL)
    return m.group(1).strip() if m else ""

def read_ar_details(repo_root: Path, ar_id_num: str) -> dict:
    """
    Le o arquivo AR_<id>_*.md e extrai campos relevantes para o dispatcher.
    Retorna dict com: ar_file, title, write_scope, validation_command,
                      ssot_touches, rollback_plan, status
    """
    ar_dir = repo_root / AR_DIR
    # Busca recursiva - ARs podem estar em subpastas por modulo
    matches = list(ar_dir.rglob(f"AR_{ar_id_num}_*.md"))
    if not matches:
        return {}
    ar_file = matches[0]
    try:
        content = ar_file.read_text(encoding="utf-8")
    except Exception:
        return {}
    ar_rel = str(ar_file.relative_to(repo_root)).replace("\\", "/")
    # Extrair write_scope
    write_scope_raw = _extract_field(content, r"## Write Scope\s*\n(.*?)(?=\n##|\Z)")
    write_scope = [
        line.strip().lstrip("-").strip()
        for line in write_scope_raw.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    # Extrair validation_command
    validation_cmd = _extract_field(
        content,
        r"## Validation Command.*?\n```[^\n]*\n(.*?)\n```"
    )
    # Extrair ssot_touches
    ssot_pattern = re.findall(r"\[.?\]\s+(docs/ssot/\S+)", content)
    ssot_checked = re.findall(r"\[x\]\s+(docs/ssot/\S+)", content)
    # Extrair rejection_reason
    rejection = _extract_field(content, r"Reason:\s*(.+?)(?=\n|$)")
    # Status atual
    status_m = re.search(r"\*\*Status\*\*:\s*(.+)", content)
    status = status_m.group(1).strip() if status_m else ""
    return {
        "ar_file": ar_rel,
        "write_scope": [ws for ws in write_scope if ws],
        "validation_command": validation_cmd,
        "ssot_touches": ssot_checked or ssot_pattern,
        "rejection_reason": rejection,
        "status": status,
    }

def parse_index(repo_root: Path) -> list:
    """
    Le _INDEX.md e retorna lista de ARs.
    Cada item: {"id": "055", "id_num": "055", "title": "...", "status": "...", "evidence": "..."}
    """
    index_path = repo_root / INDEX_PATH
    if not index_path.exists():
        return None  # Sinaliza erro
    ars = []
    pattern = re.compile(r"\|\s*(AR_([\w.]+))\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]*)\s*\|")
    try:
        for line in index_path.read_text(encoding="utf-8").splitlines():
            m = pattern.search(line)
            if not m:
                continue
            ar_full  = m.group(1).strip()
            ar_num   = m.group(2).strip()
            title    = m.group(3).strip()[:50]
            status   = m.group(4).strip()
            evidence = m.group(5).strip() if m.lastindex >= 5 else "\u2014"
            if ar_num == "ID":
                continue
            id_match = re.match(r"^(\d+)", ar_num)
            id_num = id_match.group(1) if id_match else ar_num
            ars.append({
                "id": ar_full,
                "id_num": id_num,
                "title": title,
                "status": status,
                "evidence": evidence,
            })
    except Exception as e:
        print(f"Erro ao ler _INDEX.md: {e}")
        return []
    return ars

def build_executor_context(repo_root: Path, action_items: list, ars: list) -> dict:
    """Constroi contexto rico para sessao Claude Code do Executor."""
    pending_ars = []
    for ar_id in action_items:
        ar_info = next((a for a in ars if a["id"] == ar_id), None)
        if not ar_info:
            continue
        id_num  = ar_info["id_num"]
        details = read_ar_details(repo_root, id_num)
        val_cmd = details.get("validation_command", "<ver AR>")
        ar_file_val = details.get("ar_file", f"{AR_DIR}/{ar_id}_*.md")
        write_scope_val = details.get("write_scope", [])
        next_action = (
            f"1. READ {ar_file_val} completamente\n"
            f"2. Preencher secao Analise de Impacto\n"
            f"3. Implementar mudancas em: {write_scope_val}\n"
            f"4. Executar: python scripts/run/hb_cli.py report {id_num} "
            + '"' + val_cmd + '"' + "\n"
            f"5. Aguardar hb_autotest.py fazer verify+seal automaticamente"
        )
        pending_ars.append({
            "id": id_num,
            "ar_id_full": ar_id,
            "ar_file": ar_file_val,
            "title": ar_info["title"],
            "write_scope": write_scope_val,
            "validation_command": val_cmd,
            "ssot_touches": details.get("ssot_touches", []),
            "next_action": next_action,
        })
    return {
        "role": "executor",
        "protocol": "v1.2.0",
        "timestamp_utc": now_utc(),
        "contract": "docs/_canon/contratos/Executor Contract.md",
        "pending_ars": pending_ars,
        "instructions": (
            "Voce e o Executor. Para cada AR em pending_ars:\n"
            "  1. Leia o ar_file completo antes de agir\n"
            "  2. Implemente APENAS o que esta em write_scope\n"
            "  3. Execute hb report com o validation_command EXATO\n"
            "  4. Faca git add da evidence + codigo + AR + _INDEX.md\n"
            "  5. hb_autotest.py detectara a evidence staged e rodara verify+seal"
        ),
    }

def build_architect_context(repo_root: Path, action_items: list, ars: list) -> dict:
    """Constroi contexto rico para sessao Claude Code do Arquiteto."""
    rejected     = []
    needs_review = []
    proposta     = []
    for ar_id in action_items:
        ar_info = next((a for a in ars if a["id"] == ar_id), None)
        if not ar_info:
            continue
        id_num  = ar_info["id_num"]
        details = read_ar_details(repo_root, id_num)
        status  = ar_info["status"]
        item = {
            "id": id_num,
            "ar_id_full": ar_id,
            "ar_file": details.get("ar_file", ""),
            "title": ar_info["title"],
            "status": status,
            "rejection_reason": details.get("rejection_reason", ""),
        }
        if "REJEITADO" in status:
            item["next_action"] = (
                f"Analisar rejection_reason e revisar plano JSON ou validation_command para AR_{id_num}"
            )
            rejected.append(item)
        elif "NEEDS_REVIEW" in status or "REVIEW" in status:
            item["next_action"] = f"Intervencao manual requerida em AR_{id_num}"
            needs_review.append(item)
        elif "PROPOSTA" in status or "STUB" in status:
            item["next_action"] = f"Criar plano JSON para AR_{id_num}"
            proposta.append(item)
    return {
        "role": "architect",
        "protocol": "v1.2.0",
        "timestamp_utc": now_utc(),
        "contract": "docs/_canon/contratos/Arquiteto Contract.md",
        "rejected_ars": rejected,
        "needs_review_ars": needs_review,
        "proposta_ars": proposta,
        "instructions": (
            "Voce e o Arquiteto. Acoes requeridas:\n"
            "  REJEITADO: analisar rejection_reason -> corrigir plano JSON -> hb plan --dry-run -> handoff Executor\n"
            "  NEEDS_REVIEW: intervencao humana/analise de impacto\n"
            "  PROPOSTA/STUB: criar plano JSON em docs/_canon/planos/ e executar hb plan"
        ),
    }

def write_dispatch_files(
    repo_root: Path,
    mode: str,
    action_items: list,
    ars: list,
) -> None:
    """Escreve .todo e _context.json para o modo ativo."""
    dispatch_dir = repo_root / DISPATCH_DIR
    dispatch_dir.mkdir(parents=True, exist_ok=True)
    todo_file    = dispatch_dir / f"{mode}.todo"
    context_file = dispatch_dir / f"{mode}_context.json"
    if action_items:
        todo_file.write_text("\n".join(action_items), encoding="utf-8")
        if mode == "executor":
            context = build_executor_context(repo_root, action_items, ars)
        elif mode == "architect":
            context = build_architect_context(repo_root, action_items, ars)
        else:
            # testador: hb_autotest.py cuida disso; contexto minimal aqui
            context = {
                "role": mode,
                "timestamp_utc": now_utc(),
                "action_items": action_items,
                "note": "Use hb_autotest.py para verificacao automatica",
            }
        context_file.write_text(
            json.dumps(context, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    else:
        if todo_file.exists():
            todo_file.unlink()
        if context_file.exists():
            context_file.unlink()

def render_dashboard(repo_root: Path, mode: str, ars: list) -> list:
    """
    Exibe dashboard colorido e retorna lista de action_items para o modo ativo.
    """
    clear_screen()
    now = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.BOLD}{Colors.HEADER}=== HB TRACK SENTINELA v1.2.2 - {now} ==={Colors.END}")
    print(f"{Colors.BOLD}MODO ATIVO: {Colors.CYAN}{mode.upper()}{Colors.END}")
    if ars is None:
        print(f"\n{Colors.RED}{Colors.BOLD}\u274c ERRO: {INDEX_PATH} nao encontrado{Colors.END}")
        print(f"CWD: {os.getcwd()}")
        return []
    print("-" * 80)
    print(f"{Colors.BOLD}{'ID':<12} | {'STATUS':<18} | {'TITULO'}{Colors.END}")
    print("-" * 80)
    action_items = []
    for ar in ars:
        status_text = ar["status"]
        color = Colors.END
        if "\u2705" in status_text:
            color = Colors.GREEN
        elif "\U0001f3d7\ufe0f" in status_text:
            color = Colors.YELLOW
        elif "\U0001f534" in status_text or "\u274c" in status_text:
            color = Colors.RED
        elif any(t in status_text for t in ["PROPOSTA", "PENDENTE", "STUB"]):
            color = Colors.CYAN
        print(f"{ar['id']:<12} | {color}{status_text:<18}{Colors.END} | {ar['title']}")
        triggers = TRIGGERS.get(mode, [])
        if any(token in status_text for token in triggers):
            if mode == "executor":
                if "PENDENTE" in status_text:
                    action_items.append(ar["id"])
            else:
                action_items.append(ar["id"])
    print("-" * 80)
    if action_items:
        print(
            f"{Colors.BOLD}{Colors.YELLOW}"
            f"\U0001f449 ACAO REQUERIDA [{mode.upper()}]: {', '.join(action_items)}"
            f"{Colors.END}"
        )
        context_file = f"{DISPATCH_DIR}/{mode}_context.json"
        print(f"   Contexto rico: {context_file}")
    else:
        print(f"{Colors.GREEN}\u2615 AGUARDANDO: Nenhuma tarefa para {mode}.{Colors.END}")
    return action_items

def main():
    parser = argparse.ArgumentParser(description="HB Track Sentinela + Dispatcher (v1.2.2)")
    parser.add_argument(
        "--mode", choices=["architect", "executor", "testador"], required=True
    )
    parser.add_argument(
        "--loop", type=int, default=5,
        help="Intervalo entre polls em segundos (default: 5)"
    )
    args = parser.parse_args()
    repo_root = get_repo_root()
    try:
        while True:
            ars          = parse_index(repo_root)
            action_items = render_dashboard(repo_root, args.mode, ars or [])
            write_dispatch_files(repo_root, args.mode, action_items, ars or [])
            time.sleep(args.loop)
    except KeyboardInterrupt:
        print(f"\n{Colors.BLUE}Sentinela encerrada.{Colors.END}")


if __name__ == "__main__":
    main()
