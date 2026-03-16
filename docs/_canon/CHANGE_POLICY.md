---
doc_type: canon
version: "1.1.0"
last_reviewed: "2026-03-13"
status: active
---

# Política de Mudança — HB Track

## 1. Princípio Fundamental

Toda mudança com impacto em contratos públicos, invariantes ou módulos deve passar por processo formal **antes de qualquer implementação downstream**.

**"Refatorar para depois corrigir o contrato" é uma violação desta política.**

O sistema contract-driven do HB Track garante que o contrato é a fonte de verdade, e não o código. A ordem é sempre: contrato aprovado → implementação → verificação. Invertê-la compromete a rastreabilidade e a confiança no sistema.

---

## 2. Regras Cardinais (6)

1. **Contrato antes de código**: o contrato deve ser atualizado e aprovado antes de qualquer implementação. Código que antecede o contrato é considerado não-contratado.

2. **Domínio antes de tecnologia**: mudanças em regras de negócio atualizam `HANDBALL_RULES_DOMAIN.md` ou `SYSTEM_SCOPE.md` antes de qualquer artefato técnico. Tecnologia serve ao domínio, não o contrário.

3. **ADR para mudanças arquiteturais**: decisões de stack, padrões globais ou estrutura de módulos requerem ADR (Architecture Decision Record) em `docs/_canon/decisions/` antes da implementação.

4. **Breaking change explícita**: toda mudança incompatível com contratos vigentes deve ser classificada, documentada e comunicada a consumidores conhecidos antes de qualquer merge.

5. **Gates antes de merge**: nenhum PR pode ser merged com contract gates em FAIL. O hook `scripts/git-hooks/pre-commit` roda o pipeline local; CI deve executar o mesmo pipeline de forma não-bypassável (ver `CI_CONTRACT_GATES.md`).

6. **SSOT único**: mudanças normativas só são aceitas nos paths canônicos definidos em `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`. Duplicação de fonte soberana é proibida.

---

## 3. Classificação de Mudanças

| Tipo | Descrição | Processo |
|------|-----------|----------|
| `non-breaking` | Mudança compatível (adição opcional, novo endpoint, novo valor em enum extensível) | PR + contract gates PASS |
| `breaking` | Mudança incompatível (remoção/rename/tipo/semântica) | ADR + plano de depreciação + aprovação explícita + atualização de baseline quando aplicável |
| `internal-only` | Mudança sem impacto em contratos técnicos (`contracts/**`) nem docs normativos | PR + revisão por par |
| `documentation-only` | Correção/clarificação de docs sem mudar contrato técnico | PR + revisão por par |
| `hotfix` | Correção emergencial em produção (repos de implementação) | Processo excepcional — ver §6 |

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
   → Abrir PR com:
     - tipo (non-breaking | breaking | internal-only | documentation-only)
     - justificativa clara
     - módulos afetados
     - artefatos a serem alterados (paths canônicos)

2. CONTRATO
   → Atualizar contrato(s) afetado(s):
     - OpenAPI: `contracts/openapi/openapi.yaml` e/ou `contracts/openapi/paths/<module>.yaml`
     - JSON Schemas: `contracts/schemas/<module>/` (e/ou `contracts/schemas/shared/`)
     - Workflows: `contracts/workflows/**` (Arazzo)
     - Eventos: `contracts/asyncapi/**` (AsyncAPI)
     - Docs de módulo: `docs/hbtrack/modulos/<module>/*` (invariantes, permissões, erros, state model, test matrix)
     - Docs globais: `docs/_canon/*` quando a regra é global

3. REVISÃO
   → Para breaking changes: ADR obrigatória + revisão reforçada
   → Para non-breaking/documentation-only: revisão por par é suficiente
   → Para internal-only: revisão por par (checar que não houve toque em `contracts/**` nem em docs normativos)

4. APROVAÇÃO
   → Aprovação por review do PR
   → Para breaking: notificação a consumidores conhecidos antes do merge + registro na seção de Deprecação (§7)

5. IMPLEMENTAÇÃO
   → Implementações downstream (backend/frontend/workers) devem ser fiéis ao contrato merged
   → Sem desvios — se surgir necessidade de desvio, voltar ao passo 2 (contrato) e revalidar

6. VERIFICAÇÃO
   → Rodar contract gates e anexar evidência no PR:
     - `python3 scripts/validate_contracts.py`
     - artefato gerado: `_reports/contract_gates/latest.json`
   → PR merged somente com gates em PASS (ou PASS_WITH_WARNINGS quando aplicável)
