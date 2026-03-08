#!/usr/bin/env python3
"""
Gate: check_handoff_contract.py

Valida contrato mínimo do handoff (_reports/ARQUITETO.yaml) e, opcionalmente,
do executor_main.log.

Exit codes (canônico HB Track):
- 0: PASS
- 2: FAIL_ACTIONABLE (checks falharam com arquivos presentes)
- 4: BLOCKED_INPUT (arquivo obrigatório não encontrado)

Uso:
  python scripts/gates/check_handoff_contract.py [handoff_path] [executor_log_path]

  handoff_path      default: _reports/ARQUITETO.yaml
  executor_log_path opcional; omitir para validar só o handoff
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

EXIT_PASS = 0
EXIT_FAIL_ACTIONABLE = 2
EXIT_BLOCKED_INPUT = 4


def _read_text(path: Path) -> Tuple[bool, str]:
    try:
        return True, path.read_text(encoding="utf-8", errors="replace")
    except (FileNotFoundError, OSError):
        return False, ""


def _has_any(text: str, patterns: List[str]) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE | re.MULTILINE) for p in patterns)


def _extract_ar_ids(text: str) -> List[str]:
    """
    Extrai AR IDs do handoff.

    Prioridade:
    1. Lista explícita "AR IDs: [235, 236]" ou "**AR IDs**: [235, 236]" — se presente,
       retorna SOMENTE esses IDs (não varre o corpo do texto).
    2. Campo "AR_ID: N" — se presente sem lista explícita.
    3. Fallback: varredura de "AR_###" / "AR-###" no texto inteiro.
    """
    # Prioridade 1: lista explícita (lista canônica do Arquiteto)
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
    # Prioridade 2: AR_ID: N  ou  AR ID: N  (sem lista explícita)
    for m2 in re.finditer(r"\bAR[_\-\s]?ID\s*:\s*(\d+)\b", text, flags=re.IGNORECASE):
        ids.add(m2.group(1))
    if ids:
        return sorted(ids)

    # Fallback: AR_### / AR-### no corpo
    for m3 in re.finditer(r"\bAR[_\-](\d{3,})\b", text, flags=re.IGNORECASE):
        ids.add(m3.group(1))
    return sorted(ids)


def _extract_ar_block(handoff: str, ar_id: str) -> str:
    """Extrai o bloco do handoff relevante para um AR_ID específico.

    Tenta encontrar um heading '## ... AR_{id} ...' e extrai o conteúdo
    até o próximo heading de mesmo nível.
    Fallback: contexto de 2000 chars em torno da primeira menção do ID.
    """
    # Tenta heading markdown ## que mencione AR_NNN
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

    # Fallback: contexto ao redor da primeira menção
    mm = re.search(rf"\bAR[_\-]{re.escape(ar_id)}\b", handoff, flags=re.IGNORECASE)
    if mm:
        start = max(0, mm.start() - 300)
        end = min(len(handoff), mm.end() + 2000)
        return handoff[start:end]

    return ""


def _check_handoff(handoff: str, failures: List[str]) -> List[str]:
    """Valida o conteúdo do handoff. Retorna lista de falhas (pode ser vazia)."""

    # (1) EXECUTION SET semântico: AR IDs presentes
    ar_ids = _extract_ar_ids(handoff)
    if not ar_ids:
        failures.append(
            "handoff: não encontrei AR IDs "
            "(formas aceitas: 'AR IDs:[...]', 'AR_ID: N', 'AR_###', 'AR-###')"
        )

    # (2) PRE-FLIGHT semântico
    if not _has_any(
        handoff,
        patterns=[
            r"\bPRE[\s\-_]?FLIGHT\b",
            r"\bPreflight\b",
            r"\bworkspace\s+clean\b",
            r"\bgit\s+status\b",
            r"\bgit\s+diff\b",
        ],
    ):
        failures.append(
            "handoff: não encontrei PRE-FLIGHT "
            "(aceito: PRE-FLIGHT, Preflight, 'workspace clean', 'git status/diff')"
        )

    # (3) STOP CONDITIONS semântico
    if not _has_any(
        handoff,
        patterns=[
            r"\bSTOP\s+CONDITIONS\b",
            r"\bBLOCKED_INPUT\b",
            r"\bERROR_INFRA\b",
            r"\bFAIL_ACTIONABLE\b",
            r"\bexit\s*[234]\b",
        ],
    ):
        failures.append(
            "handoff: não encontrei STOP CONDITIONS "
            "(aceito: STOP CONDITIONS, BLOCKED_INPUT, ERROR_INFRA, FAIL_ACTIONABLE, exit [234])"
        )

    # (4) Version check: tolerante
    if not _has_any(
        handoff,
        patterns=[
            r"\bProtocolo\s*:\s*1\.3\.0\b",
            r"\bProtocol\s*:\s*1\.3\.0\b",
            r"\bv1\.3\.0\b",
            r"1\.3\.0",
        ],
    ):
        failures.append(
            "handoff: não encontrei referência ao protocolo 1.3.0 "
            "(aceito: 'Protocolo: 1.3.0', 'v1.3.0', '1.3.0')"
        )

    return ar_ids


def _check_handoff_warns(handoff: str) -> List[str]:
    """Checks opcionais (WARN-only). Não afetam exit code."""
    warns: List[str] = []

    _PROOF_PATTERNS = [
        r"\bPROOF\s*[:\(]",    # PROOF: ou PROOF (AR_N):
        r"\bProof\s*[:\(]",
        r"\btests?/",           # caminho tests/ ou test/
        r"\bpytest\b",
        r"@pytest\.mark",
        r"\btest_\w+\s*\(",     # chamada de função test_*()
    ]

    # (W1) PROOF por AR_ID — cada AR deve declarar como será provada
    ar_ids = _extract_ar_ids(handoff)
    if ar_ids:
        missing_proof: List[str] = []
        for ar_id in ar_ids:
            block = _extract_ar_block(handoff, ar_id) or handoff
            if not _has_any(block, _PROOF_PATTERNS):
                missing_proof.append(f"AR_{ar_id}")
        if missing_proof:
            warns.append(
                f"handoff: PROOF ausente em {', '.join(missing_proof)} — "
                "declare como provar cada AR: 'PROOF: arquivo::test_func' "
                "ou 'PROOF: N/A (governance)' para suprimir."
            )
    else:
        # Sem AR IDs extraíveis: fallback verificação global
        if not _has_any(handoff, _PROOF_PATTERNS):
            warns.append(
                "handoff: PROOF ausente — considere declarar como provar a AR "
                "(aceito: 'tests/', 'pytest', 'Proof:', 'PROOF')"
            )

    return warns


def _check_log(log_text: str, ar_ids: List[str], failures: List[str]) -> None:
    """Valida o conteúdo do executor_main.log."""

    # (5) Workspace Clean
    if not _has_any(log_text, [r"Workspace\s+Clean\s*:\s*True"]):
        failures.append("log: não encontrei 'Workspace Clean: True'")

    # (6) Exit Code: 0
    if not _has_any(log_text, [r"Exit\s+Code\s*:\s*0"]):
        failures.append("log: não encontrei 'Exit Code: 0'")

    # (7) PASS AR_<id>
    if ar_ids:
        pass_hits = sum(
            1
            for ar_id in ar_ids
            if re.search(rf"\bPASS\b.*\bAR[_\-]{re.escape(ar_id)}\b", log_text, flags=re.IGNORECASE)
        )
        if pass_hits == 0:
            failures.append(
                f"log: não encontrei 'PASS AR_<id>' para nenhum dos IDs detectados: "
                f"{', '.join(ar_ids)}"
            )
    else:
        if not _has_any(log_text, [r"\bPASS\b.*\bAR[_\-]\d+\b"]):
            failures.append("log: não encontrei padrão 'PASS AR_<id>'")


def main(argv: List[str]) -> int:
    handoff_path = (
        Path(argv[1]) if len(argv) > 1 and argv[1].strip() else Path("_reports/ARQUITETO.yaml")
    )
    log_path: Optional[Path] = None
    if len(argv) > 2 and argv[2].strip():
        log_path = Path(argv[2].strip())

    # --- Validar handoff ---
    ok, handoff = _read_text(handoff_path)
    if not ok:
        print(f"BLOCKED_INPUT: handoff não encontrado/ilegível: {handoff_path}")
        return EXIT_BLOCKED_INPUT

    failures: List[str] = []
    ar_ids = _check_handoff(handoff, failures)
    warns = _check_handoff_warns(handoff)

    # --- Validar log (opcional) ---
    if log_path is not None:
        ok_log, log_text = _read_text(log_path)
        if not ok_log:
            print(f"BLOCKED_INPUT: executor_main.log não encontrado/ilegível: {log_path}")
            return EXIT_BLOCKED_INPUT
        _check_log(log_text, ar_ids, failures)

    # --- Resultado ---
    if failures:
        print("FAIL_ACTIONABLE: check_handoff_contract")
        for f in failures:
            print(f"  - {f}")
        for w in warns:
            print(f"  ⚠️  WARN: {w}")
        return EXIT_FAIL_ACTIONABLE

    print("PASS: check_handoff_contract")
    if ar_ids:
        print(f"  AR IDs detectados: {', '.join(ar_ids)}")
    if log_path:
        print(f"  Log validado: {log_path}")
    for w in warns:
        print(f"  ⚠️  WARN: {w}")
    return EXIT_PASS


if __name__ == "__main__":
    # Garantir stdout/stderr UTF-8 no Windows/pipe (evita UnicodeEncodeError com "⚠️").
    # Aqui (e não em main()) para não interferir quando main() é importada por testes.
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass  # Ambiente sem buffer (pipe sem buffer) — segue sem alterar
    raise SystemExit(main(sys.argv))
