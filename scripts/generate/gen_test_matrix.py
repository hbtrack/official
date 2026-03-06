#!/usr/bin/env python3
"""
scripts/generate/gen_test_matrix.py
====================================
Política HB Track — Derivado (congelada 2026-03-04)
====================================
Gera/atualiza a TEST_MATRIX a partir de @pytest.mark.trace no código.

O Executor escreve testes com @pytest.mark.trace("INV-TRAIN-XXX").
Este script lê as anotações e atualiza a coluna Status da matrix.

Convenção:
  @pytest.mark.trace("INV-TRAIN-001")
  @pytest.mark.trace("INV-TRAIN-001", "CONTRACT-TRAIN-076")   # múltiplos IDs

Uso:
  # Relatório (padrão): mostra cobertura sem alterar nada
  python scripts/generate/gen_test_matrix.py --report

  # Atualizar matrix: PENDENTE/NOT_RUN → COBERTO onde trace annotation existe
  python scripts/generate/gen_test_matrix.py --update-matrix

  # Opções adicionais:
  --scan-dir    <dir>   default: Hb Track - Backend/tests/
  --matrix      <file>  default: docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md
  --date        <YYYY-MM-DD>  default: hoje
  --dry-run     imprime diff sem escrever (só com --update-matrix)
  --json        saída JSON em vez de texto (só com --report)

Exit codes:
  0: OK
  1: Nenhuma anotação @pytest.mark.trace encontrada
  2: Matrix não encontrada (só com --update-matrix)
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, NamedTuple, Set

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCAN_DIR = REPO_ROOT / "Hb Track - Backend" / "tests"
DEFAULT_MATRIX = REPO_ROOT / "docs" / "hbtrack" / "modulos" / "treinos" / "TEST_MATRIX_TRAINING.md"

# IDs que podem ser anotados com @pytest.mark.trace
TRACEABLE_PREFIXES = ("INV-", "CONTRACT-", "FLOW-", "SCREEN-", "EXB-", "DEC-")

# Colunas da tabela (0-based) — formato canônico da TEST_MATRIX_TRAINING.md
# | ID | Nome | Tipo | Cat | TestID | Método | Auto | Prioridade | Stage | Status | Últ.Exec | Evidência | ARs |
# Índices para tabela INV-TRAIN (13 colunas)
_COL_STATUS_WIDE = 9
_COL_DATE_WIDE   = 10
_COL_EVIDENCE_WIDE = 11
# Índices para tabela CONTRACT/FLOW/SCREEN/DEC (10 colunas)
_COL_STATUS_NARROW = 6
_COL_DATE_NARROW   = 7
_COL_EVIDENCE_NARROW = 8
# Aliases de conveniência (mantidos para retrocompatibilidade em testes)
COL_STATUS = _COL_STATUS_WIDE
COL_DATE   = _COL_DATE_WIDE
COL_EVIDENCE = _COL_EVIDENCE_WIDE


# ---------------------------------------------------------------------------
# Coleta de anotações
# ---------------------------------------------------------------------------

class TraceAnnotation(NamedTuple):
    trace_ids: List[str]   # IDs declarados no mark (ex.: ["INV-TRAIN-001"])
    test_name: str         # nome da função de teste
    file_path: str         # caminho relativo ao repo root


def _extract_trace_ids_from_call(call_node: ast.Call) -> List[str]:
    """Extrai IDs de uma chamada @pytest.mark.trace("ID1", "ID2")."""
    ids: List[str] = []
    for arg in call_node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            val = arg.value.strip()
            if any(val.startswith(p) for p in TRACEABLE_PREFIXES):
                ids.append(val)
    return ids


def _is_trace_decorator(node: ast.expr) -> bool:
    """Retorna True se o nó é @pytest.mark.trace(...)."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    # pytest.mark.trace(...)
    if (
        isinstance(func, ast.Attribute)
        and func.attr == "trace"
        and isinstance(func.value, ast.Attribute)
        and func.value.attr == "mark"
        and isinstance(func.value.value, ast.Name)
        and func.value.value.id == "pytest"
    ):
        return True
    return False


def scan_test_files(scan_dir: Path) -> List[TraceAnnotation]:
    """Varre arquivos test_*.py sob scan_dir e coleta todas as anotações @pytest.mark.trace."""
    annotations: List[TraceAnnotation] = []

    for py_file in sorted(scan_dir.rglob("test_*.py")):
        try:
            source = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        try:
            rel_path = str(py_file.relative_to(REPO_ROOT)).replace("\\", "/")
        except ValueError:
            rel_path = str(py_file.relative_to(scan_dir)).replace("\\", "/")

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if not _is_trace_decorator(decorator):
                    continue
                ids = _extract_trace_ids_from_call(decorator)  # type: ignore[arg-type]
                if ids:
                    annotations.append(
                        TraceAnnotation(
                            trace_ids=ids,
                            test_name=node.name,
                            file_path=rel_path,
                        )
                    )

    return annotations


# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------

def build_coverage_map(annotations: List[TraceAnnotation]) -> Dict[str, List[str]]:
    """
    Retorna {trace_id: [test_name@file, ...]}
    """
    coverage: Dict[str, List[str]] = {}
    for ann in annotations:
        for tid in ann.trace_ids:
            coverage.setdefault(tid, []).append(f"{ann.test_name}  [{ann.file_path}]")
    return coverage


