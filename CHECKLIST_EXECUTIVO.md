# CHECKLIST EXECUTIVO — VERIFICAÇÃO OPERACIONAL DO HB Track

## 1. Objetivo

Ele responde a uma pergunta única:

**O sistema contract-driven do HB Track está operacional de forma verificável, determinística e reexecutável no ambiente-alvo?**

---

## 2. Taxonomia canônica de status

Use apenas estes quatro status:

- **PASS**  
  Critério: requisito comprovado por evidência executável, atual, no ambiente-alvo, sem restrições materiais.

- **PASS_COM_RESTRICAO**  
  Critério: requisito comprovado apenas parcialmente, ou comprovado em ambiente diferente do ambiente-alvo, ou dependente de limitação operacional ainda não sanada.

- **FAIL**  
  Critério: requisito aplicável e não atendido, ou atendido de forma insuficiente para uso operacional, ou há evidência objetiva de falha.

- **NAO_COMPROVADO**  
  Critério: não há evidência suficiente para decidir. Não equivale a PASS.

### Regra obrigatória de interpretação

- Existência de arquivo **não** prova operação.
- Gate existente **não** prova enforcement real do agente.
- PASS obtido em ambiente diferente do ambiente-alvo gera, no máximo, **PASS_COM_RESTRICAO**.
- Na presença de evidência conflitante entre ambientes, prevalece o status mais conservador para a decisão global.
- Se o item é necessário para prontidão operacional e ainda está em `FAIL` ou `NAO_COMPROVADO`, a decisão global não pode ser `PASS`.

---

## 3. Regra de Ambiente-Alvo

### Ambiente-alvo atual para decisão operacional
- **WSL / Linux**
---

## 4. Checklist Executivo

## 4.1 Premissas e decisões de governança

| Item | Status | Evidência / decisão |
|---|---|---|
| Contrato antes do código aceito | PASS | Decisão explícita no checklist original |
| Trilogia canônica aceita como autoridade | PASS | `CONTRACT_SYSTEM_LAYOUT.md`, `CONTRACT_SYSTEM_RULES.md`, `GLOBAL_TEMPLATES.md` aceitos |
| `api_rules.yaml` aceito como SSOT HTTP API | PASS | Canonical + origem preservada para compatibilidade |
| Taxonomia canônica dos 16 módulos aceita | PASS | Decisão explícita |
| Strict mode: bloquear em vez de inferir | PASS | Decisão explícita |
| Boot mínimo por tarefa aceito | PASS | Decisão explícita |
| DoD binário para contrato e módulo aceito | PASS | Decisão explícita |

### Status do bloco
**PASS**

---

## 4.2 Artefatos canônicos presentes no repositório

### 4.2.1 Núcleo contract-driven

