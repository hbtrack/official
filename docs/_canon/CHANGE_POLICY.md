---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-11"
status: active
---

# Política de Mudança — HB Track

## 1. Princípio Fundamental

Toda mudança com impacto em contratos públicos, invariantes ou módulos deve passar por processo formal antes de implementação.

**"Refatorar para depois corrigir o contrato" é uma violação desta política.**

O sistema contract-driven do HB Track garante que o contrato é a fonte de verdade, e não o código. A ordem é sempre: contrato aprovado → implementação → verificação. Invertê-la compromete a rastreabilidade e a confiança no sistema.

---

## 2. Regras Cardinais (5)

1. **Contrato antes de código**: o contrato deve ser atualizado e aprovado antes de qualquer implementação. Código que antecede o contrato é considerado não-contratado.

2. **Domínio antes de tecnologia**: mudanças em regras de negócio atualizam `HANDBALL_RULES_DOMAIN.md` ou `SYSTEM_SCOPE.md` antes de qualquer artefato técnico. Tecnologia serve ao domínio, não o contrário.

3. **ADR para mudanças arquiteturais**: decisões de stack, padrões globais ou estrutura de módulos requerem ADR (Architecture Decision Record) em `docs/_canon/decisions/` antes da implementação.

4. **Breaking change explícita**: toda mudança incompatível com contratos vigentes deve ser classificada, documentada e comunicada a consumidores conhecidos antes de qualquer merge.

5. **Docs atualizado antes de merge**: nenhum PR pode ser merged com contratos desatualizados. O pre-commit hook enforça esta regra (`scripts/git-hooks/pre-commit`).

---

## 3. Classificação de Mudanças

| Tipo | Descrição | Processo |
|------|-----------|----------|
| `non-breaking` | Adicionar campo opcional, novo endpoint, novo valor em enum extensível, query param opcional com default razoável | AR normal — sem processo especial |
| `breaking` | Remover ou renomear campo, alterar tipo, remover endpoint, alterar semântica de campo existente | AR obrigatório + ADR + notificação a consumidores |
| `internal-only` | Refatoração sem impacto em nenhum contrato público | AR simplificado — sem revisão de arquiteto obrigatória |
| `documentation-only` | Correção de doc sem mudança de comportamento ou contrato | PR direto sem AR — apenas revisão |
| `hotfix` | Correção emergencial de bug crítico em produção | Processo excepcional — ver §6 |

---

## 4. O Que É Breaking Change

### 4.1 Breaking (requer processo formal)

- Remover campo de resposta que estava contratado
- Alterar tipo de campo existente (ex: `string` → `number`, `string` → `array`)
- Renomear campo existente (ex: `team_id` → `squad_id`)
- Remover endpoint
- Alterar semântica de campo (ex: `start_at` passa a ser UTC+3 quando era UTC)
- Tornar campo opcional obrigatório
- Remover valor de enum fechado
- Alterar `operationId` de endpoint existente
- Alterar estrutura de URL de recurso existente
- Alterar método HTTP de operação existente (ex: GET → POST)
- Alterar autenticação/autorização de forma incompatível
- Alterar formato de erro (structure do Problem Details)

### 4.2 Não-Breaking (permitido sem processo formal)

- Adicionar campo OPCIONAL em resposta
- Adicionar endpoint novo
- Adicionar valor a enum extensível (documentado com `examples`)
- Adicionar query param opcional com default razoável e bem documentado
- Melhorar mensagem de erro sem alterar estrutura ou código de status
- Adicionar header de resposta informativo
- Otimização de performance sem mudança de comportamento observável
- Adicionar documentação ou exemplos a campo existente
- Expandir constraint existente para permitir mais valores (ex: aumentar limite de tamanho de string)

---

## 5. Fluxo de Mudança (6 Passos)

```
1. PROPOSTA
   → Criar AR em docs/hbtrack/ars/ com:
     - tipo (non-breaking | breaking | internal-only)
     - justificativa clara
     - módulos afetados
     - contratos a serem alterados

2. CONTRATO
   → Atualizar contrato(s) afetado(s):
     - OpenAPI do módulo (01_<MODULO>_OPENAPI.yaml)
     - Invariantes (15_<MODULO>_INVARIANTS.yaml) se aplicável
     - DB contract (13_<MODULO>_DB_CONTRACT.yaml) se aplicável
     - Este documento, se a própria política muda

3. REVISÃO
   → Para breaking changes: revisão obrigatória por arquiteto/PO
   → Para non-breaking: revisão por par é suficiente
   → Para internal-only: auto-revisão com evidências

4. APROVAÇÃO
   → AR marcado como APROVADO no backlog
   → Para breaking: notificação a consumidores conhecidos antes de aprovação

5. IMPLEMENTAÇÃO
   → Código deve ser fiel ao contrato aprovado
   → Sem desvios — se surgir necessidade de desvio, volta ao passo 2

6. VERIFICAÇÃO
   → hb verify confirma conformidade do código com o contrato
   → hb seal sela o AR com evidências
   → PR merged somente após seal
```

**Regra de travamento**: em nenhuma hipótese o passo 5 antecede o passo 4.

---

## 6. Exceções — Hotfix Emergencial

Mudanças emergenciais (bug crítico em produção com impacto real) podem comprimir etapas 1-4 com as seguintes condições obrigatórias:

