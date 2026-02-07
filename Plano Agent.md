## **DELIVERABLE: Passo 3 — Alinhar CANON ↔ Verificador ↔ SPEC**

### **3.1. Bloco SPEC da INV-TRAIN-002 em INVARIANTS_TRAINING.md**

**Trecho completo** (INVARIANTS_TRAINING.md, linhas 265-302):

```yaml
spec_version: "1.0"
id: "INV-TRAIN-002"
status: "CONFIRMADA"
test_required: true

units:
  - unit_key: "db-column"
    class: "B"
    required: true
    description: "Database column locked_at documents the rule"
    anchors:
      db.table: "wellness_pre"
      db.column: "locked_at"
      db.comment: "pré editável até 2h antes da sessão"
  
  - unit_key: "service-validation"
    class: "C2"
    required: true
    description: "Service enforces 2h deadline with ValidationError"
    anchors:
      code.file: "app/services/wellness_pre_service.py"
      code.symbol: "_check_edit_window"
      code.lines: [93, 102, 231, 232]
      code.error_type: "ValidationError"

tests:
  primary: "tests/training/invariants/test_inv_train_002_wellness_pre_deadline.py"
  node: "TestInvTrain002WellnessPreDeadline"
```

**Resumo do SPEC**:
- ✅ **units[0]**: Classe **B** (DB column documenta regra)
- ✅ **units[1]**: Classe **C2** (Service + DB) com oráculo **ValidationError**
- ✅ **anchors C2**: `code.file`, `code.symbol`, `code.lines`, `code.error_type` (NÃO menciona SQLSTATE)
- ✅ **tests.primary**: `tests/training/invariants/test_inv_train_002_wellness_pre_deadline.py`

---

### **3.2. Trechos do verificador (verify_invariants_tests.py)**

#### **3.2.1. Onde o erro OBLIG_B_NO_SQLSTATE é gerado**

verify_invariants_tests.py, linhas 870-883:

```python
        else:
            # Verificar SQLSTATE (23xxx)
            if not re.search(r'23\d{3}', all_docstrings):
                violations.append(Violation(
                    inv_id=analysis.inv_id,
                    file=str(file_path),
                    line=0,
                    col=0,
                    level='ERROR',
                    code='OBLIG_B_NO_SQLSTATE',
                    message='Obrigação B missing SQLSTATE (23xxx)',
                    action='add expected SQLSTATE (23514 for CHECK, 23505 for UNIQUE, etc)'
                ))
```

**Problema identificado**: A validação de SQLSTATE é **incondicional** após verificar que "Obrigação B" existe no docstring. Não considera a classe da INV.

---

#### **3.2.2. Onde decide quando exigir SQLSTATE (condição)**

**NÃO HÁ CONDICIONAL** atualmente. O código acima (linhas 870-883) **sempre exige SQLSTATE** se "Obrigação B" estiver presente no docstring, **independentemente da classe** (A/B/C2/D).

---

#### **3.2.3. Como associa INV-TRAIN-002 à classe**

verify_invariants_tests.py, linhas 1356-1366:

```python
                # Class-specific rules
                # Determinar classes a validar (SPEC ou legacy)
                classes_to_validate = inv.primary_classes
                
                for class_type in classes_to_validate:
                    if class_type == 'A':
                        violations.extend(validator.validate_class_a(analysis, file_path))
                    elif class_type == 'D':
                        violations.extend(validator.validate_class_d(analysis, file_path))
                    # Adicionar outras classes conforme necessário
```

**Método `primary_classes`** ([linhas 87-92](docs/scripts/verify_invariants_tests.py)):

```python
    @property
    def primary_classes(self) -> List[str]:
        """Retorna lista de classes requeridas"""
        if self.has_spec:
            return [unit.class_type for unit in self.units if unit.required]
        elif self.class_type:
            return [self.class_type]
        return []
```

**Origem da classe**: O verificador **lê do bloco SPEC** (`units[].class` onde `required=true`). Para INV-TRAIN-002, isso retorna `["B", "C2"]`.

---

### **3.3. Proposta de Patch Mínimo (NÃO APLICAR AINDA)**

#### **Objetivo**
Condicionar a exigência de SQLSTATE e constraint_name à classe efetiva da INV:
- **Classe A/B (DB)**: SQLSTATE obrigatório ✅
- **Classe C2 (Service + DB)**: ValidationError + anchors obrigatórios, SQLSTATE **NÃO** obrigatório ❌
- **Classe D (Router)**: operationId obrigatório, SQLSTATE **NÃO** obrigatório ❌

#### **Diff Lógico (o que mudar)**

**Função afetada**: `validate_obligations()` (linhas 817-902)

**Mudanças propostas**:

1. **Adicionar parâmetro** `inv: InvariantSpec` à função `validate_obligations()` para ter acesso às classes da INV.

2. **Condicionar validação SQLSTATE** (linhas 870-883):
   ```python
   # ANTES (incondicional):
   if not re.search(r'23\d{3}', all_docstrings):
       violations.append(...)  # ERRO sempre
   
   # DEPOIS (condicional):
   db_classes = {'A', 'B'}
   requires_sqlstate = any(cls in db_classes for cls in inv.primary_classes)
   
   if requires_sqlstate and not re.search(r'23\d{3}', all_docstrings):
       violations.append(...)  # ERRO apenas para A/B
   ```

3. **Adicionar validação alternativa para C2** (novo bloco):
   ```python
   # Para C2, validar error_type no docstring (ex: "ValidationError")
   service_classes = {'C1', 'C2'}
   requires_error_type = any(cls in service_classes for cls in inv.primary_classes)
   
   if requires_error_type and 'ValidationError' not in all_docstrings:
       violations.append(Violation(
           code='OBLIG_B_NO_ERROR_TYPE',
           message='Obrigação B missing error_type (ValidationError)',
           action='add error_type reference (ex: ValidationError, PermissionError)'
       ))
   ```

4. **Atualizar chamada** em `main()` (linha 1352):
   ```python
   # ANTES:
   violations.extend(validator.validate_obligations(analysis, file_path))
   
   # DEPOIS:
   violations.extend(validator.validate_obligations(analysis, file_path, inv))
   ```

---

### **3.4. PENDING — Autorização Necessária**

⚠️ **PENDING: verificador em desacordo com o SPEC**

**Evidência do desalinhamento**:
- ✅ SPEC de INV-TRAIN-002 declara Classe **C2** com oráculo **ValidationError**
- ❌ Verificador exige **SQLSTATE** incondicionalmente para qualquer INV com "Obrigação B"
- ❌ Isso viola o CANON: "Para C2, OBRIGAÇÃO B deve validar error_type + anchors, **sem SQLSTATE**"

**Ação necessária**:
✋ **Preciso de autorização para aplicar patch mínimo no verify_invariants_tests.py** (alinhamento com SPEC/CANON para classes C2).

**Arquivos que serão modificados**:
1. verify_invariants_tests.py (função `validate_obligations` + chamada em `main`)
2. `docs/_generated/verify_patch_notes.txt` (documentação do patch, será criado)

**Aguardando autorização para prosseguir com o patch.**