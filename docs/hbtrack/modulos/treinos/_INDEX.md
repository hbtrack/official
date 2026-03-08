# Módulo TRAINING — Índice de Autoridade SSOT

**Versão:** v1.8.0  
**Última revisão:** 2026-03-08  
**Tipo:** Navigation Index / Authority Map / Spec-Driven Change Protocol  
**Módulo:** TRAINING  
**Fase atual:** FASE_2 + FASE_3 REAL CONCLUÍDAS — `DONE_TRAINING_ATINGIDO = TRUE`

> Changelog v1.8.0 (2026-03-08) — Batch 35 Done Contract:
> - AR_265 (AR-TRAIN-081, G): `DONE_CONTRACT_TRAINING.md.md` registrado na cadeia canônica como camada de decisão de encerramento (DONE_TECNICO / DONE_SEMANTICO / DONE_PRODUTO).
> - Artefatos obrigatórios criados: `TRAINING_SCOPE_REGISTRY.yaml`, `TRAINING_STATE_MACHINE.yaml`, `TRAINING_PERF_LIMITS.json`, `traceability_training_core.csv` (skeleton).
> - ARs totais e última selagem atualizadas (até AR-TRAIN-086, Batch 35).

> Changelog v1.7.0 (2026-03-07) — Batch 34 sealed:
> - ARs totais e última selagem atualizadas (até AR-TRAIN-080, Batch 34).
> - AR_263 (AR-TRAIN-079, D/E): `trainingAlertsSuggestionsApi` singleton adicionado em `api-instance.ts`; TRAINING_FRONT_BACK_CONTRACT.md §5.10 CONTRACT-TRAIN-077..085 DIVERGENTE→IMPLEMENTADO VERIFICADO.
> - AR_264 (AR-TRAIN-080, G): sync documental pós-Batch 34 VERIFICADO.
> - FE_MIGRATION_COMPLETE = TRUE (100% endpoints canônicos; useSuggestions.ts deferred a CAP-001 — roteador inativo, não-canônico).

> Changelog v1.6.0 (2026-03-07) — Batch 33 sealed:
> - ARs totais e última selagem atualizadas (até AR-TRAIN-078, Batch 33).
> - AR_256..AR_260 (AR-TRAIN-072..076, D): FE migration completa para generated client VERIFICADO.
> - AR_261 (AR-TRAIN-077, B): BE fix exports.py 503→202 VERIFICADO.
> - AR_262 (AR-TRAIN-078, G): sync documental pós-Batch 33 VERIFICADO.
> - FE_MIGRATION_COMPLETE = TRUE (exceto useSuggestions.ts — DIVERGENTE_DO_SSOT pendente).

> Changelog v1.5.0 (2026-03-06) — Batch 32 sealed:
> - ARs totais e última selagem atualizadas (até AR-TRAIN-071, Batch 32).
> - AR_254 (AR-TRAIN-070, T): testes impl CONTRACT-031/032/037/038 VERIFICADO.
> - AR_255 (AR-TRAIN-071, G): sync documental pós-Batch 31+32 VERIFICADO.

> Changelog v1.4.1 (2026-03-06):
> - Corrigida formatação (removido fence acidental e bullets concatenados).
> - `TRAINING_CLOSSARY.yaml` adicionado ao Mapa de Autoridade (auxiliar anti-alucinação).
> - ARs totais e última selagem atualizadas (até AR-TRAIN-069).
> - Artefatos derivados e baseline (`contracts/openapi/baseline/openapi_baseline.json`) explicitados.

> Changelog v1.4.0 (2026-03-06):
> - Adicionada política `CONTRACT_DIFF_GATE`.
> - Formalizadas ferramentas oficiais do pipeline spec-driven: Redocly CLI, oasdiff, OpenAPI Generator, Schemathesis e Playwright (futuro TRUTH_FE).
> - Adicionadas regras `SPEC_VERSIONING`, `CI_PIPELINE` e `SPEC_FREEZE_RULE`.
> - Fluxo spec-driven consolidado: spec válida + spec compatível + client FE gerado + runtime validation + TRUTH.

