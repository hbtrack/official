#!/usr/bin/env python3
"""
Gate: trace_stitcher.py — DOC-GATE-021

Para cada AR do handoff (_reports/ARQUITETO.yaml):
  - Verifica que o campo PROOF está declarado.
  - Verifica que o campo TRACE está declarado.
  - Valida que os arquivos referenciados no TRACE existem em disco.
  - (Opcional) lista âncoras TRACE_MATRIX para sync sugerido.

WARN-only: exit 0 sempre (o Testador trata WARN como FAIL_ACTIONABLE).
Objetivo: eliminar o caso "esqueci de linkar teste ↔ matriz".

Exit codes (canônico HB Track):
  0: PASS (com ou sem WARNs)
  4: BLOCKED_INPUT (handoff não encontrado/ilegível)

Uso:
  python scripts/gates/trace_stitcher.py [handoff_path] [repo_root]

  handoff_path  default: _reports/ARQUITETO.yaml
  repo_root     default: cwd
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

EXIT_PASS = 0
EXIT_BLOCKED_INPUT = 4

# Extensões válidas para validação de existência de arquivo
_FILE_EXTENSIONS = frozenset(
    (".md", ".py", ".yaml", ".yml", ".json", ".sql", ".txt", ".toml", ".ini", ".ts", ".tsx")
)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _read_text(path: Path) -> Tuple[bool, str]:
    try:
        return True, path.read_text(encoding="utf-8", errors="replace")
    except (FileNotFoundError, OSError):
        return False, ""


# ---------------------------------------------------------------------------
# Extração de AR IDs e blocos (standalone — sem import de outros gates)
# ---------------------------------------------------------------------------

def _extract_ar_ids(text: str) -> List[str]:
    """Prioridade: lista explícita 'AR IDs: [N,M]' → AR_ID: N → fallback varredura."""
    m = re.search(r"AR\s*IDs?\s*\*\*?\s*:\s*\[([^\]]+)\]", text, flags=re.IGNORECASE)
    if not m:
        m = re.search(r"AR\s*IDs?\s*:\s*\[([^\]]+)\]", text, flags=re.IGNORECASE)
    if m:
        ids: set[str] = set()
        for token in re.split(r"[,\s]+", m.group(1).strip()):
            t = token.strip().strip('"').strip("'")
            if t.isdigit():
                ids.add(t)
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
    """Extrai o bloco do handoff relevante para um AR_ID específico."""
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
# Parsing de campos PROOF e TRACE
# ---------------------------------------------------------------------------

def _parse_field(block: str, field: str) -> Optional[str]:
    """
    Extrai valor do campo `field` no bloco.
    Aceita:
      - **PROOF**: valor
      - **PROOF (AR_232)**: valor
      - * PROOF: valor
      - PROOF: valor  (sem marcadores)
    Retorna a primeira linha de valor encontrada, ou None se ausente.
    """
    pattern = re.compile(
        rf"(?:[\*\-]\s*)?(?:\*\*)?{re.escape(field)}\s*(?:\(AR[_\-]\d+\))?\s*(?:\*\*)?\s*:\s*(.+)",
        flags=re.IGNORECASE,
    )
    m = pattern.search(block)
    return m.group(1).strip() if m else None


def _has_field_declared(block: str, field: str) -> bool:
    """True se o campo existe no bloco (valor não-vazio, não-NA com burocracia)."""
    val = _parse_field(block, field)
    return val is not None and len(val.strip()) > 0


def _is_suppressed(value: Optional[str]) -> bool:
    """True se o valor indica supressão explícita (N/A, governance, etc.)."""
    if value is None:
        return False
    return bool(re.search(r"\bN/?A\b|\bgovernance\b", value, flags=re.IGNORECASE))


# ---------------------------------------------------------------------------
# Extração e validação de caminhos de arquivo no TRACE
# ---------------------------------------------------------------------------

def _extract_file_paths(trace_value: str) -> List[str]:
    """
    Extrai caminhos de arquivo de um valor TRACE.
    Aceita:
      - Backtick spans: `docs/path/file.md`
      - Caminhos bare: docs/path/file.md (sem espaços, com extensão válida)
    Ignora seções como §0, §9 e texto livre.
    """
    paths: List[str] = []

    # Backtick spans: `path/to/file.ext`
    for m in re.finditer(r"`([^`]+)`", trace_value):
        candidate = m.group(1).strip()
        if "/" in candidate and Path(candidate).suffix.lower() in _FILE_EXTENSIONS:
            paths.append(candidate)

    # Caminhos bare (sem espaços): path/to/file.ext
    for m in re.finditer(r"[\w\-\.]+(?:/[\w\-\.]+)+", trace_value):
        candidate = m.group(0)
        if Path(candidate).suffix.lower() in _FILE_EXTENSIONS:
            if candidate not in paths:
                paths.append(candidate)

    return paths


def _validate_trace_files(
    trace_value: str, repo_root: Path
) -> Tuple[List[str], List[str]]:
    """
    Retorna (existing, missing) para arquivos referenciados no trace_value.
    Arquivos são avaliados relativos ao repo_root.
    """
    paths = _extract_file_paths(trace_value)
    existing, missing = [], []
    for p in paths:
        full = repo_root / p
        (existing if full.exists() else missing).append(p)
    return existing, missing


# ---------------------------------------------------------------------------
# Verificação por AR
# ---------------------------------------------------------------------------

class ArResult:
    def __init__(self, ar_id: str):
        self.ar_id = ar_id
        self.warns: List[str] = []
        self.proof_value: Optional[str] = None
        self.trace_value: Optional[str] = None
        self.missing_files: List[str] = []

    @property
    def label(self) -> str:
        return f"AR_{self.ar_id}"


def _check_ar(ar_id: str, block: str, repo_root: Path) -> ArResult:
    result = ArResult(ar_id)

    # --- PROOF ---
    proof_val = _parse_field(block, "PROOF")
    result.proof_value = proof_val
    if proof_val is None:
        result.warns.append(
            f"{result.label}: PROOF não declarado — "
            "adicione 'PROOF: <arquivo::test_func>' ou 'PROOF: N/A (governance)'"
        )

    # --- TRACE ---
    trace_val = _parse_field(block, "TRACE")
    result.trace_value = trace_val
    if trace_val is None:
        result.warns.append(
            f"{result.label}: TRACE não declarado — "
            "adicione 'TRACE: <docs/caminho/arquivo.md §seção>' ou 'TRACE: N/A (governance)'"
        )
    elif not _is_suppressed(trace_val):
        # Validar arquivos referenciados
        _, missing = _validate_trace_files(trace_val, repo_root)
        result.missing_files = missing
        for missing_path in missing:
            result.warns.append(
                f"{result.label}: TRACE aponta para arquivo inexistente: {missing_path}"
            )

    return result


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv: List[str]) -> int:
    handoff_path = (
        Path(argv[1]) if len(argv) > 1 and argv[1].strip() else Path("_reports/ARQUITETO.yaml")
    )
    repo_root = (
        Path(argv[2]).resolve() if len(argv) > 2 and argv[2].strip() else Path.cwd()
    )

    ok, handoff = _read_text(handoff_path)
    if not ok:
        print(f"BLOCKED_INPUT: handoff não encontrado/ilegível: {handoff_path}")
        return EXIT_BLOCKED_INPUT

    ar_ids = _extract_ar_ids(handoff)

    results: List[ArResult] = []
    for ar_id in ar_ids:
        block = _extract_ar_block(handoff, ar_id) or handoff
        results.append(_check_ar(ar_id, block, repo_root))

    all_warns = [w for r in results for w in r.warns]

    print("PASS: trace_stitcher")
    if ar_ids:
        print(f"  AR IDs avaliados: {', '.join(ar_ids)}")

    if not ar_ids:
        print("  ⚠️  WARN: nenhum AR_ID detectado no handoff — avaliação impossível")
    else:
        for r in results:
            for w in r.warns:
                print(f"  ⚠️  WARN: {w}")
        if not all_warns:
            print(f"  PROOF+TRACE declarados e arquivos presentes em {len(ar_ids)} AR(s)")

    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
