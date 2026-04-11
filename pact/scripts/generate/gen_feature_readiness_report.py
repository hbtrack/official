#!/usr/bin/env python3
"""
gen_feature_readiness_report.py
Lê docs/_canon/FEATURE_REGISTRY.yaml e gera _reports/feature_readiness.json.

Saída em linguagem de produto:
  - Contagem de features por status
  - % de completude por módulo
  - Features bloqueadas e motivo

Uso:
  python3 scripts/generate/gen_feature_readiness_report.py
"""

import datetime
import json
import sys
from collections import defaultdict
from pathlib import Path


STATUS_ORDER = ["planned", "in_contract", "validated", "implemented", "released"]
STATUS_WEIGHT = {
    "planned": 0,
    "in_contract": 25,
    "validated": 50,
    "implemented": 75,
    "released": 100,
}
STATUS_LABEL = {
    "planned": "Planejada",
    "in_contract": "Com Contrato",
    "validated": "Validada",
    "implemented": "Implementada",
    "released": "Em Produção",
}


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "docs" / "_canon" / "FEATURE_REGISTRY.yaml").exists():
            return parent
    return Path.cwd()


def main() -> int:
    try:
        import yaml
    except ImportError:
        print("ERRO: PyYAML não instalado. Execute: pip install pyyaml", file=sys.stderr)
        return 1

    root = _repo_root()
    registry_path = root / "docs" / "_canon" / "FEATURE_REGISTRY.yaml"
    output_path = root / "_reports" / "feature_readiness.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not registry_path.exists():
        print(f"ERRO: {registry_path} não encontrado.", file=sys.stderr)
        return 1

    with open(registry_path, encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    features = registry.get("features", [])
    ts = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    # Agrupar por módulo
    by_module: dict[str, list[dict]] = defaultdict(list)
    for ft in features:
        by_module[ft["module"]].append(ft)

    # Calcular métricas por módulo
    modules_report = {}
    for module, fts in sorted(by_module.items()):
        total = len(fts)
        by_status = defaultdict(list)
        for ft in fts:
            by_status[ft["status"]].append(ft)

        total_weight = sum(STATUS_WEIGHT.get(ft["status"], 0) for ft in fts)
        completion_pct = round(total_weight / (total * 100) * 100, 1) if total else 0

        modules_report[module] = {
            "total_features": total,
            "completion_pct": completion_pct,
            "by_status": {
                s: len(by_status[s])
                for s in STATUS_ORDER
                if by_status[s]
            },
            "features": [
                {
                    "id": ft["id"],
                    "name": ft["name"],
                    "status": ft["status"],
                    "status_label": STATUS_LABEL.get(ft["status"], ft["status"]),
                    "endpoints_count": len(ft.get("endpoints", [])),
                }
                for ft in fts
            ],
        }

    # Sumário global
    total_features = len(features)
    global_by_status = defaultdict(int)
    for ft in features:
        global_by_status[ft["status"]] += 1

    global_weight = sum(STATUS_WEIGHT.get(ft["status"], 0) for ft in features)
    global_pct = round(global_weight / (total_features * 100) * 100, 1) if total_features else 0

    report = {
        "generated_at_utc": ts,
        "source": str(registry_path.relative_to(root)),
        "registry_version": registry.get("version", "unknown"),
        "summary": {
            "total_features": total_features,
            "global_completion_pct": global_pct,
            "by_status": {
                s: global_by_status[s]
                for s in STATUS_ORDER
                if global_by_status[s]
            },
            "modules_count": len(modules_report),
        },
        "modules": modules_report,
    }

    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Relatório gerado: {output_path}")
    print(f"Features totais : {total_features}")
    print(f"Conclusão global: {global_pct}%")
    for module, data in modules_report.items():
        print(f"  [{module}] {data['completion_pct']}% ({data['total_features']} features)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
