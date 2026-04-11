from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys


def _repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for p in here.parents:
        if (p / ".git").exists():
            return p
        if (p / "contracts").exists() and (p / ".contract_driven").exists():
            return p
    return here.parents[4] if len(here.parents) >= 5 else here.parent


def _atomic_write(path: pathlib.Path, data: bytes) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == data:
        return False
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)
    return True


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    scripts_dir = root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    from contracts.validate.api.intent_compiler import (  # noqa: PLC0415
        compile_intent,
    )
    from contracts.validate.api.policy_compiler import (  # noqa: PLC0415
        PolicyCompilerError,
        write_expected,
    )

    ap = argparse.ArgumentParser(description="Compila `.intent.yaml` (intenção) -> contrato OpenAPI e manifesto.")
    ap.add_argument("--module", required=True, help="Módulo (lower_snake_case).")
    ap.add_argument("--surface", default="sync", choices=["sync"], help="Surface para OpenAPI (padrão: sync).")
    ap.add_argument("--intent", help="Caminho explícito para o arquivo .intent.yaml (opcional).")
    ap.add_argument("--apply", action="store_true", help="Escreve contracts/openapi/paths/<module>.yaml e generated/.")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="Formato de saída (json é estável).")
    args = ap.parse_args(argv)

    try:
        intent_path = pathlib.Path(args.intent) if args.intent else None
        res = compile_intent(root, module=args.module, surface=args.surface, intent_path=intent_path)

        written_contract = False
        written_generated: list[str] = []
        if args.apply:
            contract_path = root / pathlib.Path(res.openapi_paths_relpath)
            written_contract = _atomic_write(contract_path, res.openapi_paths_bytes)
            written_generated = write_expected(root, res.expected)

        if args.format == "json":
            print(
                json.dumps(
                    {
                        "artifact_id": "HBTRACK_API_INTENT_COMPILER_RESULT",
                        "status": "PASS",
                        "mode": "apply" if args.apply else "check",
                        "module": args.module,
                        "intent": {"path": res.intent_relpath},
                        "contract": {"path": res.openapi_paths_relpath, "written": written_contract},
                        "generated_written": written_generated,
                    },
                    ensure_ascii=False,
                )
            )
            return 0

        if args.apply:
            print("OK: intent compilada e aplicada.")
            if written_contract:
                print(f"  - updated: {res.openapi_paths_relpath}")
            if written_generated:
                print("  - generated/:")
                for p in written_generated:
                    print(f"    - {p}")
        else:
            print("OK: intent válida (nenhum arquivo foi escrito). Use --apply para materializar o contrato.")
        return 0
    except PolicyCompilerError as e:
        if args.format == "json":
            print(json.dumps(e.to_report(), ensure_ascii=False), file=sys.stderr)
        else:
            print(f"FAIL: {e.summary}", file=sys.stderr)
            for v in e.violations[:20]:
                loc = ""
                if v.location:
                    loc = f":{v.location.get('line')}:{v.location.get('column')}"
                print(f"  - [{v.gate_id}] {v.rule_id} {v.code} @ {v.artifact}{loc} {v.json_path}: {v.message}", file=sys.stderr)
                if v.hint:
                    print(f"    hint: {v.hint}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