> Changelog v1.3.0 (2026-03-06):
> - Adicionado fluxo canônico spec-driven do módulo TRAINING.
> - OpenAPI Generator formalizado como ponte técnica obrigatória FE↔BE.
> - `Hb Track - Frontend/src/api/generated/*` classificado como artefato derivado canônico.
> - `src/lib/api/*` rebaixado para adapter/manual layer subordinado ao cliente gerado.
> - Adicionada regra `CONTRACT_SYNC_FE` no protocolo de mudança.

> Este arquivo é a entrada canônica para navegar a documentação do módulo TRAINING.  
> Ele define:
> 1. qual arquivo responde por cada responsabilidade;
> 2. quem é autoridade em caso de conflito;
> 3. qual é o pipeline normativo de mudança no fluxo spec-driven do módulo.

---

## Mapa de Autoridade

### Cadeia normativa do módulo TRAINING
1. `INVARIANTS_TRAINING.md`
   - Define regras de domínio e enforcement. Fonte normativa principal.
2. `TRAINING_CLOSSARY.yaml`
   - Vocabulário controlado (anti-alucinação) para termos/enums/labels. **Auxiliar**: não redefine contrato nem substitui invariantes/SSOTs.
3. `TRAINING_FRONT_BACK_CONTRACT.md`
   - Define contratos FE↔BE, shapes normativos, operationIds, regras de paridade e sincronização FE gerada.
4. `TRAINING_USER_FLOWS.md`
   - Define a sequência operacional dos fluxos.
5. `TRAINING_SCREENS_SPEC.md`
   - Define comportamento de UI/UX e estados de tela.
6. `TEST_MATRIX_TRAINING.md`
   - **Autoridade operacional**: define o que conta como evidência válida, TRUTH_BE, TRUTH_FE_FUTURO, LEGACY_INVALID, API_SYNC_REQUIRED, GENERATED_CLIENT_SYNC e roteamento de impacto por mudança.
6b. `DONE_CONTRACT_TRAINING.md.md`
   - **Autoridade de encerramento**: define os gates `DONE_TECNICO`, `DONE_SEMANTICO` e `DONE_PRODUTO`. Governa a legitimidade de qualquer declaração de conclusão do módulo TRAINING. Camada superior de decisão — não substitui INVARIANTS, CONTRACT, FLOWS, SCREENS ou TEST_MATRIX. Atua como critério formal de aceitação de produto sobre os demais SSOTs.
7. `AR_BACKLOG_TRAINING.md`
   - Organiza execução por ARs/Batches.
8. `TRAINING_ROADMAP.md`
   - Define apenas evolução futura / pós-DONE. Nunca bloqueia PASS atual.

### Cadeia técnica de materialização
1. SSOT normativo (`INVARIANTS`, `CONTRACT`, `FLOWS`, `SCREENS`)
2. Backend real (`schema.sql`, models, services, routers, Pydantic/FastAPI)
3. `openapi.json` derivado do backend
4. OpenAPI Generator
5. `Hb Track - Frontend/src/api/generated/*`
6. Frontend real (telas/componentes/fluxos que consomem o cliente gerado)

### Regra de precedência em conflito
Ordem:
`DB > Services > OpenAPI > FE Generated > FE Manual/Adapter > PRD`

Interpretação:
- `src/api/generated/*` é subordinado ao `openapi.json`, mas é a forma canônica de consumo do contrato no FE.
- `src/lib/api/*` (quando existir) não define contrato; apenas adapta/compõe chamadas sobre o cliente gerado.

---

## POLÍTICA DE TESTES (NORMATIVO)

Autoridade:
- `TEST_MATRIX_TRAINING.md` é a autoridade operacional de testes: define TRUTH SUITE, NO_MOCKS_GLOBAL, validade de PASS, TRUTH_BE, TRUTH_FE_FUTURO, LEGACY_INVALID, API_SYNC_REQUIRED e GENERATED_CLIENT_SYNC.

