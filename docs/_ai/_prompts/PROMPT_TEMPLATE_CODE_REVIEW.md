# PROMPT_TEMPLATE_CODE_REVIEW.md

## Descrição
Template padrão para code review: estrutura, seções esperadas, e outputs obrigatórios.

---

## Estrutura de Saída (§1-§6 Hard Format)

### § 1 — Análise Geral (3-5 linhas)
Strengths + weaknesses curto e objetivo.

**Exemplo:**
```
Clean code, good SRP, but cyclomatic complexity > 6 em 2 funções.
Proper error handling, but logging vaza PII em 3 locais.
```

### § 2 — Feedback Específico por Severidade
Formato obrigatório:
- **SEVERIDADE**: BLOCKER | MAJOR | MINOR | NIT
- **EVIDÊNCIA**: `@arquivo.ext#Lx-Ly` (linha exata) ou trecho curto
- **IMPACTO**: (curto e quantificável)
- **SUGESTÃO**: (acionável + código se necessário)

**Exemplo:**
```
MAJOR: Hardcoded UUID in test
Evidência: @tests/test_models.py#L42-L44
Impacto: Flaky test, breaks on CI
Sugestão: Use pytest.fixture em vez de UUID hardcoded
```

### § 3 — Priorizadas (3-5 recomendações)
Em ordem de maior ROI (retorno de investimento).

### § 4 — Patch (somente se solicitado)
Diff mínimo e seguro por arquivo.

### § 5 — Validação
Comandos aprovados (de `08_APPROVED_COMMANDS.md`) + resultado esperado.

### § 6 — Métricas
LOC antes/depois, funções > 50 LOC, complexidade > 6, etc.

---

## Variáveis de Input
- `FILE`: arquivo alvo
- `GOAL`: objetivo (reduzir duplicação, complexidade, etc.)
- `MODE`: SUGGEST | APPLY
- `CONSTRAINTS`: restrições adicionais

---

## TODO
- [ ] Documentar edge cases (muito grande, muito duplicado, código obfuscado)
- [ ] Criar formulário interativo para parametrizar review
- [ ] Adicionar scoring rubric (para automatizar severity)