1. **Justificativa documentada**: o commit deve conter `HOTFIX:` no título e descrever o impacto do bug
2. **Escopo explicitamente limitado**: apenas a correção mínima — sem aproveitamento para refatorações
3. **Prazo de retroatualização**: máximo de 48 horas para criar AR e atualizar toda documentação afetada
4. **Responsável identificado**: nome do responsável pela retroatualização documentado no commit
5. **Revisão pós-hotfix**: PR de retroatualização deve ser revisado normalmente

Hotfixes que introduzem breaking change **não são elegíveis para este processo excepcional** — breaking changes nunca são emergenciais por definição (têm alternativa que preserva compatibilidade).

---

## 7. Deprecação de APIs

### 7.1 Sequência Formal

1. Adicionar headers de deprecação nos responses do endpoint/campo afetado:
   ```
   Deprecation: Tue, 11 Mar 2026 00:00:00 GMT
   Sunset: Thu, 11 Jun 2026 00:00:00 GMT
   Link: </new-endpoint>; rel="successor-version"
   ```
2. Registrar na tabela de depreciações ativas deste documento (§7.2)
3. Documentar no OpenAPI do módulo com `deprecated: true` e `description` explicando o substituto
4. Comunicar consumidores conhecidos (frontend, integrações, scripts)
5. Remover APENAS após a data de Sunset

### 7.2 Períodos Mínimos de Sunset

| Tipo de Consumer | Período mínimo |
|-----------------|---------------|
| APIs internas (apenas frontend HB Track) | 90 dias |
| APIs com integrações externas documentadas | 180 dias |
| APIs marcadas como `public` no contrato | 180 dias |

### 7.3 Depreciações Ativas

| Recurso Deprecado | Tipo | Deprecado em | Sunset | Substituto |
|-------------------|------|-------------|--------|-----------|
| (nenhuma) | — | — | — | — |

---

## 8. ADRs (Architecture Decision Records)

### 8.1 Quando é Obrigatório

- Mudanças de stack (ex: trocar biblioteca de ORM, mudar de Redis para outro broker)
- Novos padrões globais que afetam múltiplos módulos
- Breaking changes em múltiplos módulos simultaneamente
- Adição de novo módulo à taxonomia canônica
- Mudanças no processo MCP ou nas regras do sistema contract-driven

### 8.2 Localização

`docs/_canon/decisions/<YYYY-MM-DD>-<slug>.md`

Exemplos:
- `docs/_canon/decisions/2026-03-11-camelcase-json-fields.md`
- `docs/_canon/decisions/2026-03-11-page-token-pagination.md`

### 8.3 Template Mínimo

```markdown
# ADR-NNN: <Título da Decisão>

**Data**: YYYY-MM-DD
**Status**: Proposto | Aprovado | Depreciado | Substituído
**Decisores**: [nomes/papéis]
**Tags**: api | data | infra | security | módulo

## Contexto
[Qual problema motivou esta decisão? Qual era o estado anterior?]

## Decisão
[O que foi decidido? Seja específico e definitivo.]

## Consequências

### Positivas
- [Benefício 1]
- [Benefício 2]

### Negativas / Trade-offs
- [Custo 1]
- [Risco aceito 1]

## Alternativas Consideradas
- **[Alternativa A]**: [por que foi rejeitada]
- **[Alternativa B]**: [por que foi rejeitada]

## Documentos Relacionados
- [Contratos afetados]
- [ARs relacionados]
```

---

## 9. Processo de AR (Architecture Record)

### 9.1 Localização

`docs/hbtrack/ars/features/AR_NNN_<slug>.md`

### 9.2 Estados de Ciclo de Vida

```
RASCUNHO → APROVADO → EM_EXECUCAO → VERIFICADO → SELADO
```

- **RASCUNHO**: AR proposto, aguardando revisão
- **APROVADO**: contrato revisado e aprovado, pronto para implementação
- **EM_EXECUCAO**: implementação em andamento
- **VERIFICADO**: `hb verify` passou sem erros
- **SELADO**: `hb seal` executado — AR imutável com evidências

### 9.3 Critério de Selagem

Um AR só pode ser selado (`hb seal`) quando:
- Todos os contratos afetados estão atualizados
- `hb verify` passa sem erros bloqueantes
- Evidências estão em `docs/hbtrack/evidence/AR_NNN/`
- Nenhum TODO ou placeholder não resolvido nos contratos afetados

---

## 10. Governança de Modelos de Dados no Banco

Mudanças em schema do banco de dados seguem protocolo adicional:

1. Migration Alembic: nome descritivo, sempre com `upgrade()` e `downgrade()`
2. `downgrade()` DEVE ser implementado e testado — migrations sem downgrade são bloqueadas em review
3. Migrations que alteram dados existentes requerem: script de validação pré-migração + plano de rollback documentado no AR
4. `ssot_touches` do AR deve listar o arquivo de migration como evidência

---

## 11. Referências Cruzadas

- `.contract_driven/templates/api/api_rules.yaml` — SSOT de convenções/templates/validações de API HTTP
- `API_CONVENTIONS.md` — guia/ponteiros (não-SSOT) para API
- `DATA_CONVENTIONS.md` — convenções de dados e breaking changes de schema
- `CONTRACT_SYSTEM_RULES.md` — regras operacionais do sistema contract-driven
- `docs/_canon/decisions/` — registro de ADRs aprovados
- `docs/hbtrack/ars/` — backlog e histórico de ARs
- `scripts/run/hb_cli.py` — ferramentas `hb verify` e `hb seal`