| Item | Status | Evidência |
|---|---|---|
| `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | PASS | Arquivo presente |
| `.contract_driven/CONTRACT_SYSTEM_RULES.md` | PASS | Arquivo presente |
| `.contract_driven/GLOBAL_TEMPLATES.md` | PASS | Arquivo presente |
| `.contract_driven/templates/api/api_rules.yaml` | PASS | Arquivo presente e apontado como SSOT |
| `.contract_driven/templates/api/ARCHITECTURE_MATRIX.yaml` | PASS | Arquivo presente |
| `.contract_driven/templates/api/MODULE_PROFILE_REGISTRY.yaml` | PASS | Arquivo presente |
| `.contract_driven/DOMAIN_AXIOMS.json` | PASS | Arquivo presente |
| `contracts/schemas/shared/domain_axioms_module.schema.json` | PASS | Arquivo presente |
| `docs/hbtrack/modulos/README.md` | PASS | Arquivo presente |

### 4.2.2 Canon global

| Item | Status |
|---|---|
| `docs/_canon/README.md` | PASS |
| `docs/_canon/SYSTEM_SCOPE.md` | PASS |
| `docs/_canon/ARCHITECTURE.md` | PASS |
| `docs/_canon/MODULE_MAP.md` | PASS |
| `docs/_canon/CHANGE_POLICY.md` | PASS |
| `docs/_canon/API_CONVENTIONS.md` | PASS |
| `docs/_canon/DATA_CONVENTIONS.md` | PASS |
| `docs/_canon/ERROR_MODEL.md` | PASS |
| `docs/_canon/GLOBAL_INVARIANTS.md` | PASS |
| `docs/_canon/DOMAIN_GLOSSARY.md` | PASS |
| `docs/_canon/HANDBALL_RULES_DOMAIN.md` | PASS |
| `docs/_canon/SECURITY_RULES.md` | PASS |
| `docs/_canon/security/OWASP_API_CONTROL_MATRIX.yaml` | PASS |
| `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml` | PASS |
| `docs/_canon/CI_CONTRACT_GATES.md` | PASS |
| `docs/_canon/TEST_STRATEGY.md` | PASS |
| `docs/_canon/C4_CONTEXT.md` | PASS |
| `docs/_canon/C4_CONTAINERS.md` | PASS |
| `docs/_canon/UI_FOUNDATIONS.md` | PASS |
| `docs/_canon/DESIGN_SYSTEM.md` | PASS |

### Status do bloco
**PASS**

---

## 4.3 Estrutura real de contratos no repositório

### 4.3.1 Estrutura-base

| Item | Status | Evidência |
|---|---|---|
| `contracts/openapi/openapi.yaml` existe | PASS | Arquivo presente |
| `contracts/openapi/paths/` contém os 16 módulos canônicos | PASS | Estrutura confirmada no checklist original |
| `contracts/openapi/intents/` existe | PASS | DSL presente |
| `contracts/schemas/` existe | PASS | Estrutura presente |
| `contracts/workflows/` existe | PASS | Estrutura presente |
| `contracts/asyncapi/` existe | PASS | Estrutura presente |
| READMEs das árvores contratuais existem | PASS | Presença confirmada |
| Árvore segue layout canônico | PASS | `PATH_CANONICALITY_GATE` → PASS |
| Não há contratos fora da árvore canônica | PASS | Higiene + gates PASS |
| Não há módulos fora da taxonomia | PASS | Evidência indicada no checklist original |

### 4.3.2 Prompts e aderência dos prompts

| Item | Status | Evidência |
|---|---|---|
| Prompt de docs de módulo existe | PASS_COM_RESTRICAO | Existe, mas conteúdo pendente de validação |
| Prompt de OpenAPI existe | PASS_COM_RESTRICAO | Existe, mas conteúdo pendente de validação |
| Prompt de state model existe | PASS_COM_RESTRICAO | Existe, mas conteúdo pendente de validação |
| Prompt de UI contract existe | PASS_COM_RESTRICAO | Existe, mas conteúdo pendente de validação |
| Prompt de AsyncAPI existe | FAIL | Ausente no checklist original |
| Prompt de Arazzo existe | FAIL | Ausente no checklist original |
| Alinhamento prompt ↔ templates ↔ rules | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ artefatos de módulo | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ domínio do handebol | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ convenções API/dados | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ segurança | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ change policy | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ test strategy | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ governança/layout/validação/extensão modular | NAO_COMPROVADO | Sem evidência de validação executável |

### Status do bloco
**PASS_COM_RESTRICAO**

---

## 4.4 Ferramentas instaladas no ambiente-alvo

| Item | Status | Evidência |
|---|---|---|
| `node` disponível no PATH | FAIL | No WSL atual, `node` não resolve |
| Redocly CLI instalado e utilizável | FAIL | Existe, mas falha por `node: not found` |
| Spectral instalado e utilizável | FAIL | Existe, mas falha por `node: not found` |
| `oasdiff` no PATH | FAIL | Não encontrado |
| `schemathesis` no PATH | FAIL | Não encontrado |
| `ajv` instalado e utilizável | FAIL | Existe, mas falha por `node: not found` |
| AsyncAPI validator/parser utilizável | FAIL | Existe, mas falha por `node: not found` |
| Validator/linter Arazzo | PASS | `ARAZZO_VALIDATION_GATE` → PASS via `python3 scripts/validate_contracts.py` |
| Storybook disponível, se aplicável | NAO_COMPROVADO | Sem evidência suficiente |
| Intent compiler disponível | PASS | Executa |
| Policy compiler disponível | PASS | Executa |
| Ferramentas de geração de artefatos configuradas e testadas | NAO_COMPROVADO | Sem evidência suficiente |

### Status do bloco
**FAIL**

---

## 4.5 Ferramentas funcionando de verdade

### Leitura executiva

Há prova de funcionamento de parte da cadeia de compilação e validação, inclusive com evidências de PASS em comandos Python. Porém, a camada dependente de Node/OpenAPI/AsyncAPI no ambiente-alvo permanece insuficiente para declarar PASS pleno.

| Item | Status | Evidência |
|---|---|---|
| Validadores/compilers Python centrais executam | PASS | Evidências descritas no checklist original |
| Intent compiler processa casos válidos e inválidos | PASS | Evidência explícita |
| Policy compiler detecta drift semântico | PASS | Evidência explícita |
| Cadeia OpenAPI dependente de Node roda no WSL | FAIL | Bloqueada por ausência de `node` operacional |
| Cadeia AsyncAPI dependente de Node roda no WSL | FAIL | Bloqueada por ausência de `node` operacional |
| Toolchain completo roda de ponta a ponta no ambiente-alvo | PASS_COM_RESTRICAO | Parte roda; parte crítica não |

### Status do bloco
**PASS_COM_RESTRICAO**

---

## 4.6 Enforcement real

### 4.6.1 Enforcement comprovado

| Item | Status | Evidência |
|---|---|---|
| Script/comando único para validar contratos | PASS | Declarado e Evidênciado |
| Rotina de falha para contrato inválido | PASS | Evidênciada |
| Validador consome `DOMAIN_AXIOMS.json` explicitamente | PASS | Declarado como explícito |
| Rotina de falha para breaking change | PASS_COM_RESTRICAO | Evidência cita `oasdiff`, mas ferramenta não está operacional no WSL atual |
| Rotina de falha para drift fonte soberana ↔ derivado | PASS | `DERIVED_DRIFT_GATE` semântico |
| Rotina de falha para placeholder residual | PASS | `PLACEHOLDER_RESIDUE_GATE` |
| Rotina de falha para artefato obrigatório ausente | PASS | `REQUIRED_ARTIFACT_PRESENCE_GATE` |
| Rotina de falha para matriz OWASP | PASS | `OWASP_API_CONTROL_MATRIX_GATE` |
| Rotina de falha para matriz de autoridade/fonte | PASS | `MODULE_SOURCE_AUTHORITY_MATRIX_GATE` |
| Rotina de falha para boundary `users` vs `identity_access` | PASS | Gate citado |
| Rotina de falha para boundary `wellness` vs `medical` | PASS | Gate citado |
| Rotina de falha para taxonomia de scout sem artefato canônico | PASS | Gate citado |
| Rotina de falha para módulo que exige async/workflow sem artefatos | PASS | Gate citado |
| Rotina de falha para benchmark tratado como SSOT | PASS | Gate citado |

### 4.6.2 Enforcement não fechado

| Item | Status | Evidência |
|---|---|---|
| Rotina de falha para crossref módulo ↔ contrato | FAIL | Marcado como ausente no checklist original |
| Rotina de falha para alinhamento artefato de módulo ↔ contrato/implementação | FAIL | Marcado como ausente |
| Rotina de falha para alinhamento com domínio do handebol | FAIL | Marcado como ausente |
| Rotina de falha para violação de regra de domínio na implementação | NAO_COMPROVADO | Depende de testes ainda não comprovados |
| Rotina de falha para violação de invariantes na implementação | NAO_COMPROVADO | Depende de testes ainda não comprovados |
| Rotina de falha quando agente improvisa | NAO_COMPROVADO | Sem logs executáveis apresentados |
| Rotina de falha quando agente cria módulo/path/evento/workflow/regra fora da autoridade | NAO_COMPROVADO | Sem logs executáveis apresentados |
| Rotina de falha para edição manual de gerados | NAO_COMPROVADO | Sem evidência executável suficiente |

### Status do bloco
**PASS_COM_RESTRICAO**

---

## 4.7 Artefatos gerados

| Item | Status | Evidência |
|---|---|---|
| Pasta canônica de gerados existe (`generated/`) | PASS | Confirmado |
| Tipos/políticas/manifests vão para essa pasta | PASS | Confirmado |
| Clientes gerados vão sempre para essa pasta | NAO_COMPROVADO | Sem prova suficiente |
| Docs geradas vão sempre para essa pasta | NAO_COMPROVADO | Sem prova suficiente |
| Artefatos gerados não são editados manualmente | NAO_COMPROVADO | Sem prova suficiente |
| Artefatos gerados são regeneráveis | PASS | Compiler determinístico |
| Drift entre gerado e soberano é detectável | PASS | Comparação semântica |
| Há rotina de falha para drift entre gerado e soberano | PASS | `DERIVED_DRIFT_GATE` |
| Gerados alinhados com domínio do handebol | NAO_COMPROVADO | Sem gate/teste fechado |
| Gerados alinhados com regras de domínio documentadas | NAO_COMPROVADO | Sem teste fechado |
| Gerados alinhados com invariantes documentadas | NAO_COMPROVADO | Sem teste fechado |

### Status do bloco
**PASS_COM_RESTRICAO**

---

## 4.8 Agente / fluxo operacional

### Leitura executiva

Este é um dos maiores vazios de prova do sistema. O checklist original formula muitas expectativas corretas, mas quase todas permanecem sem evidência executável de comportamento real do agente.

| Item | Status |
|---|---|
| Agente usa a ordem de boot definida | NAO_COMPROVADO |
| Agente usa boot mínimo por tarefa | NAO_COMPROVADO |
| Agente bloqueia em lacuna crítica | NAO_COMPROVADO |
| Agente emite códigos de bloqueio fechados | NAO_COMPROVADO |
| Agente não cria módulo fora da taxonomia | NAO_COMPROVADO |
| Agente não cria path fora de contrato | NAO_COMPROVADO |
| Agente não cria evento fora de AsyncAPI | NAO_COMPROVADO |
| Agente não cria workflow sem Arazzo | NAO_COMPROVADO |
| Agente não cria regra esportiva fora do domínio documentado | NAO_COMPROVADO |
| Agente não edita gerado manualmente | NAO_COMPROVADO |
| Agente gera artefato correto quando o prompt é seguido | NAO_COMPROVADO |
| Agente bloqueia quando o prompt é seguido incorretamente | NAO_COMPROVADO |
| Agente gera artefato alinhado com domínio/regras/invariantes | NAO_COMPROVADO |

### Status do bloco
**NAO_COMPROVADO**

---

## 4.9 Domínio do handebol

| Item | Status | Evidência |
|---|---|---|
| `HANDBALL_RULES_DOMAIN.md` existe | PASS | Confirmado |
| Cobre impacto em `training` | PASS | Confirmado |
| Cobre impacto em `matches` | PASS | Confirmado |
| Cobre impacto em `scout` | PASS | Confirmado |
| Cobre impacto em `competitions` | PASS | Confirmado |
| Adaptações locais do produto estão registradas | NAO_COMPROVADO | Sem prova suficiente |
| Não há regra crítica fora do documento | NAO_COMPROVADO | Sem prova suficiente |
| Agente bloqueia tentativa de criar regra esportiva fora do documento | NAO_COMPROVADO | Sem logs executáveis |
| Contratos refletem o domínio documentado | NAO_COMPROVADO | Gate de alinhamento ainda não fechado |
| Implementação real respeita o domínio documentado | NAO_COMPROVADO | Sem teste fechado |
| Não há lacunas críticas entre domínio documentado e implementação real | NAO_COMPROVADO | Sem teste fechado |
| Domínio documentado é suficiente para features críticas | NAO_COMPROVADO | Sem prova executável |
| Domínio documentado é suficiente para criação de contratos | NAO_COMPROVADO | Sem prova executável |
| Domínio documentado é suficiente para criação de artefatos de módulo | NAO_COMPROVADO | Sem prova executável |
| Domínio documentado é suficiente para criação de testes automatizados | NAO_COMPROVADO | Sem prova executável |
| Domínio documentado é suficiente para geração de artefatos | NAO_COMPROVADO | Sem prova executável |

### Status do bloco
**PASS_COM_RESTRICAO**

Racional: existe base documental relevante, mas a suficiência operacional do domínio ainda não foi provada.

---

## 4.10 Módulo real piloto: `training`

| Item | Status | Evidência |
|---|---|---|
| `README` | PASS | Confirmado |
| `MODULE_SCOPE` | PASS | Confirmado |
| `DOMAIN_RULES` | PASS | Confirmado |
| `INVARIANTS` | PASS | Confirmado |
| `TEST_MATRIX` | PASS | Confirmado |
| OpenAPI path | PASS | Confirmado |
| Schemas | PASS | Confirmado |
| `STATE_MODEL`, se aplicável | NAO_COMPROVADO | Ausência não foi qualificada com prova de não aplicabilidade |
| `PERMISSIONS`, se aplicável | NAO_COMPROVADO | Ausência não foi qualificada com prova de não aplicabilidade |
| `ERRORS`, se aplicável | NAO_COMPROVADO | Ausência não foi qualificada com prova de não aplicabilidade |
| `UI_CONTRACT`, se aplicável | NAO_COMPROVADO | Ausência não foi qualificada com prova de não aplicabilidade |
| `SCREEN_MAP`, se aplicável | NAO_COMPROVADO | Ausência não foi qualificada com prova de não aplicabilidade |
| Arazzo, se aplicável | PASS | Confirmado |
| AsyncAPI, se aplicável | PASS | Confirmado |
| Estado operacional do piloto em WSL | FAIL | `_reports/contract_gates/latest.json` indicado como FAIL em 2026-03-13 |

### Status do bloco
**PASS_COM_RESTRICAO**

Racional: o piloto existe estruturalmente, mas não fecha prontidão operacional no ambiente-alvo.

---

## 4.11 Prontidão real

| Item | Status | Evidência |
|---|---|---|
| Existe pelo menos 1 contrato validado ponta a ponta no ambiente-alvo | FAIL | Em WSL (`2026-03-13`), `python3 scripts/validate_contracts.py` → FAIL |

### Status do bloco
**FAIL**

---

# 5. PRONTIDÃO DE GOVERNANCA CONTRACT-DRIVEN
  
### 5.0 Objetivo da seção

Esta seção verifica se a governança do sistema está suficientemente definida para que um agente consiga:

* ler a base normativa correta;
* distinguir regra, template, exemplo, evidência e artefato derivado;
* identificar o que existe e o que falta;
* marcar a checklist com evidência verificável;
* propor as próximas tarefas corretas;
* bloquear progressão quando houver lacunas normativas críticas;
* liberar a produção de contratos, implementação e testes sem inferência indevida.

### 5.0.1 Regra de decisão desta seção

A seção 5 não mede apenas presença de arquivos.
Ela mede se a governança está operacionalmente apta para suportar um fluxo contract-driven executável por agente.

### 5.0.2 Status permitido

Cada item desta seção deve usar exclusivamente um dos quatro status canônicos do documento:

* `PASS`
* `PASS_COM_RESTRICAO`
* `FAIL`
* `NAO_COMPROVADO`

### 5.0.3 Regra de marcação

Um item desta seção só pode ser marcado como `PASS` quando houver, simultaneamente:

* fonte normativa identificada;
* critério de uso explícito pelo agente;
* evidência verificável no repositório ou no fluxo;
* ausência de ambiguidade material para a decisão correspondente.

Presença de arquivo, menção documental ou intenção declarada não bastam, por si só, para `PASS`.

### 5.0.4 Regra de impacto

Se qualquer item crítico desta seção estiver em `FAIL`, a governança contract-driven deve ser considerada **não pronta** para liberação plena da fase correspondente.

Se qualquer item crítico desta seção estiver em `NAO_COMPROVADO`, a governança contract-driven deve ser considerada **não pronta para decisão positiva** sem evidência adicional.

### 5.0.5 Itens críticos desta seção

São itens críticos desta seção:

* `5.1.1`
* `5.1.3`
* `5.2.2`
* `5.2.3`
* `5.3.1`
* `5.3.3`
* `5.4.1`
* `5.5.5`
* `5.6.3`
* `5.6.5`
* `5.7.1`
* `5.7.4`

### 5.0.6 Saída obrigatória do agente ao auditar esta seção

Para cada item auditado, o agente deve registrar:

* `Item`
* `Status`
* `Evidência`
* `Lacuna`
* `Impacto`
* `Próxima_ação`
* `Criterio_para_PASS`

### 5.0.7 Regra de integração com a decisão global

A seção 5 mede prontidão de governança, não prontidão operacional plena do sistema.

Portanto:

* `PASS` na seção 5 libera a fase de produção contratual, desde que não haja bloqueio explícito em outra seção;
* `FAIL` ou `NAO_COMPROVADO` em item crítico da seção 5 impede liberação da fase contratual;
* `PASS` na seção 5 não implica, por si só, `PASS` no `STATUS GLOBAL` do sistema.

---

### 5.1 Autoridade normativa e precedência

| Item                                            | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ----------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 5.1.1 Matriz de precedência normativa definida | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.1.2 Classificação canônica dos artefatos     | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.1.3 Autoridade por tipo de decisão           | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.1.4 Ausência de precedência circular         | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 5.1

**5.1.1 Matriz de precedência normativa definida**
Critério:

* existe regra explícita de precedência entre canon global, regras modulares, layout, templates, contratos humanos, contratos formais, evidências e artefatos derivados;
* conflitos entre arquivos podem ser resolvidos sem interpretação subjetiva do agente.

Evidência esperada:

* documento canônico de precedência ou seção equivalente claramente vinculada ao canon.

**5.1.2 Classificação canônica dos artefatos**
Critério:

* está explícito o que é:

  * regra normativa,
  * template,
  * exemplo,
  * evidência,
  * artefato derivado,
  * artefato promovível,
  * artefato descartável;
* o agente não precisa inferir o papel de cada arquivo.

Evidência esperada:

* taxonomia documental ou matriz de classificação vinculada ao sistema.

**5.1.3 Autoridade por tipo de decisão**
Critério:

* para cada decisão relevante, existe fonte de autoridade explícita, por exemplo:

  * arquitetura do módulo,
  * contrato humano,
  * contrato OpenAPI/AsyncAPI/Arazzo,
  * tipo canônico,
  * política de segurança,
  * política de inferência,
  * política de promoção.

Evidência esperada:

* matriz `decisão → arquivo/fonte mandatória`.

**5.1.4 Ausência de precedência circular**
Critério:

* não existe ciclo onde plano operacional, gate, template ou checklist dependem circularmente uns dos outros para validar autoridade normativa.

Evidência esperada:

* revisão explícita ou estrutura documental que elimine circularidade.

---

### 5.2 Limites de inferência do agente

| Item                                              | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 5.2.1 Política explícita de inferência permitida | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.2.2 Política explícita de inferência proibida  | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.2.3 Regra de bloqueio por lacuna normativa     | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.2.4 Regra de escalonamento de lacunas          | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 5.2

**5.2.1 Política explícita de inferência permitida**
Critério:

* existe definição normativa do que o agente pode inferir sem input humano adicional.

Evidência esperada:

* documento, seção ou matriz de inferência permitida.

**5.2.2 Política explícita de inferência proibida**
Critério:

* existe definição normativa do que o agente não pode inferir, incluindo pelo menos:

  * campos obrigatórios normativos,
  * estados de negócio,
  * eventos de domínio,
  * regras de segurança,
  * retenção,
  * workflows críticos,
  * integrações externas,
  * boundaries entre módulos.

Evidência esperada:

* documento, seção ou matriz de não inferência.

**5.2.3 Regra de bloqueio por lacuna normativa**
Critério:

* quando faltar informação normativa obrigatória, o agente deve bloquear progressão e registrar lacuna, em vez de improvisar.

Evidência esperada:

* regra explícita de bloqueio e formato de saída do bloqueio.

**5.2.4 Regra de escalonamento de lacunas**
Critério:

* está definido quando a lacuna:

  * vira pergunta ao humano,
  * vira pendência normativa,
  * vira tarefa de criação de artefato,
  * impede geração contratual.

Evidência esperada:

* protocolo de tratamento de lacunas.

---

### 5.3 Fluxo canônico de produção contract-driven

| Item                                                                | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ------------------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 5.3.1 Sequência obrigatória de produção definida                   | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.3.2 Critério de entrada para criação de contrato humano          | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.3.3 Critério de promoção de contrato humano para contrato formal | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.3.4 Critério de liberação para implementação                     | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.3.5 Critério de liberação para testes e validação                | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 5.3

**5.3.1 Sequência obrigatória de produção definida**
Critério:

* existe fluxo normativo explícito, no mínimo cobrindo:

  * checklist,
  * contrato humano,
  * contrato formal,
  * gates,
  * implementação,
  * testes,
  * evidência,
  * promoção.

Evidência esperada:

* fluxograma, playbook ou contrato operacional canônico.

**5.3.2 Critério de entrada para criação de contrato humano**
Critério:

* existe definição clara do input mínimo necessário para o agente criar contrato humano por módulo.

Evidência esperada:

* template ou especificação de entrada mínima.

**5.3.3 Critério de promoção de contrato humano para contrato formal**
Critério:

* está definido quando um contrato humano pode virar OpenAPI, AsyncAPI, Arazzo ou equivalente.

Evidência esperada:

* regra de promoção com pré-condições objetivas.

**5.3.4 Critério de liberação para implementação**
Critério:

* está definido quais artefatos e gates precisam estar válidos antes da implementação.

Evidência esperada:

* checklist de entrada de implementação ou política equivalente.

**5.3.5 Critério de liberação para testes e validação**
Critério:

* está definido quando o sistema já pode gerar testes, validar invariantes e produzir evidência.

Evidência esperada:

* política de entrada para testes e auditoria.

---

### 5.4 Binding módulo → arquitetura → contrato

| Item                                                             | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ---------------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 5.4.1 Perfil arquitetural por módulo definido                   | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.4.2 Boundaries e integrações permitidas por módulo            | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.4.3 Artefatos obrigatórios por módulo e por tipo arquitetural | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.4.4 Regra contra generalização indevida entre módulos         | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 5.4

**5.4.1 Perfil arquitetural por módulo definido**
Critério:

* cada módulo possui definição canônica de perfil arquitetural.

Exemplos de decisão que devem estar normativamente expostos quando aplicável:

* CRUD clássico,
* workflow/state machine,
* eventos de domínio,
* projeções,
* sagas/orquestração,
* leitura vs escrita,
* sincronismo vs assincronismo.

Evidência esperada:

* matriz ou registry de arquitetura por módulo.

**5.4.2 Boundaries e integrações permitidas por módulo**
Critério:

* cada módulo possui fronteiras explícitas com outros módulos e integrações permitidas ou proibidas.

Evidência esperada:

* matriz de boundary ou autoridade equivalente.

**5.4.3 Artefatos obrigatórios por módulo e por tipo arquitetural**
Critério:

* a governança define quais artefatos são obrigatórios para cada módulo conforme seu perfil arquitetural.

Evidência esperada:

* matriz `tipo de módulo/arquitetura → artefatos obrigatórios`.

**5.4.4 Regra contra generalização indevida entre módulos**
Critério:

* o agente não pode aplicar padrão de um módulo em outro sem respaldo normativo explícito.

Evidência esperada:

* política ou regra de restrição modular.

---

### 5.5 Gates de governança

| Item                                                       | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ---------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 5.5.1 Gates de presença estrutural definidos              | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.5.2 Gates de consistência semântica definidos           | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.5.3 Gates de aderência arquitetural definidos           | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.5.4 Gates de vínculo contrato ↔ implementação definidos | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.5.5 Bloqueio de progressão por gate crítico             | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 5.5

**5.5.1 Gates de presença estrutural definidos**
Critério:

* existem gates para validar presença dos artefatos normativos mínimos.

Evidência esperada:

* gates implementados e vinculados à governança.

**5.5.2 Gates de consistência semântica definidos**
Critério:

* existem gates para validar coerência entre regras, contratos, tipos, semântica e referências cruzadas.

Evidência esperada:

* gates ou validadores correspondentes.

**5.5.3 Gates de aderência arquitetural definidos**
Critério:

* existem gates para validar que o contrato respeita o perfil arquitetural do módulo.

Evidência esperada:

* gate ou política automatizável correspondente.

**5.5.4 Gates de vínculo contrato ↔ implementação definidos**
Critério:

* existem gates ou procedimentos que validam que contrato e implementação não divergiram materialmente.

Evidência esperada:

* verificador, parity gate ou mecanismo equivalente.

**5.5.5 Bloqueio de progressão por gate crítico**
Critério:

* está explícito quais gates são bloqueantes e qual fase cada gate bloqueia.

Evidência esperada:

* registry de gates ou política equivalente.

---

### 5.6 Operação do agente sobre a checklist

| Item                                                     | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| -------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 5.6.1 Formato canônico de leitura da checklist definido | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.6.2 Formato canônico de saída do agente definido      | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.6.3 Regra de proibição de PASS sem evidência          | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.6.4 Geração de próximas tarefas a partir dos FAILs    | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.6.5 Priorização por caminho crítico                   | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 5.6

**5.6.1 Formato canônico de leitura da checklist definido**
Critério:

* está definido como o agente deve interpretar a checklist e quais fontes consultar para cada item.

Evidência esperada:

* protocolo de leitura da checklist.

**5.6.2 Formato canônico de saída do agente definido**
Critério:

* está definido como o agente deve devolver a auditoria da checklist.

Campos mínimos:

* `Item`
* `Status`
* `Evidência`
* `Lacuna`
* `Impacto`
* `Próxima_ação`
* `Criterio_para_PASS`

Evidência esperada:

* template ou contrato de saída.

**5.6.3 Regra de proibição de PASS sem evidência**
Critério:

* o agente está normativamente proibido de marcar `PASS` sem evidência verificável.

Evidência esperada:

* regra explícita vinculada à checklist.

**5.6.4 Geração de próximas tarefas a partir dos FAILs**
Critério:

* o agente deve derivar backlog de correção diretamente dos `FAIL` e `NAO_COMPROVADO`.

Evidência esperada:

* protocolo de geração de próximas tarefas.

**5.6.5 Priorização por caminho crítico**
Critério:

* o agente deve priorizar tarefas que:

  * destravam governança,
  * destravam contrato,
  * destravam implementação,
  * destravam teste,
  * reduzem inferência indevida.

Evidência esperada:

* regra explícita de priorização.

---

### 5.7 Critério de liberação por fase

| Item                                                         | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ------------------------------------------------------------ | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 5.7.1 Regra de prontidão para iniciar produção de contratos | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.7.2 Regra de prontidão para iniciar implementação         | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.7.3 Regra de prontidão para iniciar testes formais        | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 5.7.4 Regra de prontidão global do sistema                  | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 5.7

**5.7.1 Regra de prontidão para iniciar produção de contratos**
Critério:

* estão definidos os itens mínimos obrigatórios para iniciar contratos formais.

Evidência esperada:

* política de readiness para fase contratual.

**5.7.2 Regra de prontidão para iniciar implementação**
Critério:

* estão definidos os itens mínimos obrigatórios para iniciar código de produção.

Evidência esperada:

* política de readiness para fase de implementação.

**5.7.3 Regra de prontidão para iniciar testes formais**
Critério:

* estão definidos os itens mínimos obrigatórios para iniciar testes e validação formal.

Evidência esperada:

* política de readiness para fase de testes.

**5.7.4 Regra de prontidão global do sistema**
Critério:

* existe regra objetiva para decidir quando a governança contract-driven está pronta o suficiente para sustentar o fluxo do sistema.

Evidência esperada:

* critério consolidado de prontidão global.

---

### 5.8 Critério executivo de conclusão da seção 5

#### 5.8.1 Regra de conclusão

A seção 5 só pode ser considerada concluída quando:

* todos os itens críticos estiverem em `PASS`; e
* não houver `FAIL` em autoridade normativa, limites de inferência, fluxo canônico ou gates críticos; e
* os itens em `PASS_COM_RESTRICAO` não comprometerem a próxima fase pretendida; e
* os itens em `NAO_COMPROVADO` não incidirem sobre decisões bloqueantes.

#### 5.8.2 Regra de bloqueio

Se qualquer um dos grupos abaixo contiver `FAIL`, a governança contract-driven deve ser considerada **não pronta** para operar de forma confiável:

* `5.1 Autoridade normativa e precedência`
* `5.2 Limites de inferência do agente`
* `5.3 Fluxo canônico de produção`
* `5.5 Gates de governança`
* `5.6 Operação do agente sobre a checklist`

### 5.8.3 Resultado executivo da seção

Status executivo da seção 5: `NAO_COMPROVADO`

Valores permitidos:

* `PASS`
* `PASS_COM_RESTRICAO`
* `FAIL`
* `NAO_COMPROVADO`

Justificativa executiva:
`__________________________________________________`

---

### 5.9 Saída resumida obrigatória do agente após auditar a seção 5

Ao final da auditoria, o agente deve produzir obrigatoriamente:

#### 5.9.1 Resumo executivo

* status executivo da seção;
* principais bloqueios;
* principais restrições;
* risco atual de inferência indevida;
* fase liberada;
* fase ainda bloqueada.

#### 5.9.2 Backlog mínimo derivado

Lista ordenada de tarefas no formato:

* `Tarefa`
* `Motivo`
* `Item_da_checklist_que_ela_fecha`
* `Impacto_no_fluxo`
* `Dependencia`
* `Criterio_de_conclusao`

#### 5.9.3 Próxima tarefa lógica

O agente deve apontar apenas a próxima tarefa do caminho crítico, e não uma lista genérica de opções.
---

## 6. AUDITORIA DE QUALIDADE DOS 3 SSOTs CENTRAIS

### 6.0 Objetivo da seção

Esta seção verifica se os 3 arquivos SSOT centrais da governança contract-driven não apenas existem e possuem autoridade formal, mas também se o **conteúdo** deles é suficientemente sólido para sustentar a criação de contratos, o bloqueio de lacunas, a orientação do agente e a evolução segura do sistema.

SSOTs auditados nesta seção:

* `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
* `.contract_driven/CONTRACT_SYSTEM_RULES.md`
* `.contract_driven/GLOBAL_TEMPLATES.md`

