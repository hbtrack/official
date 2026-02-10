# EXEC_TASK: Implementação de Testes para 51 Invariantes do Módulo Training

**Derivado de:** 004-ADR-TRAIN-invariantes-como-contrato
**Status:** READY TO EXECUTE
**Prioridade:** P0 (CRÍTICO — Bloqueador de cobertura de testes de negócio)
**Estimativa:** 15-20 dias (51 invariantes × 2-4h cada)
**Assignee:** Davi + Claude (AI Assistant)

---

## 🎯 OBJETIVO EXECUTÁVEL

Criar **51 testes automatizados** (1:1 com invariantes) em `tests/invariants/` seguindo rigorosamente o protocolo canônico de `INVARIANTS_TESTING_CANON.md`, garantindo cobertura executável de todas as regras críticas do domínio Training.

---

## 📋 PRÉ-REQUISITOS

### Verificações Obrigatórias (ANTES DE INICIAR)

```powershell
# ✅ CHECK 1: Artifacts atualizados
Test-Path "docs\_generated\schema.sql"
Test-Path "docs\_generated\openapi.json"
# Esperado: True para ambos

# ✅ CHECK 2: INVARIANTS_TRAINING.md com 51 invariantes
$invs = Select-String -Path "docs\02_modulos\training\INVARIANTS\INVARIANTS_TRAINING.md" -Pattern "^## INV-TRAIN-\d{3}" | Measure-Object
$invs.Count -eq 51
# Esperado: True

# ✅ CHECK 3: Testing canon presente
Test-Path "docs\02_modulos\training\INVARIANTS\INVARIANTS_TESTING_CANON.md"
# Esperado: True

# ✅ CHECK 4: Ambiente pytest
pytest --version
# Esperado: pytest 7.x+

# ✅ CHECK 5: Fixtures disponíveis
Test-Path "Hb Track - Backend\tests\conftest.py"
# Esperado: True (contém async_db, client, auth_client)
```

**ABORTAR SE:** qualquer check falhar. Resolver dependências antes de prosseguir.

---

## 🔄 FASES DE EXECUÇÃO

### FASE 1: Construção da Worklist (0.5 dias)

#### Entregável 1.1: Inventário completo de invariantes

**Objetivo:** Criar CSV/JSON mapeando as 51 invariantes com metadados.

**Script:** `scripts/build_invariants_worklist.py`

```python
#!/usr/bin/env python3
"""
Lê INVARIANTS_TRAINING.md e extrai:
- ID (INV-TRAIN-XXX)
- Enunciado (título da invariante)
- Status (CONFIRMADA/PRETENDIDA/INATIVA)
- Classe (A/B/C1/C2/D/E1/E2/F) do bloco SPEC
- Evidência (db.constraint, api.operation_id, code.file)
- Test file path (tests/invariants/test_inv_train_XXX_<slug>.py)
- Test required (true/false para aliases)
"""

import re
import yaml
from pathlib import Path

def parse_invariants_md(md_path: Path) -> list[dict]:
    content = md_path.read_text(encoding='utf-8')

    # Regex para capturar blocos INV-TRAIN-XXX
    inv_pattern = r'## (INV-TRAIN-\d{3}):\s*(.+?)\n.+?```yaml\n(.+?)\n```'
    matches = re.findall(inv_pattern, content, re.DOTALL)

    worklist = []
    for inv_id, title, spec_block in matches:
        spec = yaml.safe_load(spec_block)

        # Extrair classe do primeiro unit
        classes = [u['class'] for u in spec.get('units', [])]
        primary_class = classes[0] if classes else "UNKNOWN"

        # Extrair evidências
        evidences = []
        for unit in spec.get('units', []):
            anchors = unit.get('anchors', {})
            if 'db.constraint' in anchors:
                evidences.append(f"constraint:{anchors['db.constraint']}")
            if 'api.operation_id' in anchors:
                evidences.append(f"operationId:{anchors['api.operation_id']}")
            if 'code.file' in anchors:
                evidences.append(f"file:{anchors['code.file']}")

        worklist.append({
            'id': inv_id,
            'title': title.strip(),
            'status': spec.get('status', 'UNKNOWN'),
            'class': primary_class,
            'test_required': spec.get('test_required', True),
            'test_file': spec.get('tests', {}).get('primary', ''),
            'evidences': evidences,
            'canonical_id': spec.get('canonical_id'),  # Para aliases
        })

    return worklist

if __name__ == '__main__':
    inv_md = Path('docs/02_modulos/training/INVARIANTS/INVARIANTS_TRAINING.md')
    worklist = parse_invariants_md(inv_md)

    # Salvar CSV
    import csv
    with open('docs/_generated/invariants_worklist.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=worklist[0].keys())
        writer.writeheader()
        writer.writerows(worklist)

    print(f"✅ Worklist gerada: {len(worklist)} invariantes")
    print(f"   - Test required: {sum(1 for w in worklist if w['test_required'])}")
    print(f"   - Aliases (skip): {sum(1 for w in worklist if not w['test_required'])}")
```

