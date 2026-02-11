# CHECKLIST_AGENT_DOCUMENTATION.md

## Descrição
Checklist para atualização de documentação: validar que docs ficaram ordenadas, consistentes, e aderentes ao canon.

---

## Pré-Edição

### Planejamento
- [ ] Identificar qual doc deve ser editado (usar MAP_ROUTING_AGENT_DOCUMENTATION.md)
- [ ] Tier da doc (SSOT/Canon/ADR/Reference)?
- [ ] Se Tier 2-3: ADR necessária ou direto edit?
- [ ] Escopo da mudança
  - [ ] Línea ou duas → direto
  - [ ] Seção nova → talvez ADR
  - [ ] Mudança arquitetural → definitivamente ADR

### Autoridade
- [ ] Canon docs citadas? (qual path e seção)
- [ ] SSOT validado? (schema.sql, openapi.json, artefatos)
- [ ] Sem conflict com ADRs existentes?

---

## Durante Edição

### Estrutura & Formatting
- [ ] Markdown válido (headers, links, listas)
  ```powershell
  # Dica: abrir arquivo em VS Code, verificar erros syntax
  ```
- [ ] Links relativos (não absolutos, não file://)
  - ✅ `docs/_canon/00_START_HERE.md`
  - ❌ `C:\HB TRACK\docs\_canon\00_START_HERE.md`
  - ❌ `file:///docs/...`
- [ ] Código blocks com linguagem especificada (```python, ```powershell)
- [ ] Não há orphaned headings (##  sem # antes)
- [ ] Indentação consistente (2 ou 4 espaços, pick one)

### Content Quality
- [ ] Nenhuma PII/secrets disperso (senhas, tokens, emails pessoais)
- [ ] Exemplos concretos (não genéricos)
- [ ] Linguagem clara (evitar jargão sem explicação)
- [ ] Se técnico: cita fontes (código, commit, artefato)

### Referências Cruzadas
- [ ] Todos links dentro do doc são validos (não quebrados)
- [ ] Backlinks: outras docs que referenciam este arquivo, foram atualizadas?
  ```powershell
  # Use grep_search para encontrar refs
  grep_search -query "filename_novo" -isRegexp false
  ```
- [ ] Índice principal (_INDEX.md) foi atualizado?

### Versionamento
- [ ] Data de "lastUpdated" está correta
  ```yaml
  lastUpdated: "YYYY-MM-DD"  # data atual
  ```
- [ ] Changelog mencionará esta edição
- [ ] EXECUTIONLOG mencionará esta edição

---

## Pós-Edição

### Validação do Arquivo
- [ ] Abrir arquivo em browser/markdown previewer → sem erros de rendering
- [ ] Copiar alguns links e testar (clicáveis?)
- [ ] Procurar typos (PT-BR spell check, se disponível)

### Git Diff Review
```powershell
git diff docs/_canon/meu_arquivo.md

# Verificar:
# ✓ Apenas mudanças intentadas foram feitas
# ✓ Nenhuma linha acidentalmente deletada
# ✓ Formatting é consistente
```

### Commit Message
- [ ] Formato padrão: `docs(<tier>): <change>`
  - ✅ `docs(canon): add guardrail-baseline section`
  - ✅ `docs(adr): decision on models pipeline architecture`
  - ❌ `update docs` ou `fix`
- [ ] Menciona qual tier foi editado
- [ ] Descreve a mudança (não "updated stuff")

### Changelog + Executionlog Update
- [ ] CHANGELOG.md tem nova entrada
  ```
  ## [YYYY-MM-DD] Documentation Updates
  - Added/Fixed/Updated <what>
  - Impact: <quem é afetado>
  ```
- [ ] EXECUTIONLOG.md tem entrada com task ID
  ```
  T-NNN: Edit canonical docs (<scope>)
  - Command: git add/commit
  - ExitCode: 0
  - Artifacts: <paths>
  ```

---

## Final Gate (Before Committing)

### Checklist Consolidado
- ✓ Markdown válido (syntax, formatting)
- ✓ Links validos (relativos, não quebrados)
- ✓ Referências cruzadas atualizadas
- ✓ Nenhuma PII
- ✓ Canon/SSOT referencias citadas
- ✓ Commit message descritivo
- ✓ CHANGELOG + EXECUTIONLOG atualizados
- ✓ git diff é limpo e intentado
- ✓ git status --porcelain mostra apenas docs editados

### Go/No-Go Decision
- ✅ **GO**: Todos checks passados → `git add + git commit`
- ❌ **NO-GO**: Qualquer falha → fix + re-validate

---

## TODO
- [ ] Criar markdown linter (syntax + content validações)
- [ ] Adicionar spell checker (PT-BR)
- [ ] Criar automated checker para links quebrados
- [ ] Documentar como testar links (especially external)
