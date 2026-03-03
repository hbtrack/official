"""Fix path bug: adiciona .parent extra nos arquivos de teste AR_179."""
import pathlib

ROOT = pathlib.Path(__file__).parent.parent

TARGETS = [
    ROOT / "Hb Track - Backend/tests/training/invariants/test_inv_train_012_export_rate_limit.py",
    ROOT / "Hb Track - Backend/tests/training/invariants/test_inv_train_025_export_lgpd_endpoints.py",
]

OLD = 'Path(__file__).parent.parent.parent\n            / "app"'
NEW = 'Path(__file__).parent.parent.parent.parent\n            / "app"'

for p in TARGETS:
    content = p.read_text(encoding="utf-8")
    count = content.count(OLD)
    content_new = content.replace(OLD, NEW)
    remaining = content_new.count(OLD)
    p.write_text(content_new, encoding="utf-8")
    print(f"{p.name}: {count} ocorrencia(s) corrigida(s), {remaining} restante(s)")