Regra de conflito:
- Se qualquer arquivo, comentário, histórico ou prática sugerir mocks/stubs, prevalece `NO_MOCKS_GLOBAL`.
- Se qualquer arquivo, comentário, histórico ou prática sugerir consumo manual de contrato FE↔BE quando já houver contrato tipado no OpenAPI, prevalece `CONTRACT_SYNC_FE`.

Frase operacional:
- **Resultados PASS só são válidos se vierem da TRUTH SUITE (Postgres real hb_track + reset+migrations+seed) e respeitarem NO_MOCKS_GLOBAL. Qualquer PASS fora disso não conta como evidência.**

Status atual:
- `TRUTH_BE` = vigente e obrigatória
- `TRUTH_FE` = futuro (ainda não materializada)

Regra temporária de FE:
- Enquanto `TRUTH_FE` não existir, mudanças de UI/UX no TRAINING são validadas por:
  - `TRAINING_SCREENS_SPEC.md`
  - `TRAINING_USER_FLOWS.md`
  - contratos FE↔BE vigentes
  - regeneração obrigatória do cliente gerado quando o contrato mudar

---

## PROTOCOLO SPEC-DRIVEN (NORMATIVO)

### Objetivo
Garantir que qualquer mudança no módulo TRAINING seja implementada, sincronizada e validada de forma determinística, partindo do SSOT até o produto real.

### Regra central
O fluxo canônico do módulo TRAINING é:

1. SSOT normativo
2. Backend real
3. `openapi.json`
4. OpenAPI Generator
5. `Hb Track - Frontend/src/api/generated/*`
6. Frontend real
7. TRUTH_BE
8. (futuro) TRUTH_FE

### CONTRACT_SYNC_FE (obrigatório)
Sempre que houver mudança em:
- `CONTRACT-TRAIN-*`,
- path HTTP,
- `operationId`,
- request schema,
- response schema,
- enum canônico,
- tipo canônico (`uuid`, `datetime`, `date`, etc.),

o agente DEVE:

1. materializar a mudança no Backend real;
2. regenerar `Hb Track - Backend/docs/ssot/openapi.json`;
3. regenerar `Hb Track - Frontend/src/api/generated/*`;
4. sobrescrever o cliente FE anterior;
5. ajustar telas/adapters impactados para consumir o cliente gerado;
6. só então declarar paridade FE↔BE validada.

### Regra do código gerado
- `Hb Track - Frontend/src/api/generated/*` é artefato **derivado**.
- É proibido editar manualmente arquivos dentro de `src/api/generated/*`.
- O FE deve preferir os tipos e APIs gerados quando o contrato já estiver materializado no OpenAPI.
- `src/lib/api/*` não pode redefinir shapes, operationIds, enums ou payloads já tipados no cliente gerado.

---

## FERRAMENTAS OFICIAIS DO PIPELINE

Mapeamento canônico entre gates e ferramentas do módulo TRAINING:

- `OPENAPI_SPEC_QUALITY` → **Redocly CLI**
  - finalidade: lint/validate da spec OpenAPI
  - comando canônico:
    ```bash
    npx @redocly/cli@latest lint "Hb Track - Backend/docs/ssot/openapi.json"
    ```

- `CONTRACT_DIFF_GATE` → **oasdiff**
  - finalidade: detectar breaking changes entre spec anterior e spec nova
  - comando canônico:
    ```bash
    oasdiff breaking "contracts/openapi/baseline/openapi_baseline.json" "Hb Track - Backend/docs/ssot/openapi.json"
    ```

- `GENERATED_CLIENT_SYNC` → **OpenAPI Generator**
  - finalidade: gerar cliente FE derivado do contrato
  - comando canônico:
    ```bash
    cd "C:\HB TRACK\Hb Track - Frontend" && npx @openapitools/openapi-generator-cli generate -i openapi.json -g typescript-axios -o ./src/api/generated
    ```

- `RUNTIME CONTRACT VALIDATION` → **Schemathesis**
  - finalidade: validar a API real contra a spec OpenAPI
  - comando canônico:
    ```bash
    schemathesis run "Hb Track - Backend/docs/ssot/openapi.json" --base-url=http://localhost:8000
    ```

