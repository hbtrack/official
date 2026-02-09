Validador Binário de Testes de Invariantes

## Para que serve?

Este script valida automaticamente se os **testes de invariantes** do módulo TRAINING estão em conformidade com o **Canon de Testes** (INVARIANTS_TESTING_CANON.md). Ele funciona como um **gate binário**: ou tudo está correto (PASS), ou há violações que impedem o commit (FAIL).

### O que ele valida?

1. **Cobertura 1:1**: Cada invariante em `INVARIANTS_TRAINING.md` tem exatamente 1 arquivo de teste correspondente
2. **Blocos SPEC**: Invariantes possuem blocos normativos parseáveis (em modo `--strict-spec`)
3. **DoD-0**: Nomenclatura correta de classes/métodos de teste
4. **Obrigação A/B**: Docstrings contêm evidências obrigatórias (anchors, SQLSTATE, constraint names)
5. **Matriz por Classe**: Regras específicas por tipo de invariante (A/B/C1/C2/D/E1/E2/F):
   - Classe A (DB constraint): fixtures corretos, testes válidos/inválidos, estruturas de erro
   - Classe D (Router/RBAC): testes de autenticação (401/403/200)
   - Classe F (OpenAPI): validação de ponteiros, sem fixtures de IO

## Como rodar?

### Execução Básica

```powershell
# A partir da raiz do projeto (C:\HB TRACK)
python "docs\scripts\verify_invariants_tests.py"
```

### Modo Strict (100% SPEC obrigatório)

```powershell
# Falha se qualquer invariante não tiver bloco SPEC
python "docs\scripts\verify_invariants_tests.py" --strict-spec
```

### Com Relatórios Salvos

```powershell
# Gera report.json e report.txt na pasta atual
python "docs\scripts\verify_invariants_tests.py" --report-json report.json --report-txt report.txt
```

### Apenas Arquivos Modificados (pre-commit)

```powershell
# Valida apenas arquivos específicos (otimização)
python "docs\scripts\verify_invariants_tests.py" --files-changed "tests\training\invariants\test_inv_train_001.py"
```

### Modo Verbose (debug)

```powershell
# Mostra análise AST detalhada
python "docs\scripts\verify_invariants_tests.py" --verbose
```

## O que acontece quando rodo?

### Output Console (TXT)

O script imprime:

1. **Sumário inicial**: Total de invariantes, cobertura
2. **Violations agrupadas por INV-TRAIN-ID** no formato:
   ```
   file:line:col: LEVEL [CODE]: message — action
   ```
3. **Sumário final**: Contadores, exit code

**Exemplo**:
```
=== INVARIANTS TESTS VALIDATION REPORT ===
Level: strict
Total Invariants: 36
Covered: 36
Exit Code: 2

--- INV-TRAIN-001 ---
tests/training/invariants/test_inv_train_001.py:0:0: ERROR [OBLIG_A_MISSING]: missing "Obrigacao A" literal in docstring — add "Obrigacao A: <anchors>" to module/class docstring

--- INV-TRAIN-004 ---
tests/training/invariants/test_inv_train_004_edit_window_time.py:0:0: ERROR [COVERAGE_DUPLICATE]: found 2 main test files, expected 1 — consolidate into single test file

=== SUMMARY ===
PASS: False
Errors: 153
Warnings: 0
Exit Code: 2
```

### Relatórios JSON/TXT (opcional)

Se você especificar `--report-json` ou `--report-txt`, os arquivos conterão:

**report.json** (máquina-legível):
```json
{
  "pass": false,
  "level": "strict",
  "timestamp": "2026-02-01T10:30:00",
  "summary": {
    "total_invariants": 36,
    "covered_invariants": 36,
    "error_count": 153,
    "warning_count": 0
  },
  "violations": [
    {
      "inv_id": "INV-TRAIN-001",
      "file": "tests/training/invariants/test_inv_train_001.py",
      "line": 0,
      "col": 0,
      "level": "ERROR",
      "code": "OBLIG_A_MISSING",
      "message": "missing \"Obrigacao A\" literal in docstring",
      "action": "add \"Obrigacao A: <anchors>\" to module/class docstring"
    }
  ]
}
```

**report.txt** (humano-legível, mesma estrutura do console)

### Exit Codes

O script retorna um código de saída que você pode usar em CI/pre-commit:

- **0 (PASS)**: Sem violations, todos os testes estão conformes
- **2 (FAIL)**: Violations encontradas, precisa corrigir antes de commit
- **1 (ERROR)**: Erro de execução (bug do script, arquivo não encontrado, etc.)

**Uso em CI/pre-commit**:
```powershell
python verify_invariants_tests.py --strict-spec
if ($LASTEXITCODE -ne 0) {
    Write-Error "Validation failed! Fix violations before commit."
    exit $LASTEXITCODE
}
```

## Integração com VS Code

O formato de output (`file:line:col: LEVEL [CODE]: message`) é compatível com o **problemMatcher** do VS Code. Você pode criar uma task em tasks.json:

```json
{
  "label": "Verify Invariants Tests",
  "type": "shell",
  "command": "python",
  "args": [
    "docs/scripts/verify_invariants_tests.py",
    "--strict-spec"
  ],
  "problemMatcher": {
    "pattern": {
      "regexp": "^(.+):(\\d+):(\\d+): (ERROR|WARN) \\[(\\w+)\\]: (.+)$",
      "file": 1,
      "line": 2,
      "column": 3,
      "severity": 4,
      "code": 5,
      "message": 6
    }
  }
}
```

Violations aparecem na aba **Problems** e você pode clicar para ir direto ao arquivo.

## Quando usar cada modo?

| Situação | Comando | Quando usar |
|----------|---------|-------------|
| **Desenvolvimento local** | `python verify_invariants_tests.py` | Antes de commit, para verificar conformidade básica |
| **Pre-commit hook** | `python verify_invariants_tests.py --files-changed <files>` | Automaticamente antes de cada commit (otimizado) |
| **CI/CD** | `python verify_invariants_tests.py --strict-spec` | No pipeline, bloqueia merge se houver violations |
| **Debug de violations** | `python verify_invariants_tests.py --verbose --report-txt report.txt` | Quando precisar de análise detalhada |
| **Após migração 100% SPEC** | Sempre `--strict-spec` | Quando todos INVs tiverem blocos SPEC (futuro) |

## Próximos Passos Após Rodar

Se o script retornar **exit code 2** (violations):

1. **Leia o relatório** (console ou report.txt) e identifique os códigos de erro
2. **Corrija por prioridade**:
   - `COVERAGE_DUPLICATE`: Consolidar arquivos duplicados
   - `SPEC_MISSING`: Adicionar bloco SPEC ao INVARIANTS_TRAINING.md
   - `OBLIG_A_MISSING`/`OBLIG_B_MISSING`: Adicionar Obrigações aos docstrings
   - `DOD0_NO_CLASS`/`DOD0_NO_TESTS`: Corrigir nomenclatura/estrutura
   - Violations específicas de classe (A_MIN_INVALID, D_REQUIRES_CLIENT, etc.)
3. **Re-rode o script** até obter exit code 0
4. **Commit** quando tudo estiver PASS

