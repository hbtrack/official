import os
import sys

PASS = 0
FAIL_ACTIONABLE = 2
ERROR_INFRA = 3
BLOCKED_INPUT = 4

REQUIRED_PATH = os.path.join("docs", "_INDEX.yaml")

REQUIRED_MARKERS = [
    "authority:",
    "precedence_order:",
    "entrypoints:",
]

def main() -> int:
    if not os.path.exists(REQUIRED_PATH):
        print(f"[DOCS_INDEX_CHECK] MISSING: {REQUIRED_PATH}")
        return FAIL_ACTIONABLE

    try:
        with open(REQUIRED_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"[DOCS_INDEX_CHECK] ERROR reading {REQUIRED_PATH}: {e}")
        return ERROR_INFRA

    missing = [m for m in REQUIRED_MARKERS if m not in content]
    if missing:
        print(f"[DOCS_INDEX_CHECK] FAIL: missing markers in {REQUIRED_PATH}: {missing}")
        return FAIL_ACTIONABLE

    # Checagens determinísticas "mínimas" (sem parse YAML completo)
    # 1) precedence_order deve listar as 5 camadas na ordem canônica (texto)
    expected_order = [
        "ssot_factual",
        "runtime_evidence",
        "canon_docs",
        "derived_docs",
        "narrative",
    ]
    for item in expected_order:
        if item not in content:
            print(f"[DOCS_INDEX_CHECK] FAIL: precedence_order missing item: {item}")
            return FAIL_ACTIONABLE

    # 2) entrypoints mínimos (o repo declarou como portas canônicas)
    expected_entrypoints = [
        "docs/product/SYSTEM_OVERVIEW.md",
        "docs/_canon/HB_TRACK_PROFILE.yaml",
        "docs/_canon/UDS_SPEC.md",
        "docs/_canon/contratos/HB_TRACK_CONTRACT.md",
        "docs/_canon/specs/HB_TRACK_SPEC.md",
        "docs/product/runtime/_INDEX.yaml",
    ]
    for ep in expected_entrypoints:
        if ep not in content:
            print(f"[DOCS_INDEX_CHECK] FAIL: entrypoints missing: {ep}")
            return FAIL_ACTIONABLE

    print("[DOCS_INDEX_CHECK] PASS")
    return PASS

if __name__ == "__main__":
    sys.exit(main())