- `TRUTH_FE` → **Playwright** (futuro)
  - finalidade: validar FE real, UI/UX e integração FE↔BE
  - comando canônico: a definir quando os testes FE forem materializados

---

## SPEC_VERSIONING (NORMATIVO)

Objetivo:
Garantir que toda comparação de contrato use uma versão anterior aceita da spec OpenAPI.

Regra:
- Toda spec aceita do módulo TRAINING deve possuir uma versão/base canônica para comparação.
- `CONTRACT_DIFF_GATE` compara:
  - spec anterior aceita
  - spec nova regenerada

Path canônico recomendado:
- `contracts/openapi/baseline/openapi_baseline.json`
OU
- estrutura versionada equivalente definida no repositório

Regras:
- Não existe `CONTRACT_DIFF_GATE` sem baseline anterior identificada.
- Não é permitido declarar compatibilidade de contrato sem referência explícita à spec anterior.

---

## CI_PIPELINE (NORMATIVO)

Objetivo:
Automatizar o pipeline spec-driven do módulo TRAINING.

Etapas mínimas obrigatórias do pipeline:
1. `OPENAPI_SPEC_QUALITY`
2. `CONTRACT_DIFF_GATE`
3. `GENERATED_CLIENT_SYNC` (quando aplicável)
4. `RUNTIME CONTRACT VALIDATION`
5. `TRUTH_BE`
6. `TRUTH_FE` (quando materializado)

Regra:
Nenhuma mudança de contrato pode ser considerada convergida sem execução sequencial das etapas acima, respeitando dependências entre gates.

---

## SPEC_FREEZE_RULE (NORMATIVO)

Regra:
Nenhuma mudança de código que afete contrato FE↔BE pode ser considerada válida se `openapi.json` não estiver atualizado, validado e sincronizado com o cliente FE gerado quando aplicável.

FAIL se:
- código de backend mudar contrato sem atualização do `openapi.json`
- frontend mudar consumo contratual sem `GENERATED_CLIENT_SYNC`
- convergência FE↔BE for declarada com spec desatualizada

Efeito:
- execução bloqueada
- convergência FE↔BE inválida
- DONE inválido enquanto a spec estiver desatualizada

---

## COMANDOS CANÔNICOS

### Backend — TRUTH SUITE
```bash
cd "C:\HB TRACK\Hb Track - Backend" && python scripts/db/reset_hb_track_test.py && pytest -q tests/training/
```

### Backend — NO_MOCKS_GLOBAL

```bash
cd "C:\HB TRACK\Hb Track - Backend" && rg -n "unittest\.mock|\bmocker\.|monkeypatch\b|\bMagicMock\b|\bMock\b|patch\(" tests/training/ && exit 1 || exit 0
```

```bash
cd "C:\HB TRACK\Hb Track - Backend" && rg -n "\"\"\"Stub|Stub local|implementa .*logica minima" tests/training/ && exit 1 || exit 0
```

### Frontend — geração do cliente OpenAPI

```bash
cd "C:\HB TRACK\Hb Track - Frontend" && npx @openapitools/openapi-generator-cli generate -i openapi.json -g typescript-axios -o ./src/api/generated
```

Regras:

* O comando do generator é obrigatório quando `CONTRACT_SYNC_FE` for acionado.
* O comando do generator não substitui a TRUTH_BE.
* O generator materializa o cliente FE; a implementação das telas continua sendo trabalho real do produto.

---

## PROTOCOLO DE MUDANÇA (NORMATIVO)

PASSO 0 — Classificar a mudança
Classificar em UMA categoria:
A) Bugfix
B) Refactor funcional
C) UX/Fluxo
D) Nova Capability
E) Contrato

PASSO 1 — Ler a ordem canônica
1. `INVARIANTS_TRAINING.md`
2. `TRAINING_FRONT_BACK_CONTRACT.md`
3. `TRAINING_USER_FLOWS.md`
4. `TRAINING_SCREENS_SPEC.md`
5. `TEST_MATRIX_TRAINING.md`
6. `AR_BACKLOG_TRAINING.md`
7. `TRAINING_ROADMAP.md` (somente se pós-DONE)

