
## REGRAS ESTRUTURAIS - hb_plan.py e hb_verify.py

	1.	cada regra passa a ter checker_id obrigatório;
	2.	assertion vira apenas documentação humana;
	3.	o hb_plan.py e o hb_verify.py só executam checker_id -> função Python;
	4.	o snapshot de hashes só pode ser emitido pelo hb_plan.py;
	5.	STUB-003 precisa distinguir símbolo contratado de símbolo privado auxiliar.

Abaixo estão os dois artefatos que faltavam.

# Bootstrap correto do snapshot e hashes

Sua crítica ao paradoxo do hash está correta. O fluxo certo é:

ARQUITETO edita contratos
↓
hb_plan.py valida schemas e cross-rules
↓
se PASS:
    hb_plan.py calcula hashes
    hb_plan.py gera 16_ATLETAS_AGENT_HANDOFF.json
    hb_plan.py sela snapshot
senão:
    nenhum handoff válido é emitido

Ou seja: o Arquiteto não gera hash.
O hb_plan.py é a única fonte de verdade para snapshot e integridade. Isso evita hash “manual” inconsistente.

# Zona de sombra dos símbolos: contratado vs privado

A sua crítica à STUB-003 também procede. A regra correta não é “nenhum símbolo novo”. É:
	•	nenhum novo símbolo público/contratado
	•	símbolos privados auxiliares são permitidos apenas dentro da zona ancorada e sob política explícita

A forma correta em `08_ATLETAS_TRACEABILITY.yaml` ou no handoff é algo assim:

```yaml
symbol_policy:
  public_symbols_declared_only: true
  private_helper_symbols:
    allowed: true
    naming_pattern: "^_"
    allowed_scope: "inside_anchor_region_only"
    export_forbidden: true
```

* Então o validador precisa tratar:
	•	função pública nova: falha
	•	classe pública nova: falha
	•	helper _xyz dentro da âncora: permitido
	•	helper _xyz fora da âncora: falha
	•	helper importado/exportado como API: falha

# Algoritmo do validador de âncoras em hb_verify.py

A base técnica certa é AST para Python, porque o módulo ast foi feito exatamente para processar a gramática sintática do Python de forma programática.   

Objetivo

Garantir que, em arquivos Python gerados:
	•	imports fora da âncora não mudaram
	•	decorators fora da âncora não mudaram
	•	assinatura de função não mudou
	•	nome de símbolo público não mudou
	•	apenas o corpo entre âncoras foi alterado

Estratégia

Não confiar só em diff textual.
Usar dois níveis:
	1.	Anchor Range Check
	•	localizar pares HB-BODY-START / HB-BODY-END
	•	qualquer mudança textual fora dessas faixas = suspeita
	2.	AST Structural Check
	•	parse do arquivo original e do modificado
	•	normalizar AST removendo os corpos permitidos nas regiões ancoradas
	•	comparar ASTs normalizadas

Pseudocódigo rigoroso

```python
from dataclasses import dataclass
import ast
from pathlib import Path

@dataclass
class AnchorRegion:
    symbol_id: str
    start_line: int
    end_line: int

def extract_anchor_regions(source: str) -> list[AnchorRegion]:
    # Localiza comentários HB-BODY-START / HB-BODY-END
    # Valida pareamento, ordem e unicidade
    ...

def parse_ast(source: str) -> ast.AST:
    return ast.parse(source)

def node_within_anchor(node: ast.AST, anchors: list[AnchorRegion]) -> bool:
    lineno = getattr(node, "lineno", None)
    end_lineno = getattr(node, "end_lineno", lineno)
    if lineno is None:
        return False
    for a in anchors:
        if lineno >= a.start_line and end_lineno <= a.end_line:
            return True
    return False

def normalize_module(tree: ast.Module, anchors: list[AnchorRegion]) -> ast.Module:
    """
    Produz uma versão comparável da AST em que:
    - corpos de funções ancoradas são substituídos por um placeholder estável
    - helpers privados permitidos só sobrevivem se estiverem dentro da âncora
    - símbolos públicos fora da âncora permanecem intocados para comparação
    """
    class Normalizer(ast.NodeTransformer):
        def visit_FunctionDef(self, node: ast.FunctionDef):
            # Se a função pública tem âncora, mantém assinatura e decorator,
            # substitui corpo por placeholder fixo.
            if is_public_symbol(node.name) and has_anchor_for_symbol(node.name, anchors):
                node.body = [ast.Pass()]
                return node

            # Helper privado fora da âncora não é permitido
            if is_private_symbol(node.name) and not node_within_anchor(node, anchors):
                raise ValidationError(f"Private helper outside anchor: {node.name}")

            return self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            return self.visit_FunctionDef(node)

        def visit_ClassDef(self, node: ast.ClassDef):
            # Classe pública nova fora do contrato = falha
            if is_uncontracted_public_class(node.name):
                raise ValidationError(f"Uncontracted public class: {node.name}")
            return self.generic_visit(node)

    normalized = Normalizer().visit(tree)
    ast.fix_missing_locations(normalized)
    return normalized

def compare_normalized_ast(original_src: str, modified_src: str) -> list[str]:
    original_anchors = extract_anchor_regions(original_src)
    modified_anchors = extract_anchor_regions(modified_src)

    # âncoras não podem mudar
    if original_anchors != modified_anchors:
        return ["Anchor layout changed"]

    original_tree = parse_ast(original_src)
    modified_tree = parse_ast(modified_src)

    norm_original = normalize_module(original_tree, original_anchors)
    norm_modified = normalize_module(modified_tree, modified_anchors)

    dump_a = ast.dump(norm_original, include_attributes=False)
    dump_b = ast.dump(norm_modified, include_attributes=False)

    if dump_a != dump_b:
        return ["Structural AST drift outside allowed anchor bodies"]

    return []

def validate_python_stub(original_path: Path, modified_path: Path) -> int:
    errors = compare_normalized_ast(
        original_path.read_text(encoding="utf-8"),
        modified_path.read_text(encoding="utf-8"),
    )
    if errors:
        emit_report(errors)
        return 2
    return 0
```

# Regras executáveis: tabela checker_id -> função

O motor do linter **não pode interpretar a frase**. Ele precisa fazer **dispatch explícito**.

```python
CHECKERS = {
    "check_openapi_operation_ids_are_traceable": check_openapi_operation_ids_are_traceable,
    "check_traceability_operations_exist_in_openapi": check_traceability_operations_exist_in_openapi,
    "check_db_nullability_matches_api_write_contract": check_db_nullability_matches_api_write_contract,
    "check_handoff_hashes_match_snapshot": check_handoff_hashes_match_snapshot,
    "check_projection_handlers_are_side_effect_free": check_projection_handlers_are_side_effect_free,
    "check_temporal_invariants_forbid_system_clock": check_temporal_invariants_forbid_system_clock,
    "check_stub_edits_stay_within_anchors": check_stub_edits_stay_within_anchors
}

Execução:

def run_rule(rule: dict, context: ValidationContext) -> RuleResult:
    checker_id = rule["checker_id"]
    fn = CHECKERS.get(checker_id)
    if fn is None:
        return RuleResult.fail(rule["rule_id"], f"Unknown checker_id: {checker_id}")
    return fn(rule, context)
```
Isso fecha a lacuna entre “texto” e “bit”.

6) Veredito objetivo

* O ponto que faltava era exatamente este:
	•	schema formal do meta-contrato
	•	despacho determinístico por checker_id
	•	snapshot emitido só pelo hb_plan.py
	•	AST validator para âncoras
	•	distinção formal entre símbolo contratado e helper privado

- Com isso, a arquitetura deixa de ser “regra escrita” e passa a ser regra executável.

# HB PLAN

Objetivo do hb_plan.py

Entrada:
	•	diretório do módulo, por exemplo docs/hbtrack/modulos/atletas/

Saída:
	•	_reports/hb_plan_result.json
	•	_reports/hb_plan_result.md
	•	docs/hbtrack/modulos/atletas/16_ATLETAS_AGENT_HANDOFF.json
	•	_reports/anchor_manifest.json

Exit codes:
	•	0 = PASS
	•	2 = FAIL_ACTIONABLE
	•	3 = ERROR_INFRA
	•	4 = BLOCKED_INPUT

**JUSTIFICATIVA**: 

## Estrutura de diretórios recomendada

scripts/
  hb_plan.py
  hb_verify.py
  hbtrack_lint/
    __init__.py
    context.py
    loader.py
    hashing.py
    reports.py
    schemas.py
    anchor_manifest.py
    handoff_builder.py
    checker_registry.py
    checkers/
      __init__.py
      documents.py
      cross.py
      db.py
      ui.py
      invariants.py
      handoff.py
      events.py
      side_effects.py
      time.py
      tests.py
      anchors.py
      restrictions.py

hb_plan.py — esqueleto principal

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from hbtrack_lint.context import ValidationContext
from hbtrack_lint.loader import load_contract_pack
from hbtrack_lint.schemas import validate_documents_against_schemas
from hbtrack_lint.checker_registry import run_allowed_rules
from hbtrack_lint.anchor_manifest import build_anchor_manifest
from hbtrack_lint.handoff_builder import build_handoff
from hbtrack_lint.hashing import sha256_file, sha256_jsonable
from hbtrack_lint.reports import write_plan_reports


