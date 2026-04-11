from __future__ import annotations

import argparse
import pathlib
import sys
import json


def _repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for p in here.parents:
        if (p / ".git").exists():
            return p
        if (p / "contracts").exists() and (p / ".contract_driven").exists():
            return p
    return here.parents[4] if len(here.parents) >= 5 else here.parent


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    scripts_dir = root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    from contracts.validate.api.policy_compiler import (  # noqa: PLC0415
        Drift,
        PolicyCompilerError,
        check_expected,
        compile_all_expected,
        compile_expected,
        detect_global_input_recompile_gap,
        write_expected,
    )
    from generate.gen_openapi_root_inventory import sync_openapi_root  # noqa: PLC0415

    ap = argparse.ArgumentParser(description="Compila policy de API e gera manifests determinísticos em generated/.")
    ap.add_argument("--module", help="Módulo (lower_snake_case).")
    ap.add_argument("--surface", choices=["sync", "event"], help="Surface a compilar.")
    ap.add_argument("--all", action="store_true", help="Compilar todos os módulos/surfaces habilitados no registry.")
    ap.add_argument("--check", action="store_true", help="Não escreve; apenas verifica drift contra o esperado.")
    ap.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Formato de saída. `json` é estável para consumo por agente.",
    )
    args = ap.parse_args(argv)

    try:
        global_input_gaps = detect_global_input_recompile_gap(root)
        if not args.all and global_input_gaps:
            payload = {
                "artifact_id": "HBTRACK_API_POLICY_COMPILER_RESULT",
                "status": "FAIL",
                "mode": "check" if args.check else "write",
                "global_input_changed_not_fully_recompiled": True,
                "impacted_global_inputs": global_input_gaps,
                "actions": [
                    "Rodar `python3 scripts/contracts/validate/api/compile_api_policy.py --all`.",
                ],
            }
            if args.format == "json":
                print(json.dumps(payload, ensure_ascii=False))
            else:
                for source_path, manifests in global_input_gaps.items():
                    print(f"GLOBAL_INPUT_DRIFT: {source_path} -> {', '.join(manifests)}")
                print("FAIL: mudança em input global exige recompilação total (--all).")
            return 2

        if args.all:
            expected = compile_all_expected(root)
        else:
            if not args.module or not args.surface:
                ap.error("Use --all OU informe --module e --surface.")
            expected = compile_expected(root, module=args.module, surface=args.surface)

        if args.check:
            drifts = check_expected(root, expected)
            openapi_sync = sync_openapi_root(root, check_only=True)
            if openapi_sync.changed:
                drifts.append(Drift(openapi_sync.relpath, openapi_sync.reason or "openapi_root_inventory_out_of_sync"))
            if drifts:
                if args.format == "json":
                    print(
                        json.dumps(
                            {
                                "artifact_id": "HBTRACK_API_POLICY_COMPILER_RESULT",
                                "status": "FAIL",
                                "mode": "check",
                                "global_input_changed_not_fully_recompiled": False,
                                "drifts": [{"relpath": d.relpath, "reason": d.reason} for d in drifts],
                            },
                            ensure_ascii=False,
                        )
                    )
                    return 2

                for d in drifts[:20]:
                    print(f"DRIFT: {d.relpath} ({d.reason})")
                print(f"FAIL: {len(drifts)} drift(s) detectado(s).")
                return 2
            if args.format == "json":
                print(
                    json.dumps(
                        {
                            "artifact_id": "HBTRACK_API_POLICY_COMPILER_RESULT",
                            "status": "PASS",
                            "mode": "check",
                            "global_input_changed_not_fully_recompiled": False,
                            "drifts": [],
                        },
                        ensure_ascii=False,
                    )
                )
                return 0

            print("OK: sem drift (generated/ está alinhado ao compiler).")
            return 0

        written = write_expected(root, expected)
        openapi_sync = sync_openapi_root(root, check_only=False)
        if openapi_sync.changed:
            written.append(openapi_sync.relpath)
        if args.format == "json":
            print(
                json.dumps(
                    {
                        "artifact_id": "HBTRACK_API_POLICY_COMPILER_RESULT",
                        "status": "PASS",
                        "mode": "check" if args.check else "write",
                        "global_input_changed_not_fully_recompiled": False,
                        "written": written,
                    },
                    ensure_ascii=False,
                )
            )
            return 0

        if written:
            print("OK: artefatos gerados/atualizados:")
            for p in written:
                print(f"  - {p}")
        else:
            print("OK: nada a atualizar (generated/ já está alinhado).")
        return 0
    except PolicyCompilerError as e:
        if args.format == "json":
            print(json.dumps(e.to_report(), ensure_ascii=False), file=sys.stderr)
        else:
            print(f"FAIL: {e.summary}", file=sys.stderr)
            for v in e.violations[:20]:
                loc = f"{v.artifact}:{v.json_path}"
                print(f"  - [{v.gate_id}] {v.rule_id} {v.code} @ {loc}: {v.message}", file=sys.stderr)
                if v.hint:
                    print(f"    hint: {v.hint}", file=sys.stderr)
            if e.actions:
                print("Ações:", file=sys.stderr)
                for a in e.actions:
                    print(f"  - {a}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
