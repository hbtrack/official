version: 1.0.0
status: PROPOSED
scope: hb_track
artifact_type: human_manual
authority: operational_manual
owners:
  - architecture
  - product
  - backend
  - ai_governance

## 1. Objetivo

Explicar o protocolo completo para transformar pesquisa feita no ChatGPT do navegador em implementação determinística de módulo no repositório do HB Track.

Este manual existe para humanos.
Ele NÃO é a gramática executável.
A gramática executável é o `MODULE_DECISION_IR` validado pelo `DECISION_IR_CONFORMANCE_GATE`.

## 2. Visão geral do protocolo

O protocolo tem 3 camadas:

1. Pesquisa
   - ambiente: ChatGPT no navegador
   - objetivo: descobrir e fechar decisões de arquitetura, modelagem, UI, API, estados, regras e limites de inferência

2. Decisão
   - ambiente: consolidação humana
   - objetivo: converter a pesquisa em `MODULE_DECISION_IR.yaml/json`

3. Materialização
   - ambiente: agente do repositório
   - objetivo: validar o IR, bloquear ambiguidades e gerar superfícies canônicas via templates determinísticos

Regra principal:
**o navegador pesquisa e decide; o repositório materializa; o pipeline valida.**

## 3. Papel de cada arquivo do pacote

### 3.1 `MODULE_DECISION_IR_SCHEMA.json`
Schema formal do IR.
Serve para validar forma e campos obrigatórios.

### 3.2 `DECISION_IR_CONFORMANCE_GATE.md`
Especificação do gate que valida:
- schema
- registries
- coerência semântica
- completude por superfície
- readiness de geração determinística

### 3.3 `IR_TO_SURFACE_MAPPING.yaml`
Matriz que diz como cada bloco do IR alimenta superfícies do pipeline.

### 3.4 `training.module_decision_ir.yaml`
Exemplo inicial para o módulo `training`.

### 3.5 `MANUAL_PESQUISA_IMPLEMENTACAO.md`
Manual humano para uso correto do protocolo.

## 4. Quando usar o navegador

Use o ChatGPT do navegador quando você precisar:
- pesquisar como sistemas maduros resolvem um módulo
- comparar decisões arquitetônicas
- fechar modelagem conceitual
- descobrir entidades, fluxos e boundaries
- decidir o que o agente pode e não pode inferir
- fechar UI/fluxos em nível de decisão
- fechar casos de uso HTTP em nível de intenção
- identificar gaps antes do repositório

NÃO use o navegador como fonte de verdade final do sistema.

## 5. Quando usar o agente do repositório

Use o agente do repositório quando você já tiver:
- decisões fechadas do módulo
- `MODULE_DECISION_IR` preenchido
- fontes canônicas definidas
- inferências proibidas explicitadas

O agente do repositório deve:
- ler o canon
- validar o IR
- bloquear se houver drift ou ambiguidade
- instanciar templates
- gerar artefatos canônicos
- validar contratos
- só então implementar

## 6. Momento certo de uso de cada camada

### 6.1 Fase de exploração
Use o navegador.
Saída esperada:
- decisões brutas
- comparação de mercado
- arquitetura do módulo
- lista de entidades
- lista de fluxos
- lista do que não pode ser inferido

### 6.2 Fase de consolidação
Use humano + IR.
Saída esperada:
- `MODULE_DECISION_IR.yaml/json`

### 6.3 Fase de conformidade
Use o gate.
Saída esperada:
- passa / bloqueia

### 6.4 Fase de materialização
Use o agente do repositório.
Saída esperada:
- docs normativas
- OpenAPI
- schemas
- artefatos condicionais aplicáveis
- implementação

## 7. Como extrair a informação certa do ChatGPT no navegador

Você NÃO deve pedir:
- “crie o módulo completo”
- “me dê os contratos finais”
- “implemente tudo”
- “decida por mim”

Você deve pedir, em ordem:

### 7.1 Perguntas para arquitetura de módulo
- Qual é a função operacional real do módulo?
- Quais entidades são obrigatórias?
- Quais fluxos são críticos?
- Quais boundaries o módulo toca?
- Quais decisões arquitetônicas aparecem repetidamente em sistemas maduros?
- O que diferencia esse módulo de um CRUD comum?
- O que pode ser inferido e o que não pode ser inferido?

