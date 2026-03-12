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
        PolicyCompilerError,
        check_expected,
        compile_all_expected,
        compile_expected,
        write_expected,
    )

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
        if args.all:
            expected = compile_all_expected(root)
        else:
            if not args.module or not args.surface:
                ap.error("Use --all OU informe --module e --surface.")
            expected = compile_expected(root, module=args.module, surface=args.surface)

        if args.check:
            drifts = check_expected(root, expected)
            if drifts:
                if args.format == "json":
                    print(
                        json.dumps(
                            {
                                "artifact_id": "HBTRACK_API_POLICY_COMPILER_RESULT",
                                "status": "FAIL",
                                "mode": "check",
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
                            "drifts": [],
                        },
                        ensure_ascii=False,
                    )
                )
                return 0

            print("OK: sem drift (generated/ está alinhado ao compiler).")
            return 0

        written = write_expected(root, expected)
        if args.format == "json":
            print(
                json.dumps(
                    {
                        "artifact_id": "HBTRACK_API_POLICY_COMPILER_RESULT",
                        "status": "PASS",
                        "mode": "check" if args.check else "write",
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