PASSO 2 — Materializar no Backend
Implementar no produto real:
- schema / constraints
- models / services
- routers
- Pydantic / FastAPI

PASSO 3 — Validar subset backend
Rodar o subset definido em `TEST_MATRIX_TRAINING.md` conforme a categoria A–E.

PASSO 4 — Se contrato mudou, sincronizar FE obrigatoriamente
Executar `CONTRACT_SYNC_FE`:
- regenerar `openapi.json`
- regenerar `src/api/generated/*`
- ajustar telas/adapters impactados

PASSO 5 — Rodar TRUTH_BE completa
Executar a TRUTH SUITE do backend.

PASSO 6 — Validar NO_MOCKS_GLOBAL
Executar os scans `rg` no escopo `tests/training/`.

PASSO 7 — Atualizar SSOT mínimo
- Regra mudou → `INVARIANTS_TRAINING.md`
- Contrato mudou → `TRAINING_FRONT_BACK_CONTRACT.md`
- Fluxo mudou → `TRAINING_USER_FLOWS.md`
- Tela/UX mudou → `TRAINING_SCREENS_SPEC.md`
- Roteamento/evidência mudou → `TEST_MATRIX_TRAINING.md`
- Execução/entregável novo → `AR_BACKLOG_TRAINING.md`

PASSO 8 — Evidência mínima
Registrar apenas:
- saída da TRUTH_BE
- scans NO_MOCKS_GLOBAL (rg=0)
- evidência de geração/sync do cliente FE quando contrato mudou

---

## STATUS DO MÓDULO

| Item                      | Status                                                                            |
| ------------------------- | --------------------------------------------------------------------------------- |
| Done Gate                 | ✅ `DONE_TRAINING_ATINGIDO (= DONE_FASE_2_ATINGIDO AND DONE_FASE_3_REAL_ATINGIDO)` |
| Fase atual                | FASE_2 + FASE_3 REAL CONCLUÍDAS                                                   |
| ARs totais                | 86 ARs (`AR-TRAIN-001..086`) — todas VERIFICADO (exceto OBSOLETO/REJEITADO)       |
| ARs FASE_3 REAL           | 11 ARs `[FASE_3_REAL]`: `AR-TRAIN-015..021` + `055..058`                          |
| Última AR selada          | AR_270 (`AR-TRAIN-086`, Batch 35, 2026-03-08)                                |
| Frontend generated client | ✅ FE_MIGRATION_COMPLETE = TRUE (100% endpoints canônicos; `useSuggestions.ts` deferred a CAP-001) |
| Frontend automated tests  | ⏳ Ainda não materializados                                                        |
| Próxima revisão           | 2026-03-10                                                                        |

---

## ARQUIVOS DERIVADOS

Arquivos derivados do fluxo do módulo TRAINING:
- `Hb Track - Backend/docs/ssot/openapi.json` (derivado do backend)
- `Hb Track - Backend/docs/ssot/schema.sql` (derivado do DB)
- `docs/ssot/*` (espelho derivado no nível do repo; não editar manualmente)
- `Hb Track - Frontend/src/api/generated/*` (cliente FE derivado via OpenAPI Generator; não editar manualmente)
- `_reports/training/*` (evidências/relatórios de execução, incluindo `DONE_GATE_TRAINING.md`)

Artefatos de governança (baseline):
- `contracts/openapi/baseline/openapi_baseline.json` (baseline para `CONTRACT_DIFF_GATE`; só promover após `TRUTH_BE = PASS`)

Regras:
- arquivos derivados não são fonte normativa primária;
- arquivos derivados devem ser regenerados, não editados manualmente;
- divergência entre SSOT normativo e derivado exige correção no backend/contrato e nova regeneração.

---

## ARQUIVOS HISTÓRICOS / FORA DA CADEIA ATIVA

