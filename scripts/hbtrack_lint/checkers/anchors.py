"""
Checkers de âncoras e integridade de stubs — STUB-001..004, DIFF-001..003.

cannot_waive: STUB-001, STUB-002
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from hbtrack_lint.engine import register_checker, RuleResult

# ─── Infraestrutura de âncora (baseada em MOTORES.md) ─────────────────────

ANCHOR_START_RE = re.compile(
    r"^\s*#\s*<HB-BODY-START:([a-zA-Z0-9_]+)>\s*$"
)
ANCHOR_END_RE = re.compile(
    r"^\s*#\s*<HB-BODY-END:([a-zA-Z0-9_]+)>\s*$"
)


@dataclass(eq=True, frozen=True)
class AnchorRegion:
    symbol_id: str
    start_line: int
    end_line: int


def extract_anchor_regions(source: str) -> list[AnchorRegion]:
    stack: dict[str, int] = {}
    anchors: list[AnchorRegion] = []
    lines = source.splitlines()

    for idx, line in enumerate(lines, start=1):
        m_start = ANCHOR_START_RE.match(line)
        if m_start:
            symbol_id = m_start.group(1)
            if symbol_id in stack:
                raise ValueError(f"Duplicate start anchor for '{symbol_id}' at line {idx}")
            stack[symbol_id] = idx
            continue

        m_end = ANCHOR_END_RE.match(line)
        if m_end:
            symbol_id = m_end.group(1)
            if symbol_id not in stack:
                raise ValueError(f"End anchor without matching start for '{symbol_id}' at line {idx}")
            anchors.append(AnchorRegion(symbol_id, stack.pop(symbol_id), idx))

    if stack:
        raise ValueError(f"Unclosed anchors: {sorted(stack.keys())}")

    return sorted(anchors, key=lambda a: a.start_line)


def node_within_anchor(node: ast.AST, anchors: list[AnchorRegion]) -> bool:
    lineno = getattr(node, "lineno", None)
    end_lineno = getattr(node, "end_lineno", lineno)
    if lineno is None:
        return False
    for a in anchors:
        if lineno >= a.start_line and (end_lineno or lineno) <= a.end_line:
            return True
    return False


def _has_anchor(symbol_name: str, anchors: list[AnchorRegion]) -> bool:
    return any(a.symbol_id.endswith(f"__{symbol_name}") or a.symbol_id == symbol_name for a in anchors)


def normalize_module(tree: ast.Module, anchors: list[AnchorRegion]) -> ast.Module:
    """Produz versão comparável: substitui corpos de funções ancoradas por ast.Pass()."""

    class Normalizer(ast.NodeTransformer):
        def visit_FunctionDef(self, node: ast.FunctionDef):
            if not node.name.startswith("_") and _has_anchor(node.name, anchors):
                node.body = [ast.Pass()]
                return node
            if node.name.startswith("_") and not node_within_anchor(node, anchors):
                return None  # private helper outside anchor — remove
            return self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            return self.visit_FunctionDef(node)  # type: ignore[arg-type]

    normalized = Normalizer().visit(tree)
    ast.fix_missing_locations(normalized)
    return normalized  # type: ignore[return-value]


def compare_normalized_ast(original_src: str, modified_src: str) -> list[str]:
    original_anchors = extract_anchor_regions(original_src)
    modified_anchors = extract_anchor_regions(modified_src)

    if original_anchors != modified_anchors:
        return ["Anchor layout changed"]

    try:
        orig_tree = ast.parse(original_src)
        mod_tree = ast.parse(modified_src)
    except SyntaxError as exc:
        return [f"SyntaxError: {exc}"]

    norm_orig = normalize_module(orig_tree, original_anchors)
    norm_mod = normalize_module(mod_tree, modified_anchors)

    dump_a = ast.dump(norm_orig, include_attributes=False)
    dump_b = ast.dump(norm_mod, include_attributes=False)

    if dump_a != dump_b:
        return ["Structural AST drift outside allowed anchor bodies"]

    return []


# ─── Checkers ─────────────────────────────────────────────────────────────

def check_stub_edits_stay_within_anchors(rule: dict, ctx) -> RuleResult:
    """STUB-001 (POST_EXECUTION, cannot_waive): Edições em stubs devem ficar dentro das âncoras."""
    if ctx.anchor_manifest is None:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "anchor_manifest ausente — POST_EXECUTION sem dados de âncora")

    if ctx.original_files_dir is None or ctx.working_files_dir is None:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "original_files_dir/working_files_dir ausentes")

    violations = []
    for file_entry in (ctx.anchor_manifest.get("files") or []):
        if file_entry.get("language") != "python":
            continue

        rel_path = file_entry["path"]
        original_path = ctx.original_files_dir / rel_path
        modified_path = ctx.working_files_dir / rel_path

        if not original_path.exists() or not modified_path.exists():
            continue

        original_src = original_path.read_text(encoding="utf-8")
        modified_src = modified_path.read_text(encoding="utf-8")

        try:
            errors = compare_normalized_ast(original_src, modified_src)
        except Exception as exc:
            errors = [f"Erro interno: {exc}"]

        if errors:
            violations.append({"file": rel_path, "errors": errors})

    if violations:
        msgs = [f"{v['file']}: {'; '.join(v['errors'])}" for v in violations]
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], " | ".join(msgs))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_generated_symbols_are_immutable(rule: dict, ctx) -> RuleResult:
    """STUB-002 (POST_EXECUTION, cannot_waive): Assinaturas de símbolos públicos não podem mudar."""
    if ctx.anchor_manifest is None:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "anchor_manifest ausente")

    if ctx.original_files_dir is None or ctx.working_files_dir is None:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "original_files_dir/working_files_dir ausentes")

    violations = []
    for file_entry in (ctx.anchor_manifest.get("files") or []):
        if file_entry.get("language") != "python":
            continue

        rel_path = file_entry["path"]
        original_path = ctx.original_files_dir / rel_path
        modified_path = ctx.working_files_dir / rel_path

        if not original_path.exists() or not modified_path.exists():
            continue

        try:
            orig_tree = ast.parse(original_path.read_text(encoding="utf-8"))
            mod_tree = ast.parse(modified_path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            violations.append(f"{rel_path}: SyntaxError {exc}")
            continue

        # Coletar assinaturas de símbolos públicos
        def _get_public_signatures(tree: ast.AST) -> dict[str, str]:
            sigs = {}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_"):
                        args = [a.arg for a in node.args.args]
                        sigs[node.name] = f"({', '.join(args)})"
            return sigs

        orig_sigs = _get_public_signatures(orig_tree)
        mod_sigs = _get_public_signatures(mod_tree)

        for name, sig in orig_sigs.items():
            if name in mod_sigs and mod_sigs[name] != sig:
                violations.append(
                    f"{rel_path}: assinatura de '{name}' mudou de {sig} para {mod_sigs[name]}"
                )
            elif name not in mod_sigs:
                violations.append(f"{rel_path}: símbolo público '{name}' removido")

    if violations:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], " | ".join(violations))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_no_uncontracted_public_symbols(rule: dict, ctx) -> RuleResult:
    """STUB-003 (POST_EXECUTION): Símbolos públicos não declarados no contrato são proibidos."""
    if ctx.anchor_manifest is None:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "anchor_manifest ausente")

    if ctx.working_files_dir is None:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "working_files_dir ausente")

    # Coletar símbolos contratados do anchor_manifest
    contracted_symbols: set[str] = set()
    for file_entry in (ctx.anchor_manifest.get("files") or []):
        for anchor in (file_entry.get("anchors") or []):
            sym = anchor.get("public_symbol") or anchor.get("symbol_id", "")
            # Extrair nome da função do símbolo composto (ex: "athletes__athlete__list" → "athlete_list")
            contracted_symbols.add(sym.split("__")[-1] if "__" in sym else sym)

    violations = []
    for file_entry in (ctx.anchor_manifest.get("files") or []):
        if file_entry.get("language") != "python":
            continue
        mod_path = ctx.working_files_dir / file_entry["path"]
        if not mod_path.exists():
            continue
        try:
            tree = ast.parse(mod_path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_") and node.name not in contracted_symbols:
                    violations.append(f"{file_entry['path']}: símbolo público não contratado '{node.name}'")

    if violations:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], " | ".join(violations))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_contract_hash_comment_matches_snapshot(rule: dict, ctx) -> RuleResult:
    """STUB-004: Hash de contrato no comentário do stub deve bater com snapshot_hash do handoff."""
    if ctx.handoff is None:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "handoff ausente")

    snapshot_hash = (ctx.handoff.get("integrity") or {}).get("snapshot_hash")
    if not snapshot_hash:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "handoff.integrity.snapshot_hash ausente")

    if ctx.working_files_dir is None:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "working_files_dir ausente")

    if ctx.anchor_manifest is None:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "anchor_manifest ausente")

    # Padrão: # HB-CONTRACT-HASH: <sha256>
    HASH_COMMENT_RE = re.compile(r"#\s*HB-CONTRACT-HASH:\s*([0-9a-f]{64})", re.IGNORECASE)

    violations = []
    for file_entry in (ctx.anchor_manifest.get("files") or []):
        if file_entry.get("language") != "python":
            continue
        mod_path = ctx.working_files_dir / file_entry["path"]
        if not mod_path.exists():
            continue

        source = mod_path.read_text(encoding="utf-8")
        match = HASH_COMMENT_RE.search(source)
        if match:
            embedded_hash = match.group(1).lower()
            if embedded_hash != snapshot_hash.lower():
                violations.append(
                    f"{file_entry['path']}: hash embarcado '{embedded_hash[:16]}...' "
                    f"!= snapshot_hash '{snapshot_hash[:16]}...'"
                )

    if violations:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], " | ".join(violations))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── Checkers DIFF ────────────────────────────────────────────────────────

def check_diff_scope_is_within_declared_files(rule: dict, ctx) -> RuleResult:
    """DIFF-001: Diff de implementação deve cobrir apenas arquivos declarados no contrato."""
    bindings_doc = ctx.contracts.get("12_ATLETAS_EXECUTION_BINDINGS.yaml") or {}
    bindings = bindings_doc.get("bindings") or []

    contracted_paths: set[str] = set()
    for binding in bindings:
        for fp in (binding.get("file_paths") or []):
            contracted_paths.add(fp)

    if not contracted_paths:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "Nenhum arquivo declarado em execution_bindings")

    if ctx.working_files_dir is None:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "working_files_dir ausente")

    # Verificar se arquivos modificados estão na lista contratada
    modified_files: list[str] = []
    if ctx.working_files_dir.exists():
        for f in ctx.working_files_dir.rglob("*.py"):
            rel = str(f.relative_to(ctx.working_files_dir)).replace("\\", "/")
            modified_files.append(rel)

    uncontracted = [f for f in modified_files if f not in contracted_paths]
    if uncontracted:
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            f"Arquivos fora do escopo contratado: {', '.join(uncontracted)}"
        )
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_diff_does_not_include_test_files(rule: dict, ctx) -> RuleResult:
    """DIFF-002: Diff de implementação não deve incluir arquivos de teste."""
    if ctx.working_files_dir is None:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "working_files_dir ausente")

    test_files: list[str] = []
    if ctx.working_files_dir.exists():
        for f in ctx.working_files_dir.rglob("test_*.py"):
            test_files.append(str(f.relative_to(ctx.working_files_dir)).replace("\\", "/"))
        for f in ctx.working_files_dir.rglob("*_test.py"):
            test_files.append(str(f.relative_to(ctx.working_files_dir)).replace("\\", "/"))

    if test_files:
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            f"Diff contém arquivos de teste: {', '.join(test_files)}"
        )
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_diff_migration_matches_schema_changes(rule: dict, ctx) -> RuleResult:
    """DIFF-003: Se houver mudança de schema, deve haver migração correspondente."""
    db_doc = ctx.contracts.get("13_ATLETAS_DB_CONTRACT.yaml") or {}
    file_map = db_doc.get("file_map") or {}
    canonical = file_map.get("canonical_files") or {}
    migration_file = canonical.get("alembic_migration_file")

    if not migration_file:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    migration_path = ctx.repo_root / migration_file
    fallback = ctx.repo_root / "Hb Track - Backend" / "db" / "alembic" / "versions"

    # Se o arquivo de migração foi declarado, cabe ao checker verificar se existe
    if migration_path.exists():
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    # Tentar fallback por padrão de nome
    if fallback.exists():
        stem = Path(migration_file).stem
        matches = list(fallback.glob(f"*{stem}*"))
        if matches:
            return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    return RuleResult.fail(
        rule["rule_id"], rule["checker_id"],
        f"Mudança de schema declarada mas migração não encontrada: '{migration_file}'"
    )


# ─── Registro ─────────────────────────────────────────────────────────────

register_checker("check_stub_edits_stay_within_anchors", check_stub_edits_stay_within_anchors)
register_checker("check_generated_symbols_are_immutable", check_generated_symbols_are_immutable)
register_checker("check_no_uncontracted_public_symbols", check_no_uncontracted_public_symbols)
register_checker("check_contract_hash_comment_matches_snapshot", check_contract_hash_comment_matches_snapshot)
register_checker("check_diff_scope_is_within_declared_files", check_diff_scope_is_within_declared_files)
register_checker("check_diff_does_not_include_test_files", check_diff_does_not_include_test_files)
register_checker("check_diff_migration_matches_schema_changes", check_diff_migration_matches_schema_changes)