### 6.0.1 Regra de decisão desta seção

A Seção 6 não mede presença de arquivo nem papel normativo.
Ela mede a **qualidade substantiva** do conteúdo dos 3 SSOTs.

### 6.0.2 Status permitido

Cada item desta seção deve usar exclusivamente um dos quatro status canônicos do documento:

* `PASS`
* `PASS_COM_RESTRICAO`
* `FAIL`
* `NAO_COMPROVADO`

### 6.0.3 Regra de marcação

Um item desta seção só pode ser marcado como `PASS` quando houver, simultaneamente:

* evidência textual verificável nos 3 SSOTs;
* ausência de contradição material com o canon e com os contratos técnicos;
* suficiência prática para orientar o agente ou a fase avaliada;
* ausência de lacuna crítica para a decisão correspondente.

Presença de tópico, menção superficial ou intenção declarada não bastam, por si só, para `PASS`.

### 6.0.4 Regra de impacto

Se qualquer item crítico desta seção estiver em `FAIL`, os 3 SSOTs devem ser considerados **não suficientemente confiáveis** para sustentar liberação plena da fase correspondente.

Se qualquer item crítico desta seção estiver em `NAO_COMPROVADO`, os 3 SSOTs devem ser considerados **não auditados de forma suficiente** para decisão positiva.

