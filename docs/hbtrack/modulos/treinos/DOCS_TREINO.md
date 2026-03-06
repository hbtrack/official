# DOCS_TREINO.md — Auditoria de Documentação (Spec-Driven) do Módulo TRAINING

**Data da auditoria:** 2026-03-06  
**Escopo analisado (somente):** `docs/hbtrack/modulos/treinos/*` (referências externas checadas apenas quando citadas pelos SSOTs)  
**Objetivo:** identificar inconsistências/gaps/drifts/erros/duplicatas e descrever a **solução necessária** para que a documentação gere o produto real corretamente.

---

## 0) Resumo executivo (o que impede “spec-driven perfeito”)

1. **RESOLVIDO — DONE_GATE como SSOT**: DONE_GATE deixou de ser SSOT; norma está em `TEST_MATRIX_TRAINING.md` e evidência em `_reports/training/DONE_GATE_TRAINING.md`.  
2. **RESOLVIDO — Batch Plan como dependência normativa**: `TRAINING_BATCH_PLAN_v1.md` foi rebaixado a histórico/out-of-chain e removido de `AR_BACKLOG_TRAINING.md`/`TEST_MATRIX_TRAINING.md`.  
3. **RESOLVIDO — datas futuras**: entradas futuras foram removidas/ajustadas para manter auditabilidade em 2026-03-06.  
4. **RESOLVIDO — drift do default `visibility_mode`**: `TRAINING_ROADMAP.md` foi amendado para refletir default `restricted` (com referência a INV-TRAIN-060/EXB-ACL-001).  
5. **PENDENTE — status do SSOT de invariantes**: `_INDEX.md` trata `INVARIANTS_TRAINING.md` como fonte normativa principal, mas o arquivo ainda está `Status: DRAFT`.  
6. **RESOLVIDO — GAP em IMPLEMENTADO**: `INVARIANTS_TRAINING.md` foi normalizado para remover `evidence: GAP:` em itens `status: IMPLEMENTADO`.  
7. **RESOLVIDO — SPEC_VERSIONING baseline**: baseline foi criado em `contracts/openapi/baseline/openapi_baseline.json` e a doc foi atualizada para usá-lo no `CONTRACT_DIFF_GATE`.  
8. **RESOLVIDO — canonicidade OpenAPI/Schema**: SSOT técnico canônico é `Hb Track - Backend/docs/ssot/*` (espelho derivado: `docs/ssot/*`) e a doc foi alinhada para isso.

---

## 1) Achados detalhados (inconsistências, gaps, drifts, erros, duplicatas)

### CRIT-001 — DONE_GATE ausente no local canônico
**Onde aparecia como canônico (antes da correção):**
- `AR_BACKLOG_TRAINING.md` e `INVARIANTS_TRAINING.md` referenciavam `DONE_GATE_TRAINING.md` como norma (drift).
- `TEST_MATRIX_TRAINING.md` citava `DONE_GATE_TRAINING_v3.md` como artefato obrigatório.

**Status atual:**
- DONE_GATE é tratado como **evidência derivada** em `_reports/training/DONE_GATE_TRAINING.md`.
- A norma/gates estão em `TEST_MATRIX_TRAINING.md`.

**Impacto spec-driven:**
- Links quebrados e referência normativa sem arquivo → agentes podem inferir regras (RH-06/RH-08) “no escuro”.
- A separação SSOT vs evidência fica confusa: parte da doc trata DONE_GATE como SSOT, mas ele está em `_reports/` (que deveria ser evidência derivada).

**Solução necessária:**
DONE_GATE não deve voltar como SSOT.
Ele deve virar artefato derivado da TEST_MATRIX.
Arquitetura correta:
_INDEX.md
TEST_MATRIX_TRAINING.md
↓
TRUTH execution
↓
_reports/training/DONE_GATE_TRAINING.md
Ou seja:
DONE_GATE = relatório
não = norma
Patch documental
Remover referências normativas a DONE_GATE.
Substituir por:
Resultado registrado em:
_reports/training/DONE_GATE_TRAINING.md

---

### CRIT-002 — DONE_GATE_v3 referenciado mas inexistente
**Onde aparece:**
- `AR_BACKLOG_TRAINING.md` e `TEST_MATRIX_TRAINING.md` citam `docs/hbtrack/modulos/treinos/DONE_GATE_TRAINING_v3.md` como artefato gerado/obrigatório.

**Fato observado:**
- Arquivo não existe no módulo, nem em `_reports/`.

**Impacto spec-driven:**
- “Evidência/declaração formal” do Done Gate fica ambígua (v1/v2 em `_reports`, v3 esperado no módulo).

**Solução necessária:**
Eliminar qualquer versionamento de DONE_GATE como SSOT.
Substituir por:
DONE_GATE_TRAINING.md
como relatório único regenerado a cada execução.
Regra correta
DONE_GATE não é versionado
SSOTs são versionados
substituir:
DONE_GATE_TRAINING_v3.md
por:
_reports/training/DONE_GATE_TRAINING.md

---

### CRIT-003 — TRAINING_BATCH_PLAN_v1.md citado como peça do sistema, mas ausente
**Onde aparece:**
- `_INDEX.md`: lista `TRAINING_BATCH_PLAN_v1.md` na seção de arquivos “históricos/fora da cadeia ativa”.
- `AR_BACKLOG_TRAINING.md` e `TEST_MATRIX_TRAINING.md`: citam o Batch Plan como parte de “sync governança” e critérios de AR.

**Fato observado:**
- `docs/hbtrack/modulos/treinos/TRAINING_BATCH_PLAN_v1.md` **não existe**.