**Testes de aceitação:**
```powershell
# TEST 1.1.1: Script executa sem erros
python scripts/build_invariants_worklist.py
$LASTEXITCODE -eq 0

# TEST 1.1.2: CSV gerado com 51 linhas (+ header)
(Get-Content "docs\_generated\invariants_worklist.csv").Count -eq 52

# TEST 1.1.3: Todas as classes A-F presentes
$csv = Import-Csv "docs\_generated\invariants_worklist.csv"
$classes = $csv.class | Sort-Object -Unique
# Esperado: A, B, C1, C2, D, E1, E2, F
```

**Critério de DONE:**
- ✅ CSV com 51 invariantes gerado
- ✅ Classes A-F todas representadas
- ✅ Test_required indica quais necessitam testes (aliases marcados como false)
- ✅ Evidências extraídas corretamente dos blocos SPEC

---

### FASE 2: Geração de Testes por Classe (10-12 dias)

#### Estratégia de Execução

**Batch 1 (Classe A — DB Constraints): 4 dias**
- Invariantes com `class: A` (mais comuns: ~25-30 casos)
- Template: `tests/invariants/templates/template_class_a.py`
- Padrão: 1 caso válido + 2 casos inválidos (bordas)
- Assert: SQLSTATE `23514` (CHECK) ou `23505` (UNIQUE) + constraint_name

**Batch 2 (Classes B, C1, C2 — Service/Trigger): 3 dias**
- Classe B: Triggers/Functions (~5 casos)
- Classe C1: Service puro (~3 casos)
- Classe C2: Service + DB (~8 casos)
- Templates específicos por classe

**Batch 3 (Classes D, E1, E2, F — API/Celery/Contract): 3-5 dias**
- Classe D: RBAC (~5 casos)
- Classe E1/E2: Celery (~3 casos)
- Classe F: OpenAPI contract (~5 casos)

---

#### Entregável 2.1: Template base para Classe A (DB Constraint)

**Arquivo:** `tests/invariants/templates/template_class_a.py`

```python
"""
Template canônico para Classe A (DB Constraint).
Referência: INVARIANTS_TESTING_CANON.md, DoD-0 a DoD-9.
"""
import pytest
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
from app.models.training_sessions import TrainingSession  # Exemplo


@pytest.mark.asyncio
async def test_inv_train_XXX_<slug>(async_db, inv_org):
    """
    INV-TRAIN-XXX: <título da invariante>

    Classe: A (DB Constraint - CHECK)
    Evidência: schema.sql:<linha> — <constraint_name>
    Prova primária: Runtime Integration (Postgres rejeita com SQLSTATE)

    Setup requirements (fonte: schema.sql):
    - organization_id: FK obrigatória (inv_org fixture)
    - status: NOT NULL, enum [draft, scheduled, in_progress, pending_review, readonly]
    - created_at: NOT NULL com default now()
    """

    # ==================== CASO 1: Válido (Borda do Range) ====================
    obj_valid = TrainingSession(
        id=uuid4(),
        organization_id=inv_org.id,  # FK obrigatória
        status='draft',              # NOT NULL + enum
        # Campo alvo: valor no limite VÁLIDO do range
        target_field=100,  # Exemplo: max permitido
    )
    async_db.add(obj_valid)
    await async_db.flush()  # Sucesso esperado

    # ==================== CASO 2: Inválido (Acima do Range) ====================
    obj_invalid_above = TrainingSession(
        id=uuid4(),
        organization_id=inv_org.id,
        status='draft',
        target_field=121,  # Mínima violação específica (ex: >120)
    )
    async_db.add(obj_invalid_above)

    with pytest.raises(IntegrityError) as exc_info:
        await async_db.flush()

    # Assert estável: SQLSTATE (primário)
    assert exc_info.value.orig.pgcode == '23514', \
        f"Esperado CHECK violation (23514), obteve {exc_info.value.orig.pgcode}"

    # Assert estável: constraint_name (secundário, quando exposto)
    # Nota: PostgreSQL expõe via exc.orig.diag.constraint_name
    constraint_name = getattr(exc_info.value.orig.diag, 'constraint_name', None)
    if constraint_name:
        assert constraint_name == '<constraint_name>', \
            f"Esperado constraint '<constraint_name>', obteve '{constraint_name}'"

    await async_db.rollback()  # DoD-5: Isolamento de sessão

    # ==================== CASO 3: Inválido (Abaixo do Range) ====================
    obj_invalid_below = TrainingSession(
        id=uuid4(),
        organization_id=inv_org.id,
        status='draft',
        target_field=-1,  # Mínima violação específica (ex: <0)
    )
    async_db.add(obj_invalid_below)

    with pytest.raises(IntegrityError) as exc_info:
        await async_db.flush()

    assert exc_info.value.orig.pgcode == '23514'
    await async_db.rollback()
```

