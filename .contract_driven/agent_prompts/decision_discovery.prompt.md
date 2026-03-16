## Prompt Operacional — Decision Discovery (DSS)

**Objetivo**: executar o estágio `Decision Discovery` antes de `contract_creation_mode` ou `contract_revision_mode` quando há lacuna arquitetural relevante no módulo alvo.

### Entrada esperada (do humano)
- `module` (lower_snake_case) — deve existir na taxonomia do LAYOUT.
- `task_type` — `contract_creation` | `contract_revision` | `architecture_review`.
- `decision_topic` (opcional) — tópico específico a ser analisado (ex.: `AUTH_STRATEGY`).

### Leitura mínima obrigatória (ordem)
1. `docs/_canon/DECISION_POLICY.md` (**SSOT deste estágio**)
2. `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` (decisões em aberto)
3. `docs/_canon/decisions/` — ADRs aprovadas relevantes ao módulo
4. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
5. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
6. `docs/_canon/ARCHITECTURE.md`
7. `docs/_canon/SECURITY_RULES.md` (se o tópico for AUTH, AUTHZ, dados sensíveis ou secrets)
8. `docs/_canon/DATA_CONVENTIONS.md` (se o tópico for DATE_TIME ou TIMEZONE)
9. `docs/_canon/HANDBALL_RULES_DOMAIN.md` (se gatilho esportivo ativo — ver §6 de DECISION_POLICY.md)
10. `docs/hbtrack/modulos/<MODULE>/SPORT_SCIENCE_RULES_<MODULE>.md` (se existir e gatilho esportivo ativo)
11. `docs/hbtrack/modulos/<MODULE>/MODULE_SCOPE_<MODULE>.md`

### Verificações iniciais (falhar cedo)

1. **Verificar se `module` existe** na taxonomia de LAYOUT §2. Se não existir: `BLOCKED_MISSING_MODULE`.
2. **Verificar backlog**: consultar `ARCHITECTURE_DECISION_BACKLOG.md` para o módulo alvo.
   - Se houver entrada com `criticidade: obrigatória` e `status: open` → emitir `BLOCKED_MISSING_ARCH_DECISION` e não prosseguir para contrato sem resolução.
   - Se houver entradas `importante` em aberto → listar como aviso, prosseguir apenas com aprovação humana explícita.
3. **Verificar checklist mínima** conforme `DECISION_POLICY.md` §4 se `task_type = contract_creation`:
   - Para cada tópico da checklist: checar se existe ADR aceita ou seção canônica resolvida.
   - Tópicos `obrigatórios` sem evidência → adicionar ao relatório de decisões pendentes.
4. **Verificar gatilho esportivo**: se o módulo for `matches`, `competitions`, `training`, `wellness`, `medical` ou se a decisão tocar semântica de handebol → ativar gatilho esportivo (leituras 9 e 10 tornam-se obrigatórias).

### Procedimento

1. Completar leituras mínimas conforme checagem inicial.
2. Para cada decisão pendente identificada:
   a. Classificar em `obrigatória`, `importante` ou `opcional` conforme `DECISION_POLICY.md` §3.
   b. Gerar proposta estruturada usando o template de `DECISION_POLICY.md` §5.
   c. Listar no Impact Map: quais artefatos canônicos precisam ser alterados e quais gates executados.
3. Apresentar ao humano:
   - Sumário de decisões blockeantes (`obrigatória` em aberto)
   - Sumário de decisões com aviso (`importante` em aberto)
   - Proposta(s) DSS para cada item relevante
4. **Aguardar aprovação humana** — não executar implementação até aprovação explícita.
5. Após aprovação:
   - Criar `docs/_canon/decisions/ADR-NNN-<slug>.md` com status `Accepted`.
   - Atualizar artefatos do Impact Map.
   - Atualizar `ARCHITECTURE_DECISION_BACKLOG.md` (status → `resolved`).
   - Rodar `python3 scripts/validate_contracts.py`.

### Bloqueios (emitir e parar)

| Código | Condição |
|--------|----------|
| `BLOCKED_MISSING_MODULE` | Módulo não existe na taxonomia de LAYOUT §2 |
| `BLOCKED_MISSING_ARCH_DECISION` | Decisão `obrigatória` em aberto no backlog para o módulo |
| `BLOCKED_CONTRACT_CONFLICT` | Duas fontes canônicas no mesmo nível dizem coisas diferentes sobre a decisão |

### Saída

**Se Decision Discovery for aprovado sem bloqueios:**
- Relatório de decisões verificadas (com links para ADRs)
- Lista de decisões `importante` em aberto (aviso)
- Confirmação de que `contract_creation_mode` / `contract_revision_mode` pode proceder

**Se houver bloqueios:**
- Relatório com cada `BLOCKED_MISSING_ARCH_DECISION` identificado
- Proposta(s) DSS estruturada(s) para resolução
- Instrução: aguardar aprovação humana e promoção para ADR antes de prosseguir

**Após promoção:**
- `docs/_canon/decisions/ADR-NNN-<slug>.md` criado
- `ARCHITECTURE_DECISION_BACKLOG.md` atualizado
- Artefatos canônicos do Impact Map atualizados
- Gates verificados via `python3 scripts/validate_contracts.py`