Os arquivos abaixo podem permanecer no repositório como trilha histórica, mas não governam mais o fluxo ativo do módulo TRAINING:
- `TRAINING_BATCH_PLAN_v1.md` (histórico; se existir)
- `SSOT_PATCH_*` (patches históricos)
- redirects/legados de snapshots operacionais antigos (quando existirem)

Regra:
- o agente não deve usar esses arquivos para decidir implementação atual, PASS, DONE ou contrato.
- em caso de conflito, prevalecem os SSOTs canônicos listados neste índice.
---
## QUESTÕES CRÍTICAS OBRIGATÓRIAS DE GOVERNANÇA SPEC-DRIVEN

Esta seção define guardrails obrigatórios para manter o fluxo spec-driven do módulo TRAINING seguro, determinístico e operacional para agentes.

Estas regras complementam:
- `TRAINING_FRONT_BACK_CONTRACT.md`
- `TEST_MATRIX_TRAINING.md`
- `INVARIANTS_TRAINING.md`

Violação destas regras invalida convergência FE↔BE ou DONE do módulo.

---

# 1. BREAKING CHANGES DO CONTRATO

Mudanças incompatíveis no contrato OpenAPI são proibidas sem política explícita de evolução.

Considera-se **breaking change**:

- remoção de endpoint
- remoção de campo em request/response
- alteração de tipo de campo
- alteração de enum
- renomeação de `operationId`
- alteração de status codes documentados

Regra:

Breaking changes só podem ocorrer via:

1) depreciação + substituição
OU
2) nova versão de contrato

É proibido:

- remover endpoint usado pelo FE sem período de depreciação
- alterar payload sem compatibilidade reversa

---

# 2. POLICY DE DEPRECATION

Endpoints ou campos substituídos devem seguir:

1. campo ou endpoint marcado como `deprecated`
2. nova operação disponibilizada
3. migração do frontend
4. remoção somente após janela de compatibilidade

Regra:

Depreciação deve ser documentada no contrato OpenAPI.

---

# 3. OPENAPI SPEC QUALITY

Mudanças no contrato exigem validação da spec.

Obrigatório antes de gerar cliente FE:

1. `openapi.json` atualizado
2. lint/validate da spec
3. ausência de erros bloqueantes

FAIL se:

- cliente FE for gerado a partir de spec inválida
- contrato mudar sem validação da spec

---

# 4. RUNTIME CONTRACT VALIDATION

A API real deve ser compatível com o contrato OpenAPI.

Mudanças no contrato exigem verificação de:

- request schema
- response schema
- status codes documentados

Regra:

A implementação não pode divergir do contrato materializado.

FAIL se:

- endpoint retorna estrutura diferente da definida na spec
- contrato documenta resposta que a API não produz

---

# 5. PROVIDER STATES DETERMINÍSTICOS

Testes do backend devem executar em estado determinístico.

Regras:

- cada cenário define seu estado inicial
- dados de teste devem ser isolados
- nenhum teste depende da execução anterior

É proibido:

- depender de estado residual de outro teste
- assumir dados persistentes de execução anterior

---

# 6. FRONTEIRA DO ADAPTER FRONTEND

O frontend possui duas camadas:

FE Generated  
`src/api/generated/*`

FE Manual / Adapter  
`src/lib/api/*`

Regra:

O adapter manual NÃO pode:

- redefinir payloads do contrato
- alterar enums do OpenAPI
- modificar estrutura de request/response

O adapter manual pode:

- compor chamadas
- tratar autenticação
- adicionar retry/configuração
- simplificar consumo no FE

Contrato OpenAPI e cliente gerado são a fonte de verdade.

---

# 7. SINCRONIZAÇÃO FRONTEND ↔ BACKEND

Mudanças no contrato exigem:

1. atualização do backend
2. geração de novo `openapi.json`
3. validação da spec
4. regeneração do cliente FE
5. atualização do frontend

Convergência FE↔BE só é válida quando:

- cliente gerado está sincronizado
- TRUTH_BE = PASS
- contrato consumido pelo FE corresponde ao backend real

---

# 8. COMPATIBILIDADE DE DEPLOY

Deploy de backend e frontend deve respeitar compatibilidade de contrato.

É proibido:

- publicar backend incompatível com FE em produção
- publicar FE que consome endpoints inexistentes

Mudanças devem seguir:

evolução compatível ou janela de migração.

---

# 9. AUTORIDADE

Em conflitos de implementação prevalece:

DB constraints  
> Service rules  
> OpenAPI contract  
> FE Generated  
> FE Manual / Adapter  
> PRD / documentação descritiva

---

# 10. EFEITO NO FLUXO DO MÓDULO

O fluxo spec-driven do módulo TRAINING passa a ser:

Spec normativa  
→ Backend implementa invariantes  
→ OpenAPI materializa contrato  
→ Spec validada  
→ Cliente FE gerado  
→ Frontend consome contrato  
→ Testes TRUTH validam implementação

DONE do módulo só pode ocorrer quando todo o fluxo acima estiver satisfeito.

## CONTRACT_DIFF_GATE (NORMATIVO)

Objetivo:
Impedir breaking changes silenciosas no contrato OpenAPI do módulo TRAINING.

Definição:
Toda mudança em `Hb Track - Backend/docs/ssot/openapi.json` DEVE ser comparada com a última versão aceita da spec antes de ser considerada convergida.

Esta comparação é obrigatória quando houver mudança em:
- path HTTP
- `operationId`
- request schema
- response schema
- enum canônico
- tipo canônico (`uuid`, `datetime`, `date`, etc.)
- status codes documentados

### Regra central

Spec válida não é suficiente.

Para convergência FE↔BE ser aceita, a nova spec deve ser:
1. tecnicamente válida (`OPENAPI_SPEC_QUALITY`)
2. compatível com a spec anterior
OU
3. explicitamente evoluída com política de breaking change aprovada

### Considera-se breaking change

- remoção de endpoint
- remoção de campo em request/response
- alteração incompatível de tipo
- alteração incompatível de enum
- renomeação de `operationId`
- remoção ou alteração incompatível de status code documentado
- mudança que torne inválido o consumo do cliente FE gerado anterior sem política de migração

### Regras obrigatórias

Breaking changes só podem ocorrer via:

1. **Depreciação + substituição**
   - endpoint/campo/operação anterior permanece disponível por janela de compatibilidade
   - nova operação/campo substituto é disponibilizado
   - migração do FE ocorre antes da remoção

OU

2. **Nova versão de contrato**
   - a mudança incompatível é isolada em versão nova explicitamente documentada

OU

3. **Waiver explícito**
   - aprovado pelo Arquiteto
   - com justificativa, escopo, impacto e plano de migração registrados

### FAIL se

- houver breaking change silenciosa entre a spec nova e a anterior
- `operationId` mudar sem política de migração
- endpoint/campo/enum/status code for removido sem depreciação, versão nova ou waiver
- o cliente FE gerado novo exigir mudança incompatível sem governança explícita

### Relação com o fluxo spec-driven

`CONTRACT_DIFF_GATE` complementa:
- `OPENAPI_SPEC_QUALITY`
- `CONTRACT_SYNC_FE`
- `API_SYNC_REQUIRED`
- `GENERATED_CLIENT_SYNC`

Ordem obrigatória:
1. backend atualizado
2. `openapi.json` regenerado
3. `OPENAPI_SPEC_QUALITY` = PASS
4. `CONTRACT_DIFF_GATE` = PASS
5. `GENERATED_CLIENT_SYNC`
6. FE ajustado
7. `TRUTH_BE` = PASS

Sem `CONTRACT_DIFF_GATE = PASS`, não existe convergência FE↔BE válida.

## RESUMO EXECUTIVO

O módulo TRAINING opera agora sob um fluxo spec-driven normativo:

**SSOT normativo → backend real → `openapi.json` → OpenAPI Generator → `src/api/generated/*` → frontend → TRUTH**

Qualquer agente do repo deve seguir esse pipeline.
Qualquer PASS fora desse pipeline é inválido.
Qualquer correção deve ocorrer no produto real.
Qualquer contrato alterado exige regeneração do cliente FE.
Qualquer artefato derivado não pode ser editado manualmente.