**Impacto spec-driven:**
- Documentos discordam se o Batch Plan é “fora da cadeia ativa” ou “obrigatório para sync”.  
- Referências a versões (v1.6.0→v1.7.0) tornam-se impossíveis de validar.

**Solução necessária:**
- Batch Plan é **histórico** (então remover sua exigência de ARs/matrizes).  
- Remover referências normativas (PASS/AC) a ele em `AR_BACKLOG_TRAINING.md` e `TEST_MATRIX_TRAINING.md`.

No _INDEX.md:
TRAINING_BATCH_PLAN_v1.md
deve aparecer apenas em:
ARQUIVOS HISTÓRICOS / FORA DA CADEIA ATIVA
e remover qualquer menção obrigatória a ele em:
AR_BACKLOG_TRAINING.md
TEST_MATRIX_TRAINING.md
Regra correta
Backlog governa execução
Batch plan é ferramenta auxiliar
---

### CRIT-004 — Datas futuras em changelog e “Última revisão”
**Onde aparece:**
- `TEST_MATRIX_TRAINING.md`: incluía changelog datado no futuro.
- `AR_BACKLOG_TRAINING.md`: incluía “Última revisão” e changelog datados no futuro.

**Problema:**
- Hoje é **2026-03-06** → entradas futuras quebram rastreabilidade e confiança (“o que foi realmente revisado?”).

**Solução necessária:**
- Converter entradas futuras em seção explícita **PLANEJADO** (sem promover versão/status).  
- Ou corrigir as datas para o dia real em que a mudança ocorreu.
- Regra: changelog só contém eventos **ocorridos**; “planejado” fica separado e não altera `Versão`/`Última revisão`.

**Status atual:** corrigido para não haver datas no futuro.

---

### CRIT-005 — Contradição normativa: default `visibility_mode` (ORG) na DEC do ROADMAP
**Onde aparece (contradição):**
- `TRAINING_ROADMAP.md` (DEC-TRAIN-EXB-001B): “Default … `org_wide`”.
- `INVARIANTS_TRAINING.md` (INV-TRAIN-060 + INV-TRAIN-EXB-ACL-001): default `restricted`.
- `TRAINING_USER_FLOWS.md` (FLOW-TRAIN-009): default `restricted`.
- `TRAINING_FRONT_BACK_CONTRACT.md` (§3.5 defaults): default `restricted`.
- `AR_BACKLOG_TRAINING.md` (AR-TRAIN-011): migration default `restricted`.

**Impacto spec-driven:**
- RBAC/privacidade e catálogo de exercícios: default errado muda exposição de dados entre treinadores (vazamento).

**Solução necessária:**
- Atualizar `TRAINING_ROADMAP.md` para registrar a **emenda**: DEC original (2026-02-25) → default alterado para `restricted` por decisão humana (referência cruzada a INV-TRAIN-060 / emenda v1.3.0).  
- Alternativamente, remover “Texto normativo final” de dentro do Roadmap e tratá-lo como histórico (Roadmap não deve carregar regra normativa que já mudou).

---

### CRIT-006 — Status “DRAFT” no documento que o índice chama de autoridade principal
**Onde aparece:**
- `_INDEX.md`: “INVARIANTS_TRAINING.md … Fonte normativa principal.”
- `INVARIANTS_TRAINING.md`: `Status: DRAFT`.

**Impacto spec-driven:**
- Incerteza operacional: “pode mudar a qualquer momento” vs “é a lei do módulo”.

**Solução necessária:**
- Definir regra objetiva para `Status` dos SSOTs:
  - `ATIVO` quando DONE atingido e invariantes estão seladas,
  - `DRAFT` apenas quando houver gaps críticos sem decisão.
- Ajustar `INVARIANTS_TRAINING.md` para refletir o status real do módulo (se DONE é verdadeiro).

---

### CRIT-007 — “GAP” dentro de invariantes marcadas como IMPLEMENTADO (drift interno)
**Onde aparece:**
- Diversas invariantes (ex.: INV-TRAIN-047..053, INV-TRAIN-EXB-ACL-001..007, INV-TRAIN-079..081) mantêm `evidence: - GAP: ...` apesar de:
  - `status: IMPLEMENTADO`
  - `note: Promovido por Kanban+evidencia ...`

**Impacto spec-driven:**
- Agentes e humanos podem abrir ARs desnecessárias (“materializar constraint”) mesmo já estando implementado/selado.
- Ruído de governança: “IMPLEMENTADO” deixa de ser confiável.

**Solução necessária:**
- Para qualquer item `status: IMPLEMENTADO`, o bloco `evidence:` deve conter **somente** evidências positivas verificáveis (paths reais + logs/AR selada), e o `GAP:` deve ser removido ou movido para `history:`/`note:` com data.  
- Regra simples: `GAP:` só é permitido quando `status ∈ {GAP, PARCIAL, DIVERGENTE_DO_SSOT}`.

---

### CRIT-008 — SPEC_VERSIONING exige baseline, mas baseline não existe
**Onde aparece:**
- `_INDEX.md` e `TRAINING_FRONT_BACK_CONTRACT.md` definem `SPEC_VERSIONING` e exigem uma “spec anterior aceita” (baseline).

**Status atual:**
- Baseline criado em `contracts/openapi/baseline/openapi_baseline.json`.

**Impacto spec-driven:**
- `CONTRACT_DIFF_GATE` torna-se “paper gate”: regra existe, mas é inexequível; breaking changes podem passar sem detecção.

