# PROMPT_TEMPLATE_TESTING.md

## Descrição
Template padrão para geração de testes: estrutura, naming, assertions, e validação de coverage.

---

## Estrutura de Teste Padrão

### Anatomia do Teste
```
test_<module>_<unit>_<scenario>_<outcome>
  ├─ Setup (fixtures, mocks)
  ├─ Execute (ação a testar)
  ├─ Assert (resultado esperado)
  └─ Cleanup (se necessário)
```

**Exemplo:**
```python
def test_model_athlete_create_with_valid_data_returns_athlete_object():
    # Setup
    data = {"name": "John", "age": 25}
    
    # Execute
    athlete = Athlete(**data)
    
    # Assert
    assert athlete.name == "John"
    assert athlete.age == 25
    assert athlete.id is None  # Pre-save
```

---

## Naming Convention
- **Módulo**: `test_<modulo>`
- **Classe**: `Test<UnitUnderTest>`
- **Método**: `test_<scenario>_<outcome>`

**Bom:**
```
test_model_athlete_with_missing_required_field_raises_validation_error()
test_parity_gate_when_schema_differs_returns_exit_code_2()
```

**Ruim:**
```
test_athlete()
test_parity()
test_fix()
```

---

## Validações Obrigatórias
- [ ] Sem hardcoded UUIDs/timestamps → usar fixtures
- [ ] Sem `create_engine` manual em testes → usar session fixture
- [ ] Sem `assert True/False` genérico → assert específico
- [ ] Sem commented-out assertions → remover ou reativar
- [ ] Coverage mínimo: 80% (crítico), 90% (nice-to-have)

---

## Test Types
- **Unit**: Função/método isolado, sem DB/IO
- **Integration**: Com DB/fixtures, validações cruzadas
- **Contract**: API schemas (Pydantic), request/response shapes
- **Invariant**: Regras de negócio imutáveis (soft delete, auditoria, etc.)

---

## TODO
- [ ] Criar test data factory para models
- [ ] Documentar mock strategy para dependências externas
- [ ] Adicionar parametrized test examples
- [ ] Especificar pytest.ini + markers padrão