```

**Regra de travamento**: em nenhuma hipótese o passo 5 antecede o passo 4.

---

## 6. Exceções — Hotfix Emergencial

Mudanças emergenciais (bug crítico em produção com impacto real) podem comprimir etapas 1-4 com as seguintes condições obrigatórias:

1. **Justificativa documentada**: o commit deve conter `HOTFIX:` no título e descrever o impacto do bug
2. **Escopo explicitamente limitado**: apenas a correção mínima — sem aproveitamento para refatorações
3. **Prazo de retroatualização**: máximo de 48 horas para abrir PR(s) de retroatualização de contrato/docs e atualizar evidências de gates
4. **Responsável identificado**: nome do responsável pela retroatualização documentado no PR/issue
5. **Revisão pós-hotfix**: PR de retroatualização deve ser revisado normalmente

Hotfixes que introduzem breaking change **não são elegíveis para este processo excepcional** — breaking changes nunca são emergenciais por definição (têm alternativa que preserva compatibilidade).

---

## 7. Deprecação de APIs

> Esta seção é formalizada como decisão arquitetural normativa em **[ADR-014](decisions/ADR-014-deprecation-policy.md)**.
> Em caso de conflito entre este texto e o ADR, o ADR prevalece.

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
- Promoção de novo artefato normativo soberano (nova superfície SSOT / novo doc canônico por módulo)
- Mudanças no processo de contract gates ou nas regras do sistema contract-driven

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
- [PRs/changes relacionados]
```

---

## 9. Governança de Modelos de Dados no Banco (implementações)

Mudanças em schema do banco de dados seguem protocolo adicional:

1. Migrations: nome descritivo e reversibilidade planejada
2. Mudanças que alteram dados existentes exigem: script/rotina de validação pré/pós migração + plano de rollback
3. Se a mudança impactar contrato público (OpenAPI/schemas/eventos), o contrato deve ser atualizado e validado antes do deploy

**Nota**: este workspace governa contratos e docs normativas. Migrations e código vivem nos repositórios de implementação, mas não podem divergir dos contratos publicados aqui.

---

## 11. Revisão Científica Periódica (SPORT_SCIENCE_RULES)

Regras registradas em `docs/hbtrack/modulos/<module>/SPORT_SCIENCE_RULES_<MODULE>.md` são baseadas em evidência técnico-científica e possuem critérios de revisão próprios, complementares ao fluxo geral desta política.

### 11.1 Gatilhos de revisão

Uma regra em `SPORT_SCIENCE_RULES_<MODULE>.md` deve ser revisada quando:
- A fonte autorizada (ex: ACSM, Aspetar, EHF) publica atualização relevante que contradiz ou refina a regra.
- Evidência de nível igual ou superior à da regra original for publicada contestando seu conteúdo.
- O contexto de aplicabilidade (população, posição, faixa etária, fase) mudar por decisão de produto documentada em ADR.
- O artefato atingir o ciclo de revisão declarado no campo `Observações` da tabela (ex.: "revisar anualmente").

### 11.2 Processo

1. Abrir PR do tipo `documentation-only` (se não houver impacto em contratos técnicos) ou `non-breaking` (se houver adição downstream).
2. Declarar na descrição do PR: regra afetada (ID), fonte original, nova fonte/evidência, natureza da mudança.
3. Para remoção de regra que alimenta cálculo ou decisão em contrato downstream: tratar como `breaking` e abrir ADR.

### 11.3 Proibições

- **Não atualizar threshold** sem nova fonte rastreável com nível de evidência igual ou superior.
- **Não remover campo `Fonte`** de nenhuma regra existente — regra sem fonte é inválida por definição.
- **Não promover benchmark funcional** (XPS, Teamworks) a fonte de autoridade técnico-científica neste artefato.

### 11.4 Autoridade de fontes

Ver `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml` para lista de `source_id` autorizados por módulo. O `EXTERNAL_SOURCE_AUTHORITY_GATE` bloqueia automaticamente marcação de fontes externas como SSOT.

---

## 10. Referências Cruzadas

- `.contract_driven/templates/api/api_rules.yaml` — SSOT de convenções/templates/validações de API HTTP
- `API_CONVENTIONS.md` — guia/ponteiros (não-SSOT) para API
- `DATA_CONVENTIONS.md` — convenções de dados e breaking changes de schema
- `CONTRACT_SYSTEM_RULES.md` — regras operacionais do sistema contract-driven
- `docs/_canon/decisions/` — registro de ADRs aprovados
- `CI_CONTRACT_GATES.md` — especificação dos gates e evidências esperadas
- `scripts/validate_contracts.py` — execução local do pipeline de contract gates