def print_report(coverage: Dict[str, List[str]], *, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(coverage, indent=2, ensure_ascii=False))
        return

    if not coverage:
        print("Nenhuma anotação @pytest.mark.trace encontrada.")
        return

    print(f"@pytest.mark.trace — {len(coverage)} ID(s) cobertos:")
    for tid in sorted(coverage):
        tests = coverage[tid]
        print(f"  {tid}")
        for t in tests:
            print(f"    → {t}")


# ---------------------------------------------------------------------------
# Atualização da matrix
# ---------------------------------------------------------------------------

_TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")


def _split_row(line: str) -> List[str]:
    """Divide uma linha de tabela Markdown em células (sem os | externos)."""
    inner = line.strip().strip("|")
    return [c.strip() for c in inner.split("|")]


def _join_row(cells: List[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _row_id(cells: List[str]) -> str:
    return cells[0].strip() if cells else ""


def update_matrix(
    matrix_path: Path,
    coverage: Dict[str, List[str]],
    today: str,
    *,
    dry_run: bool = False,
) -> int:
    """
    Atualiza linhas da matrix onde:
    - ID da linha está em coverage
    - Status atual é PENDENTE ou NOT_RUN

    Retorna: número de linhas alteradas.
    """
    if not matrix_path.exists():
        print(f"ERRO: matrix não encontrada: {matrix_path}")
        return -1

    original = matrix_path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    changed = 0
    new_lines: List[str] = []

    for line in lines:
        stripped = line.rstrip("\n\r")
        m = _TABLE_ROW_RE.match(stripped)
        if not m:
            new_lines.append(line)
            continue

        cells = _split_row(stripped)
        # Detecta estrutura da tabela pelo nº de colunas
        if len(cells) >= 13:
            col_status, col_date, col_evidence = _COL_STATUS_WIDE, _COL_DATE_WIDE, _COL_EVIDENCE_WIDE
        elif len(cells) >= 10:
            col_status, col_date, col_evidence = _COL_STATUS_NARROW, _COL_DATE_NARROW, _COL_EVIDENCE_NARROW
        else:
            new_lines.append(line)
            continue

        if len(cells) <= max(col_status, col_evidence):
            new_lines.append(line)
            continue

        row_id = _row_id(cells)
        if row_id not in coverage:
            new_lines.append(line)
            continue

        current_status = cells[col_status].strip()
        if current_status not in ("PENDENTE", "NOT_RUN"):
            # Não sobreescrever COBERTO / FAIL / ERROR / PARCIAL
            new_lines.append(line)
            continue

        # Montar evidência: lista de arquivos únicos
        test_files: Set[str] = set()
        for entry in coverage[row_id]:
            # entry = "test_name  [path/to/test.py]"
            m2 = re.search(r"\[(.+?)\]", entry)
            if m2:
                test_files.add(m2.group(1))
        evidence_str = ", ".join(sorted(test_files)) if test_files else cells[col_evidence]

        cells[col_status] = "COBERTO"
        cells[col_date] = today
        cells[col_evidence] = evidence_str

        new_line = _join_row(cells) + "\n"
        if dry_run:
            print(f"  ~ {row_id}: {current_status} → COBERTO  [{today}]")
        new_lines.append(new_line)
        changed += 1

    if dry_run:
        print(f"\n[dry-run] {changed} linha(s) seriam alteradas.")
        return changed

    if changed:
        matrix_path.write_text("".join(new_lines), encoding="utf-8")
        print(f"TEST_MATRIX atualizada: {changed} linha(s) alteradas em {matrix_path}")
    else:
        print("TEST_MATRIX: nenhuma linha PENDENTE/NOT_RUN encontrada para os IDs anotados.")

    return changed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Gera/atualiza TEST_MATRIX a partir de @pytest.mark.trace.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--report", action="store_true", default=True,
                      help="Exibe relatório de cobertura (padrão)")
    mode.add_argument("--update-matrix", action="store_true", default=False,
                      help="Atualiza TEST_MATRIX: PENDENTE/NOT_RUN → COBERTO")

    p.add_argument("--scan-dir", type=Path, default=DEFAULT_SCAN_DIR,
                   help=f"Diretório de testes (default: {DEFAULT_SCAN_DIR})")
    p.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX,
                   help=f"Arquivo TEST_MATRIX (default: {DEFAULT_MATRIX})")
    p.add_argument("--date", default=str(date.today()), metavar="YYYY-MM-DD",
                   help="Data para coluna Últ.Exec (default: hoje)")
    p.add_argument("--dry-run", action="store_true",
                   help="Imprime diff sem escrever (só com --update-matrix)")
    p.add_argument("--json", action="store_true",
                   help="Saída JSON (só com --report)")
    return p


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # --update-matrix implica não usar o --report default
    report_mode = not args.update_matrix

    # 1. Coletar anotações
    scan_dir: Path = args.scan_dir
    if not scan_dir.exists():
        print(f"WARN: scan_dir não existe: {scan_dir}  (nenhuma anotação coletada)")
        annotations: List[TraceAnnotation] = []
    else:
        annotations = scan_test_files(scan_dir)

    coverage = build_coverage_map(annotations)

    # 2. Modo relatório
    if report_mode:
        print_report(coverage, as_json=args.json)
        return 0 if coverage else 1

    # 3. Modo atualização
    if not coverage:
        print("Nenhuma anotação @pytest.mark.trace encontrada — matrix não alterada.")
        return 1

    result = update_matrix(
        args.matrix,
        coverage,
        args.date,
        dry_run=args.dry_run,
    )
    return 0 if result >= 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