**Solução necessária:**
- Documentar “como promover baseline” (quem, quando, comando) e integrar no protocolo do `_INDEX.md`.
Criar:
contracts/openapi/baseline/openapi_baseline.json
Regra
baseline atualizado após TRUTH_BE PASS
Fluxo
spec nova
↓
lint
↓
diff vs baseline
↓
test
↓
promote → baseline

---

### CRIT-009 — Duplicidade de “SSOT técnico” para OpenAPI/Schema
**Onde aparece:**
- Alguns SSOTs apontam `Hb Track - Backend/docs/ssot/*`, outros falam `docs/ssot/*`.
- Ambos existem com conteúdo igual **hoje**, porém sem declaração formal de canonicidade.

**Impacto spec-driven:**
- Alto risco de drift silencioso (um arquivo muda, o outro fica desatualizado e ainda parece “SSOT”).

**Solução necessária:**
O `scripts/ssot/gen_docs_ssot.py` gera o `openapi.json` em  dois lugares (primary + cópia):
Primary: `Hb Track - Backend/docs/ssot/openapi.json`
Cópia (repo-level): `openapi.json`
Isso vem das constantes no script:
OUTPUT_DIR= BACKEND_ROOT / "docs" / "ssot" # → path canônico: Hb Track - Backend/docs/ssot/
REPO_OUTPUT_DIR = REPO_ROOT / "docs" / "ssot" # → docs/ssot/
- Atualizar `_INDEX.md`/`TRAINING_FRONT_BACK_CONTRACT.md`/`TEST_MATRIX_TRAINING.md` para apontar para o mesmo path canônico.

---

