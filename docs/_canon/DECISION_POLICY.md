---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-15"
status: active
adr_origin: ADR-006-Inserção-Decision-Support-System
---

# Política de Decisão — HB Track

## 0. Objetivo

Este documento define as regras operacionais do **Decision Support System (DSS)** do HB Track.

Ele governa:
- quando o estágio `Decision Discovery` é obrigatório
- como decisões são classificadas, estruturadas e promovidas para artefato canônico
- quais lacunas arquiteturais mínimas devem ser fechadas antes de qualquer contrato de produção
- como o DSS interage com a hierarquia normativa existente

Este documento deve ser lido junto com:
- `docs/_canon/ARCHITECTURE.md` §6A (estágio Decision Discovery)
- `docs/_canon/CHANGE_POLICY.md` (processo formal de mudança)
- `docs/_canon/decisions/ADR-006-Inserção-Decision-Support-System.md` (ADR de origem)
- `.contract_driven/agent_prompts/decision_discovery.prompt.md` (prompt operacional)
- `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` (backlog de decisões em aberto)

---

## 1. Princípio Fundamental

O DSS é uma camada de **apoio à decisão**. Ele nunca é fonte primária da verdade.

Toda decisão recomendada pelo DSS fica pendente até aprovação humana explícita.
Toda decisão aprovada deve ser promovida para `docs/_canon/decisions/ADR-*.md` antes de qualquer implementação downstream.

**Inferir e implementar silenciosamente é proibido.**

---

## 2. Quando o Estágio `Decision Discovery` é Obrigatório

O estágio `Decision Discovery` deve preceder `contract_creation_mode` e `contract_revision_mode` quando qualquer uma das condições abaixo for verdadeira:

| Condição | Gatilho |
|----------|---------|
| O módulo alvo possui decisão classificada como `obrigatória` em aberto no `ARCHITECTURE_DECISION_BACKLOG.md` | Sempre |
| O contrato sendo criado/revisado envolve autenticação, autorização, dados sensíveis ou events assíncronos | Sempre |
| Existe placeholder não resolvido (`{{...}}`) em artefato canônico relevante ao módulo | Sempre |
| A decisão impacta semântica de handebol ou ciência do esporte | Sempre (ativa gatilho esportivo) |
| O agente não encontra ADR que cubra uma convenção que precisa ser adotada | Sempre |

Quando nenhuma condição acima se aplica, o estágio é `SKIP_NOT_APPLICABLE`.

---

## 3. Classificação de Criticidade

| Criticidade | Definição | Comportamento |
|-------------|-----------|---------------|
| `obrigatória` | Sem decisão documentada, é impossível criar contrato correto ou a implementação diverge entre módulos | Bloqueia com `BLOCKED_MISSING_ARCH_DECISION`. Não continuar sem ADR aprovada. |
| `importante` | A ausência não bloqueia o contrato, mas cria risco de inconsistência futura | Emite aviso. Registrar no backlog. Prosseguir apenas se o humano aprovar explicitamente. |
| `opcional` | Melhora a qualidade, mas não é estruturalmente necessária agora | Registrar no backlog. Não bloqueia. |

---

## 4. Checklist Mínima de Lacunas Arquiteturais de Produção

Antes de qualquer contrato de produção (não experimental/placeholder), o DSS deve verificar se as seguintes decisões possuem ADR aprovada ou seção canônica resolvida:

