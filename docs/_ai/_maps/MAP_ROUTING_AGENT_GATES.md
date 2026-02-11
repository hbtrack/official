# MAP_ROUTING_AGENT_GATES.md

## Descrição
Detalhamento dos 3 gates principais: guard, parity, requirements. Entry point, sequência, e critérios de parada.

---

## Overview dos 3 Gates

### Guard Gate (agent_guard.py)
**Propósito**: Detectar mudanças no código do agente e baseline drift

**Quando rodar**:
- Antes de snapshot baseline
- Antes de grandes mudanças estruturais de modelo

**Sequência**:
1. `agent_guard.py guard` (detecta drift em artefatos)
2. Se exit=3 → baseline está desatualizado
3. `agent_guard.py snapshot baseline` (REQUER APROVAÇÃO)

**Critério de Parada**:
- Exit=0: Sem drift, prosseguir
- Exit=3: Drift detectado; revisar e snapshot

---

### Parity Gate (parity_gate.ps1)
**Propósito**: Comparar estrutura entre schema.sql (DB SSOT) e models (código)

**Quando rodar**:
- Detectar DIFFs estruturais (coluna faltando, tipo errado, constraint divergente)
- Validar que model.py reflete exatamente o DB

**Sequência**:
1. `inv.ps1 refresh` (ONCE, atualiza schema.sql e docs)
2. `parity_gate.ps1 -Table <T>` (compara específica tabela)
3. Se exit=2 → diff encontrado, investigar
4. Opções: editar model.py OR editar schema.sql+Alembic

**Critério de Parada**:
- Exit=0: Parity perfeita
- Exit=2: Diferença estrutural; loop até resolver

---

### Requirements Gate (model_requirements.py)
**Propósito**: Validar requirements de negócio: validators, defaults, constraints, tipos, profiles

**Quando rodar**:
- Após model.py editado manualmente
- Validação final antes de snapshot

**Sequência**:
1. `model_requirements.py --table <T> --profile <P>`
2. Se exit=4 → violations encontradas
3. Investigar linha específica + corrigir
4. Rerunner reqs até exit=0

**Profiles**:
- `strict`: Sem warnings, zero violations (default)
- `fk`: Permite ciclos FK c/ `-AllowCycleWarning`
- `lenient`: Apenas erros críticos

**Critério de Parada**:
- Exit=0: Todos reqs passados
- Exit=4: Violations; corrigir e retry

---

## Sequential Execution (Typical Flow)

```
## Cenário: Adicionar coluna em tabela

1. Editar schema.sql (via Alembic ou diretamente)
2. inv.ps1 refresh
   └─ Exit=0: schema.sql atualizado
3. parity_gate.ps1 -Table <T>
   ├─ Exit=0: Sem diff (model já sinc)
   └─ Exit=2: Diff encontrado → editar model.py OR autogen
4. models_autogen_gate.ps1 -Table <T> -Profile strict
   └─ Exit=0: Model regenerado
5. parity_gate.ps1 -Table <T>
   └─ Exit=0: Agora em sync
6. model_requirements.py --table <T> --profile strict
   └─ Exit=0: Reqs validados
7. git diff (revisar mudanças)
8. git add + git commit (com aprovação)
9. agent_guard.py snapshot baseline (OPCIONAL, com aprovação)
```

---

## TODO
- [ ] Criar decision tree visual (quando skip qual gate)
- [ ] Documentar timeout/retry policies
- [ ] Adicionar alert para gates travados
