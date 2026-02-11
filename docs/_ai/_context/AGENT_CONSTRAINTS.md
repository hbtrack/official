# AGENT_CONSTRAINTS.md

## Descrição
Constraints explícitas: o que o agente NÃO pode fazer, como proceder no edge cases, e limites de escopo.

---

## Constraints Técnicas

### Write Operations — Requer Autorização Explícita
- `git add`, `git commit`, `git restore`
- `inv.ps1 refresh`
- `agent_guard.py snapshot`
- `docker-compose ...`, `alembic upgrade ...`
- Qualquer arquivo em `docs/_canon/` (exceto via workflow)
- Qualquer arquivo em `.hb_guard/` (exceto via gate)

### Read Operations — Sempre Permitidas
- `git status --porcelain`
- `git diff`, `git log`
- Leitura de artefatos SSOT
- Inspeção de schema/models/tests

### Proibições Absoltas
- Invoke-Expression / iex (PowerShell)
- Conectar-se a URLs remotas sem aprovação
- Alterar `.gitignore` sem ADR
- Remover arquivos sem verificar referências

### Limites de Escopo
- Máximo 1 teste por vez (para fail-fast)
- Máximo 3 arquivos em batch (para traceability)
- Máximo 50 LOC de geração por arquivo (para revisão)

---

## TODO
- [ ] Criar lookup para exceções (se houver)
- [ ] Documentar approval workflow (quem autoriza o quê)
- [ ] Adicionar retry policy para falhas transientes
