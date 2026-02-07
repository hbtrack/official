import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_invariants_tests import InvariantsParser  # noqa

root = Path(r"C:\HB TRACK")
md = root / "docs" / "02-modulos" / "training" / "INVARIANTS_TRAINING.md"

parser = InvariantsParser()
invariants, _ = parser.parse(md)

inv = [i for i in invariants if i.id == "INV-TRAIN-040"][0]
print("INV:", inv.id, "has_spec=", inv.has_spec, "units=", len(inv.units))

for u in inv.units:
    print("UNIT:", u.unit_key, "class=", u.class_type, "required=", u.required)
    print("ANCHORS:", u.anchors)