**Critério de DONE:**
- ✅ Template segue DoD-0 a DoD-9 do canon
- ✅ Comentários explicam requisitos de setup (fonte: schema.sql)
- ✅ Assert usa SQLSTATE (não string match em mensagens)
- ✅ Payload mínimo (apenas FKs/NOT NULL necessários)
- ✅ Isolamento de sessão (rollback após IntegrityError)

---

#### Entregável 2.2: Generator de testes automatizado

**Script:** `scripts/generate_invariant_test.py`

```python
#!/usr/bin/env python3
"""
Gera arquivo de teste a partir de template + worklist entry.
Uso: python scripts/generate_invariant_test.py INV-TRAIN-037
"""
import sys
import csv
from pathlib import Path
from jinja2 import Template

def load_worklist() -> dict:
    worklist_path = Path('docs/_generated/invariants_worklist.csv')
    with open(worklist_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return {row['id']: row for row in reader}

def generate_test(inv_id: str):
    worklist = load_worklist()

    if inv_id not in worklist:
        print(f"❌ Invariante {inv_id} não encontrada na worklist")
        sys.exit(1)

    entry = worklist[inv_id]

    if not entry['test_required']:
        print(f"⏭️  {inv_id} é alias, não requer teste separado (canonical: {entry['canonical_id']})")
        return

    # Carregar template baseado na classe
    template_map = {
        'A': 'templates/template_class_a.py',
        'B': 'templates/template_class_b.py',
        'C1': 'templates/template_class_c1.py',
        'C2': 'templates/template_class_c2.py',
        'D': 'templates/template_class_d.py',
        'E1': 'templates/template_class_e1.py',
        'E2': 'templates/template_class_e2.py',
        'F': 'templates/template_class_f.py',
    }

    template_file = Path('tests/invariants') / template_map.get(entry['class'], 'templates/template_class_a.py')

    if not template_file.exists():
        print(f"❌ Template não encontrado: {template_file}")
        sys.exit(1)

    template = Template(template_file.read_text(encoding='utf-8'))

    # Gerar arquivo de teste
    slug = entry['title'].lower().replace(' ', '_').replace('/', '_')[:30]
    test_filename = f"test_inv_train_{inv_id.split('-')[-1]}_{slug}.py"
    test_path = Path('tests/invariants') / test_filename

    rendered = template.render(
        inv_id=inv_id,
        title=entry['title'],
        constraint_name=next((e.split(':')[1] for e in entry['evidences'] if e.startswith('constraint:')), 'UNKNOWN'),
        class_type=entry['class'],
    )

    test_path.write_text(rendered, encoding='utf-8')
    print(f"✅ Gerado: {test_path}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python scripts/generate_invariant_test.py INV-TRAIN-XXX")
        sys.exit(1)

    generate_test(sys.argv[1])
```