### 6.0.5 Itens críticos desta seção

São itens críticos desta seção:

* `6.1.1`
* `6.2.1`
* `6.3.1`
* `6.4.1`
* `6.5.1`
* `6.6.1`
* `6.7.1`
* `6.8.1`
* `6.9.1`
* `6.10.1`

### 6.0.6 Saída obrigatória do agente ao auditar esta seção

Para cada item auditado, o agente deve registrar:

* `Item`
* `Status`
* `Evidência`
* `Lacuna`
* `Impacto`
* `Próxima_ação`
* `Criterio_para_PASS`

### 6.0.7 Regra de integração com a decisão global

A Seção 6 mede qualidade dos SSOTs centrais, não prontidão operacional global do sistema.

Portanto:

* `PASS` na Seção 6 indica que os 3 SSOTs estão suficientemente sólidos para sustentar o fluxo avaliado;
* `FAIL` ou `NAO_COMPROVADO` em item crítico da Seção 6 impede tratar os 3 SSOTs como base confiável para a fase correspondente;
* `PASS` na Seção 6 não implica, por si só, `PASS` no `STATUS GLOBAL`.

---

### 6.1 Completude

| Item                                                                  | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --------------------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.1.1 Completude normativa mínima dos 3 SSOTs                        | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.1.2 Cobertura das decisões fundamentais do sistema contract-driven | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.1.3 Cobertura das decisões necessárias para operação do agente     | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 6.1