### MAJOR-001 — Problemas de formatação que quebram leitura automática/visual
**Onde aparece:**
- `_INDEX.md` tem bullets concatenados e com `\` (ex.: seção “ARQUIVOS DERIVADOS” e “ARQUIVOS HISTÓRICOS / FORA DA CADEIA ATIVA”).

**Impacto:**
- Perde clareza e pode quebrar parsing/linters de markdown, além de confundir humanos.

**Solução necessária:**
Rodar: markdownlint ou prettier no  `_INDEX.md.`

---

### MAJOR-002 — Glossário existe, mas está fora da cadeia de autoridade
**Onde aparece:**
- `TRAINING_CLOSSARY.yaml` define vocabulário controlado (“anti-alucinação”), mas `_INDEX.md` não o inclui no mapa de autoridade.

**Impacto:**
- Termos/enums podem divergir entre SSOTs sem mecanismo de contenção; agentes podem “inventar” termos apesar do arquivo existir.

**Solução necessária:**
- Incluir o glossário no `_INDEX.md` como componente do SSOT (ou declarar explicitamente como “apoio não normativo”).  
- Definir gatilho: mudanças em enums/termos do contrato exigem revisão do glossário 

---

## ATT-001 - ANALISAR SE VALE A PENA IMPLEMENTAR AS SUGESTÕES ABAIXO ## 

1) Acoplamento excessivo do módulo TRAINING ao próprio contrato gerado**
Em escala, isso aparece assim:
```text
OpenAPI vira centro de tudo
→ backend muda
→ client FE muda
→ flows mudam
→ screens mudam
→ invariants começam a refletir contrato
→ qualquer ajuste pequeno explode em vários SSOTs
```
No começo isso parece organização.
Quando o sistema cresce, vira **acoplamento estrutural**.
---
# O nome real do problema
## **Contract Gravity**

O contrato começa a “puxar” regras que não deveriam morar nele.

Isso acontece quando:

* invariantes começam a ser escritas para servir o payload
* flows começam a refletir endpoint
* screens começam a refletir schema
* frontend fica dependente demais do client gerado bruto
* qualquer mudança pequena no OpenAPI gera cascata documental e técnica

No seu módulo, o risco é real porque você já consolidou:

* OpenAPI como autoridade técnica de integração; 
* `src/api/generated/*` como consumo canônico do FE; 
* `_INDEX` e `TEST_MATRIX` como pipeline spec-driven central;

Isso está certo.
O problema aparece quando o contrato deixa de ser **ponte** e vira **modelo de domínio por acidente**.

---

# Como esse problema aparece na prática

## 1) Mudança pequena vira refactor sistêmico

Exemplo:

* você muda um enum
* muda `openapi.json`
* roda diff
* regenera client
* quebra telas
* quebra adapter
* muda flow
* muda screen
* talvez muda invariante

Ou seja:

```text
mudança contratual pequena
≠
impacto pequeno
```

Em escala, isso desacelera o time.

---

## 2) O frontend fica “refém” do client gerado bruto

Se o FE consumir diretamente tudo de `src/api/generated/*`, sem uma camada de composição bem definida, qualquer detalhe do contrato vaza para a UI.

Resultado:

* telas ficam frágeis
* rename simples gera refactor amplo
* UX fica moldada pelo schema, não pelo produto

---

## 3) INVARIANTS, FLOWS e SCREENS podem começar a derivar do OpenAPI

Você já percebeu esse risco quando discutimos que esses documentos **não podem redefinir contrato**.

Se isso não for policiado, o sistema degrada para:

```text
OpenAPI manda em tudo
```

quando o correto é:

```text
Domínio manda
→ backend materializa
→ OpenAPI publica
→ FE consome
```

---

* O módulo fica bom isoladamente, mas ruim para escalar para outros módulos

Hoje isso funciona no TRAINING porque você está olhando tudo com muita atenção.

Quando esse padrão for para:

* TEAMS
* GAMES
* COMPETITIONS
* SCOUT

o risco é surgir:

* 4 contratos muito fortes
* 4 generated clients
* 4 conjuntos de flows/screens/invariants
* e sem uma camada comum de política de evolução

Aí aparece o problema clássico:

## **fragmentação de governança por módulo**

---

# O que está faltando para evitar isso

## Falta uma camada explícita de **anti-corruption / composition layer**

JÁ EXISTE tem a distinção:

* FE Generated
* FE Manual/Adapter

Mas ela ainda está definida mais como “subordinação” do que como **barreira arquitetural**.

Essa camada precisa ter missão explícita:

### o client gerado:

* representa o contrato bruto

### a camada adapter/composition:

* traduz contrato bruto em objetos/ações úteis para a UI
* protege a tela de churn contratual pequeno
* concentra compatibilidades temporárias
* impede que a UI fique acoplada demais ao schema

Sem isso, o generated client vira uma dependência estrutural da interface.

---

# Em uma frase

O problema sério que ainda existe é:

## **o risco de o contrato OpenAPI deixar de ser ponte e virar o centro acoplado do domínio, da UI e da governança**

Isso normalmente só explode quando:

* há mais módulos,
* mais telas,
* mais consumidores,
* mais mudanças pequenas em contrato.

---

# Como neutralizar esse problema

Você precisa formalizar uma regra arquitetural assim:

## **Generated Client Boundary Rule**

* `src/api/generated/*` é contrato bruto e derivado
* telas não consomem diretamente tipos brutos quando isso acoplar UX ao schema
* `src/lib/api/*` (ou camada equivalente) não redefine contrato, mas **compõe, adapta e estabiliza consumo**
* invariantes, flows e screens continuam descrevendo domínio/UX, não detalhes do schema

Ou seja:

```text
Domínio
→ Contrato
→ Client gerado
→ Adapter/composition
→ UI
```

e não:

```text
Domínio
→ Contrato
→ UI direta
```

---

# O que isso evita

* refactor em cascata
* churn de tela por mudança pequena de contrato
* duplicação de regra entre OpenAPI e UX
* dependência excessiva do schema bruto
* explosão de complexidade ao expandir para outros módulos

---

# Conclusão

Seu fluxo atual já está muito bom para:

* um módulo,
* um contrato,
* um generated client,
* um pipeline controlado.

O problema que aparece quando escala é:

## **falta de uma barreira arquitetural forte entre contrato gerado e aplicação real do frontend**
**`GENERATED_CLIENT_BOUNDARY_RULE (NORMATIVO)`**

```md
## GENERATED_CLIENT_BOUNDARY_RULE (NORMATIVO)

### Objetivo
Evitar acoplamento excessivo entre o contrato OpenAPI gerado e a aplicação real do Frontend do módulo TRAINING.

### Problema que esta regra resolve
O cliente gerado em `Hb Track - Frontend/src/api/generated/*` é necessário para materializar o contrato FE↔BE, mas ele NÃO deve se tornar a camada de domínio nem a camada de UX do sistema.

Sem esta barreira, pequenas mudanças no contrato OpenAPI podem provocar refactors em cascata em:
- telas,
- fluxos,
- adapters,
- regras de UI,
- e documentação semântica do módulo.

### Regra central
O cliente gerado é **contrato bruto derivado**.  
Ele NÃO é:
- modelo de domínio do Frontend,
- especificação de UX,
- fonte normativa de regras de negócio,
- nem autorização para acoplar a tela diretamente ao schema OpenAPI.

### Camadas obrigatórias do Frontend

#### 1. FE Generated
Path canônico:
- `Hb Track - Frontend/src/api/generated/*`

Função:
- materializar o contrato OpenAPI
- expor endpoints, operationIds, tipos e schemas gerados
- refletir fielmente o backend publicado

Restrições:
- é artefato derivado
- não pode ser editado manualmente
- não deve conter regra de domínio nem regra de UX

#### 2. FE Manual / Adapter / Composition Layer
Path canônico:
- `Hb Track - Frontend/src/lib/api/*` (ou camada equivalente do repositório)

Função:
- compor chamadas ao cliente gerado
- concentrar autenticação, retry, headers, config e orquestração de consumo
- estabilizar o consumo do contrato para a UI
- absorver compatibilidades transitórias permitidas pelo contrato
- transformar o contrato bruto em interfaces de uso adequadas para componentes e telas

Restrições:
- não pode redefinir contrato OpenAPI
- não pode alterar payloads, enums, operationIds, status codes ou tipos já materializados
- não pode se tornar fonte paralela de contrato
- não pode inventar schema alternativo incompatível com o contrato vigente

#### 3. UI / Telas / Componentes
Função:
- implementar comportamento visual e experiência do usuário
- consumir a camada adapter/composition
- refletir fluxos e screens specs do módulo

Restrições:
- telas não devem depender diretamente do contrato bruto quando isso acoplar a UX ao schema OpenAPI
- telas não definem contrato técnico
- telas não são autorizadas a reimplementar payloads do backend

### Precedência arquitetural no Frontend
Para o consumo do contrato no Frontend, a ordem correta é:

1. OpenAPI materializado
2. FE Generated (`src/api/generated/*`)
3. FE Manual / Adapter / Composition Layer
4. UI / Screens / Components

### Regra de desenho
A arquitetura correta do módulo TRAINING no Frontend é:

Domínio / Backend  
→ OpenAPI  
→ Cliente gerado  
→ Adapter / Composition Layer  
→ UI

É proibido convergir para:

Domínio / Backend  
→ OpenAPI  
→ UI direta

### Relação com os SSOTs do módulo
- `TRAINING_FRONT_BACK_CONTRACT.md` define o contrato FE↔BE
- `INVARIANTS_TRAINING.md` define regras normativas de domínio
- `TRAINING_USER_FLOWS.md` define fluxos semânticos
- `TRAINING_SCREENS_SPEC.md` define UX e estados de tela
- este bloco define a barreira arquitetural entre contrato gerado e aplicação FE real

### FAIL se
- componentes/telas consumirem diretamente o cliente gerado de forma que a UX fique acoplada ao schema bruto
- `src/lib/api/*` redefinir contrato já tipado no OpenAPI
- mudanças pequenas no contrato exigirem refactor em cascata por ausência de camada de adaptação
- o cliente gerado for usado como modelo de domínio do Frontend

### Efeito no fluxo spec-driven
Quando `GENERATED_CLIENT_SYNC` ocorrer, o agente deve:

1. regenerar o cliente FE
2. manter o cliente gerado como contrato bruto
3. ajustar a camada adapter/composition quando necessário
4. preservar a estabilidade das telas sempre que possível
5. evitar vazamento do schema OpenAPI bruto para a UX

### Regra final
O cliente gerado é obrigatório, mas a UI não pode ser refém dele.
```

---

# PATCH — `TRAINING_FRONT_BACK_CONTRACT.md`

Inserir **logo após a seção `CONTRACT_SYNC_FE (normativo)`**.

```md
### GENERATED_CLIENT_BOUNDARY_RULE (referência normativa)

O consumo do cliente gerado no Frontend deve obedecer à regra arquitetural definida em:

_INDEX.md → GENERATED_CLIENT_BOUNDARY_RULE (NORMATIVO)

Resumo operacional:

1. O cliente gerado em  
   `Hb Track - Frontend/src/api/generated/*`  
   representa **o contrato OpenAPI bruto**.

2. Ele **não é** modelo de domínio do Frontend nem especificação de UX.

3. O consumo correto do contrato no Frontend deve respeitar as camadas:

   OpenAPI  
   → FE Generated (`src/api/generated/*`)  
   → FE Manual / Adapter / Composition (`src/lib/api/*`)  
   → UI / Screens / Components

4. Telas e componentes **não devem depender diretamente do contrato bruto**
quando isso acoplar a UX ao schema OpenAPI.

5. A camada `src/lib/api/*` pode:
   - compor chamadas
   - estabilizar consumo
   - adaptar respostas

   mas **não pode redefinir contrato OpenAPI**.

Regra de precedência:

OpenAPI contract  
> FE Generated client  
> FE Adapter / Composition layer  
> UI / Screens

FAIL se:

- telas consumirem diretamente o cliente gerado de forma estrutural
- a camada adapter redefinir contrato já tipado no OpenAPI
- o cliente gerado for tratado como modelo de domínio da UI
```

---

# Resultado arquitetural final

Depois desse patch, seu sistema fica protegido contra o problema de **Contract Gravity** que expliquei antes.

Arquitetura final:

```
DOMÍNIO
   ↓
Backend (FastAPI + Pydantic)
   ↓
OpenAPI (contrato)
   ↓
Cliente gerado
   ↓
Adapter / Composition Layer
   ↓
UI
```

E **nenhuma tela depende diretamente do schema bruto**.

---

# fluxo agora está completo

Com os últimos patches, o pipeline do módulo TRAINING ficou:

```
SPEC_VERSIONING
      ↓
OPENAPI_SPEC_QUALITY (Redocly)
      ↓
CONTRACT_DIFF_GATE (oasdiff)
      ↓
BACKEND CONTRACT ALIGNMENT
      ↓
GENERATED_CLIENT_SYNC (OpenAPI Generator)
      ↓
RUNTIME CONTRACT VALIDATION (Schemathesis)
      ↓
TRUTH_BE (pytest real + postgres real)
      ↓
TRUTH_FE (Playwright — quando existir)
```

E agora com:

```
GENERATED_CLIENT_BOUNDARY_RULE
```

evita o problema que aparece **quando o sistema cresce**.

---

2) **fragmentação de contrato por módulo sem governança transversal**

Hoje o seu fluxo do TRAINING está ficando muito forte.
O problema é que, quando você repetir o mesmo modelo em:

* TEAMS
* GAMES
* COMPETITIONS
* SCOUT
* ANALYTICS

pode acabar com vários “micro-SSOTs de módulo” muito bem organizados localmente, mas **sem uma camada comum de governança entre contratos**.

Em escala, isso aparece assim:

```text
cada módulo evolui bem sozinho
↓
mas os contratos começam a divergir entre si
↓
tipos, enums, ids, paginação, filtros, erros e headers deixam de ser homogêneos
↓
o sistema inteiro vira coerente por módulo, mas inconsistente como plataforma
```

Esse é o risco mais sério que costuma surgir depois que o fluxo spec-driven local já está bom.

---

# Como isso se manifesta na prática

## 1) Enums e tipos canônicos começam a divergir

Exemplo:

* TRAINING usa `restricted`
* outro módulo usa `private`
* outro usa `team_only`

Todos significam quase a mesma coisa, mas com nomes diferentes.

Resultado:

* clients gerados diferentes
* adapters mais complexos
* lógica duplicada
* mais chance de bug de integração

---

## 2) Padrões de API começam a divergir entre módulos

Sem governança transversal, um módulo pode usar:

```text
GET /training-sessions
```

e outro:

```text
GET /teams/list
```

Um usa paginação com:

```text
page / page_size
```

outro usa:

```text
offset / limit
```

Um responde erro com:

```text
detail
```

outro com:

```text
message
```

O resultado é:

## **OpenAPI válido por módulo, plataforma inconsistente no todo**

---

## 3) Generated clients ficam corretos, mas heterogêneos

Cada módulo gera seu client corretamente.

Mas o frontend passa a lidar com:

* convenções diferentes
* payloads diferentes
* erros diferentes
* nomenclatura diferente

Então você troca o problema de “sem contrato” por outro:

## **contratos demais sem padrão comum**

---

## 4) Regras duplicadas de domínio começam a aparecer em vários contratos

Exemplo:

* UUID de `team_id`
* filtros por organização
* regras RBAC
* paginação
* ordenação
* metadados de auditoria

Se cada módulo documenta isso do seu jeito, o sistema cresce com:

* duplicação semântica
* pequenas variações
* manutenção cara

---

# Em uma frase

O risco que ainda existe é:

## **você pode construir um excelente spec-driven por módulo e, ao mesmo tempo, perder coerência da plataforma HB Track como sistema único**

---

# O nome arquitetural desse problema

## **Module Contract Drift**

Ou, em termos práticos:

```text
contratos locais corretos
≠
arquitetura global coerente
```

---

# Por que isso é perigoso

Porque ele não aparece no começo.

No começo tudo parece saudável:

* TRAINING bem documentado
* contrato bem gerado
* FE sincronizado
* testes fortes

O problema aparece quando você tem:

* 5+ módulos
* 30–40+ endpoints
* vários generated clients
* features transversais
* integrações cruzadas

Aí você percebe que faltava uma camada acima dos módulos.

---

# O que está faltando para neutralizar isso

Você precisa criar uma camada **global de governança contratual**, acima dos módulos.

Algo como:

## **PLATFORM API GOVERNANCE RULES**

Essa camada deveria definir, para todos os módulos:

* convenção de path
* convenção de `operationId`
* convenção de paginação
* convenção de erro
* convenção de filtros
* convenção de enums compartilhados
* convenção de ids UUID
* convenção de metadados (`request_id`, `trace_id`, `correlation_id`)
* convenção de depreciação/versionamento
* convenção de segurança e headers

Ou seja:

```text
módulos mantêm autonomia funcional
mas não inventam protocolo próprio
```

---

# Como isso se encaixa no que você já tem

Hoje você já tem um bom fluxo local no TRAINING:

```text
_INDEX
TEST_MATRIX
CONTRACT
INVARIANTS
FLOWS
SCREENS
```

O próximo nível é:

```text
PLATFORM API GOVERNANCE
↓
MÓDULO TRAINING
MÓDULO TEAMS
MÓDULO GAMES
...
```

---

# O que eu recomendaria formalizar

Não precisa criar isso agora como documento gigante.
Mas deveria existir pelo menos um SSOT global curto com:

## **HB_TRACK_API_PLATFORM_RULES.md**

com 10–15 regras fixas, por exemplo:

1. todos os IDs são UUID
2. todos os endpoints REST seguem convenção X
3. toda lista paginada responde com estrutura Y
4. todo erro segue shape Z
5. toda operação autenticada responde com headers padrão
6. enums compartilhados não podem ser redefinidos por módulo
7. breaking changes seguem política única de depreciação

---

# Conclusão

O risco arquitetural que ainda existe é:

## **você pode ter documentação excelente no TRAINING e mesmo assim construir uma plataforma inconsistente entre módulos**

Esse é o próximo risco real de escala.

O fluxo local está forte.
O que falta, para o HB Track crescer sem fragmentar, é **governança de contrato no nível da plataforma**, não só no nível do módulo.

---

## 2) Solução necessária (estado TO-BE) — para “documentação perfeita”

### 2.1 Decisões finais (para remover ambiguidade)

As decisões abaixo são **normativas para a documentação** (TO-BE) e devem ser aplicadas como “fonte de verdade” ao corrigir os SSOTs:

**DEC-DOCS-001 — DONE_GATE é evidência (derivado), não SSOT**
- `DONE_GATE_TRAINING.md` (em `_reports/training/`) é **relatório derivado** da execução do que está definido em `TEST_MATRIX_TRAINING.md` (e/ou TRUTH).
- É **proibido** usar DONE_GATE como referência normativa (RH-06/RH-08, regras, critérios) dentro dos SSOTs.
- Todo trecho que hoje aponta “ver DONE_GATE…” deve apontar para:
  - a regra em `TEST_MATRIX_TRAINING.md` (ou SSOT normativo equivalente), e
  - a evidência em `_reports/training/DONE_GATE_TRAINING.md` (quando necessário).

**DEC-DOCS-002 — DONE_GATE não é versionado**
- Remover `DONE_GATE_TRAINING_v*.md` do modelo mental/documental.
- A execução sempre sobrescreve `_reports/training/DONE_GATE_TRAINING.md` (relatório mais recente).
- Se for necessário histórico: manter histórico **por timestamp** em `_reports/training/archive/` (opcional), nunca em `docs/hbtrack/modulos/treinos/`.

**DEC-DOCS-003 — TRAINING_BATCH_PLAN_v1.md é histórico/out-of-chain**
- O módulo TRAINING não depende de Batch Plan para governança vigente.
- Referências a Batch Plan em critérios PASS/AC/“sync obrigatório” devem ser removidas de `AR_BACKLOG_TRAINING.md` e `TEST_MATRIX_TRAINING.md`.
- No `_INDEX.md` ele pode existir (se existir) apenas como “histórico”; se não existir, o índice não deve exigir nem mencionar versões (v1.6.0→v1.7.0 etc.).

**DEC-DOCS-004 — SSOT técnico (OpenAPI/Schema) tem canonicidade explícita**
- **Canônico técnico:** `Hb Track - Backend/docs/ssot/*`.
- **Espelho derivado (repo-level):** `docs/ssot/*` é **cópia gerada** por `scripts/ssot/gen_docs_ssot.py` (não é SSOT primário).
- Todo SSOT do módulo deve apontar para o path canônico (e opcionalmente mencionar o espelho como conveniência).

**DEC-DOCS-005 — SPEC_VERSIONING: baseline obrigatório e operacional**
- Baseline padrão: `contracts/openapi/baseline/openapi_baseline.json`.
- Promoção do baseline acontece **somente após** `TRUTH_BE` PASS (e gates de spec/diff).
- `CONTRACT_DIFF_GATE` deve sempre comparar:
  - baseline atual (`openapi_baseline.json`)
  - spec nova gerada (`Hb Track - Backend/docs/ssot/openapi.json`)

**DEC-DOCS-006 — ROADMAP não pode carregar norma que conflita com SSOT**
- `TRAINING_ROADMAP.md` é não-bloqueante e pode registrar decisões/histórico, mas:
  - se houver emenda posterior por `INVARIANTS/CONTRACT/FLOWS`, o Roadmap deve registrar **AMENDMENT** (data + autoridade), ou
  - remover “Texto normativo final” que ficou desatualizado.

---

### 2.2 Plano de correção (sequência recomendada)

#### Fase 1 — Remover quebras de referência e consolidar SSOT vs evidência (alta prioridade)
1. **Eliminar DONE_GATE como SSOT**
   - Atualizar em `INVARIANTS_TRAINING.md`: substituir “Ver RH-06 em DONE_GATE…” por referência a `TEST_MATRIX_TRAINING.md` (seção que define RH-06) + evidência opcional em `_reports/training/DONE_GATE_TRAINING.md`.
   - Atualizar em `AR_BACKLOG_TRAINING.md` e `TEST_MATRIX_TRAINING.md`: remover links e requisitos de arquivos inexistentes (`DONE_GATE_TRAINING.md` no módulo, `DONE_GATE_TRAINING_v3.md`).
2. **Eliminar referências normativas ao Batch Plan**
   - Atualizar `AR_BACKLOG_TRAINING.md` e `TEST_MATRIX_TRAINING.md` para remover `TRAINING_BATCH_PLAN_v1.md` de critérios/entregáveis/sync obrigatório.
   - Atualizar `_INDEX.md` para manter Batch Plan somente como “histórico” (se aplicável), sem exigir versão/arquivo.
3. **Atualizar o Mapa de Autoridade**
   - Em `_INDEX.md`, adicionar uma tabela curta “SSOT vs DERIVADO” contendo, no mínimo:
     - SSOT: `_INDEX`, `INVARIANTS`, `CONTRACT`, `FLOWS`, `SCREENS`, `TEST_MATRIX`, `AR_BACKLOG`, `ROADMAP`
     - Derivado: `Hb Track - Backend/docs/ssot/*`, `docs/ssot/*`, `Hb Track - Frontend/src/api/generated/*`, `docs/hbtrack/evidence/*`, `_reports/*`

#### Fase 2 — Restaurar auditabilidade (datas futuras e versões)
4. **Remover datas futuras**
   - Em `AR_BACKLOG_TRAINING.md` e `TEST_MATRIX_TRAINING.md`: mover entradas com data futura para seção `PLANEJADO` (sem bump de versão) **ou** corrigir as datas para a data real.
   - Regra: `Última revisão` não pode estar no futuro.
5. **Reconciliar status/versionamento do módulo**
   - Em `_INDEX.md`: atualizar contagem/intervalo de ARs e “última AR selada” para refletir o estado real documentado em `AR_BACKLOG_TRAINING.md`/`TEST_MATRIX_TRAINING.md`.
   - Em `INVARIANTS_TRAINING.md`: alinhar `Status:` com o estado real do módulo (se DONE é verdadeiro, evitar `DRAFT`).

#### Fase 3 — Eliminar contradições normativas (domínio/contrato/roadmap)
6. **Consertar DEC-TRAIN-EXB-001B no Roadmap**
   - Registrar emenda explícita: default `visibility_mode` passou a `restricted` (referência cruzada INV-TRAIN-060/EXB-ACL-001).
   - Alternativa: remover o “Default … org_wide” do Roadmap e deixar a regra apenas nos SSOTs normativos.

#### Fase 4 — Limpar drifts internos (INVARIANTS status/evidence)
7. **Normalizar `evidence:` em invariantes**
   - Para todo item `status: IMPLEMENTADO`, remover `GAP:` do `evidence:` e substituí-lo por evidência positiva (paths + logs/AR selada).
   - Regra: `GAP:` só pode existir quando `status ∈ {GAP, PARCIAL, DIVERGENTE_DO_SSOT}`.
8. **Garantir consistência “evidência antes de implementado” (MCP.md)**
   - Aplicar MP-PRINC-005: nada “IMPLEMENTADO” sem evidência objetiva.

#### Fase 5 — Tornar `SPEC_VERSIONING` e `CONTRACT_DIFF_GATE` executáveis
9. **Criar baseline OpenAPI**
   - Adicionar `contracts/openapi/baseline/openapi_baseline.json`.
10. **Documentar a promoção do baseline**
   - Atualizar `_INDEX.md` e `TRAINING_FRONT_BACK_CONTRACT.md` com o fluxo completo:
     - gerar OpenAPI (`scripts/ssot/gen_docs_ssot.py`)
     - lint (`OPENAPI_SPEC_QUALITY`)
     - diff (`CONTRACT_DIFF_GATE`)
     - regenerar FE (`GENERATED_CLIENT_SYNC`)
     - TRUTH_BE
     - promover baseline

#### Fase 6 — Endurecer o pipeline documental (qualidade recorrente)
11. **Format/lint documental**
   - Corrigir formatação de `_INDEX.md` (bullets concatenados/`\`).
   - Adotar um comando padrão para markdownlint/prettier (se existir no repo) como gate local.
12. **Glossário**
   - Incluir `TRAINING_CLOSSARY.yaml` no `_INDEX.md` (SSOT auxiliar) e definir gatilho de revisão quando enums/termos mudarem no contrato.

---

### 2.3 Itens opcionais (DEVEM SER IMPLEMENTADOS)

**OPT-001 — GENERATED_CLIENT_BOUNDARY_RULE (anti “Contract Gravity”)**
- Se aprovado, formalizar no `_INDEX.md` e/ou `TRAINING_FRONT_BACK_CONTRACT.md` uma regra explícita de barreira:
  - `src/api/generated/*` = contrato bruto derivado,
  - `src/lib/api/*` = composição/adaptação/estabilização,
  - telas não devem acoplar UX ao schema bruto quando isso gerar churn.

**OPT-002 — Governança transversal (plataforma)**
- O padrão spec-driven for replicado em múltiplos módulos, criar um SSOT global curto:
  - `HB_TRACK_API_PLATFORM_RULES.md` (paths, paginação, erros, enums compartilhados, depreciação/versionamento).

---

## 3) Checklist de aceitação (quando considerar “DOCS PERFEITAS”)

### 3.1 Checks objetivos (rodar/validar)
1. **Sem links quebrados no módulo**
   - PASS se não houver referência a arquivo inexistente dentro de `docs/hbtrack/modulos/treinos/*.md`.
   - Comando sugerido (exemplo):
     - `python3 - <<'PY' ... PY` (script que varre links relativos) **ou** check equivalente automatizado do repo.
2. **DONE_GATE não aparece como SSOT**
   - PASS se não existir referência a `docs/hbtrack/modulos/treinos/DONE_GATE_TRAINING*.md` nem a `DONE_GATE_TRAINING_v3.md` como artefato obrigatório/SSOT.
   - PASS se DONE_GATE for sempre citado como `_reports/training/DONE_GATE_TRAINING.md` (evidência).
   - Comando sugerido: `rg -n \"DONE_GATE_TRAINING(_v\\d+)?\\.md\" docs/hbtrack/modulos/treinos`
3. **Batch Plan não é exigência normativa**
   - PASS se `TRAINING_BATCH_PLAN_v1.md` não aparecer em critérios PASS/AC/“sync obrigatório” de `AR_BACKLOG_TRAINING.md` e `TEST_MATRIX_TRAINING.md`.
   - Comando sugerido: `rg -n \"TRAINING_BATCH_PLAN_v1\\.md\" docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`
4. **Sem datas futuras**
   - PASS se nenhum SSOT do módulo tiver `Última revisão`/changelog com data posterior a 2026-03-06 (enquanto essa for a data corrente do repositório).
5. **Sem contradição normativa do default `visibility_mode`**
   - PASS se `TRAINING_ROADMAP.md` não contradizer `INVARIANTS/CONTRACT/FLOWS` sobre default `restricted` (ou se registrar AMENDMENT explícito).
6. **INVARIANTS consistente**
   - PASS se não houver `status: IMPLEMENTADO` com `evidence:` contendo `GAP:`.
7. **SPEC_VERSIONING executável**
   - PASS se existir `contracts/openapi/baseline/openapi_baseline.json` e o protocolo do `_INDEX.md` instruir claramente como atualizar/promover.
8. **Canonicidade OpenAPI/Schema explícita**
   - PASS se todos os SSOTs do módulo apontarem para `Hb Track - Backend/docs/ssot/*` como canônico e tratarem `docs/ssot/*` como espelho derivado (gerado).
9. **Formatação do índice**
   - PASS se `_INDEX.md` não tiver bullets concatenados/`\` soltos e permanecer legível/parseável.

### 3.2 Resultado final esperado (humano)
- Um leitor novo consegue responder, sem inferência:
  - “Qual é o SSOT do quê?”
  - “O que é derivado e como regenerar?”
  - “Como detectar breaking change?”
  - “Como provar TRUTH (e onde está a evidência)?”

---

## 4) Observação de governança (para evitar regressão)

### 4.1 Regras mínimas (adicionar ao `_INDEX.md` como normativo do módulo)
1. **POLICY-DOCS-001 — Separação SSOT vs DERIVADO**
   - Todo arquivo citado no módulo deve estar classificado como `SSOT` ou `DERIVADO` (com path fixo).
2. **POLICY-DOCS-002 — Changelog sem futuro**
   - Changelog e `Última revisão` só registram fatos ocorridos; “planejado” fica em seção própria e não altera versão.
3. **POLICY-DOCS-003 — Consistência interna de status/evidence**
   - `IMPLEMENTADO` exige evidência positiva; `GAP:` não pode coexistir com `IMPLEMENTADO`.
4. **POLICY-DOCS-004 — Gates “paper” são proibidos**
   - Se o SSOT exige um gate (ex.: baseline para diff), o artefato e o comando devem existir e ser executáveis.

### 4.2 Integração com MCP (para agentes)
Mapear explicitamente estas correções aos princípios do `docs/hbtrack/modulos/MCP.md`:
- MP-PRINC-003 (separação descrição vs norma)
- MP-PRINC-005 (evidência antes de “implementado”)
- GATE-L4 (paridade contrato↔código)

### 4.3 Próximo passo recomendado (fora do escopo imediato)
Se o HB Track escalar para múltiplos módulos, formalizar governança transversal:
- criar `HB_TRACK_API_PLATFORM_RULES.md` (curto) para impedir “Module Contract Drift”.