**Testes de aceitação:**
```powershell
# TEST 2.2.1: Gerar teste para INV-TRAIN-037 (Classe A)
python scripts/generate_invariant_test.py INV-TRAIN-037
Test-Path "tests\invariants\test_inv_train_037_focus_total.py"  # True

# TEST 2.2.2: Arquivo contém estrutura canônica
$content = Get-Content "tests\invariants\test_inv_train_037_focus_total.py" -Raw
$content -match "async def test_inv_train_037"  # True
$content -match "assert exc_info.value.orig.pgcode"  # True (assert estável)
```

**Critério de DONE:**
- ✅ Generator cria arquivo baseado em template + worklist
- ✅ Slugification correta (title → snake_case)
- ✅ Template selection baseada em classe (A-F)
- ✅ Arquivo gerado passa linter (ruff/black)

---

#### Entregável 2.3: Batch execution de geração

**Script:** `scripts/generate_all_invariant_tests.ps1`

```powershell
# Gera testes para todas as invariantes que requerem testes

$worklist = Import-Csv "docs\_generated\invariants_worklist.csv"
$totalGenerated = 0
$totalSkipped = 0

foreach ($inv in $worklist) {
    if ($inv.test_required -eq 'True') {
        Write-Host "[GENERATE] $($inv.id) — $($inv.title)" -ForegroundColor Cyan
        python scripts/generate_invariant_test.py $inv.id

        if ($LASTEXITCODE -eq 0) {
            $totalGenerated++
        } else {
            Write-Host "[ERROR] Falha ao gerar $($inv.id)" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[SKIP] $($inv.id) — alias de $($inv.canonical_id)" -ForegroundColor Gray
        $totalSkipped++
    }
}

Write-Host "`n✅ GERAÇÃO COMPLETA" -ForegroundColor Green
Write-Host "   Gerados: $totalGenerated testes"
Write-Host "   Pulados (aliases): $totalSkipped"
```

**Testes de aceitação:**
```powershell
# TEST 2.3.1: Batch execution cria todos os testes
.\scripts\generate_all_invariant_tests.ps1
$LASTEXITCODE -eq 0

# TEST 2.3.2: Contagem de arquivos gerados
$testFiles = Get-ChildItem "tests\invariants\test_inv_train_*.py"
$testFiles.Count -ge 45  # Pelo menos 45 testes (51 - ~6 aliases)
```

**Critério de DONE:**
- ✅ Script gera todos os testes não-alias
- ✅ Exit code 0 (sucesso)
- ✅ Contagem de testes >= 45 (considerando aliases)

---

### FASE 3: Validação e Refinamento (2-3 dias)

#### Entregável 3.1: Execução de testes com pytest

**Comando:**
```powershell
# Executar todos os testes de invariantes
pytest tests/invariants/ -v --tb=short --maxfail=5

# Relatório de cobertura por classe
pytest tests/invariants/ -v --collect-only | Select-String "test_inv_train" | Measure-Object
```

**Esperado:**
```
======================== test session starts ========================
collected 45+ items

tests/invariants/test_inv_train_001_focus_sum.py::test_inv_train_001_focus_sum PASSED
tests/invariants/test_inv_train_002_wellness_deadline.py::test_inv_train_002_wellness_deadline PASSED
...
======================== 45+ passed in 120.00s ========================
```

**Tratamento de falhas:**
1. **Se SQLSTATE incorreto:** Revisar evidência no schema.sql (constraint pode ser de tipo diferente)
2. **Se constraint_name não exposto:** Documentar fallback no teste (comentário explicando limitação do driver)
3. **Se payload insuficiente:** Consultar schema.sql para FKs/NOT NULL faltantes

---

#### Entregável 3.2: Relatório de cobertura

**Script:** `scripts/generate_coverage_report.py`

```python
#!/usr/bin/env python3
"""
Gera relatório de cobertura: worklist vs testes existentes.
"""
import csv
from pathlib import Path