**6.1.1 Completude normativa mínima dos 3 SSOTs**
Critério:

* os 3 SSOTs cobrem layout, regras operacionais e templates oficiais sem lacunas críticas óbvias;
* não dependem de documentos implícitos para decisões estruturais básicas.

Evidência esperada:

* conteúdo verificável nos 3 SSOTs cobrindo esses três eixos.

**6.1.2 Cobertura das decisões fundamentais do sistema contract-driven**
Critério:

* os SSOTs cobrem, pelo menos:

  * precedência,
  * taxonomia,
  * artefatos canônicos,
  * regras de bloqueio,
  * produção de contratos,
  * natureza de derivados.

**6.1.3 Cobertura das decisões necessárias para operação do agente**
Critério:

* os SSOTs fornecem base suficiente para o agente saber:

  * o que ler,
  * o que gerar,
  * o que bloquear,
  * o que não inferir.

---

### 6.2 Consistência interna

| Item                                                    | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.2.1 Ausência de contradições internas em cada SSOT   | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.2.2 Terminologia interna estável e não ambígua       | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.2.3 Regras e exceções definidas sem conflito interno | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 6.2

**6.2.1 Ausência de contradições internas em cada SSOT**
Critério:

* o mesmo documento não define duas regras materiais incompatíveis para o mesmo assunto.

