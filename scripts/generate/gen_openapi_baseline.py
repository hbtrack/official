from __future__ import annotations

import argparse
import json
import pathlib
import os
from typing import Any


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def _collect_and_rewrite_refs(
    obj: Any,
    *,
    source_dir: pathlib.Path,
    baseline_dir: pathlib.Path,
) -> Any:
    """
    Reescreve refs de arquivo para continuarem resolvendo quando o baseline
    é gravado em `baseline_dir`.
    """
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                ref = v.strip()
                if ref.startswith("#") or ref.startswith("http://") or ref.startswith("https://"):
                    out[k] = v
                    continue
                if "#" in ref:
                    ref_path, frag = ref.split("#", 1)
                    frag = "#" + frag
                else:
                    ref_path, frag = ref, ""
                abs_target = (source_dir / ref_path).resolve()
                rel_target = pathlib.Path(os.path.relpath(abs_target, baseline_dir)).as_posix()
                out[k] = rel_target + frag
                continue
            out[k] = _collect_and_rewrite_refs(v, source_dir=source_dir, baseline_dir=baseline_dir)
        return out
    if isinstance(obj, list):
        return [_collect_and_rewrite_refs(v, source_dir=source_dir, baseline_dir=baseline_dir) for v in obj]
    return obj


def main() -> int:
    ap = argparse.ArgumentParser(description="Gera baseline JSON do OpenAPI para oasdiff.")
    ap.add_argument(
        "--input",
        default="contracts/openapi/openapi.yaml",
        help="Caminho do OpenAPI root (YAML).",
    )
    ap.add_argument(
        "--output",
        default="contracts/openapi/baseline/openapi_baseline.json",
        help="Caminho do baseline JSON.",
    )
    args = ap.parse_args()

    root = _repo_root()
    in_path = (root / args.input).resolve()
    out_path = (root / args.output).resolve()

    if not in_path.exists():
        raise SystemExit(f"Input não encontrado: {in_path}")

    try:
        import yaml  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise SystemExit("PyYAML não instalado (necessário para ler o OpenAPI YAML).") from e

    data = yaml.safe_load(in_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("OpenAPI root inválido: esperado mapping no YAML.")

    # Importante: baseline é gravado em subpasta (`contracts/openapi/baseline/`).
    # Reescrever $refs para não quebrar resolução por path relativo.
    source_dir = in_path.parent
    baseline_dir = out_path.parent
    data = _collect_and_rewrite_refs(data, source_dir=source_dir, baseline_dir=baseline_dir)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"OK: baseline gerado em {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
