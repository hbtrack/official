#!/usr/bin/env python3
"""
Gate: check_trace_contract.py  —  DOC-GATE-020

Valida rastreabilidade do handoff (_reports/ARQUITETO.yaml).
Gate WARN-only: nunca bloqueia execução, mas o Testador trata WARN como FAIL_ACTIONABLE.

Heurística AR-centric (2 níveis):
  Nível A: handoff tem AR IDs   → AR "não é vazia", vale checar trace.
  Nível B: handoff tem sinais de mudança comportamental/spec
           (contract, invariant, flow, schema, pytest, endpoint, …)
           → exige declaração de rastreabilidade.
  Supressão explícita: campo "TRACE: N/A" silencia o gate sem WARN.

Exit codes (canônico HB Track):
  0: PASS (com ou sem WARNs)
  4: BLOCKED_INPUT (handoff não encontrado/ilegível)

Uso:
  python scripts/gates/check_trace_contract.py [handoff_path]

  handoff_path   default: _reports/ARQUITETO.yaml
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

EXIT_PASS = 0
EXIT_BLOCKED_INPUT = 4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_text(path: Path) -> Tuple[bool, str]:
    try:
        return True, path.read_text(encoding="utf-8", errors="replace")
    except (FileNotFoundError, OSError):
        return False, ""


def _has_any(text: str, patterns: List[str]) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE | re.MULTILINE) for p in patterns)


def _extract_ar_ids(text: str) -> List[str]:
    """
    Duplicado intencional (standalone). Prioridade: lista explícita → AR_ID → fallback.
    Quando 'AR IDs: [N,M]' está presente, retorna SOMENTE esses IDs.
    """
    m = re.search(r"AR\s*IDs?\s*\*\*?\s*:\s*\[([^\]]+)\]", text, flags=re.IGNORECASE)
    if not m:
        m = re.search(r"AR\s*IDs?\s*:\s*\[([^\]]+)\]", text, flags=re.IGNORECASE)
    if m:
        ids: set[str] = set()
        for token in re.split(r"[,\s]+", m.group(1).strip()):
            token = token.strip().strip('"').strip("'")
            if token.isdigit():
                ids.add(token)
        return sorted(ids)
    ids = set()
    for m2 in re.finditer(r"\bAR[_\-\s]?ID\s*:\s*(\d+)\b", text, flags=re.IGNORECASE):
        ids.add(m2.group(1))
    if ids:
        return sorted(ids)
    for m3 in re.finditer(r"\bAR[_\-](\d{3,})\b", text, flags=re.IGNORECASE):
        ids.add(m3.group(1))
    return sorted(ids)


def _extract_ar_block(handoff: str, ar_id: str) -> str:
    """Extrai o bloco do handoff relevante para um AR_ID específico.

    Duplicado intencional de check_handoff_contract._extract_ar_block —
    scripts de gate são entrypoints standalone.
    """
    heading_re = re.compile(
        rf"^(##[^\n]*\bAR[_\-]{re.escape(ar_id)}\b[^\n]*)$",
        flags=re.MULTILINE | re.IGNORECASE,
    )
    m = heading_re.search(handoff)
    if m:
        tail = handoff[m.end():]
        next_h = re.search(r"^##\s", tail, flags=re.MULTILINE)
        end = m.end() + next_h.start() if next_h else len(handoff)
        return handoff[m.start():end]

    mm = re.search(rf"\bAR[_\-]{re.escape(ar_id)}\b", handoff, flags=re.IGNORECASE)
    if mm:
        start = max(0, mm.start() - 300)
        end = min(len(handoff), mm.end() + 2000)
        return handoff[start:end]

    return ""


# ---------------------------------------------------------------------------
# Lógica de trace
# ---------------------------------------------------------------------------

def _has_trace_suppression(handoff: str) -> bool:
    """Supressão explícita: TRACE: N/A ou CLASS: GOVERNANCE_ONLY silencia o gate."""
    return _has_any(handoff, [
        r"\bTRACE\s*:\s*N/?A\b",
        r"\bTRACE\s*:\s*governance\b",
        r"\bCLASS\s*:\s*GOVERNANCE_ONLY\b",
    ])


def _has_behavioral_signals(handoff: str) -> bool:
    """
    Nível B: sinais de mudança comportamental/spec.
    Se qualquer um destes aparece, a AR não é puramente governança.
    """
    return _has_any(handoff, [
        r"\bcontract\b",
        r"\binvariant\b",
        r"\bflow\b",
        r"\bscreen\b",
        r"\btest_matrix",        # prefixo: casa TEST_MATRIX e TEST_MATRIX_TRAINING
        r"\bpytest\b",
        r"\bendpoint\b",
        r"\bschema\b",
        r"\bservice\b",
        r"\buser.?flow\b",
        r"\bscreens.?spec\b",
        r"\bDEC-",
        r"\bP0\b",
        r"\bUS-\d",
        r"\bREQ\b",
    ])


def _has_trace_link(handoff: str) -> bool:
    """
    Declaração de rastreabilidade aceita (campo TRACE: preenchido ou arquivo referenciado).
    """
    return _has_any(handoff, [
        r"\bTRACE\s*:(?!\s*N/?A)(?!\s*governance)",   # TRACE: <algo> (não N/A)
        r"\bTEST_MATRIX",            # prefixo: casa TEST_MATRIX e TEST_MATRIX_TRAINING
        r"\bINVARIANTS_TRAINING\b",
        r"Atualizar.*TEST_MATRIX",
        r"Trace\s+updates?\s*:",
        r"_CONTRACT\.md\b",
        r"_FLOWS\.md\b",
        r"_SCREENS_SPEC\.md\b",
    ])


def _check_trace_warns(handoff: str) -> List[str]:
    """
    Retorna lista de WARNs (pode ser vazia).

    Algoritmo por AR_ID:
      1. Sem AR IDs → não avaliável → []
      2. Supressão global no handoff → []
      3. Para cada AR_ID: bloco com sinais comportamentais + sem trace link → WARN
      4. Sem sinais comportamentais em nenhum AR → []
    """
    warns: List[str] = []

    ar_ids = _extract_ar_ids(handoff)
    if not ar_ids:
        return warns

    # Supressão global
    if _has_trace_suppression(handoff):
        return warns

    missing: List[str] = []
    for ar_id in ar_ids:
        block = _extract_ar_block(handoff, ar_id) or handoff
        if _has_trace_suppression(block):
            continue
        if _has_behavioral_signals(block) and not _has_trace_link(block):
            missing.append(f"AR_{ar_id}")

    if missing:
        warns.append(
            f"handoff: TRACE ausente para {', '.join(missing)} — "
            "AR declara mudança comportamental/spec mas não vincula rastreabilidade. "
            "Adicione: 'TRACE: <arquivo/linhas afetadas>' "
            "ou 'TRACE: N/A (governance)' para suprimir."
        )

    return warns


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv: List[str]) -> int:
    handoff_path = (
        Path(argv[1]) if len(argv) > 1 and argv[1].strip() else Path("_reports/ARQUITETO.yaml")
    )

    ok, handoff = _read_text(handoff_path)
    if not ok:
        print(f"BLOCKED_INPUT: handoff não encontrado/ilegível: {handoff_path}")
        return EXIT_BLOCKED_INPUT

    warns = _check_trace_warns(handoff)

    print("PASS: check_trace_contract")
    ar_ids = _extract_ar_ids(handoff)
    if ar_ids:
        print(f"  AR IDs avaliados: {', '.join(ar_ids)}")
    for w in warns:
        print(f"  ⚠️  WARN: {w}")

    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