**6.2.2 Terminologia interna estável e não ambígua**
Critério:

* termos como SSOT, template, derivado, canônico, bloqueio, módulo, artefato obrigatório, gate, promoção e autoridade são usados com consistência.

**6.2.3 Regras e exceções definidas sem conflito interno**
Critério:

* quando houver exceção, ela não invalida silenciosamente a regra principal.

---

### 6.3 Consistência cruzada

| Item                                                               | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ------------------------------------------------------------------ | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.3.1 Ausência de contradição material entre os 3 SSOTs           | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.3.2 Alinhamento dos 3 SSOTs com o canon global                  | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.3.3 Alinhamento dos 3 SSOTs com a estrutura real do repositório | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 6.3

**6.3.1 Ausência de contradição material entre os 3 SSOTs**
Critério:

* layout, regras e templates não se desautorizam mutuamente.

**6.3.2 Alinhamento dos 3 SSOTs com o canon global**
Critério:

* os 3 SSOTs não conflitam materialmente com `docs/_canon/**`.

**6.3.3 Alinhamento dos 3 SSOTs com a estrutura real do repositório**
Critério:

* os paths, artefatos e fluxos mencionados nos SSOTs correspondem ao que realmente existe ou ao que está formalmente exigido.

---

### 6.4 Ausência de ambiguidade