EXIT_PASS = 0
EXIT_FAIL_ACTIONABLE = 2
EXIT_ERROR_INFRA = 3
EXIT_BLOCKED_INPUT = 4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HB Track deterministic planner")
    parser.add_argument(
        "module_root",
        type=Path,
        help="Path to module contract pack, e.g. docs/hbtrack/modulos/atletas"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root"
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("_reports"),
        help="Output directory for reports"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        module_root = args.module_root.resolve()
        repo_root = args.repo_root.resolve()
        reports_dir = (repo_root / args.reports_dir).resolve()
        reports_dir.mkdir(parents=True, exist_ok=True)

        if not module_root.exists():
            write_plan_reports(
                reports_dir=reports_dir,
                status="BLOCKED_INPUT",
                errors=[{"reason": f"Module root does not exist: {module_root}"}],
                warnings=[],
                results=[],
                handoff_path=None,
                anchor_manifest_path=None,
            )
            return EXIT_BLOCKED_INPUT

        contracts = load_contract_pack(module_root)

        schema_results = validate_documents_against_schemas(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
        )
        if schema_results.errors:
            write_plan_reports(
                reports_dir=reports_dir,
                status="FAIL_ACTIONABLE",
                errors=schema_results.errors,
                warnings=schema_results.warnings,
                results=schema_results.results,
                handoff_path=None,
                anchor_manifest_path=None,
            )
            return EXIT_FAIL_ACTIONABLE

        ctx = ValidationContext(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
            handoff=None,
            anchor_manifest=None,
            original_files_dir=None,
            working_files_dir=None,
        )

        lint_results = run_allowed_rules(ctx)

        failures = [r for r in lint_results if r.status == "FAIL"]
        errors = [r for r in lint_results if r.status == "ERROR"]

        if failures or errors:
            write_plan_reports(
                reports_dir=reports_dir,
                status="FAIL_ACTIONABLE" if failures else "ERROR_INFRA",
                errors=[r.__dict__ for r in failures + errors],
                warnings=[],
                results=[r.__dict__ for r in lint_results],
                handoff_path=None,
                anchor_manifest_path=None,
            )
            return EXIT_FAIL_ACTIONABLE if failures else EXIT_ERROR_INFRA

        anchor_manifest = build_anchor_manifest(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
        )

        anchor_manifest_path = reports_dir / "anchor_manifest.json"
        anchor_manifest_path.write_text(
            json.dumps(anchor_manifest, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        handoff = build_handoff(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
            anchor_manifest=anchor_manifest,
            reports_dir=reports_dir,
        )

        # hash do manifesto entra no handoff
        handoff.setdefault("integrity", {})
        handoff["integrity"]["anchor_manifest_sha256"] = sha256_file(anchor_manifest_path)

        # snapshot hash final calculado somente após materializar o handoff sem snapshot_hash
        provisional_handoff = json.loads(json.dumps(handoff))
        provisional_handoff["integrity"]["snapshot_hash"] = "0" * 64
        snapshot_hash = sha256_jsonable(provisional_handoff)
        handoff["integrity"]["snapshot_hash"] = snapshot_hash

        handoff_path = module_root / "16_ATLETAS_AGENT_HANDOFF.json"
        handoff_path.write_text(
            json.dumps(handoff, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        write_plan_reports(
            reports_dir=reports_dir,
            status="PASS",
            errors=[],
            warnings=[],
            results=[r.__dict__ for r in lint_results],
            handoff_path=handoff_path,
            anchor_manifest_path=anchor_manifest_path,
        )
        return EXIT_PASS

    except Exception as exc:
        write_plan_reports(
            reports_dir=args.reports_dir,
            status="ERROR_INFRA",
            errors=[{"reason": f"{type(exc).__name__}: {exc}"}],
            warnings=[],
            results=[],
            handoff_path=None,
            anchor_manifest_path=None,
        )
        return EXIT_ERROR_INFRA


if __name__ == "__main__":
    sys.exit(main())
```

⸻

load_contract_pack

Esse loader não pode “tentar adivinhar”. Ele carrega por nome canônico.
```python
from __future__ import annotations

import json
from pathlib import Path
import yaml


REQUIRED_DOCS = [
    "00_ATLETAS_CROSS_LINTER_RULES.json",
    "01_ATLETAS_OPENAPI.yaml",
    "08_ATLETAS_TRACEABILITY.yaml",
    "13_ATLETAS_DB_CONTRACT.yaml",
    "14_ATLETAS_UI_CONTRACT.yaml",
    "15_ATLETAS_INVARIANTS.yaml",
    "17_ATLETAS_PROJECTIONS.yaml",
    "18_ATLETAS_SIDE_EFFECTS.yaml",
    "19_ATLETAS_TEST_SCENARIOS.yaml",
    "20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md",
]

OPTIONAL_DOCS = [
    "05_ATLETAS_EVENTS.asyncapi.yaml",
]


def _load_file(path: Path):
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return path.read_text(encoding="utf-8")


def load_contract_pack(module_root: Path) -> dict[str, object]:
    contracts: dict[str, object] = {}

    for name in REQUIRED_DOCS + OPTIONAL_DOCS:
        path = module_root / name
        if path.exists():
            contracts[name] = _load_file(path)

    return contracts
```

⸻

validate_documents_against_schemas

Aqui mora o “meta-juiz”.
A regra é: cada artefato tipado deve ter schema próprio.

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
from jsonschema import Draft202012Validator


@dataclass
class SchemaValidationResult:
    errors: list[dict] = field(default_factory=list)
    warnings: list[dict] = field(default_factory=list)
    results: list[dict] = field(default_factory=list)


SCHEMA_MAP = {
    "00_ATLETAS_CROSS_LINTER_RULES.json": "schemas/00_ATLETAS_CROSS_LINTER_RULES.schema.json",
    "16_ATLETAS_AGENT_HANDOFF.json": "schemas/16_AGENT_HANDOFF.schema.json",
    # restantes entram progressivamente
}


def validate_documents_against_schemas(repo_root: Path, module_root: Path, contracts: dict[str, object]) -> SchemaValidationResult:
    result = SchemaValidationResult()

    for doc_name, schema_rel in SCHEMA_MAP.items():
        if doc_name not in contracts:
            continue

        schema_path = repo_root / schema_rel
        if not schema_path.exists():
            result.errors.append({
                "document": doc_name,
                "reason": f"Missing schema: {schema_path}"
            })
            continue

        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)

        doc_errors = sorted(validator.iter_errors(contracts[doc_name]), key=lambda e: list(e.path))
        if doc_errors:
            for err in doc_errors:
                result.errors.append({
                    "document": doc_name,
                    "reason": err.message,
                    "path": list(err.path),
                })
        else:
            result.results.append({
                "document": doc_name,
                "status": "PASS_SCHEMA"
            })

    return result
```

⸻

run_allowed_rules

O hb_plan.py não deve executar tudo cegamente.
Ele executa os checker_id permitidos pelo meta-contrato e pelo módulo.


```python
from __future__ import annotations

from hbtrack_lint.checkers import register_all_checkers
from hbtrack_lint.engine import run_rule


def run_allowed_rules(ctx):
    register_all_checkers()

    cross_rules = ctx.contracts["00_ATLETAS_CROSS_LINTER_RULES.json"]
    allowed_checker_ids = set()

    # união das regras declaradas no meta-contrato
    for section in [
        "document_shape_rules",
        "cross_rules",
        "event_rules",
        "projection_rules",
        "side_effect_rules",
        "concurrency_rules",
        "ui_state_rules",
        "time_determinism_rules",
        "test_scenario_rules",
        "stub_anchor_rules",
        "handoff_rules",
        "restriction_prompt_rules",
        "diff_validation_rules",
    ]:
        for rule in cross_rules.get(section, []):
            allowed_checker_ids.add(rule["checker_id"])

    results = []
    for section in [
        "document_shape_rules",
        "cross_rules",
        "event_rules",
        "projection_rules",
        "side_effect_rules",
        "concurrency_rules",
        "ui_state_rules",
        "time_determinism_rules",
        "test_scenario_rules",
        "stub_anchor_rules",
        "handoff_rules",
        "restriction_prompt_rules",
        "diff_validation_rules",
    ]:
        for rule in cross_rules.get(section, []):
            if rule["checker_id"] not in allowed_checker_ids:
                continue
            results.append(run_rule(rule, ctx))

    return results
```

⸻

build_anchor_manifest

Esse é o artefato que “mapeia a mina”.

Regras que ele deve seguir
	•	cada arquivo gerado com âncoras entra no manifesto
	•	cada âncora tem symbol_id
	•	cada âncora tem public_symbol
	•	cada âncora tem anchor_hash
	•	o manifesto é referenciado por hash no handoff

```python
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_anchor_manifest(repo_root: Path, module_root: Path, contracts: dict[str, object]) -> dict:
    traceability = contracts["08_ATLETAS_TRACEABILITY.yaml"]
    handoff_files = []

    for op in traceability.get("operations", []):
        operation_id = op["operation_id"]
        binding = op["implementation_binding"]

        backend_handler = binding.get("backend_handler")
        if backend_handler:
            file_path = binding.get("backend_handler_file", "backend/app/services/athlete_service.py")
            start_marker = f"# <HB-BODY-START:{operation_id}>"
            end_marker = f"# <HB-BODY-END:{operation_id}>"
            handoff_files.append({
                "path": file_path,
                "language": "python",
                "anchors": [
                    {
                        "symbol_id": operation_id,
                        "public_symbol": backend_handler,
                        "anchor_type": "function_body",
                        "start_marker": start_marker,
                        "end_marker": end_marker,
                        "anchor_hash": _hash_text(start_marker + end_marker + backend_handler)
                    }
                ]
            })

    return {
        "module_id": traceability["meta"]["module_id"],
        "snapshot_hash": "0" * 64,
        "files": handoff_files
    }
```
Observação crítica

Na implementação real, o manifesto deve ser derivado de stubs gerados, não só dos contratos.
Ou seja: o ideal é gerar os stubs primeiro e depois extrair do arquivo físico.

⸻

build_handoff

Aqui o planner transforma o pack em ordem de execução.

```python
from __future__ import annotations

from pathlib import Path
from hbtrack_lint.hashing import sha256_file


def build_handoff(repo_root: Path, module_root: Path, contracts: dict[str, object], anchor_manifest: dict, reports_dir: Path) -> dict:
    traceability = contracts["08_ATLETAS_TRACEABILITY.yaml"]
    openapi = contracts["01_ATLETAS_OPENAPI.yaml"]
    cross = contracts["00_ATLETAS_CROSS_LINTER_RULES.json"]

    allowed_operation_ids = [op["operation_id"] for op in traceability.get("operations", [])]

    operation_file_bindings = []
    allowed_file_paths = set()

    for op in traceability.get("operations", []):
        binding = op["implementation_binding"]
        file_paths = []

        for key in [
            "backend_handler_file",
            "backend_service_file",
            "repository_file",
            "projection_file",
            "side_effect_file",
            "frontend_screen_file",
            "frontend_component_file",
            "e2e_spec_file",
        ]:
            value = binding.get(key)
            if value:
                file_paths.append(value)
                allowed_file_paths.add(value)

        operation_file_bindings.append({
            "operation_id": op["operation_id"],
            "file_paths": sorted(set(file_paths)),
            "public_symbols": [
                sym for sym in [
                    binding.get("backend_handler"),
                    binding.get("backend_service"),
                    binding.get("frontend_component"),
                ] if sym
            ]
        })

    artifacts = []
    for name in [
        "00_ATLETAS_CROSS_LINTER_RULES.json",
        "01_ATLETAS_OPENAPI.yaml",
        "08_ATLETAS_TRACEABILITY.yaml",
        "13_ATLETAS_DB_CONTRACT.yaml",
        "14_ATLETAS_UI_CONTRACT.yaml",
        "15_ATLETAS_INVARIANTS.yaml",
        "05_ATLETAS_EVENTS.asyncapi.yaml",
        "17_ATLETAS_PROJECTIONS.yaml",
        "18_ATLETAS_SIDE_EFFECTS.yaml",
        "19_ATLETAS_TEST_SCENARIOS.yaml",
        "20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md",
    ]:
        path = module_root / name
        if path.exists():
            artifacts.append({
                "path": str(path.relative_to(repo_root)),
                "role": _role_for_doc(name),
                "sha256": sha256_file(path)
            })

    return {
        "meta": {
            "handoff_id": "HANDOFF-ATHLETES-2026-03-07-001",
            "module_id": traceability["meta"]["module_id"],
            "module_version": traceability["meta"]["module_version"],
            "status": "READY_FOR_EXECUTION",
            "authority_level": "EXECUTION_GATE",
            "issued_by": "HB_PLAN",
            "issued_at": "2026-03-07T13:00:00-03:00",
            "conversation_independent": True
        },
        "integrity": {
            "snapshot_mode": "hash_locked",
            "artifacts": artifacts,
            "stale_snapshot_policy": "block_execution"
        },
        "execution_scope": {
            "allowed_operation_ids": allowed_operation_ids,
            "allowed_file_paths": sorted(allowed_file_paths),
            "forbidden_write_paths": [],
            "operation_file_bindings": operation_file_bindings,
            "public_symbol_policy": {
                "public_symbols_declared_only": True,
                "private_helper_symbols": {
                    "allowed": True,
                    "naming_pattern": "^_",
                    "allowed_scope": "inside_anchor_region_only",
                    "export_forbidden": True
                }
            }
        },
        "codegen_requirements": {
            "openapi_codegen_required": True,
            "frontend_client_generation_required": True,
            "backend_stub_generation_required": True,
            "manual_symbol_creation_allowed": False,
            "required_generated_artifacts": [
                "frontend/src/lib/generated/athletes-client.ts",
                "backend/app/generated/athletes_contract_types.py",
                "backend/app/generated/athletes_stub_bindings.py"
            ]
        },
        "validator_requirements": {
            "allowed_checker_ids": _collect_checker_ids(cross),
            "required_checker_ids": [
                "check_handoff_hashes_match_snapshot",
                "check_stub_edits_stay_within_anchors",
                "check_generated_symbols_are_immutable",
                "check_no_uncontracted_public_symbols"
            ],
            "diff_validator_mode": "ast_python_and_ts"
        },
        "task_plan": {
            "ordered_steps": [
                {"step_id": "STEP-001", "actor": "HB_PLAN", "action": "validate_contract_pack_against_json_schemas", "blocking": True},
                {"step_id": "STEP-002", "actor": "HB_PLAN", "action": "run_cross_linter_with_allowed_checker_ids", "blocking": True},
                {"step_id": "STEP-003", "actor": "HB_PLAN", "action": "generate_handoff_snapshot_and_hash_lock", "blocking": True},
                {"step_id": "STEP-004", "actor": "EXECUTOR", "action": "generate_required_stubs_and_clients", "blocking": True}
            ]
        },
        "entry_gates": [
            {"gate_id": "EG-001", "name": "cross_linter_pass", "required": True}
        ],
        "exit_gates": [
            {"gate_id": "XG-001", "name": "contract_tests_pass", "required": True}
        ],
        "prohibitions": [
            "do_not_use_chat_history_as_source_of_truth",
            "do_not_create_new_symbols_outside_traceability",
            "do_not_edit_outside_anchor_regions"
        ]
    }
```

⸻

Como o hb_plan.py fecha o bootstrap

A sequência correta é:

1. carregar contratos
2. validar contratos contra schemas
3. executar checkers
4. gerar stubs
5. extrair manifesto de âncoras dos stubs
6. calcular hashes
7. gerar handoff
8. selar snapshot

Ponto importante

No esboço acima eu mantive build_anchor_manifest ainda contratual para clareza.
Na versão forte, o passo 4 e 5 precisam ser:

4. generate_stubs_from_contracts()
5. build_anchor_manifest_from_generated_files()

Porque o manifesto tem que refletir os arquivos reais.

⸻

O que falta para esse hb_plan.py virar produção
	1.	schema para cada documento do pack
	2.	gerador real de stubs Python e TSX
	3.	extração real de âncoras a partir dos stubs físicos
	4.	registry completo de checkers
	5.	escrita de report markdown/json consistente com exit code
	6.	integração com hb_verify.py

# HB VERIFY - CHECKERS 

Checkers do checkers restantes do hb_verify.py.

**check_projection_atomic_shell_integrity**

Objetivo

- Garantir que, no handler de projeção gerado, continuem existindo:
	•	with transaction_scope(projection_context) as tx
	•	projection_event_already_applied(..., tx=tx)
	•	mark_projection_event_applied(..., tx=tx)

- Impede que o Executor:
	•	apague with transaction_scope(...)
	•	apague projection_event_already_applied(...)
	•	apague mark_projection_event_applied(...)
	•	remova o tx da propagação

Ou seja: protege atomicidade + idempotência.

Estratégia:
- Para cada handler_symbol declarado em 17_ATLETAS_PROJECTIONS.yaml:
	•	localizar a FunctionDef correspondente
	•	verificar se há um With com transaction_scope(projection_context)
	•	verificar se dentro desse With existe:
	•	um if projection_event_already_applied(...): return
	•	a região ancorada
	•	uma chamada a mark_projection_event_applied(..., tx=tx) após a âncora
	•	reprovar se o With foi removido, se a chamada ao ledger foi removida, ou se o tx deixou de ser propagado

Implementação

```python
import ast


def _extract_call_name(func: ast.AST) -> tuple[str | None, str | None]:
    if isinstance(func, ast.Name):
        return func.id, None
    if isinstance(func, ast.Attribute):
        if isinstance(func.value, ast.Name):
            return func.value.id, func.attr
        return None, func.attr
    return None, None


def _keyword_uses_name(node: ast.Call, keyword_name: str, var_name: str) -> bool:
    for kw in node.keywords:
        if kw.arg == keyword_name and isinstance(kw.value, ast.Name) and kw.value.id == var_name:
            return True
    return False


class ProjectionAtomicShellVisitor(ast.NodeVisitor):
    def __init__(self, target_function: str):
        self.target_function = target_function
        self.function_found = False
        self.with_transaction_scope = False
        self.idempotency_guard_found = False
        self.ledger_mark_found = False
        self.tx_aliases: set[str] = set()
        self.violations: list[dict] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name != self.target_function:
            return

        self.function_found = True

        for stmt in node.body:
            if isinstance(stmt, ast.With):
                for item in stmt.items:
                    if isinstance(item.context_expr, ast.Call):
                        name, attr = _extract_call_name(item.context_expr.func)
                        if name == "transaction_scope" and attr is None:
                            self.with_transaction_scope = True
                            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                                self.tx_aliases.add(item.optional_vars.id)
                            else:
                                self.violations.append({
                                    "kind": "missing_tx_alias",
                                    "lineno": stmt.lineno,
                                })
                            self._inspect_transaction_block(stmt)

        if not self.with_transaction_scope:
            self.violations.append({
                "kind": "missing_transaction_scope",
                "function": node.name,
                "lineno": node.lineno,
            })

    def _inspect_transaction_block(self, with_node: ast.With) -> None:
        for stmt in with_node.body:
            # idempotency guard
            if isinstance(stmt, ast.If) and isinstance(stmt.test, ast.Call):
                name, attr = _extract_call_name(stmt.test.func)
                if name == "projection_event_already_applied" and attr is None:
                    tx_ok = any(_keyword_uses_name(stmt.test, "tx", tx_name) for tx_name in self.tx_aliases)
                    if tx_ok:
                        self.idempotency_guard_found = True
                    else:
                        self.violations.append({
                            "kind": "idempotency_guard_missing_tx",
                            "lineno": stmt.lineno,
                        })

            # ledger mark
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                name, attr = _extract_call_name(stmt.value.func)
                if name == "mark_projection_event_applied" and attr is None:
                    tx_ok = any(_keyword_uses_name(stmt.value, "tx", tx_name) for tx_name in self.tx_aliases)
                    if tx_ok:
                        self.ledger_mark_found = True
                    else:
                        self.violations.append({
                            "kind": "ledger_mark_missing_tx",
                            "lineno": stmt.lineno,
                        })

    def finalize(self):
        if self.function_found:
            if not self.idempotency_guard_found:
                self.violations.append({"kind": "missing_idempotency_guard"})
            if not self.ledger_mark_found:
                self.violations.append({"kind": "missing_ledger_mark"})

Checker

@register_checker("check_projection_atomic_shell_integrity")
def check_projection_atomic_shell_integrity(rule: dict, ctx: ValidationContext) -> RuleResult:
    projections = ctx.contracts["17_ATLETAS_PROJECTIONS.yaml"]
    violations = []

    for read_model in projections.get("read_models", []):
        file_path = ctx.repo_root / read_model["target_file"]
        if not file_path.exists():
            violations.append({
                "file": str(file_path),
                "reason": "projection_file_missing",
            })
            continue

        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))

        for handler in read_model.get("event_handlers", []):
            visitor = ProjectionAtomicShellVisitor(handler["handler_symbol"])
            visitor.visit(tree)
            visitor.finalize()

            if not visitor.function_found:
                violations.append({
                    "file": str(file_path),
                    "handler_symbol": handler["handler_symbol"],
                    "reason": "handler_not_found",
                })
                continue

            for v in visitor.violations:
                v["file"] = str(file_path)
                v["handler_symbol"] = handler["handler_symbol"]
                violations.append(v)

    if violations:
        return RuleResult.fail(
            rule["rule_id"],
            rule["checker_id"],
            "Projection atomic shell integrity violation detected.",
            violations=violations,
        )

    return RuleResult.pass_(
        rule["rule_id"],
        rule["checker_id"],
        "Projection atomic shell integrity preserved."
    )
```

**check_side_effect_result_usage**

- Objetivo
* Garantir que o side effect gerado continue respeitando o contrato:
	•	a função retorna SideEffectResult | None
	•	o wrapper ainda faz if result is not None: mark_side_effect_delivery(...)
	•	o Executor não trocou o retorno por dict, str, bool, etc.
	•	o retorno relevante da âncora é representado por variável result

- Impede que o Executor:
	•	transforme o wrapper em função “solta”
	•	retorne dict
	•	retorne string/boolean
	•	elimine a gravação do resultado na casca
	•	elimine o return result

Ou seja: protege auditabilidade + pureza da borda.

**Limitação honesta**

A AST do Python não sabe inferir o tipo real de runtime sem análise de tipos externa. Então o checker V1 deve validar estruturalmente:
	1.	a assinatura de retorno contém SideEffectResult ou SideEffectResult | None;
	2.	existe uma variável result;
	3.	existe return result;
	4.	existe mark_side_effect_delivery(..., result=result) condicionado a result is not None;
	5.	não existe return { ... }, return "ok", etc. fora da casca prevista.

Isso já elimina a sabotagem mais comum.

Visitor

```python
class SideEffectResultUsageVisitor(ast.NodeVisitor):
    def __init__(self, target_function: str):
        self.target_function = target_function
        self.function_found = False
        self.return_annotation_ok = False
        self.result_return_found = False
        self.result_guard_found = False
        self.delivery_log_call_found = False
        self.bad_returns: list[dict] = []
        self.violations: list[dict] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name != self.target_function:
            return

        self.function_found = True
        self.return_annotation_ok = self._check_return_annotation(node.returns)

        for stmt in node.body:
            # if result is not None: mark_side_effect_delivery(..., result=result)
            if isinstance(stmt, ast.If):
                if self._is_result_not_none_check(stmt.test):
                    self.result_guard_found = True
                    for inner in stmt.body:
                        if isinstance(inner, ast.Expr) and isinstance(inner.value, ast.Call):
                            name, attr = _extract_call_name(inner.value.func)
                            if name == "mark_side_effect_delivery" and attr is None:
                                if _keyword_uses_name(inner.value, "result", "result"):
                                    self.delivery_log_call_found = True

            # return result / return None
            if isinstance(stmt, ast.Return):
                if isinstance(stmt.value, ast.Name) and stmt.value.id == "result":
                    self.result_return_found = True
                elif isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
                    pass
                else:
                    self.bad_returns.append({
                        "kind": "unexpected_top_level_return",
                        "lineno": stmt.lineno,
                        "ast": ast.dump(stmt.value, include_attributes=False) if stmt.value else None,
                    })

        if not self.return_annotation_ok:
            self.violations.append({"kind": "invalid_return_annotation"})
        if not self.result_guard_found:
            self.violations.append({"kind": "missing_result_guard"})
        if not self.delivery_log_call_found:
            self.violations.append({"kind": "missing_delivery_log_call"})
        if not self.result_return_found:
            self.violations.append({"kind": "missing_return_result"})
        self.violations.extend(self.bad_returns)

    @staticmethod
    def _is_result_not_none_check(test: ast.AST) -> bool:
        # result is not None
        return (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.id == "result"
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.IsNot)
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value is None
        )

    @staticmethod
    def _check_return_annotation(annotation: ast.AST | None) -> bool:
        if annotation is None:
            return False
        dumped = ast.dump(annotation, include_attributes=False)
        return "SideEffectResult" in dumped

Checker

@register_checker("check_side_effect_result_usage")
def check_side_effect_result_usage(rule: dict, ctx: ValidationContext) -> RuleResult:
    contract = ctx.contracts["18_ATLETAS_SIDE_EFFECTS.yaml"]
    violations = []

    for consumer in contract.get("consumers", []):
        file_path = ctx.repo_root / consumer["handler_file"]
        if not file_path.exists():
            violations.append({
                "consumer_id": consumer["consumer_id"],
                "reason": "handler_file_missing",
                "file": str(file_path),
            })
            continue

        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))

        visitor = SideEffectResultUsageVisitor(consumer["handler_symbol"])
        visitor.visit(tree)

        if not visitor.function_found:
            violations.append({
                "consumer_id": consumer["consumer_id"],
                "reason": "handler_not_found",
                "handler_symbol": consumer["handler_symbol"],
                "file": str(file_path),
            })
            continue

        for v in visitor.violations:
            v["consumer_id"] = consumer["consumer_id"]
            v["handler_symbol"] = consumer["handler_symbol"]
            v["file"] = str(file_path)
            violations.append(v)

    if violations:
        return RuleResult.fail(
            rule["rule_id"],
            rule["checker_id"],
            "Side-effect result contract violation detected.",
            violations=violations,
        )

    return RuleResult.pass_(
        rule["rule_id"],
        rule["checker_id"],
        "Side-effect handlers preserve SideEffectResult contract."
    )
```

* Limitação honesta
O checker de SideEffectResult em AST garante estrutura, não tipo semântico completo de runtime.

- Para chegar ainda mais longe, a V2 pode usar:
	•	mypy/pyright sobre os stubs gerados
	•	Protocols das integrações
	•	retorno tipado obrigatório com análise estática complementar

Mas a V1 acima já fecha o que mais importa para o HB Track agora: o Executor não consegue “desmontar” o wrapper sem ser detectado.

Âncora precisa ser materializada em arquivo físico pelo planner, antes de qualquer ação do Executor.

Então o próximo artefato correto é mesmo:

hbtrack_lint/stubs/generator.py

A função dele é simples e soberana:
	1.	ler contratos estruturados
	2.	decidir caminhos de arquivo a partir do binding
	3.	gerar arquivos físicos .py e .tsx
	4.	cravar âncoras nos lugares corretos
	5.	impedir que o Executor invente estrutura

Abaixo está a V1 real do gerador de stubs para o módulo ATHLETES.

hbtrack_lint/stubs/generator.py

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import hashlib


@dataclass(frozen=True)
class GeneratedFile:
    path: Path
    content: str


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_if_changed(path: Path, content: str) -> None:
    _ensure_parent(path)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing == content:
            return
    path.write_text(content, encoding="utf-8")


def _py_anchor_start(operation_id: str) -> str:
    return f"# <HB-BODY-START:{operation_id}>"


def _py_anchor_end(operation_id: str) -> str:
    return f"# <HB-BODY-END:{operation_id}>"


def _tsx_anchor_start(screen_id: str) -> str:
    return f"{{/* <HB-UI-BODY-START:{screen_id}> */}}"


def _tsx_anchor_end(screen_id: str) -> str:
    return f"{{/* <HB-UI-BODY-END:{screen_id}> */}}"


def _header_comment(module_id: str, contract_hash: str, extra: list[str] | None = None) -> str:
    lines = [
        "# GENERATED FILE - DO NOT EDIT OUTSIDE AUTHORIZED ANCHORS",
        f"# HB_MODULE: {module_id}",
        f"# HB_CONTRACT_HASH: {contract_hash}",
    ]
    if extra:
        lines.extend(extra)
    return "\n".join(lines)


def _ts_header_comment(module_id: str, contract_hash: str, extra: list[str] | None = None) -> str:
    lines = [
        "// GENERATED FILE - DO NOT EDIT OUTSIDE AUTHORIZED ANCHORS",
        f"// HB_MODULE: {module_id}",
        f"// HB_CONTRACT_HASH: {contract_hash}",
    ]
    if extra:
        lines.extend([f"// {line}" for line in extra])
    return "\n".join(lines)


def _role_for_path(path_str: str) -> str:
    p = path_str.replace("\\", "/")
    if "/services/" in p:
        return "service"
    if "/repositories/" in p:
        return "repository"
    if "/models/" in p:
        return "model"
    if "/schemas/" in p:
        return "schema"
    if "/projections/" in p:
        return "projection"
    if "/side_effects/" in p:
        return "side_effect"
    if "/reference/" in p:
        return "reference"
    if p.endswith(".tsx") and "/screens/" in p:
        return "screen"
    if p.endswith(".tsx") and "/components/" in p:
        return "component"
    if p.endswith(".ts") and "/generated/" in p:
        return "generated_ts"
    if p.endswith(".py") and "/generated/" in p:
        return "generated_py"
    if "/tests/" in p:
        return "test"
    return "other"


def _py_function_stub(
    module_id: str,
    contract_hash: str,
    operation_id: str,
    function_name: str,
    request_type: str = "dict",
    response_type: str = "dict",
) -> str:
    start = _py_anchor_start(operation_id)
    end = _py_anchor_end(operation_id)
    header = _header_comment(
        module_id=module_id,
        contract_hash=contract_hash,
        extra=[
            f"HB_OPERATION: {operation_id}",
            f"HB_PUBLIC_SYMBOL: {function_name}",
        ],
    )
    return f'''{header}

from __future__ import annotations


def {function_name}(payload: {request_type}) -> {response_type}:
    {start}
    raise NotImplementedError("{function_name} body must be implemented inside anchor only.")
    {end}
'''


def _py_class_stub(
    module_id: str,
    contract_hash: str,
    class_name: str,
    fields: list[tuple[str, str]],
) -> str:
    header = _header_comment(
        module_id=module_id,
        contract_hash=contract_hash,
        extra=[f"HB_PUBLIC_SYMBOL: {class_name}"],
    )
    field_lines = "\n".join([f"    {name}: {typ}" for name, typ in fields]) or "    pass"
    return f'''{header}

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class {class_name}:
{field_lines}
'''


def _py_projection_stub(
    module_id: str,
    contract_hash: str,
    event_type: str,
    version: int,
    handler_symbol: str,
) -> str:
    operation_id = f"projection__{event_type.lower()}__v{version}"
    start = _py_anchor_start(operation_id)
    end = _py_anchor_end(operation_id)
    header = _header_comment(
        module_id=module_id,
        contract_hash=contract_hash,
        extra=[
            f"HB_EVENT_TYPE: {event_type}",
            f"HB_EVENT_VERSION: {version}",
            f"HB_PUBLIC_SYMBOL: {handler_symbol}",
            "HB_ROLE: PROJECTION_HANDLER",
        ],
    )
    return f'''{header}

from __future__ import annotations


def {handler_symbol}(event: dict) -> None:
    {start}
    raise NotImplementedError("{handler_symbol} must be replay-safe and implemented inside anchor only.")
    {end}
'''


def _py_side_effect_stub(
    module_id: str,
    contract_hash: str,
    side_effect_id: str,
    event_type: str,
    handler_symbol: str,
    idempotency_key: str,
) -> str:
    operation_id = f"side_effect__{side_effect_id.lower()}__dispatch"
    start = _py_anchor_start(operation_id)
    end = _py_anchor_end(operation_id)
    header = _header_comment(
        module_id=module_id,
        contract_hash=contract_hash,
        extra=[
            f"HB_SIDE_EFFECT_ID: {side_effect_id}",
            f"HB_EVENT_TYPE: {event_type}",
            f"HB_PUBLIC_SYMBOL: {handler_symbol}",
            f"HB_IDEMPOTENCY_KEY_TEMPLATE: {idempotency_key}",
            "HB_ROLE: SIDE_EFFECT_HANDLER",
        ],
    )
    return f'''{header}

from __future__ import annotations


def {handler_symbol}(event: dict) -> None:
    {start}
    raise NotImplementedError("{handler_symbol} must enforce idempotency key contract and be implemented inside anchor only.")
    {end}
'''


def _tsx_screen_stub(
    module_id: str,
    contract_hash: str,
    screen_id: str,
    component_name: str,
    required_testids: list[str],
) -> str:
    start = _tsx_anchor_start(screen_id)
    end = _tsx_anchor_end(screen_id)
    header = _ts_header_comment(
        module_id=module_id,
        contract_hash=contract_hash,
        extra=[
            f"HB_SCREEN_ID: {screen_id}",
            f"HB_PUBLIC_SYMBOL: {component_name}",
        ],
    )
    root_testid = f'{screen_id}.screen'
    extra_testid_nodes = "\n".join(
        [f'      <div data-testid="{tid}" />' for tid in required_testids if tid != root_testid]
    )
    return f'''{header}

import React from "react";

export function {component_name}() {{
  return (
    <div data-testid="{root_testid}">
      {start}
      <div data-testid="{root_testid}" />
{extra_testid_nodes if extra_testid_nodes else ""}
      {{/* implementation goes inside anchor only */}}
      {end}
    </div>
  );
}}
'''


def _tsx_component_stub(
    module_id: str,
    contract_hash: str,
    component_id: str,
    component_name: str,
    required_testids: list[str],
) -> str:
    start = _tsx_anchor_start(component_id)
    end = _tsx_anchor_end(component_id)
    header = _ts_header_comment(
        module_id=module_id,
        contract_hash=contract_hash,
        extra=[
            f"HB_COMPONENT_ID: {component_id}",
            f"HB_PUBLIC_SYMBOL: {component_name}",
        ],
    )
    nodes = "\n".join([f'      <div data-testid="{tid}" />' for tid in required_testids])
    return f'''{header}

import React from "react";

export function {component_name}() {{
  return (
    <div>
      {start}
{nodes if nodes else "      <div />"}
      {end}
    </div>
  );
}}
'''


def _generated_contract_types_py(module_id: str, contract_hash: str) -> str:
    header = _header_comment(module_id, contract_hash, extra=["HB_ROLE: GENERATED_CONTRACT_TYPES"])
    return f'''{header}

from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID
from datetime import date, datetime
from typing import Optional


@dataclass
class AthleteCreateRequest:
    full_name: str
    birth_date: date
    category_id: UUID
    team_id: Optional[UUID] = None
    federation_id: Optional[str] = None
    dominant_hand: Optional[str] = None
    competition_reference_year: Optional[int] = None


@dataclass
class AthleteResponse:
    athlete_id: UUID
    full_name: str
    birth_date: date
    category_id: UUID
    team_id: Optional[UUID]
    federation_id: Optional[str]
    dominant_hand: Optional[str]
    status: str
    created_at: datetime
'''


def _generated_stub_bindings_py(module_id: str, contract_hash: str, operations: list[dict]) -> str:
    header = _header_comment(module_id, contract_hash, extra=["HB_ROLE: GENERATED_STUB_BINDINGS"])
    lines = [
        f'"{op["operation_id"]}": "{op["implementation_binding"].get("backend_handler", "")}"'
        for op in operations
        if op["implementation_binding"].get("backend_handler")
    ]
    mapping = ",\n    ".join(lines)
    return f'''{header}

from __future__ import annotations

OPERATION_TO_HANDLER = {{
    {mapping}
}}
'''


def _generated_client_ts(module_id: str, contract_hash: str) -> str:
    header = _ts_header_comment(module_id, contract_hash, extra=["HB_ROLE: GENERATED_FRONTEND_CLIENT"])
    return f'''{header}

export type AthleteCreateRequest = {{
  full_name: string;
  birth_date: string;
  category_id: string;
  team_id?: string | null;
  federation_id?: string | null;
  dominant_hand?: string | null;
  competition_reference_year?: number | null;
}};

export type AthleteResponse = {{
  athlete_id: string;
  full_name: string;
  birth_date: string;
  category_id: string;
  team_id?: string | null;
  federation_id?: string | null;
  dominant_hand?: string | null;
  status: string;
  created_at: string;
}};

export async function athletesCreate(payload: AthleteCreateRequest): Promise<AthleteResponse> {{
  throw new Error("Generated client placeholder.");
}}

export async function athletesList(): Promise<AthleteResponse[]> {{
  throw new Error("Generated client placeholder.");
}}

export async function athletesGet(athleteId: string): Promise<AthleteResponse> {{
  throw new Error("Generated client placeholder.");
}}
'''


def _snake_to_pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def _collect_ui_testids(ui_contract: dict, screen_id: str) -> list[str]:
    for screen in ui_contract.get("screens", []):
        if screen["screen_id"] == screen_id:
            values = []
            for sel in screen.get("selectors", []):
                dom = sel.get("dom_contract", {})
                if dom.get("attribute") == "data-testid" and dom.get("value"):
                    values.append(dom["value"])
            return values
    return []


def _build_python_service_files(
    module_id: str,
    contract_hash: str,
    operations: list[dict],
) -> dict[str, str]:
    files: dict[str, list[str]] = {}

    for op in operations:
        binding = op["implementation_binding"]
        operation_id = op["operation_id"]

        file_specs = [
            ("backend_handler_file", binding.get("backend_handler")),
            ("backend_service_file", binding.get("backend_service")),
            ("repository_file", binding.get("repository_symbol")),
        ]

        for file_key, symbol in file_specs:
            file_path = binding.get(file_key)
            if not file_path or not symbol:
                continue
            files.setdefault(file_path, [])
            files[file_path].append(
                _py_function_stub(
                    module_id=module_id,
                    contract_hash=contract_hash,
                    operation_id=operation_id,
                    function_name=symbol,
                    request_type="dict",
                    response_type="dict",
                )
            )

    return {path: "\n\n".join(content_blocks).rstrip() + "\n" for path, content_blocks in files.items()}


def _build_projection_files(
    module_id: str,
    contract_hash: str,
    projections_contract: dict,
) -> dict[str, str]:
    files: dict[str, list[str]] = {}

    for projection in projections_contract.get("projections", []):
        for handler in projection.get("handlers", []):
            file_path = handler["file_path"]
            files.setdefault(file_path, [])
            files[file_path].append(
                _py_projection_stub(
                    module_id=module_id,
                    contract_hash=contract_hash,
                    event_type=handler["event_type"],
                    version=1,
                    handler_symbol=handler["handler_symbol"],
                )
            )

    return {path: "\n\n".join(content_blocks).rstrip() + "\n" for path, content_blocks in files.items()}


def _build_side_effect_files(
    module_id: str,
    contract_hash: str,
    side_effects_contract: dict,
) -> dict[str, str]:
    files: dict[str, list[str]] = {}

    for effect in side_effects_contract.get("side_effect_policies", []):
        file_path = effect["handler_file"]
        files.setdefault(file_path, [])
        files[file_path].append(
            _py_side_effect_stub(
                module_id=module_id,
                contract_hash=contract_hash,
                side_effect_id=effect["side_effect_id"],
                event_type=effect["event_type"],
                handler_symbol=effect["handler_symbol"],
                idempotency_key=effect["idempotency_key"],
            )
        )

    return {path: "\n\n".join(content_blocks).rstrip() + "\n" for path, content_blocks in files.items()}


def _build_ui_files(
    module_id: str,
    contract_hash: str,
    ui_contract: dict,
    traceability: dict,
) -> dict[str, str]:
    files: dict[str, str] = {}

    for op in traceability.get("operations", []):
        binding = op["implementation_binding"]

        screen_file = binding.get("frontend_screen_file")
        screen_id = binding.get("screen_id")
        screen_component = binding.get("frontend_component")

        if screen_file and screen_id and screen_component:
            files[screen_file] = _tsx_screen_stub(
                module_id=module_id,
                contract_hash=contract_hash,
                screen_id=screen_id,
                component_name=screen_component,
                required_testids=_collect_ui_testids(ui_contract, screen_id),
            )

        component_file = binding.get("frontend_component_file")
        component_id = binding.get("component_id")
        component_name = binding.get("frontend_component")

        if component_file and component_id and component_name:
            files[component_file] = _tsx_component_stub(
                module_id=module_id,
                contract_hash=contract_hash,
                component_id=component_id,
                component_name=component_name,
                required_testids=_collect_ui_testids(ui_contract, screen_id or component_id),
            )

    return files


def _build_reference_files(
    module_id: str,
    contract_hash: str,
    invariants_contract: dict,
) -> dict[str, str]:
    files: dict[str, str] = {}

    for fn in invariants_contract.get("domain_functions", []):
        location = fn["location"]
        if location.endswith("category_birth_year_mapping.py"):
            files[location] = _header_comment(
                module_id,
                contract_hash,
                extra=["HB_ROLE: REFERENCE_FUNCTIONS"]
            ) + '''

from __future__ import annotations


CATEGORY_MAP = {
    2026: {
        "U14": {2012, 2013},
        "U16": {2010, 2011},
        "U18": {2008, 2009}
    }
}


def category_allowed_birth_years(competition_year: int, category_code: str) -> set[int]:
    return CATEGORY_MAP.get(competition_year, {}).get(category_code, set())
'''
    return files


def generate_stub_files(repo_root: Path, module_root: Path, contracts: dict[str, object]) -> list[GeneratedFile]:
    traceability = contracts["08_ATLETAS_TRACEABILITY.yaml"]
    ui_contract = contracts["14_ATLETAS_UI_CONTRACT.yaml"]
    invariants_contract = contracts["15_ATLETAS_INVARIANTS.yaml"]
    projections_contract = contracts["17_ATLETAS_PROJECTIONS.yaml"]
    side_effects_contract = contracts["18_ATLETAS_SIDE_EFFECTS.yaml"]

    module_id = traceability["meta"]["module_id"]
    contract_hash = _sha256_text(module_id + "::stub-seed::v1")

    operations = traceability.get("operations", [])

    generated: list[GeneratedFile] = []

    # generated core types
    generated.append(
        GeneratedFile(
            path=repo_root / "backend/app/generated/athletes_contract_types.py",
            content=_generated_contract_types_py(module_id, contract_hash),
        )
    )
    generated.append(
        GeneratedFile(
            path=repo_root / "backend/app/generated/athletes_stub_bindings.py",
            content=_generated_stub_bindings_py(module_id, contract_hash, operations),
        )
    )
    generated.append(
        GeneratedFile(
            path=repo_root / "frontend/src/lib/generated/athletes-client.ts",
            content=_generated_client_ts(module_id, contract_hash),
        )
    )

    # service/repository/model/schema-ish stubs from operation bindings
    for path_str, content in _build_python_service_files(module_id, contract_hash, operations).items():
        generated.append(GeneratedFile(path=repo_root / path_str, content=content))

    # projections
    for path_str, content in _build_projection_files(module_id, contract_hash, projections_contract).items():
        generated.append(GeneratedFile(path=repo_root / path_str, content=content))

    # side effects
    for path_str, content in _build_side_effect_files(module_id, contract_hash, side_effects_contract).items():
        generated.append(GeneratedFile(path=repo_root / path_str, content=content))

    # reference functions
    for path_str, content in _build_reference_files(module_id, contract_hash, invariants_contract).items():
        generated.append(GeneratedFile(path=repo_root / path_str, content=content))

    # UI
    for path_str, content in _build_ui_files(module_id, contract_hash, ui_contract, traceability).items():
        generated.append(GeneratedFile(path=repo_root / path_str, content=content))

    return generated


def materialize_stub_files(files: Iterable[GeneratedFile]) -> list[Path]:
    written: list[Path] = []
    for file in files:
        _write_if_changed(file.path, file.content)
        written.append(file.path)
    return written


⸻

Como esse gerador resolve o “Ovo e a Galinha”

Esse é o ponto central da sua crítica.

Antes:
	•	contrato dizia que deveria haver âncora
	•	mas âncora ainda não existia no disco

Agora:
	•	generate_stub_files() produz o arquivo físico
	•	materialize_stub_files() grava o arquivo
	•	só depois disso o build_anchor_manifest() deve ler os arquivos reais e extrair as âncoras

A ordem correta do hb_plan.py passa a ser:

1. validar contratos
2. rodar checkers contratuais
3. gerar stubs físicos
4. materializar stubs
5. extrair manifesto de âncoras dos stubs físicos
6. gerar handoff
7. calcular hashes
8. selar snapshot


⸻

Integração correta no hb_plan.py

O trecho decisivo deve trocar isto:

anchor_manifest = build_anchor_manifest(
    repo_root=repo_root,
    module_root=module_root,
    contracts=contracts,
)

por isto:

from hbtrack_lint.stubs.generator import generate_stub_files, materialize_stub_files
from hbtrack_lint.anchor_manifest import build_anchor_manifest_from_files

generated_files = generate_stub_files(
    repo_root=repo_root,
    module_root=module_root,
    contracts=contracts,
)
materialized_paths = materialize_stub_files(generated_files)

anchor_manifest = build_anchor_manifest_from_files(
    repo_root=repo_root,
    file_paths=materialized_paths,
    module_id=contracts["08_ATLETAS_TRACEABILITY.yaml"]["meta"]["module_id"],
)


⸻

build_anchor_manifest_from_files

Esse é o complemento obrigatório.

from __future__ import annotations

from pathlib import Path
import hashlib
import re


PY_START = re.compile(r"^\s*#\s*<HB-BODY-START:([^>]+)>\s*$")
PY_END = re.compile(r"^\s*#\s*<HB-BODY-END:([^>]+)>\s*$")
TS_START = re.compile(r"HB-(?:UI-)?BODY-START:([^>]+)")
TS_END = re.compile(r"HB-(?:UI-)?BODY-END:([^>]+)")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_anchor_manifest_from_files(repo_root: Path, file_paths: list[Path], module_id: str) -> dict:
    files = []

    for path in file_paths:
        source = path.read_text(encoding="utf-8")
        lines = source.splitlines()

        anchors = []
        stack = {}

        for idx, line in enumerate(lines, start=1):
            m1 = PY_START.match(line)
            if m1:
                stack[m1.group(1)] = ("python", idx, line)
                continue

            m2 = PY_END.match(line)
            if m2:
                symbol_id = m2.group(1)
                lang, start_line, start_marker = stack.pop(symbol_id)
                anchors.append({
                    "symbol_id": symbol_id,
                    "anchor_type": "function_body",
                    "start_line": start_line,
                    "end_line": idx,
                    "start_marker": start_marker,
                    "end_marker": line,
                    "anchor_hash": _sha256_text(start_marker + line)
                })
                continue

            m3 = TS_START.search(line)
            if m3:
                stack[m3.group(1)] = ("typescript", idx, line)
                continue

            m4 = TS_END.search(line)
            if m4:
                symbol_id = m4.group(1)
                lang, start_line, start_marker = stack.pop(symbol_id)
                anchors.append({
                    "symbol_id": symbol_id,
                    "anchor_type": "ui_body",
                    "start_line": start_line,
                    "end_line": idx,
                    "start_marker": start_marker,
                    "end_marker": line,
                    "anchor_hash": _sha256_text(start_marker + line)
                })

        language = "typescript" if path.suffix in {".ts", ".tsx"} else "python"

        files.append({
            "path": str(path.relative_to(repo_root)),
            "language": language,
            "anchors": anchors
        })

    return {
        "module_id": module_id,
        "files": files
    }
```

### Ajuste obrigatório no generator.py

Antes do hb_verify.py, o gerador precisa tipar os stubs com classes geradas.

No _build_python_service_files, troque a heurística genérica por algo contratual.

Versão corrigida

```python
def _request_response_types_for_operation(operation_id: str) -> tuple[str, str]:
    mapping = {
        "athletes__athlete__create": ("AthleteCreateRequest", "AthleteResponse"),
        "athletes__athlete__list": ("dict", "list[AthleteResponse]"),
        "athletes__athlete__get": ("dict", "AthleteResponse"),
    }
    return mapping.get(operation_id, ("dict", "dict"))

E no gerador:

req_type, resp_type = _request_response_types_for_operation(operation_id)

files[file_path].append(
    _py_function_stub(
        module_id=module_id,
        contract_hash=contract_hash,
        operation_id=operation_id,
        function_name=symbol,
        request_type=req_type,
        response_type=resp_type,
    )
)

```

Além disso, se usar tipos gerados, o stub precisa importar esses tipos.

```python
_py_function_stub ajustado

def _py_function_stub(
    module_id: str,
    contract_hash: str,
    operation_id: str,
    function_name: str,
    request_type: str = "dict",
    response_type: str = "dict",
) -> str:
    start = _py_anchor_start(operation_id)
    end = _py_anchor_end(operation_id)
    header = _header_comment(
        module_id=module_id,
        contract_hash=contract_hash,
        extra=[
            f"HB_OPERATION: {operation_id}",
            f"HB_PUBLIC_SYMBOL: {function_name}",
        ],
    )

    imports = []
    if request_type != "dict" or response_type != "dict":
        imports.append(
            "from backend.app.generated.athletes_contract_types import "
            f"{request_type.split('[')[0].replace(']', '')}, AthleteResponse"
        )

    imports_block = "\n".join(imports)

    return f'''{header}

from __future__ import annotations
{imports_block}


def {function_name}(payload: {request_type}) -> {response_type}:
    {start}
    raise NotImplementedError("{function_name} body must be implemented inside anchor only.")
    {end}
```

Isso fecha a reentrada de dict genérico como brecha semântica.

⸻

2) Objetivo do hb_verify.py

Entrada:
	•	16_ATLETAS_AGENT_HANDOFF.json
	•	_reports/anchor_manifest.json
	•	workspace atual

Saída:
	•	_reports/hb_verify_result.json
	•	_reports/hb_verify_result.md

Exit codes:
	•	0 PASS
	•	2 FAIL_ACTIONABLE
	•	3 ERROR_INFRA
	•	4 BLOCKED_INPUT

Regras:
	•	não recalcula handoff
	•	não corrige nada
	•	não “interpreta”
	•	só verifica

⸻

3) hb_verify.py — esqueleto principal

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from hbtrack_lint.context import ValidationContext
from hbtrack_lint.loader import load_contract_pack
from hbtrack_lint.hashing import sha256_file, sha256_jsonable
from hbtrack_lint.reports import write_verify_reports
from hbtrack_lint.schemas import validate_documents_against_schemas
from hbtrack_lint.checker_registry import run_handoff_required_rules
from hbtrack_lint.anchor_manifest import load_anchor_manifest


EXIT_PASS = 0
EXIT_FAIL_ACTIONABLE = 2
EXIT_ERROR_INFRA = 3
EXIT_BLOCKED_INPUT = 4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HB Track deterministic verifier")
    parser.add_argument(
        "module_root",
        type=Path,
        help="Path to module contract pack, e.g. docs/hbtrack/modulos/atletas"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root"
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("_reports"),
        help="Output directory for reports"
    )
    parser.add_argument(
        "--original-stubs-dir",
        type=Path,
        default=Path("_reports/original_stubs"),
        help="Directory containing planner-generated pristine stubs"
    )
    return parser.parse_args()


def verify_snapshot_hash(handoff: dict) -> tuple[bool, str]:
    provisional = json.loads(json.dumps(handoff))
    expected = provisional["integrity"]["snapshot_hash"]
    provisional["integrity"]["snapshot_hash"] = "0" * 64
    actual = sha256_jsonable(provisional)
    return actual == expected, actual


def run_ts_validator(repo_root: Path, handoff: dict, reports_dir: Path) -> tuple[bool, str]:
    mode = handoff.get("validator_requirements", {}).get("diff_validator_mode", "ast_python")
    if mode not in {"ast_python_and_ts", "hybrid"}:
        return True, "TS validator not required"

    script = repo_root / "scripts" / "hb_verify_ui.mjs"
    if not script.exists():
        return False, f"Missing TS validator script: {script}"

    result = subprocess.run(
        ["node", str(script), "--repo-root", str(repo_root), "--reports-dir", str(reports_dir)],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return False, result.stderr or result.stdout or "TS validator failed"

    return True, result.stdout.strip() or "TS validator PASS"


def main() -> int:
    args = parse_args()

    try:
        repo_root = args.repo_root.resolve()
        module_root = args.module_root.resolve()
        reports_dir = (repo_root / args.reports_dir).resolve()
        reports_dir.mkdir(parents=True, exist_ok=True)

        handoff_path = module_root / "16_ATLETAS_AGENT_HANDOFF.json"
        if not handoff_path.exists():
            write_verify_reports(
                reports_dir=reports_dir,
                status="BLOCKED_INPUT",
                errors=[{"reason": f"Missing handoff: {handoff_path}"}],
                warnings=[],
                results=[],
            )
            return EXIT_BLOCKED_INPUT

        handoff = json.loads(handoff_path.read_text(encoding="utf-8"))

        ok_hash, recalculated = verify_snapshot_hash(handoff)
        if not ok_hash:
            write_verify_reports(
                reports_dir=reports_dir,
                status="FAIL_ACTIONABLE",
                errors=[{
                    "reason": "Snapshot hash mismatch",
                    "expected": handoff["integrity"]["snapshot_hash"],
                    "actual": recalculated
                }],
                warnings=[],
                results=[],
            )
            return EXIT_FAIL_ACTIONABLE

        contracts = load_contract_pack(module_root)
        contracts["16_ATLETAS_AGENT_HANDOFF.json"] = handoff

        schema_results = validate_documents_against_schemas(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
        )
        if schema_results.errors:
            write_verify_reports(
                reports_dir=reports_dir,
                status="FAIL_ACTIONABLE",
                errors=schema_results.errors,
                warnings=schema_results.warnings,
                results=schema_results.results,
            )
            return EXIT_FAIL_ACTIONABLE

        anchor_manifest = load_anchor_manifest(reports_dir / "anchor_manifest.json")

        ctx = ValidationContext(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
            handoff=handoff,
            anchor_manifest=anchor_manifest,
            original_files_dir=(repo_root / args.original_stubs_dir).resolve(),
            working_files_dir=repo_root,
        )

        rule_results = run_handoff_required_rules(ctx)
        failures = [r for r in rule_results if r.status == "FAIL"]
        errors = [r for r in rule_results if r.status == "ERROR"]

        ts_ok, ts_message = run_ts_validator(repo_root, handoff, reports_dir)
        if not ts_ok:
            failures.append(type("Tmp", (), {
                "__dict__": {
                    "rule_id": "TS-AST-001",
                    "checker_id": "check_ts_anchor_structure",
                    "status": "FAIL",
                    "message": ts_message,
                    "evidence": {}
                }
            })())

        if failures or errors:
            write_verify_reports(
                reports_dir=reports_dir,
                status="FAIL_ACTIONABLE" if failures else "ERROR_INFRA",
                errors=[r.__dict__ for r in failures + errors],
                warnings=[],
                results=[r.__dict__ for r in rule_results],
            )
            return EXIT_FAIL_ACTIONABLE if failures else EXIT_ERROR_INFRA

        write_verify_reports(
            reports_dir=reports_dir,
            status="PASS",
            errors=[],
            warnings=[],
            results=[r.__dict__ for r in rule_results],
        )
        return EXIT_PASS

    except Exception as exc:
        write_verify_reports(
            reports_dir=args.reports_dir,
            status="ERROR_INFRA",
            errors=[{"reason": f"{type(exc).__name__}: {exc}"}],
            warnings=[],
            results=[],
        )
        return EXIT_ERROR_INFRA


if __name__ == "__main__":
    sys.exit(main())
```

4) O que o hb_verify.py realmente verifica

Ele precisa rodar dois blocos:

A. Verificação estática de snapshot
	•	schema do handoff
	•	integridade dos hashes
	•	existência dos artefatos obrigatórios
	•	checker IDs permitidos
	•	manifesto de âncoras presente

B. Verificação estrutural do workspace
	•	Python AST fora da âncora não mudou
	•	TS/TSX AST fora da âncora não mudou
	•	símbolos públicos continuam exatamente os contratados
	•	side effects usam idempotency_key
	•	invariantes temporais não usam relógio do sistema

⸻

5) run_handoff_required_rules

Esse dispatcher não roda o meta-contrato inteiro.
Ele roda o subconjunto obrigatório do handoff.

```python
from __future__ import annotations

from hbtrack_lint.checkers import register_all_checkers
from hbtrack_lint.engine import run_rule


def _find_rule_by_checker_id(cross_rules: dict, checker_id: str) -> dict | None:
    for section in [
        "document_shape_rules",
        "cross_rules",
        "event_rules",
        "projection_rules",
        "side_effect_rules",
        "concurrency_rules",
        "ui_state_rules",
        "time_determinism_rules",
        "test_scenario_rules",
        "stub_anchor_rules",
        "handoff_rules",
        "restriction_prompt_rules",
        "diff_validation_rules",
    ]:
        for rule in cross_rules.get(section, []):
            if rule["checker_id"] == checker_id:
                return rule
    return None


def run_handoff_required_rules(ctx):
    register_all_checkers()

    cross = ctx.contracts["00_ATLETAS_CROSS_LINTER_RULES.json"]
    handoff = ctx.handoff
    required_checker_ids = handoff["validator_requirements"]["required_checker_ids"]

    results = []
    for checker_id in required_checker_ids:
        rule = _find_rule_by_checker_id(cross, checker_id)
        if rule is None:
            results.append(type("Tmp", (), {
                "__dict__": {
                    "rule_id": "MISSING-RULE",
                    "checker_id": checker_id,
                    "status": "ERROR",
                    "message": f"Checker id not found in cross rules: {checker_id}",
                    "evidence": {}
                }
            })())
            continue
        results.append(run_rule(rule, ctx))

    return results
```

6) Overwrite policy correta no gerador

Você fez a pergunta certa antes, e a resposta agora precisa virar política de código.

Regra definitiva

Tipo de arquivo	Política
generated/	overwrite sempre
arquivos de implementação com âncora	overwrite só se estruturalmente equivalentes fora das âncoras
arquivo novo	criar

Isso exige um writer protegido.

Writer protegido

```python
def write_stub_with_policy(path: Path, content: str, is_generated_zone: bool, structural_guard: callable | None = None) -> None:
    _ensure_parent(path)

    if not path.exists():
        path.write_text(content, encoding="utf-8")
        return

    if is_generated_zone:
        path.write_text(content, encoding="utf-8")
        return

    existing = path.read_text(encoding="utf-8")
    if existing == content:
        return

    if structural_guard is None:
        raise RuntimeError(f"Protected file exists and no structural guard was provided: {path}")

    if not structural_guard(existing, content):
        raise RuntimeError(
            f"Protected merge rejected for {path}; structural divergence outside anchors detected."
        )

    path.write_text(content, encoding="utf-8")
```

Uso correto
	•	generated/ → is_generated_zone=True
	•	service.py, screen.tsx → is_generated_zone=False com guard AST

Isso protege a zona de trabalho do Executor.

⸻

7) O “Policial” de side effects e idempotency_key

Você pediu isso explicitamente antes. No hb_verify.py, esse checker deve ser obrigatório.

Regra forte

Se um handler de side effect chama integração externa sem passar idempotency_key, é FAIL_ACTIONABLE.

Heurística contratual aceitável

No V1, o checker pode impor o padrão:
	•	existe variável idempotency_key
	•	existe chamada com argumento nomeado idempotency_key=idempotency_key

Exemplo de checker AST

```python
import ast

class SideEffectIdempotencyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.assigned = False
        self.used_as_kwarg = False

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "idempotency_key":
                self.assigned = True
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        for kw in node.keywords:
            if kw.arg == "idempotency_key":
                if isinstance(kw.value, ast.Name) and kw.value.id == "idempotency_key":
                    self.used_as_kwarg = True
        self.generic_visit(node)

Checker

@register_checker("check_side_effect_idempotency_keys_are_declared_and_safe")
def check_side_effect_idempotency_keys_are_declared_and_safe(rule: dict, ctx: ValidationContext) -> RuleResult:
    side_effects = ctx.contracts["18_ATLETAS_SIDE_EFFECTS.yaml"]
    violations = []

    for effect in side_effects.get("side_effect_policies", []):
        file_path = ctx.repo_root / effect["handler_file"]
        if not file_path.exists():
            violations.append({"side_effect_id": effect["side_effect_id"], "reason": "Handler file missing"})
            continue

        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
        visitor = SideEffectIdempotencyVisitor()
        visitor.visit(tree)

        if not visitor.assigned or not visitor.used_as_kwarg:
            violations.append({
                "side_effect_id": effect["side_effect_id"],
                "handler_file": str(file_path),
                "reason": "idempotency_key not assigned and passed as keyword argument"
            })

    if violations:
        return RuleResult.fail(
            rule["rule_id"],
            rule["checker_id"],
            "Side effect idempotency enforcement failed.",
            violations=violations
        )

    return RuleResult.pass_(
        rule["rule_id"],
        rule["checker_id"],
        "All side effects enforce idempotency key usage."
    )
```

8) hb_verify_ui.mjs — esboço mínimo real

Você recomendou o controle de qualidade agora. Correto.
Então o wrapper Python precisa de um validador TS real.

Estrutura mínima

```python
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { Project } from "ts-morph";

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function collectExportedNames(sourceFile) {
  const exports = sourceFile.getExportedDeclarations();
  return Array.from(exports.keys()).sort();
}

function main() {
  const repoRootArgIndex = process.argv.indexOf("--repo-root");
  const repoRoot = repoRootArgIndex >= 0 ? process.argv[repoRootArgIndex + 1] : process.cwd();

  const handoffPath = path.join(repoRoot, "docs/hbtrack/modulos/atletas/16_ATLETAS_AGENT_HANDOFF.json");
  const handoff = readJson(handoffPath);

  const project = new Project({ tsConfigFilePath: path.join(repoRoot, "tsconfig.json"), skipAddingFilesFromTsConfig: false });

  const bindings = handoff.execution_scope.operation_file_bindings;
  const violations = [];

  for (const binding of bindings) {
    for (const relPath of binding.file_paths) {
      if (!relPath.endsWith(".ts") && !relPath.endsWith(".tsx")) continue;

      const absPath = path.join(repoRoot, relPath);
      if (!fs.existsSync(absPath)) {
        violations.push({ file: relPath, reason: "Missing TS/TSX file" });
        continue;
      }

      const sf = project.addSourceFileAtPathIfExists(absPath);
      if (!sf) {
        violations.push({ file: relPath, reason: "Unable to parse TS/TSX source" });
        continue;
      }

      const exported = collectExportedNames(sf);
      for (const name of exported) {
        if (!binding.public_symbols.includes(name)) {
          violations.push({
            file: relPath,
            reason: `Uncontracted public TS symbol: ${name}`
          });
        }
      }

      const sourceText = sf.getFullText();
      if (sourceText.includes("getByText(") || sourceText.includes("locator(")) {
        // regra opcional simples; a robusta deve olhar AST real
      }
    }
  }

  if (violations.length > 0) {
    console.error(JSON.stringify({ status: "FAIL", violations }, null, 2));
    process.exit(2);
  }

  console.log(JSON.stringify({ status: "PASS" }));
  process.exit(0);
}
```

main();

V1 simples, mas já útil.
V2 deve adicionar:
	•	preservação de data-testid
	•	verificação de props públicas
	•	comparação de âncoras em TSX

Expansão do generator.py para upcasters

A ideia é simples:
	•	ler x-hbtrack.upcasting.rules do 05_ATLETAS_EVENTS.asyncapi.yaml
	•	gerar:
	•	backend/app/events/upcasters/athletes_upcasters.py
	•	backend/app/generated/event_schemas.py
	•	cada upcaster nasce como função ancorada, tipada e com contrato explícito de pureza

1) Novos helpers


```python
def _py_upcaster_stub(
    module_id: str,
    contract_hash: str,
    event_type: str,
    from_version: int,
    to_version: int,
    stub_symbol: str,
    from_type: str,
    to_type: str,
    injected_fields: dict[str, object],
) -> str:
    operation_id = f"upcast__{event_type.lower()}__v{from_version}_to_v{to_version}"
    start = _py_anchor_start(operation_id)
    end = _py_anchor_end(operation_id)

    injected_repr = ", ".join([f'"{k}": {repr(v)}' for k, v in injected_fields.items()])

    header = _header_comment(
        module_id=module_id,
        contract_hash=contract_hash,
        extra=[
            f"HB_UPCAST_EVENT_TYPE: {event_type}",
            f"HB_UPCAST_FROM_VERSION: {from_version}",
            f"HB_UPCAST_TO_VERSION: {to_version}",
            f"HB_PUBLIC_SYMBOL: {stub_symbol}",
            "HB_ROLE: UPCASTER",
            "HB_PURITY: REQUIRED",
        ],
    )

    return f'''{header}

from __future__ import annotations

from backend.app.generated.event_schemas import {from_type}, {to_type}


def {stub_symbol}(event: {from_type}) -> {to_type}:
    {start}
    # PURE FUNCTION ONLY
    # FORBIDDEN:
    # - database access
    # - network calls
    # - reading current time
    # - filesystem access
    # - environment-dependent branching
    #
    # REQUIRED:
    # - derive output only from input event + constant injected fields
    #
    # DEFAULT INJECTED FIELDS:
    # {injected_repr if injected_repr else "{}"}

    raise NotImplementedError("{stub_symbol} must be implemented as a pure deterministic upcaster.")
    {end}
```

2) Geração de schemas de evento versionados

A V1 do gerador não precisa ser perfeita; precisa ser determinística e útil.

```python
def _event_python_type_name(event_type: str, version: int) -> str:
    return f"{event_type}V{version}Envelope"


def _build_event_schemas_py(module_id: str, contract_hash: str, events_contract: dict) -> str:
    header = _header_comment(
        module_id,
        contract_hash,
        extra=["HB_ROLE: GENERATED_EVENT_SCHEMAS"]
    )

    lines = [
        header,
        "",
        "from __future__ import annotations",
        "from dataclasses import dataclass",
        "from typing import Optional, Any",
        "",
        "",
        "@dataclass",
        "class EventMetadata:",
        "    event_id: str",
        "    event_type: str",
        "    event_version: int",
        "    aggregate_type: str",
        "    aggregate_id: str",
        "    stream_name: str",
        "    stream_position: int",
        "    occurred_at: str",
        "    producer: str",
        "    causation_id: str",
        "    correlation_id: str",
        "    replay: bool = False",
        "",
    ]

    for msg_name, msg in events_contract.get("components", {}).get("messages", {}).items():
        payload_ref = msg.get("payload", {}).get("$ref", "")
        schema_name = payload_ref.split("/")[-1]
        if not schema_name.endswith("Envelope"):
            continue

        lines.extend([
            "@dataclass",
            f"class {schema_name}:",
            "    metadata: EventMetadata",
            "    data: dict[str, Any]",
            "",
        ])

    return "\n".join(lines).rstrip() + "\n"
```

3) Builder dos arquivos de upcaster

```python
def _build_upcaster_files(
    module_id: str,
    contract_hash: str,
    events_contract: dict,
) -> dict[str, str]:
    files: dict[str, list[str]] = {}

    xhb = events_contract.get("x-hbtrack", {})
    upcasting = xhb.get("upcasting", {})
    rules = upcasting.get("rules", [])

    for rule in rules:
        target_file = rule["target_file"]
        stub_symbol = rule["stub_symbol"]
        event_type = rule["event_type"]
        from_version = int(rule["from_version"])
        to_version = int(rule["to_version"])

        from_type = _event_python_type_name(event_type, from_version)
        to_type = _event_python_type_name(event_type, to_version)

        injected_fields = rule.get("transformation", {}).get("injected_fields", {})

        files.setdefault(target_file, [])
        files[target_file].append(
            _py_upcaster_stub(
                module_id=module_id,
                contract_hash=contract_hash,
                event_type=event_type,
                from_version=from_version,
                to_version=to_version,
                stub_symbol=stub_symbol,
                from_type=from_type,
                to_type=to_type,
                injected_fields=injected_fields,
            )
        )

    return {path: "\n\n".join(blocks).rstrip() + "\n" for path, blocks in files.items()}
```

4) Integração no generate_stub_files

Adicionar 05_ATLETAS_EVENTS.asyncapi.yaml ao gerador:

```python
def generate_stub_files(repo_root: Path, module_root: Path, contracts: dict[str, object]) -> list[GeneratedFile]:
    traceability = contracts["08_ATLETAS_TRACEABILITY.yaml"]
    ui_contract = contracts["14_ATLETAS_UI_CONTRACT.yaml"]
    invariants_contract = contracts["15_ATLETAS_INVARIANTS.yaml"]
    projections_contract = contracts["17_ATLETAS_PROJECTIONS.yaml"]
    side_effects_contract = contracts["18_ATLETAS_SIDE_EFFECTS.yaml"]
    events_contract = contracts.get("05_ATLETAS_EVENTS.asyncapi.yaml", {})

    module_id = traceability["meta"]["module_id"]
    contract_hash = _sha256_text(module_id + "::stub-seed::v2")

    operations = traceability.get("operations", [])

    generated: list[GeneratedFile] = []

    generated.append(
        GeneratedFile(
            path=repo_root / "backend/app/generated/athletes_contract_types.py",
            content=_generated_contract_types_py(module_id, contract_hash),
        )
    )
    generated.append(
        GeneratedFile(
            path=repo_root / "backend/app/generated/athletes_stub_bindings.py",
            content=_generated_stub_bindings_py(module_id, contract_hash, operations),
        )
    )
    generated.append(
        GeneratedFile(
            path=repo_root / "frontend/src/lib/generated/athletes-client.ts",
            content=_generated_client_ts(module_id, contract_hash),
        )
    )

    if events_contract:
        generated.append(
            GeneratedFile(
                path=repo_root / "backend/app/generated/event_schemas.py",
                content=_build_event_schemas_py(module_id, contract_hash, events_contract),
            )
        )

        for path_str, content in _build_upcaster_files(module_id, contract_hash, events_contract).items():
            generated.append(GeneratedFile(path=repo_root / path_str, content=content))

    for path_str, content in _build_python_service_files(module_id, contract_hash, operations).items():
        generated.append(GeneratedFile(path=repo_root / path_str, content=content))

    for path_str, content in _build_projection_files(module_id, contract_hash, projections_contract).items():
        generated.append(GeneratedFile(path=repo_root / path_str, content=content))

    for path_str, content in _build_side_effect_files(module_id, contract_hash, side_effects_contract).items():
        generated.append(GeneratedFile(path=repo_root / path_str, content=content))

    for path_str, content in _build_reference_files(module_id, contract_hash, invariants_contract).items():
        generated.append(GeneratedFile(path=repo_root / path_str, content=content))

    for path_str, content in _build_ui_files(module_id, contract_hash, ui_contract, traceability).items():
        generated.append(GeneratedFile(path=repo_root / path_str, content=content))

    return generated
```
Como garantir que o Executor não coloque lógica impura no upcaster

Você apontou corretamente que o gerador sozinho não basta. O controle real vem do hb_verify.py.

A regra forte é:

UPCASTER PODE:
- copiar campos do evento de entrada
- injetar constantes declaradas no contrato
- reestruturar o payload em memória

UPCASTER NÃO PODE:
- abrir conexão SQL
- importar repository/service/integration
- usar requests/httpx/aiohttp
- ler datetime.now/date.today
- ler arquivo/env/cache

Checker de pureza de upcaster

Sim, seria útil você esboçar também, mas já deixo a estrutura-base pronta.

Visitor de pureza

```python
import ast

FORBIDDEN_IMPORT_ROOTS = {
    "sqlalchemy",
    "psycopg",
    "requests",
    "httpx",
    "aiohttp",
    "redis",
    "subprocess",
    "os",
    "pathlib",
}

FORBIDDEN_CALLS = {
    ("datetime", "now"),
    ("datetime", "utcnow"),
    ("date", "today"),
    ("time", "time"),
}

FORBIDDEN_SYMBOL_FRAGMENTS = {
    "repository",
    "service",
    "session",
    "engine",
    "client",
}

class UpcasterPurityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations: list[dict] = []
        self.import_aliases: dict[str, str] = {}

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in FORBIDDEN_IMPORT_ROOTS:
                self.violations.append({
                    "kind": "forbidden_import",
                    "name": alias.name,
                    "lineno": node.lineno,
                })
            self.import_aliases[alias.asname or root] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        root = module.split(".")[0] if module else ""
        if root in FORBIDDEN_IMPORT_ROOTS:
            self.violations.append({
                "kind": "forbidden_import_from",
                "name": module,
                "lineno": node.lineno,
            })

        for alias in node.names:
            imported_name = alias.asname or alias.name
            self.import_aliases[imported_name] = f"{module}.{alias.name}" if module else alias.name

            if alias.name in {"now", "today", "utcnow"}:
                self.violations.append({
                    "kind": "forbidden_direct_time_import",
                    "name": alias.name,
                    "lineno": node.lineno,
                })

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        extracted = self._extract_call(node.func)
        if extracted in FORBIDDEN_CALLS:
            self.violations.append({
                "kind": "forbidden_time_call",
                "call": f"{extracted[0]}.{extracted[1]}",
                "lineno": node.lineno,
            })

        if isinstance(node.func, ast.Name):
            fn_name = node.func.id
            origin = self.import_aliases.get(fn_name, fn_name)
            if origin in {"datetime.now", "datetime.utcnow", "date.today", "time.time"}:
                self.violations.append({
                    "kind": "forbidden_time_call_via_direct_import",
                    "call": origin,
                    "lineno": node.lineno,
                })

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        lowered = node.id.lower()
        for fragment in FORBIDDEN_SYMBOL_FRAGMENTS:
            if fragment in lowered:
                self.violations.append({
                    "kind": "suspicious_dependency_symbol",
                    "name": node.id,
                    "lineno": node.lineno,
                })
        self.generic_visit(node)

    @staticmethod
    def _extract_call(func: ast.AST) -> tuple[str, str] | None:
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            return (func.value.id, func.attr)
        return None

Checker

@register_checker("check_upcasters_are_pure_functions")
def check_upcasters_are_pure_functions(rule: dict, ctx: ValidationContext) -> RuleResult:
    events = ctx.contracts.get("05_ATLETAS_EVENTS.asyncapi.yaml", {})
    upcasting = events.get("x-hbtrack", {}).get("upcasting", {})
    rules = upcasting.get("rules", [])

    violations = []

    for up_rule in rules:
        file_path = ctx.repo_root / up_rule["target_file"]
        stub_symbol = up_rule["stub_symbol"]

        if not file_path.exists():
            violations.append({
                "upcaster": stub_symbol,
                "reason": "Upcaster file missing",
                "file": str(file_path),
            })
            continue

        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
        visitor = UpcasterPurityVisitor()
        visitor.visit(tree)

        if visitor.violations:
            violations.append({
                "upcaster": stub_symbol,
                "file": str(file_path),
                "violations": visitor.violations,
            })

    if violations:
        return RuleResult.fail(
            rule["rule_id"],
            rule["checker_id"],
            "Impure upcaster logic detected.",
            violations=violations
        )

    return RuleResult.pass_(
        rule["rule_id"],
        rule["checker_id"],
        "All upcasters satisfy purity constraints."
    )
```

Ajuste estrutural no contrato de eventos: partition key

Sua crítica sobre Kafka está correta do ponto de vista arquitetural. Para o pack ficar coerente, o contrato de eventos deve explicitar isso em x-hbtrack.

Eu endureceria o 05_ATLETAS_EVENTS.asyncapi.yaml com este bloco:

```yaml
x-hbtrack:
  transport_ordering:
    broker: kafka
    ordering_scope: per_partition_only
    required_partition_key: aggregate_id
    projection_replay_assumption: per_aggregate_order
    global_order_required: false
```
E adicionaria um checker como:

`check_event_partition_key_matches_aggregate_id`

para bloquear qualquer drift entre:
	•	aggregate_id
	•	partition key
	•	projeção por agregado


Como o 17_ATLETAS_PROJECTIONS.yaml deve declarar dependência de upcaster
Exemplo de trecho endurecido:

```yaml
projections:
  - projection_id: athletes_read_model
    target_table: athletes
    source_events:
      - event_type: AthleteRegistered
        supported_versions: [2]
        legacy_versions_require_upcast:
          - from_version: 1
            upcaster_symbol: upcast_athlete_registered_v1_to_v2
```

Isso impede que o projetor “adivinhe” como consumir v1.

Veredito técnico

O gerador expandido de upcasters fecha a ponte entre:
	•	evento histórico
	•	contrato de evolução
	•	arquivo físico ancorado
	•	verificação de pureza

Ou seja, o replay deixa de depender de convenção e passa a depender de:
	•	stub gerado
	•	checker de pureza
	•	política explícita de upcast
	•	vínculo contratual com projeção