| Tópico | Artefato canônico esperado | Criticidade |
|--------|---------------------------|-------------|
| `AUTH_STRATEGY` | ADR ou seção em `SECURITY_RULES.md` | obrigatória |
| `AUTHZ_STRATEGY` | ADR ou seção em `SECURITY_RULES.md` | obrigatória |
| `VERSIONING_STRATEGY` | ADR-003 (já aceita) | obrigatória |
| `DEPRECATION_POLICY` | Seção em `CHANGE_POLICY.md` | obrigatória |
| `DATE_TIME_STANDARD` | Seção em `DATA_CONVENTIONS.md` | obrigatória |
| `TIMEZONE_POLICY` | Seção em `DATA_CONVENTIONS.md` | obrigatória |
| `SENSITIVE_DATA_POLICY` | Seção em `SECURITY_RULES.md` | obrigatória |
| `RETENTION_POLICY` | ADR ou seção em `SECURITY_RULES.md` | importante |
| `MASKING_POLICY` | ADR ou seção em `SECURITY_RULES.md` | importante |
| `SECRETS_POLICY` | Seção em `SECURITY_RULES.md` | obrigatória |
| `ROTATION_POLICY` | ADR ou seção em `SECURITY_RULES.md` | importante |
| `LOGGING_POLICY` | ADR ou seção em `SECURITY_RULES.md` | importante |

Esta tabela é atualizada por ADR quando novos tópicos são adicionados.

---

## 5. Estrutura da Proposta DSS

Cada proposta gerada pelo DSS deve conter obrigatoriamente:

```
## Proposta DSS — <TÍTULO>

**Criticidade**: obrigatória | importante | opcional
**Módulo(s) afetado(s)**: <lista>
**Gatilho esportivo**: sim | não

### Contexto
<O que levou a esta decisão>

### Problema
<Qual lacuna ou conflito precisa ser resolvido>

### Alternativas
1. <Alternativa A> — vantagens / desvantagens
2. <Alternativa B> — vantagens / desvantagens

### Recomendação
<Qual alternativa o DSS recomenda e por quê>

### Trade-offs e Riscos
<O que se perde com a escolha recomendada>

### Impact Map
**Artefatos canônicos a atualizar:** <lista>
**Gates a executar após aprovação:** <lista>
**Contratos técnicos impactados:** <lista>

### Decisão requerida
[ ] Aprovado — prosseguir com promoção para ADR
[ ] Rejeitado — manter status quo
[ ] Postergado — criar entrada no backlog como `importante`
```

---

## 6. Fluxo de Promoção

Uma vez aprovada pelo humano:

1. Criar `docs/_canon/decisions/ADR-NNN-<slug>.md` com status `Accepted`.
2. Atualizar artefatos canônicos listados no Impact Map (ex.: `ARCHITECTURE.md`, `SECURITY_RULES.md`).
3. Atualizar contratos técnicos impactados se necessário.
4. Remover a entrada correspondente de `ARCHITECTURE_DECISION_BACKLOG.md` ou alterar seu status para `resolved`.
5. Rodar `python3 scripts/validate_contracts.py` para verificar que nenhum gate foi quebrado.

---

## 7. Gatilho Esportivo

Quando a decisão impactar:
- semântica de handebol (posições de jogo, fases de competição, regras IHF, etc.)
- ciência do esporte (sRPE, HRV, strain, readiness, protocolos de teste, recuperação)

O DSS deve **obrigatoriamente** ler antes de propor opção final:
- `docs/_canon/HANDBALL_RULES_DOMAIN.md`
- `docs/hbtrack/modulos/<MODULE>/SPORT_SCIENCE_RULES_<MODULE>.md` (se existir)

Sem essa leitura, a proposta é considerada incompleta e não pode ser promovida.

---

## 8. Código de Bloqueio

| Código | Significado |
|--------|-------------|
| `BLOCKED_MISSING_ARCH_DECISION` | Decisão arquitetural classificada como `obrigatória` não possui ADR aprovada. Implementação bloqueada até promoção formal. |

Este código é emitido pelo estágio `Decision Discovery` e pode ser verificado pelo gate `ARCH_DECISION_PRESENCE_GATE`.

---

## 9. Referências

- `docs/_canon/decisions/ADR-006-Inserção-Decision-Support-System.md`
- `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md`
- `docs/_canon/CHANGE_POLICY.md`
- `docs/_canon/ARCHITECTURE.md`
- `.contract_driven/agent_prompts/decision_discovery.prompt.md`
- `docs/_canon/gates/GATES_REGISTRY.yaml` (gate `ARCH_DECISION_PRESENCE_GATE`)