| Item                                                      | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.4.1 Regras críticas redigidas sem ambiguidade material | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.4.2 Critérios de aplicabilidade estão claros           | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.4.3 Casos “se aplicável” têm critérios suficientes     | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 6.4

**6.4.1 Regras críticas redigidas sem ambiguidade material**
Critério:

* um agente ou auditor não precisa adivinhar o significado operacional da regra.

**6.4.2 Critérios de aplicabilidade estão claros**
Critério:

* o documento deixa claro quando uma regra vale, quando não vale e o que determina isso.

**6.4.3 Casos “se aplicável” têm critérios suficientes**
Critério:

* não basta dizer “se aplicável”; é preciso haver base para decidir aplicabilidade.

---

### 6.5 Aderência ao domínio HB Track

| Item                                                              | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ----------------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.5.1 Compatibilidade dos 3 SSOTs com o domínio real do HB Track | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.5.2 Os 3 SSOTs não induzem abstração genérica demais           | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.5.3 Os 3 SSOTs suportam módulos esportivos sem distorção       | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 6.5

**6.5.1 Compatibilidade dos 3 SSOTs com o domínio real do HB Track**
Critério:

* as regras centrais não colidem com necessidades do produto sports-tech.

**6.5.2 Os 3 SSOTs não induzem abstração genérica demais**
Critério:

* os SSOTs não são tão genéricos a ponto de deixar decisões críticas soltas.

**6.5.3 Os 3 SSOTs suportam módulos esportivos sem distorção**
Critério:

* os SSOTs conseguem governar módulos como training, matches, scout, competitions e wellness sem forçar modelagem artificial.

---

### 6.6 Aderência à arquitetura por módulo

| Item                                                                           | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ------------------------------------------------------------------------------ | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.6.1 Os 3 SSOTs respeitam diferenças arquiteturais entre módulos             | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.6.2 Os 3 SSOTs permitem distinguir CRUD, evento e workflow quando aplicável | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.6.3 Os 3 SSOTs não induzem generalização indevida entre módulos             | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 6.6

**6.6.1 Os 3 SSOTs respeitam diferenças arquiteturais entre módulos**
Critério:

* não tratam todos os módulos como se tivessem mesma natureza arquitetural.

**6.6.2 Os 3 SSOTs permitem distinguir CRUD, evento e workflow quando aplicável**
Critério:

* a governança central comporta mais de uma superfície contratual com critérios claros.

**6.6.3 Os 3 SSOTs não induzem generalização indevida entre módulos**
Critério:

* o agente não é levado a aplicar o mesmo padrão em todos os módulos por falta de nuance normativa.

---

### 6.7 Poder de geração contratual

| Item                                                                                  | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ------------------------------------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.7.1 Os 3 SSOTs são suficientes para iniciar geração contratual com baixo improviso | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.7.2 Os 3 SSOTs orientam produção de artefatos mínimos por módulo                   | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.7.3 Os 3 SSOTs reduzem variação indevida entre contratos semelhantes               | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 6.7

**6.7.1 Os 3 SSOTs são suficientes para iniciar geração contratual com baixo improviso**
Critério:

* o agente consegue iniciar criação contratual sem depender de inferência estrutural excessiva.

**6.7.2 Os 3 SSOTs orientam produção de artefatos mínimos por módulo**
Critério:

* os SSOTs dizem o que precisa existir por módulo ou por superfície.

**6.7.3 Os 3 SSOTs reduzem variação indevida entre contratos semelhantes**
Critério:

* contratos produzidos sob a mesma governança tendem a sair consistentes.

---

### 6.8 Poder de bloqueio do agente

| Item                                                         | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ------------------------------------------------------------ | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.8.1 Os 3 SSOTs definem condições claras de bloqueio       | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.8.2 Os 3 SSOTs tornam lacuna crítica detectável           | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.8.3 Os 3 SSOTs reduzem espaço para improvisação do agente | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 6.8

**6.8.1 Os 3 SSOTs definem condições claras de bloqueio**
Critério:

* está claro quando o agente deve parar e não prosseguir.

**6.8.2 Os 3 SSOTs tornam lacuna crítica detectável**
Critério:

* o agente consegue reconhecer ausência de insumo obrigatório.

**6.8.3 Os 3 SSOTs reduzem espaço para improvisação do agente**
Critério:

* o conteúdo restringe suficientemente liberdade indevida.

---

### 6.9 Cobertura de casos-limite

| Item                                                                              | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --------------------------------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.9.1 Os 3 SSOTs cobrem casos-limite relevantes do fluxo contract-driven         | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.9.2 Os 3 SSOTs tratam exceções, artefatos opcionais e superfícies condicionais | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.9.3 Os 3 SSOTs evitam silêncio normativo em bordas previsíveis                 | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 6.9

**6.9.1 Os 3 SSOTs cobrem casos-limite relevantes do fluxo contract-driven**
Critério:

* há orientação suficiente para tratar exceções previsíveis.

**6.9.2 Os 3 SSOTs tratam exceções, artefatos opcionais e superfícies condicionais**
Critério:

* o agente sabe lidar com “se aplicável”, opcionalidade e condições de superfície.

**6.9.3 Os 3 SSOTs evitam silêncio normativo em bordas previsíveis**
Critério:

* não há omissões graves em situações recorrentes.

---

### 6.10 Incompatibilidades com gates e implementação

| Item                                                                              | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --------------------------------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.10.1 Os 3 SSOTs são compatíveis com os gates implementados                     | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.10.2 Os 3 SSOTs não exigem artefatos/fluxos inexistentes sem qualificação      | `____` | `____`    | `____` | `____`  | `____`       | `____`             |
| 6.10.3 Os 3 SSOTs não entram em conflito material com o estado real do workspace | `____` | `____`    | `____` | `____`  | `____`       | `____`             |

#### Critérios normativos do bloco 6.10

**6.10.1 Os 3 SSOTs são compatíveis com os gates implementados**
Critério:

* o que os SSOTs exigem pode ser validado pelos gates reais ou está claramente classificado como exigência ainda não automatizada.

**6.10.2 Os 3 SSOTs não exigem artefatos/fluxos inexistentes sem qualificação**
Critério:

* não empurram o agente para caminhos inviáveis no workspace atual sem deixar isso explícito.

**6.10.3 Os 3 SSOTs não entram em conflito material com o estado real do workspace**
Critério:

* não há incompatibilidade grave entre a norma central e a realidade operacional do repositório.

---

### 6.11 Critério executivo de conclusão da seção 6

#### 6.11.1 Regra de conclusão