### 7.2 Perguntas para modelagem
- Quais entidades são SSOT e quais são projeções?
- Quais campos mínimos cada entidade precisa?
- Quais relações existem?
- Quais entidades têm lifecycle?
- Quais regras de domínio são invariantes?
- Que tipos semânticos canônicos são necessários?

### 7.3 Perguntas para API
- Quais casos de uso HTTP são obrigatórios?
- Quais recursos principais existem?
- O que a API deve expor?
- O que a API não deve expor?
- Quais operações mínimas cada recurso precisa?

### 7.4 Perguntas para UI
- Quais fluxos do ator são obrigatórios?
- Quais telas são necessárias?
- Quais ações são obrigatórias?
- Quais estados de UI precisam existir?
- O que o agente não pode inventar na UI?

### 7.5 Perguntas para conformidade
- Quais decisões ainda estão abertas?
- Qual lacuna bloqueia materialização determinística?
- Quais registries seriam necessários?
- O que exigiria novo tipo canônico?
- O que depende de regra oficial do handebol?

## 8. Como preencher o `MODULE_DECISION_IR`

A regra é:
**nada de prosa livre onde o pipeline exigir binding.**

### 8.1 Pode usar texto curto em:
- mission
- description
- purpose
- rationale auxiliar

### 8.2 Deve usar referência canônica em:
- tipos
- enums estáveis
- termos de domínio registrados
- módulos
- eventos
- superfícies alvo
- regras linkáveis
- ownership relacional

### 8.3 Deve usar `open_decisions` quando:
- faltar tipo canônico
- faltar regra de estado
- faltar regra de handebol
- faltar semântica de erro
- faltar RBAC aplicável
- faltar workflow/evento real

## 9. O que o gate deve bloquear

O gate deve bloquear quando houver:
- schema inválido
- registry drift
- tipo sem binding canônico
- relação sem ownership/delete_policy
- lifecycle sem state model
- use case HTTP sem recurso
- UI aplicável sem fluxo
- RBAC aplicável sem permissions
- erro de domínio aplicável sem error model
- open decision bloqueante
- risco de geração não determinística

## 10. Como o agente do repositório deve operar

Modo recomendado:
- `contract_creation_mode` para criação de superfícies
- `audit_mode` para rodar conformidade
- `implementation_mode` apenas depois de readiness

Sequência:
1. carregar boot obrigatório
2. validar `MODULE_DECISION_IR`
3. rodar `DECISION_IR_CONFORMANCE_GATE`
4. mapear IR para superfícies
5. instanciar templates determinísticos
6. validar OpenAPI / Schema / docs / artefatos condicionais
7. só então implementar

## 11. Relação entre handoff e IR

O handoff continua existindo, mas agora tem papel menor.

### 11.1 O handoff deve carregar:
- objetivo da rodada
- módulo
- paths afetados
- fontes canônicas obrigatórias
- referência ao `MODULE_DECISION_IR`
- critérios de aceite
- política de bloqueio

### 11.2 O handoff NÃO deve carregar:
- a decisão normativa inteira em prosa
- modelagem completa do módulo
- regras livres
- campos sem binding

Esses conteúdos ficam no IR.

## 12. Sinal de que o protocolo está sendo usado corretamente

O protocolo está saudável quando:
- o navegador gera decisão, não contrato final
- o IR fecha decisões em forma tipada
- o gate encontra gaps antes da materialização
- o agente do repositório não precisa escolher nomes, estados, tipos ou relações
- a implementação começa apenas após readiness contratual

## 13. Sinais de uso incorreto

Você está usando errado quando:
- o ChatGPT do navegador gera contrato final em prosa
- o IR usa “string/int” sem tipo semântico
- o agente precisa decidir `operationId`, tags, enums ou ownership
- o gate passa mesmo com `open_decision` bloqueante
- o repositório recebe conversa em vez de IR

## 14. Fluxo resumido para humanos

1. Pesquise no navegador
2. Feche decisões
3. Preencha o `MODULE_DECISION_IR`
4. Rode o gate
5. Corrija bloqueios
6. Entregue ao agente do repositório
7. Materialize superfícies
8. Valide contratos
9. Implemente

## 15. Regra final

**Sem IR validado, não há materialização.**
**Sem materialização validada, não há implementação.**
