"""Patches Batch 9: AR_202, AR_203, AR_204, AR_205, AR_206"""
from pathlib import Path

BASE = Path(__file__).parent.parent / "Hb Track - Backend" / "tests" / "training"

# ---------------------------------------------------------------------------
# AR_203: schema_path 3 .parent -> 4 .parent em test_inv_train_008
# ---------------------------------------------------------------------------
p = BASE / "invariants" / "test_inv_train_008_soft_delete_reason_pair.py"
txt = p.read_text(encoding="utf-8")
old = 'Path(__file__).parent.parent.parent / "docs"'
new = 'Path(__file__).parent.parent.parent.parent / "docs"'
count = txt.count(old)
p.write_text(txt.replace(old, new), encoding="utf-8")
print(f"AR_203: {count} substituicoes em test_inv_train_008")

# ---------------------------------------------------------------------------
# AR_204: schema_path 3 .parent -> 4 .parent em test_inv_train_030
# ---------------------------------------------------------------------------
p = BASE / "invariants" / "test_inv_train_030_attendance_correction_fields.py"
txt = p.read_text(encoding="utf-8")
count = txt.count(old)
p.write_text(txt.replace(old, new), encoding="utf-8")
print(f"AR_204: {count} substituicoes em test_inv_train_030")

# ---------------------------------------------------------------------------
# AR_205: import pytest_asyncio + 6 @pytest.fixture -> @pytest_asyncio.fixture
# ---------------------------------------------------------------------------
p = BASE / "invariants" / "test_inv_train_032_wellness_post_rpe.py"
txt = p.read_text(encoding="utf-8")
txt2 = txt.replace("import pytest\n", "import pytest\nimport pytest_asyncio\n", 1)
count_fix = txt2.count("@pytest.fixture")
txt2 = txt2.replace("@pytest.fixture", "@pytest_asyncio.fixture")
p.write_text(txt2, encoding="utf-8")
print(f"AR_205: import adicionado + {count_fix} @pytest.fixture substituidos em test_inv_train_032")

# ---------------------------------------------------------------------------
# AR_206: ROUTER_PATH 3 .parent -> 4 .parent em test_contract_train_077_085
# ---------------------------------------------------------------------------
p = BASE / "contracts" / "test_contract_train_077_085_alerts_suggestions.py"
txt = p.read_text(encoding="utf-8")
old206 = 'Path(__file__).parent.parent.parent\n    / "app"'
new206 = 'Path(__file__).parent.parent.parent.parent\n    / "app"'
count = txt.count(old206)
p.write_text(txt.replace(old206, new206), encoding="utf-8")
print(f"AR_206: {count} substituicao em test_contract_train_077_085")

print("DONE")