A Seção 6 só pode ser considerada concluída quando:

* todos os itens críticos estiverem em `PASS`; e
* não houver `FAIL` em completude, consistência cruzada, aderência ao domínio, poder de geração contratual, poder de bloqueio do agente ou incompatibilidade com gates/implementação; e
* os itens em `PASS_COM_RESTRICAO` não comprometerem a fase pretendida; e
* os itens em `NAO_COMPROVADO` não incidirem sobre decisões bloqueantes.

#### 6.11.2 Regra de bloqueio

Se qualquer um dos grupos abaixo contiver `FAIL`, os 3 SSOTs devem ser considerados **não suficientemente confiáveis** para sustentar o fluxo contract-driven com segurança:

* `6.1 Completude`
* `6.3 Consistência cruzada`
* `6.5 Aderência ao domínio HB Track`
* `6.7 Poder de geração contratual`
* `6.8 Poder de bloqueio do agente`
* `6.10 Incompatibilidades com gates e implementação`

### 6.11.3 Resultado executivo da seção

Status executivo da Seção 6: `NAO_COMPROVADO`

Valores permitidos:

* `PASS`
* `PASS_COM_RESTRICAO`
* `FAIL`
* `NAO_COMPROVADO`

Justificativa executiva:
`__________________________________________________`
---

### 6.12 Saída resumida obrigatória do agente após auditar a seção 6

Ao final da auditoria, o agente deve produzir obrigatoriamente:

#### 6.12.1 Resumo executivo

* status executivo da seção;
* principais lacunas dos 3 SSOTs;
* principais contradições;
* risco atual de improvisação do agente;
* suficiência ou insuficiência dos SSOTs para a próxima fase.

#### 6.12.2 Backlog mínimo derivado

Lista ordenada de tarefas no formato:

* `Tarefa`
* `Motivo`
* `Item_da_checklist_que_ela_fecha`
* `Impacto_no_fluxo`
* `Dependencia`
* `Criterio_de_conclusao`

#### 6.12.3 Próxima tarefa lógica

O agente deve apontar apenas a próxima tarefa do caminho crítico, e não uma lista genérica de opções.

--- 

## 7. Decisão executiva atual

## STATUS GLOBAL: **FAIL**

### Fundamentação da decisão global

O repositório possui base documental relevante, parte importante da infraestrutura de validação e uma estrutura formal de governança contract-driven. Porém, **não há comprovação suficiente de prontidão operacional ponta a ponta no ambiente-alvo (WSL)**. Além disso:

* continuam sem prova suficiente os blocos de enforcement do agente, alinhamento contrato↔módulo↔domínio↔implementação e operação real de parte relevante do toolchain;
* a **prontidão de governança contract-driven** ainda precisa ser auditada formalmente pela Seção 5;
* a **qualidade substantiva dos 3 SSOTs centrais** ainda precisa ser auditada formalmente pela Seção 6.

### Regra de impacto das Seções 5 e 6 na decisão global

* `PASS` na Seção 5 libera, no máximo, a **fase contratual**, desde que não haja bloqueio explícito em outras seções.
* `PASS` na Seção 6 indica, no máximo, que os **3 SSOTs centrais** estão suficientemente confiáveis para sustentar a fase avaliada.
* `PASS` nas Seções 5 e 6 **não implica**, por si só, `PASS` no `STATUS GLOBAL`.
* `FAIL` ou `NAO_COMPROVADO` em item crítico da Seção 5 impede tratar a governança contract-driven como pronta para operação segura do agente.
* `FAIL` ou `NAO_COMPROVADO` em item crítico da Seção 6 impede tratar os 3 SSOTs centrais como base confiável para sustentar o fluxo contract-driven.

### Motivos executivos para FAIL global

1. O ambiente-alvo não comprova validação ponta a ponta de pelo menos um contrato real.
2. O toolchain essencial de OpenAPI/AsyncAPI não está comprovadamente funcional no WSL.
3. O enforcement real do agente permanece majoritariamente sem prova.
4. O alinhamento entre domínio documentado, contratos e implementação real ainda não está fechado por evidência automatizada.
5. A prontidão de governança contract-driven e a qualidade substantiva dos 3 SSOTs centrais ainda não foram formalmente aprovadas pelas Seções 5 e 6.

---

## 8. Matriz executiva por bloco

| Bloco                                   | Status             | Leitura executiva                                                                                        |
| --------------------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------- |
| Premissas e decisões de governança      | PASS               | Direção estratégica definida e aceita                                                                    |
| Artefatos canônicos presentes           | PASS               | Base documental central existe                                                                           |
| Estrutura real de contratos             | PASS_COM_RESTRICAO | Árvore canônica existe, mas parte do fluxo de prompts e alinhamento ainda não está comprovada            |
| Ferramentas instaladas                  | FAIL               | Dependências essenciais não estão operacionais no ambiente-alvo                                          |
| Ferramentas funcionando de verdade      | PASS_COM_RESTRICAO | Parte dos compilers/gates funciona, mas há lacunas relevantes no WSL                                     |
| Enforcement real                        | PASS_COM_RESTRICAO | Vários gates existem, porém enforcement de agente e alinhamento fim a fim seguem incompletos             |
| Artefatos gerados                       | PASS_COM_RESTRICAO | Há regenerabilidade e detecção de drift, mas não há fechamento completo de todos os gerados              |
| Agente / fluxo operacional              | NAO_COMPROVADO     | Falta evidência executável do comportamento real do agente                                               |
| Domínio do handebol                     | PASS_COM_RESTRICAO | Domínio-base existe, mas sua suficiência operacional ainda não foi provada                               |
| Módulo piloto `training`                | PASS_COM_RESTRICAO | Estrutura existe, mas não fecha prontidão operacional no ambiente-alvo                                   |
| Prontidão real                          | FAIL               | O sistema não está operacional de forma comprovada em WSL                                                |
| Prontidão de governança contract-driven | NAO_COMPROVADO     | Mede se a governança já permite o agente operar com segurança para liberar a fase contratual             |
| Qualidade dos 3 SSOTs centrais          | NAO_COMPROVADO     | Mede se layout, rules e templates são substantivamente confiáveis para sustentar o fluxo contract-driven |

---

## 9. Regra de uso deste documento

Ao atualizar este checklist:

- não promova item para `PASS` sem evidência executável no ambiente-alvo;
- use `PASS_COM_RESTRICAO` quando a capacidade existir, mas ainda não for confiável para decisão operacional;
- use `NAO_COMPROVADO` quando faltar evidência, mesmo que a hipótese pareça plausível;
- mantenha o `STATUS GLOBAL` conservador;
- registre sempre comando, ambiente e data da evidência usada.

---