def main():
    worklist_path = Path('docs/_generated/invariants_worklist.csv')
    tests_dir = Path('tests/invariants')

    with open(worklist_path, 'r', encoding='utf-8') as f:
        worklist = list(csv.DictReader(f))

    report = []
    for inv in worklist:
        inv_id = inv['id']
        test_file = tests_dir / Path(inv['test_file']).name if inv['test_file'] else None

        status = "✅ COVERED" if (test_file and test_file.exists()) else "❌ MISSING"

        if not inv['test_required']:
            status = "⏭️  ALIAS (skip)"

        report.append({
            'inv_id': inv_id,
            'class': inv['class'],
            'test_file': str(test_file) if test_file else 'N/A',
            'status': status,
        })

    # Salvar relatório CSV
    output_path = Path('docs/_generated/invariants_coverage_report.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['inv_id', 'class', 'test_file', 'status'])
        writer.writeheader()
        writer.writerows(report)

    # Summary
    covered = sum(1 for r in report if r['status'] == '✅ COVERED')
    missing = sum(1 for r in report if r['status'] == '❌ MISSING')
    aliases = sum(1 for r in report if r['status'] == '⏭️  ALIAS (skip)')

    print(f"📊 RELATÓRIO DE COBERTURA")
    print(f"   Total de invariantes: {len(report)}")
    print(f"   ✅ Cobertas: {covered}")
    print(f"   ❌ Faltando: {missing}")
    print(f"   ⏭️  Aliases (skip): {aliases}")
    print(f"\n   Cobertura efetiva: {covered}/{len(report) - aliases} ({100 * covered // (len(report) - aliases)}%)")

    if missing > 0:
        print(f"\n❌ ATENÇÃO: {missing} invariantes sem cobertura!")
        sys.exit(1)
    else:
        print(f"\n✅ 100% de cobertura alcançada!")

if __name__ == '__main__':
    import sys
    main()
```

**Testes de aceitação:**
```powershell
# TEST 3.2.1: Relatório gerado
python scripts/generate_coverage_report.py
Test-Path "docs\_generated\invariants_coverage_report.csv"  # True

# TEST 3.2.2: Cobertura 100%
python scripts/generate_coverage_report.py
$LASTEXITCODE -eq 0  # Sucesso = 100% cobertura
```

**Critério de DONE:**
- ✅ Relatório CSV com status de cada invariante
- ✅ Cobertura efetiva = 100% (excluindo aliases)
- ✅ Exit code 0 indica sucesso (nenhuma invariante faltando)

---

### FASE 4: Documentação e Integração (1 dia)

#### Entregável 4.1: Atualizar INVARIANTS_TESTING_CANON.md

**Objetivo:** Adicionar seção "Exemplos Reais" com links para testes aprovados.

**Modificação:**
```markdown
## EXEMPLOS APROVADOS (REAL)

### Classe A: DB Constraint (CHECK)
- **INV-TRAIN-037** (focus_total_sum ≤ 120%): [test_inv_train_037_focus_total.py](../../tests/invariants/test_inv_train_037_focus_total.py)
- **INV-TRAIN-009** (deleted_reason pair): [test_inv_train_009_soft_delete_reason.py](../../tests/invariants/test_inv_train_009_soft_delete_reason.py)

### Classe D: RBAC
- **INV-TRAIN-045** (apenas coordenador pode aprovar): [test_inv_train_045_rbac_approval.py](../../tests/invariants/test_inv_train_045_rbac_approval.py)

### Classe F: OpenAPI Contract
- **INV-TRAIN-050** (operationId presente): [test_inv_train_050_openapi_contract.py](../../tests/invariants/test_inv_train_050_openapi_contract.py)

(... adicionar 5-10 exemplos representativos de cada classe)
```

**Critério de DONE:**
- ✅ Seção "Exemplos Reais" adicionada ao canon
- ✅ Links para testes aprovados (markdown relative paths)
- ✅ Pelo menos 1 exemplo por classe A-F

---

#### Entregável 4.2: CI/CD integration

**Arquivo:** `.github/workflows/validate-invariants.yml`

```yaml
name: Validate Invariants

on:
  pull_request:
    paths:
      - 'tests/invariants/**'
      - 'app/models/**'
      - 'app/services/**'

jobs:
  test-invariants:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run invariant tests
        run: |
          pytest tests/invariants/ -v --tb=short --maxfail=10 --junit-xml=junit.xml

      - name: Generate coverage report
        run: |
          python scripts/generate_coverage_report.py

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: junit.xml
```

**Critério de DONE:**
- ✅ Workflow dispara em PRs que tocam invariantes ou código
- ✅ Executa pytest com junit output
- ✅ Gera relatório de cobertura
- ✅ Falha se cobertura < 100%

---

## 🧪 TESTES DE ACEITAÇÃO GLOBAL

### Smoke Test Final (executar APÓS todas as fases)

```powershell
# ==================== CENÁRIO 1: Cobertura total ====================
Write-Host "`n[TEST 1] Validando cobertura de 51 invariantes..." -ForegroundColor Cyan

python scripts/generate_coverage_report.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ FAIL: Cobertura incompleta" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PASS: 100% cobertura" -ForegroundColor Green

# ==================== CENÁRIO 2: Execução de testes ====================
Write-Host "`n[TEST 2] Executando todos os testes de invariantes..." -ForegroundColor Cyan

pytest tests/invariants/ -v --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ FAIL: Testes falhando" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PASS: Todos os testes passaram" -ForegroundColor Green

# ==================== CENÁRIO 3: Conformidade com canon ====================
Write-Host "`n[TEST 3] Validando conformidade com testing canon..." -ForegroundColor Cyan

# Verificar nomenclatura (DoD-0)
$invalidNames = Get-ChildItem "tests\invariants\*.py" | Where-Object {
    $_.Name -notmatch "^test_inv_train_\d{3}_\w+\.py$"
}
if ($invalidNames.Count -gt 0) {
    Write-Host "❌ FAIL: Arquivos com nomenclatura inválida:" -ForegroundColor Red
    $invalidNames | ForEach-Object { Write-Host "   $($_.Name)" }
    exit 1
}

# Verificar assert estável (DoD-4)
$unstableAsserts = Select-String -Path "tests\invariants\*.py" -Pattern 'assert.*".*violat' | Measure-Object
if ($unstableAsserts.Count -gt 0) {
    Write-Host "❌ FAIL: Testes com string match em mensagens humanas (DoD-4 violado)" -ForegroundColor Red
    exit 1
}

Write-Host "✅ PASS: Conformidade com canon" -ForegroundColor Green

Write-Host "`n✅✅✅ TODOS OS TESTES PASSARAM ✅✅✅" -ForegroundColor Green
```

**Critério de DONE GLOBAL:**
- ✅ 3 cenários de smoke test passam
- ✅ Cobertura 100% (excluindo aliases)
- ✅ Todos os testes executam sem falhas
- ✅ Conformidade com DoD-0 a DoD-9

---

## 📊 CHECKLIST DE ENTREGA

### Código

- [ ] `scripts/build_invariants_worklist.py` implementado
- [ ] `scripts/generate_invariant_test.py` implementado
- [ ] `scripts/generate_all_invariant_tests.ps1` implementado
- [ ] `scripts/generate_coverage_report.py` implementado
- [ ] Templates para classes A-F criados (`tests/invariants/templates/`)
- [ ] 45+ testes gerados em `tests/invariants/test_inv_train_*.py`

### Documentação

- [ ] `INVARIANTS_TESTING_CANON.md` atualizado com exemplos reais
- [ ] `README.md` em `tests/invariants/` explicando estrutura
- [ ] Comentários inline nos testes (evidências de schema.sql)

### Validação

- [ ] Pytest execution: 45+ passed, 0 failed
- [ ] Coverage report: 100% (excluindo aliases)
- [ ] Conformidade com DoD-0 a DoD-9 validada
- [ ] CI/CD workflow configurado (`.github/workflows/validate-invariants.yml`)

### Infra

- [ ] `docs/_generated/invariants_worklist.csv` gerado
- [ ] `docs/_generated/invariants_coverage_report.csv` gerado
- [ ] Fixtures `inv_org`, `inv_user`, etc. criadas em `tests/conftest.py`

---

## 🚨 CONDIÇÕES DE ABORT

### ABORTAR IMEDIATAMENTE SE:

1. **Pré-requisitos falharem:**
   - `INVARIANTS_TRAINING.md` com < 51 invariantes
   - `schema.sql` ou `openapi.json` desatualizados
   - Fixtures `async_db`, `client`, `auth_client` não disponíveis

2. **Cobertura < 90% após FASE 2:**
   - Indica problemas sistemáticos no generator ou templates
   - Revisar worklist e templates antes de prosseguir

3. **Testes com falsos positivos > 10%:**
   - Testes passando por motivo errado (payload insuficiente, assert errado)
   - Revisar DoD-3 e DoD-4 do canon

4. **Canon violations generalizadas:**
   - Múltiplos testes violando DoD-0 a DoD-9
   - Treinamento necessário antes de prosseguir

---

## 📅 CRONOGRAMA DETALHADO

| Dia | Fase | Horas | Entregáveis |
|-----|------|-------|-------------|
| **D1** | FASE 1 | 4h | Worklist + templates |
| **D2-D5** | FASE 2 (Batch 1 — Classe A) | 32h | ~30 testes Classe A |
| **D6-D8** | FASE 2 (Batch 2 — B/C1/C2) | 24h | ~15 testes classes B/C |
| **D9-D11** | FASE 2 (Batch 3 — D/E/F) | 24h | ~10 testes classes D/E/F |
| **D12-D13** | FASE 3 | 16h | Validação + refinamento |
| **D14** | FASE 4 | 8h | Documentação + CI/CD |

**Total:** 108 horas (~14 dias úteis com 8h/dia, ou 18 dias com 6h/dia)

---

## 🎯 CRITÉRIO DE SUCESSO FINAL

### Definição de DONE:

**O sistema está pronto quando:**

1. ✅ 45+ testes criados (1 por invariante não-alias)
2. ✅ Cobertura efetiva = 100% (`generate_coverage_report.py` exit=0)
3. ✅ Pytest execution: 100% passed, 0 failed
4. ✅ Conformidade com DoD-0 a DoD-9 validada (smoke test)
5. ✅ CI/CD workflow funcional (GitHub Actions)
6. ✅ Documentação sincronizada (canon + exemplos reais)

**Assinatura de aceite:**
- [ ] Davi (Tech Lead) — Validação técnica
- [ ] Claude (AI Assistant) — Revisão de código + conformidade canon

---

## 📎 ANEXOS

### A. Estrutura de diretórios esperada

```
Hb Track - Backend/
├── tests/
│   ├── invariants/
│   │   ├── templates/
│   │   │   ├── template_class_a.py
│   │   │   ├── template_class_b.py
│   │   │   ├── template_class_c1.py
│   │   │   ├── template_class_c2.py
│   │   │   ├── template_class_d.py
│   │   │   ├── template_class_e1.py
│   │   │   ├── template_class_e2.py
│   │   │   └── template_class_f.py
│   │   ├── test_inv_train_001_focus_sum.py
│   │   ├── test_inv_train_002_wellness_deadline.py
│   │   ├── ...
│   │   └── test_inv_train_051_<slug>.py
│   └── conftest.py  # Fixtures: async_db, inv_org, inv_user
├── scripts/
│   ├── build_invariants_worklist.py
│   ├── generate_invariant_test.py
│   ├── generate_all_invariant_tests.ps1
│   └── generate_coverage_report.py
└── docs/
    └── _generated/
        ├── invariants_worklist.csv
        └── invariants_coverage_report.csv
```

### B. Exemplo de worklist CSV

```csv
id,title,status,class,test_required,test_file,evidences,canonical_id
INV-TRAIN-001,Focus total ≤ 120%,CONFIRMADA,A,True,tests/invariants/test_inv_train_001_focus_sum.py,constraint:ck_training_sessions_focus_total_sum,
INV-TRAIN-028,Focus sum 120% (duplicate),CONFIRMADA,A,False,tests/invariants/test_inv_train_001_focus_sum.py,constraint:ck_training_sessions_focus_total_sum,INV-TRAIN-001
```

### C. Comandos de referência rápida

```powershell
# Gerar worklist
python scripts/build_invariants_worklist.py

# Gerar teste único
python scripts/generate_invariant_test.py INV-TRAIN-037

# Gerar todos os testes
.\scripts\generate_all_invariant_tests.ps1

# Executar testes
pytest tests/invariants/ -v

# Relatório de cobertura
python scripts/generate_coverage_report.py

# Smoke test completo
.\scripts\smoke_test_invariants.ps1
```

---

**FIM DA EXEC_TASK**

**Status:** ✅ PRONTO PARA EXECUÇÃO
**Próximo passo:** Iniciar FASE 1 (build worklist)
