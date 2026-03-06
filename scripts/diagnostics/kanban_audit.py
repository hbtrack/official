#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kanban_audit.py — Auditoria determinística: Kanban vs estado real das ARs

Uso:
    python scripts/diagnostics/kanban_audit.py [--verbose] [--patch-only]

Saída:
    Tabela de diagnóstico com classificação de cada AR executor-facing
    + Patch proposto para corrigir entradas divergentes no Kanban

Classificações:
    ✅ CLEAR_ADVANCE    — log OK + WS clean + PASS stdout + result PASS
                          → item do Kanban deve refletir "VERIFICADO" ou "Aguardando Testador"
    ⏳ AWAITING_TESTADOR — log OK + WS clean + PASS stdout + sem result PASS
                          → deve aparecer como "Aguardando Testador (Triple-Run)"
    🔴 NEEDS_REDO       — log existe mas WS dirty OU sem PASS no stdout
                          → deve aparecer como REDO com motivo
    ⬜ NOT_STARTED       — sem executor_main.log
                          → READY legítimo
    ✅ SEALED           — result.json com verdict PASS E kanban mostra VERIFICADO/selado
                          → consistente, sem divergência
"""

import sys
import re
import json
import argparse
from pathlib import Path

# Configurar stdout para UTF-8 (Windows fix — igual a hb_cli.py)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ── Repositório ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
KANBAN_PATH = REPO_ROOT / "docs" / "hbtrack" / "Hb Track Kanban.md"
EVIDENCE_BASE = REPO_ROOT / "docs" / "hbtrack" / "evidence"
TESTADOR_BASE = REPO_ROOT / "_reports" / "testador"

# ── Regex para extrair AR IDs de linhas Kanban ─────────────────────────────────
# Captura: AR_202, AR_002.5_A, AR_077, ...
AR_ID_RE = re.compile(r"\bAR[_\s]?(\d+(?:\.\d+)?(?:_[A-Z])?)\b")

# Seções executor-facing: qualquer header que contenha estas palavras-chave
EXECUTOR_SECTION_HEADERS = re.compile(
    r"(Em Execução|READY|PENDENTE|REDO|Backlog|aguardando Executor|Evidence Pack missing)",
    re.IGNORECASE,
)

# Linhas que indicam que uma AR já foi selada pelo humano (não precisa de ação do Executor)
SEALED_INDICATORS = re.compile(
    r"✅\s*VERIFICADO|hb seal \d+ ✅|selad[oa]|SUCESSO.*hb seal",
    re.IGNORECASE,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def parse_ar_id(raw: str) -> str:
    """Normaliza AR ID para o formato usado nos diretórios (sem prefixo AR_)."""
    return raw.strip().replace(" ", "_")


def evidence_log_path(ar_id: str) -> Path:
    return EVIDENCE_BASE / f"AR_{ar_id}" / "executor_main.log"


def read_log(ar_id: str) -> dict | None:
    """
    Lê executor_main.log e retorna campos relevantes.
    Retorna None se o arquivo não existir.
    """
    log_file = evidence_log_path(ar_id)
    if not log_file.exists():
        return None

    text = log_file.read_text(encoding="utf-8", errors="replace")
    result = {
        "raw": text,
        "exit_code": None,
        "ws_clean": None,
        "ws_status": None,
        "dirty_files": None,
        "has_pass": False,
    }

    for line in text.splitlines():
        if line.startswith("Exit Code:"):
            try:
                result["exit_code"] = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("Workspace Clean:"):
            result["ws_clean"] = line.split(":", 1)[1].strip().lower() in ("true",)
        elif line.startswith("Workspace Status:"):
            result["ws_status"] = line.split(":", 1)[1].strip()
        elif line.startswith("Dirty Files:"):
            result["dirty_files"] = line.split(":", 1)[1].strip()

    # Verifica PASS no bloco STDOUT
    in_stdout = False
    for line in text.splitlines():
        if line.strip() == "--- STDOUT ---":
            in_stdout = True
            continue
        if line.strip().startswith("---") and in_stdout:
            in_stdout = False
        if in_stdout and re.search(rf"PASS\s+AR[_\s]?{re.escape(ar_id)}", line, re.IGNORECASE):
            result["has_pass"] = True
            break

    return result


def find_result_json(ar_id: str) -> dict | None:
    """
    Procura _reports/testador/AR_<id>_*/result.json.
    Retorna o conteúdo do result.json mais recente se verdict == PASS.
    """
    pattern = f"AR_{ar_id}_*"
    candidates = sorted(TESTADOR_BASE.glob(f"{pattern}/result.json"))
    for candidate in reversed(candidates):
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
            # HB Track grava status="SUCESSO" (não "PASS") — aceitar ambos
            ok_status = data.get("status") in ("PASS", "SUCESSO")
            ok_verdict = data.get("verdict") in ("PASS", "SUCESSO")
            if ok_status or ok_verdict:
                return data
        except Exception:
            continue
    return None


def classify(ar_id: str, kanban_line: str) -> tuple[str, str]:
    """
    Retorna (classificação, motivo).
    """
    # Se a linha já indica VERIFICADO/selado → consistente
    if re.search(r"✅\s*VERIFICADO", kanban_line):
        return "✅ VERIFICADO", "Kanban já marca como VERIFICADO"

    log = read_log(ar_id)
    if log is None:
        return "⬜ NOT_STARTED", "executor_main.log não existe"

    # result.json SUCESSO é a fonte de verdade mais forte — verificado pelo Testador.
    # Classificar ANTES de checar ws_clean do executor log: o WS no momento do
    # hb report é irrelevante se o Testador já confirmou triple-run OK.
    result = find_result_json(ar_id)
    if result is not None:
        triple = result.get("triple_consistency", "?")
        return "✅ CLEAR_ADVANCE", f"result.json SUCESSO — triple={triple} (hb seal pendente)"

    # Sem result.json: checar integridade do executor log
    if log["ws_clean"] is False:
        dirty = log.get("dirty_files") or log.get("ws_status") or "?"
        return "🔴 NEEDS_REDO", f"Workspace Clean: False no executor log — Dirty: {dirty}"

    if log["exit_code"] != 0:
        return "🔴 NEEDS_REDO", f"Exit Code: {log['exit_code']} (validation falhou)"

    # log OK + WS limpo + sem result.json → aguarda hb verify
    if log["has_pass"]:
        return "⏳ AWAITING_TESTADOR", "log OK + WS clean + PASS stdout (sem result PASS)"

    return "⏳ AWAITING_TESTADOR", "log OK + WS clean + exit 0 (sem PASS literal no stdout)"


def propose_kanban_text(ar_id: str, classification: str, original_line: str) -> str | None:
    """
    Sugere o texto substituto para a linha do Kanban, se houver divergência.
    Retorna None se não houver divergência.
    """
    current = original_line.strip()

    if classification == "✅ VERIFICADO":
        return None  # já consistente

    if classification == "⬜ NOT_STARTED":
        # Se a linha já diz READY, está correto
        if "READY" in current or "ready" in current.lower():
            return None
        return f"  → sugestão: marcar {ar_id} como 🔲 READY (evidence ainda não existe)"

    if classification == "⏳ AWAITING_TESTADOR":
        if "Aguardando Testador" in current or "Triple-Run" in current:
            return None  # já correto
        return f"  → sugestão: marcar AR_{ar_id} como '✅ Evidence Exit 0 → Aguardando Testador (Triple-Run)'"

    if classification == "✅ CLEAR_ADVANCE":
        # CLEAR_ADVANCE = result.json SUCESSO mas hb seal não rodou ainda
        # Kanban deve dizer "SUCESSO — hb seal pendente" ou VERIFICADO
        if re.search(r"SUCESSO|VERIFICADO|seal", current, re.IGNORECASE):
            return None
        return f"  → sugestão: marcar AR_{ar_id} como '✅ SUCESSO — hb seal <id> pendente (HUMANO)'"

    if classification == "🔴 NEEDS_REDO":
        if "REDO" in current or "BLOQUEADA" in current or "Evidence Pack missing" in current:
            return None
        return f"  → sugestão: marcar AR_{ar_id} como '⚠️ REDO ou 🛠️ Em Execução (Evidence Pack missing)'"

    return None


# ── Extração do Kanban ─────────────────────────────────────────────────────────

def extract_executor_ars(kanban_text: str) -> list[dict]:
    """
    Percorre o Kanban linha a linha, rastreando a seção corrente.
    Retorna lista de {ar_id, kanban_line, line_no, section}.
    """
    entries = []
    current_section = ""
    in_executor_section = False

    lines = kanban_text.splitlines()
    for line_no, line in enumerate(lines, start=1):
        # Detecta cabeçalho de seção (## ou ### ou ####)
        if re.match(r"^#{1,4}\s", line):
            current_section = line.strip()
            in_executor_section = bool(EXECUTOR_SECTION_HEADERS.search(line))
            continue

        if not in_executor_section:
            continue

        # Pula linhas que já estão como VERIFICADO (consistentes, sem ação necessária)
        # mas ainda extrai o AR ID para diagnóstico
        matches = AR_ID_RE.findall(line)
        for raw_id in matches:
            ar_id = parse_ar_id(raw_id)
            # Evita duplicatas por linha
            if not any(e["ar_id"] == ar_id and e["line_no"] == line_no for e in entries):
                entries.append({
                    "ar_id": ar_id,
                    "kanban_line": line,
                    "line_no": line_no,
                    "section": current_section,
                })

    return entries


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Auditoria Kanban vs estado real das ARs")
    parser.add_argument("--verbose", action="store_true", help="Mostra detalhes de cada AR")
    parser.add_argument("--patch-only", action="store_true", help="Mostra apenas divergências com patch proposto")
    args = parser.parse_args()

    if not KANBAN_PATH.exists():
        print(f"ERRO: Kanban não encontrado em {KANBAN_PATH}", file=sys.stderr)
        sys.exit(2)

    kanban_text = KANBAN_PATH.read_text(encoding="utf-8")
    entries = extract_executor_ars(kanban_text)

    if not entries:
        print("Nenhuma AR executor-facing encontrada no Kanban.")
        sys.exit(0)

    # Deduplicar por AR ID (um AR pode aparecer em múltiplas linhas — mantém a primeirа ocorrência)
    seen = {}
    deduped = []
    for e in entries:
        if e["ar_id"] not in seen:
            seen[e["ar_id"]] = e
            deduped.append(e)

    # Classificar
    results = []
    for e in deduped:
        clf, reason = classify(e["ar_id"], e["kanban_line"])
        patch = propose_kanban_text(e["ar_id"], clf, e["kanban_line"])
        results.append({**e, "classification": clf, "reason": reason, "patch": patch})

    # ── Contadores ──
    counters = {}
    for r in results:
        k = r["classification"]
        counters[k] = counters.get(k, 0) + 1

    # ── Impressão ──
    divergences = [r for r in results if r["patch"] is not None]

    if not args.patch_only:
        print("=" * 90)
        print("KANBAN AUDIT — HB Track")
        print("=" * 90)
        print(f"{'AR_ID':<14} {'Classificação':<26} {'Seção Kanban':<40} {'Motivo'}")
        print("-" * 90)
        for r in sorted(results, key=lambda x: x["classification"]):
            sec = r["section"][:38]
            reason = r["reason"][:60]
            print(f"AR_{r['ar_id']:<10} {r['classification']:<26} {sec:<40} {reason}")
        print()
        print("RESUMO:")
        for clf, count in sorted(counters.items()):
            print(f"  {clf}: {count}")
        print()

    if divergences:
        print("=" * 90)
        print("PATCH PROPOSTO — linhas com divergência (não aplicado automaticamente):")
        print("=" * 90)
        for r in divergences:
            print(f"\n[Kanban L{r['line_no']}] AR_{r['ar_id']} — {r['section']}")
            print(f"  ATUAL:    {r['kanban_line'].strip()[:120]}")
            print(f"  STATUS:   {r['classification']} — {r['reason']}")
            print(f"  {r['patch']}")
        print()
        print(f"Total de divergências encontradas: {len(divergences)}")
        sys.exit(1)
    else:
        print("✅ Nenhuma divergência detectada entre Kanban e estado real das ARs.")
        sys.exit(0)


if __name__ == "__main__":
    main()
