from pathlib import Path
import re
import subprocess

# Verifica SSOT
ss = Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md')
t = ss.read_text(encoding='utf-8')

# INV-TRAIN-080
m080 = re.search(r'(?s)id:\s*INV-TRAIN-080.*?\n\s*status:\s*([A-Z_]+)', t)
assert m080, 'FAIL SSOT missing INV-TRAIN-080'
assert m080.group(1) == 'IMPLEMENTADO', f'FAIL INV-TRAIN-080 status={m080.group(1)}'

# INV-TRAIN-081
m081 = re.search(r'(?s)id:\s*INV-TRAIN-081.*?\n\s*status:\s*([A-Z_]+)', t)
assert m081, 'FAIL SSOT missing INV-TRAIN-081'
assert m081.group(1) == 'IMPLEMENTADO', f'FAIL INV-TRAIN-081 status={m081.group(1)}'

# Verifica arquivos
req = [
    'Hb Track - Backend/app/services/ai_coach_service.py',
    'Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py',
    'Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py'
]
miss = [p for p in req if not Path(p).exists()]
assert not miss, f'FAIL missing {miss}'

# Executa pytest
subprocess.check_call([
    'pytest',
    'Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py',
    'Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py',
    '-q'
])

print('PASS AR_166')
