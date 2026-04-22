#!/usr/bin/env python3
"""
Frontend contract code generator — Fase B1.

Gera camadas contratual + estrutural de frontend a partir da IR (source_graph).

Entrada: generated/source_graph/<module>/
Saída:
  - frontend/src/generated/<resource>/types.ts — tipos (re-export de schema.d.ts)
  - frontend/src/generated/<resource>/client.ts — wrapper tipado do OpenAPI
  - frontend/src/generated/<resource>/hooks.ts — React Query hooks
  - frontend/src/generated/<resource>/validators.ts — Zod validators
  - frontend/src/generated/<resource>/scaffolds/ — componentes base

Status: v0.1.0 PLACEHOLDER
Nota: Apenas shell de início. Implementação completa em Fase B1-extended.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional
import yaml


GENERATOR_NAME = "hbtrack_frontend_contract_codegen"
GENERATOR_VERSION = "0.1.0"
SUPPORTED_MODULES = {
    "reports", "analytics", "exercises", "notifications", "wellness",
    "medical", "ai_ingestion", "seasons", "teams", "competitions",
    "users", "matches", "scout", "video", "audit", "identity_access", "training",
}


class FrontendCodegenError(RuntimeError):
    def __init__(self, summary: str):
        super().__init__(summary)
        self.summary = summary


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists():
            return parent
        if (parent / "docs").exists() and (parent / ".contract_driven").exists():
            return parent
    return here.parents[2]


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FrontendCodegenError(f"Arquivo YAML ausente: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def cmd_generate(module: str, check: bool = False) -> int:
    """Gerar código frontend para módulo (placeholder v0.1)."""
    root = _repo_root()
    
    if module not in SUPPORTED_MODULES:
        print(f"❌ Módulo `{module}` não suportado. Suportados: {sorted(SUPPORTED_MODULES)}", file=sys.stderr)
        return 1

    try:
        source_graph_root = root / "generated" / "source_graph" / module
        if not source_graph_root.exists():
            raise FrontendCodegenError(f"Source graph não encontrada: {source_graph_root}")

        # Carregar IR
        bundle = _load_yaml(source_graph_root / f"{module}.bundle.yaml")
        openapi_view = _load_yaml(source_graph_root / f"{module}.openapi_contract_view.yaml")

        if check:
            print(f"[CHECK] frontend code validated for module `{module}` (placeholder, sem arquivos escritos)")
            return 0
        else:
            print(f"[PLACEHOLDER] frontend code generator para `{module}` — implementação em Fase B1-extended")
            print(f"  Operações encontradas: {len(openapi_view.get('operations', []))} ops")
            return 0

    except FrontendCodegenError as e:
        print(f"❌ {e.summary}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Erro inesperado: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Frontend contract code generator — v0.1.0 placeholder"
    )
    parser.add_argument("--module", required=True, help="Módulo canônico")
    parser.add_argument("--check", action="store_true", help="Validar sem escrever")
    
    args = parser.parse_args()
    return cmd_generate(args.module, args.check)


if __name__ == "__main__":
    sys.exit(main())
