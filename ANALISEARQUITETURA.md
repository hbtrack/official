# Auditoria Sênior de Arquitetura e Documentação Arquitetural

> ⚠️ **ARTEFATO DERIVADO — NON-SOVEREIGN**: Este arquivo é uma auditoria arquitetural derivada. Não possui autoridade normativa. Não deve ser usado para redefinir schemas, gates, contratos ou políticas canônicas. Em caso de conflito, prevalecem: `scripts/hb` + `validate_contracts.py` > `contracts/schemas/` > `docs/_canon/` > `.contract_driven/CONTRACT_SYSTEM_RULES.md` > este arquivo.

## PARTE 1 — Visão geral da documentação arquitetural

### Artefatos arquiteturais identificados

**Visão macro e estrutura**
- `docs/_canon/ARCHITECTURE.md`
- `docs/_canon/C4_CONTEXT.md`
- `docs/_canon/C4_CONTAINERS.md`
- `docs/_canon/CODE_ARCHITECTURE.md`
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/MODULE_MAP.md`

**Fronteiras, autoridade e lifecycle**
- `docs/_canon/SCOPE_BOUNDARY_POLICY.md`
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `docs/_canon/MODULE_REGISTRY.yaml`

**Decisão arquitetural e governança**
- `docs/_canon/DECISION_POLICY.md`
- `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md`
- `docs/_canon/decisions/ADR-026-code-architecture.md`
- `docs/_canon/decisions/ADR-030-frontend-strategy.md`
- `docs/_canon/decisions/ADR-031-backend-framework.md`
- `docs/_canon/decisions/ADR-034-scope-boundary-validation.md`

**Arquitetura alvo ainda não materializada**
- `docs/_canon/FRONTEND_CONTRACT.md`
- `docs/_canon/DEPLOY_PIPELINE.md`

### Papel geral que o conjunto tenta cumprir

O conjunto tenta cobrir quatro camadas diferentes:

1. **Arquitetura macro do produto e do sistema**: missão, módulos, boundaries, stack e C4.
2. **Arquitetura de código**: organização em camadas e mapeamento para `src/`.
3. **Governança arquitetural**: ADRs, backlog de decisões, policies de boundary e autoridade.
4. **Target-state operacional**: frontend futuro, deploy futuro, workers, WebSocket e rollout.

### Diagnóstico geral do conjunto

O conjunto é **amplo em cobertura**, mas **parcial e frágil em utilidade arquitetural real**.

Ele é forte em **governança normativa** e em **taxonomia de módulos**, mas falha em um ponto central: **não separa com disciplina o que é estado atual comprovado do que é target-state aprovado**. Isso gera três efeitos práticos:

- documentos macro e C4 vendem runtime atual que o repositório ainda não materializa;
- artefatos de governança repetem e contradizem decisões estruturais;
- a documentação ajuda a discutir arquitetura, mas ainda não ajuda com confiabilidade equivalente a navegar o sistema real.

**Síntese**: o conjunto parece **maduro em intenção**, **parcial em aderência** e **frágil como espelho fiel do sistema em execução**.

> Nota: templates em `.contract_driven/templates/globais/` foram tratados como moldes, não como artefatos arquiteturais ativos do sistema.

---

## PARTE 2 — Avaliação por arquivo

| Arquivo | Objetivo esperado | Cumpre o objetivo? | Principais problemas | Impacto prático | Veredito |
|--------|-------------------|--------------------|----------------------|-----------------|----------|
| `docs/_canon/ARCHITECTURE.md` | Ser a visão macro oficial: princípios, stack, camadas, restrições e baseline de ambiente | parcialmente | Mistura current-state e target-state; conflita com o runtime real em Python/PostgreSQL/Celery/Channels/frontend; modela camadas como `Router → Service → Repository`, enquanto o código real está mais próximo de `Interface → Application → Domain → Infrastructure`; afirma `X-Flow-ID` end-to-end sem implementação correspondente | Orienta algumas decisões, mas também induz leitura errada do sistema atual | desalinhado |
| `docs/_canon/C4_CONTEXT.md` | Explicar o contexto externo do sistema, atores e integrações relevantes | não | Genérico demais; não diferencia integrações atuais de planejadas; não ajuda a decidir trust boundaries, auth, observabilidade ou integrações reais | Serve como ilustração superficial, não como artefato de arquitetura útil | fraco |
| `docs/_canon/C4_CONTAINERS.md` | Explicar containers/runtime deployáveis e suas relações | não | Não representa os containers reais do repo; omite Redis como peça arquitetural relevante; trata storage como container interno, enquanto outros docs o tratam como externo; pressupõe web app atual que não existe no workspace | Atrasa decisões de deploy, capacidade, integração e troubleshooting | fraco |
| `docs/_canon/CODE_ARCHITECTURE.md` | Traduzir a arquitetura para organização de código e regras de implementação | parcialmente | É o artefato que mais se aproxima do `src/`, mas tem regra de dependência ambígua, path de testes divergente, cita `config/celery.py` inexistente e declara o `CODE_ARCHITECTURE_GATE` como `SKIP_NOT_APPLICABLE` mesmo com gate já ativo e código materializado | Muito útil para navegar o backend, mas ainda não fecha a lacuna entre regra e runtime | útil mas incompleto |
| `docs/_canon/SYSTEM_SCOPE.md` | Delimitar missão, atores, macrodomínios, dependências externas e fora de escopo | parcialmente | É forte na delimitação de produto, mas embute como estado atual uma arquitetura técnica ainda não totalmente materializada; dependências externas estão subespecificadas frente ao restante do conjunto | Bom para evitar scope creep; insuficiente para representar a arquitetura operacional | útil mas incompleto |
| `docs/_canon/MODULE_MAP.md` | Definir os 17 módulos, suas responsabilidades, dependências e fronteiras críticas | parcialmente | Taxonomia é boa, mas as colunas `UI`, `Workers` e `Eventos` superestimam a implementação real; workers Celery e UI são tratados como existentes por módulo sem respaldo no runtime atual | Ajuda decisões de boundary; atrapalha planejamento técnico se lido como estado atual | útil mas incompleto |
| `docs/_canon/SCOPE_BOUNDARY_POLICY.md` | Ser SSOT das referências cross-module permitidas/proibidas | parcialmente | É forte como política de gate, mas fraca como explicação arquitetural para humanos; não mostra flows, ownership ou exemplos do runtime real; depende de uma ADR com numeração conflituosa | Boa para bloquear overflow de escopo; pouco eficiente para onboarding e design review | útil mas incompleto |
| `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml` | Definir autoridade de fonte e limites de inferência por módulo | parcialmente | Útil para governança de IA e de domínio, mas não descreve arquitetura de runtime, integrações, componentes ou mecanismos reais; complementa boundary, não substitui arquitetura | Reduz inferência indevida, mas não resolve entendimento estrutural do sistema | útil mas incompleto |
| `docs/_canon/MODULE_REGISTRY.yaml` | Refletir o estado operacional/lifecycle de cada módulo e suas superfícies esperadas | não | Os módulos seguem marcados como `implementation_ready`, embora o repo já tenha `src/<module>/`, migrations e testes; como inventário de lifecycle, está atrasado em relação ao sistema real | Pode distorcer readiness, priorização e decisões de promoção | desalinhado |
| `docs/_canon/DECISION_POLICY.md` | Governar quando e como decisões arquiteturais são abertas, promovidas e bloqueadas | parcialmente | A política em si é boa, mas opera sobre um conjunto de ADRs com rastreabilidade inconsistente; não captura drift documental como dívida arquitetural formal | Processo de decisão existe, mas não garante coerência do corpus arquitetural | útil mas incompleto |
| `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` | Ser o backlog vivo de decisões arquiteturais pendentes | parcialmente | O backlog se declara praticamente resolvido, enquanto permanecem gaps estruturais de documentação atual vs target-state; não vira radar da dívida arquitetural documental | Cria falsa percepção de arquitetura “resolvida” | útil mas incompleto |
| `docs/_canon/FRONTEND_CONTRACT.md` | Definir o target-state normativo do frontend | parcialmente | É explícito ao dizer que é target-state e que o worker está congelado, o que é bom; o problema é que os artefatos macro do sistema não preservam essa mesma distinção | Útil para planejar o frontend; insuficiente para entender o sistema atual | útil mas incompleto |
| `docs/_canon/DEPLOY_PIPELINE.md` | Definir a arquitetura e o fluxo de deploy | parcialmente | Também é explícito ao dizer que a automação é parcial, mas continua descrevendo um target-state com assets e `/health` ausentes no repo; não documenta o estado operacional atual além do mínimo | Serve como roadmap de deploy, não como espelho da operação atual | útil mas incompleto |
| `docs/_canon/decisions/ADR-030-frontend-strategy.md` | Registrar a decisão de plataforma frontend e sequencing web→mobile | sim | A decisão é clara e ainda faz sentido mesmo sem frontend implementado; o problema maior está nos documentos que a tratam como já materializada | Boa base para decisão de roadmap | forte |
| `docs/_canon/decisions/ADR-031-backend-framework.md` | Registrar a decisão de stack backend | parcialmente | A decisão de stack é útil, mas mistura decisão com consequências ainda não implementadas; conflita com o runtime real e com outra ADR usando o mesmo número `031`; ainda cita Jest enquanto `ARCHITECTURE.md` já migrou a narrativa para Vitest | A decisão existe, mas a rastreabilidade e a aderência operacional estão fracas | desalinhado |
| `docs/_canon/decisions/ADR-034-scope-boundary-validation.md` | Registrar a decisão de validação de boundary entre módulos | não | O conteúdo é relevante, mas originalmente reutilizava o `adr_id` de uma ADR aceita e estruturalmente distinta; enquanto isso ocorreu, quebrou rastreabilidade de qualquer referência a “ADR-031” | Introduz ambiguidade grave em referências arquiteturais e de governança até ser renumerada | desalinhado |
| `docs/_canon/decisions/ADR-026-code-architecture.md` | Registrar a decisão base da arquitetura de código | não | Continua aceito, mas a parte mais sensível da decisão foi superseded; ainda descreve FastAPI/SQLAlchemy/React Native como stack base | Se lido isoladamente, induz implementações fora da arquitetura atual | obsoleto |

---

## PARTE 3 — Coerência entre os artefatos

### Onde o conjunto se complementa bem

- `SYSTEM_SCOPE.md` + `MODULE_MAP.md` + `SCOPE_BOUNDARY_POLICY.md` formam um bom núcleo para discutir **escopo**, **módulos** e **fronteiras funcionais**.
- `CODE_ARCHITECTURE.md` é o melhor elo entre documentação e código real do backend.
- `DECISION_POLICY.md` + `ARCHITECTURE_DECISION_BACKLOG.md` + coleção de ADRs formam uma boa trilha para **governança de decisão**, embora não para refletir o runtime atual.

### Onde há contradição ou drift interno

1. **Stack e ambiente**:
   - `ARCHITECTURE.md` e `ADR-031-backend-framework.md` tratam Python 3.12/PostgreSQL 16/Celery/Channels como baseline.
   - `ARCHITECTURE.md` seção de ambiente cita Python 3.11.9 e referência a `postgres15`.
   - `infra/docker-compose.yml` está em PostgreSQL 12 e só sobe `postgres` e `redis`.

2. **Modelo de camadas**:
   - `ARCHITECTURE.md` fala em `Router → Service → Repository → Database`.
   - `CODE_ARCHITECTURE.md` fala em `Interface → Application → Domain → Infrastructure`.
   - O código real usa mais claramente `api.py` + `application/use_cases.py` + `domain/*` + `infrastructure/*`.

3. **Frontend**:
   - `FRONTEND_CONTRACT.md` diz explicitamente que o frontend ainda é target-state.
   - `ARCHITECTURE.md`, `C4_CONTAINERS.md` e parte do conjunto falam do web app como container atual.
   - O repo não possui `frontend/`, e `package.json` não é um app frontend real.

4. **Deploy/runtime**:
   - `DEPLOY_PIPELINE.md` assume `/health` e assets de deploy ainda ausentes.
   - O runtime atual não expõe `/health`, não possui `Dockerfile`, `docker-compose.prod.yml` nem `nginx.conf`.

5. **Rastreabilidade de ADR**:
   - Há **duas ADRs com `ADR-031`**.
   - Isso torna ambíguas referências em docs, código e rules.

### Onde há repetição desnecessária

- **Stack** é repetida em `ARCHITECTURE.md`, `CODE_ARCHITECTURE.md`, `ADR-031-backend-framework.md`, `DEPLOY_PIPELINE.md`.
- **Módulos e boundaries** são repetidos em `SYSTEM_SCOPE.md`, `MODULE_MAP.md`, `SCOPE_BOUNDARY_POLICY.md`, `MODULE_SOURCE_AUTHORITY_MATRIX.yaml`.
- **Frontend target-state** é repetido em `ARCHITECTURE.md`, `FRONTEND_CONTRACT.md`, `ADR-030`.

O problema não é a repetição em si. O problema é **repetição sem fonte factual única**, o que acelera drift.

### Cobertura de contexto, containers, componentes, responsabilidades e integrações

- **Contexto**: coberto de forma superficial.
- **Containers**: coberto de forma insuficiente e não aderente ao runtime real.
- **Componentes**: **gap importante**; não existe `C4_COMPONENTS` ou equivalente útil.
- **Responsabilidades e fronteiras**: relativamente bem cobertas.
- **Integrações**: cobertas mais como intenção/contrato do que como arquitetura real executável.

**Veredito do conjunto**: os artefatos **não funcionam ainda como um sistema arquitetural plenamente coerente**. Funcionam melhor como **governança normativa + target-state** do que como **documentação arquitetural fiel do sistema atual**.

---

## PARTE 4 — Drift entre documentação e sistema real

### Drift comprovado entre documentos e repositório

1. **Backend real existe e está mais implementado do que o registry admite**
- O repo possui 17 apps Django em `src/` com `api.py`, `models.py`, `schemas.py`, `application/`, `domain/`, `infrastructure/`, migrations e testes.
- Mesmo assim, `MODULE_REGISTRY.yaml` ainda marca todos como `implementation_ready`, não `implemented`.

2. **A arquitetura de código real bate mais com `CODE_ARCHITECTURE.md` do que com `ARCHITECTURE.md`**
- `config/urls.py` monta `NinjaAPI`.
- Os módulos usam `api.py` + `application/use_cases.py` + `domain/*` + `infrastructure/repository.py`.
- `ARCHITECTURE.md` omite `Domain` como camada explícita e usa o termo `Service`, que não é o modelo mais fiel ao código atual.

3. **Celery e Channels são tratados como parte do sistema atual, mas não aparecem no runtime**
- Não existe `tasks.py` em nenhum módulo.
- Não existe `config/celery.py`.
- Não há código de `channels`, `websocket`, `AsyncWebsocketConsumer` ou equivalente em `src/`/`config/`.
- Mesmo assim, `ARCHITECTURE.md`, `MODULE_MAP.md` e `ADR-031-backend-framework.md` tratam workers e WebSocket como baseline arquitetural.

4. **Frontend atual não existe no workspace**
- Não há diretório `frontend/`.
- `package.json` contém ferramentas de validação/geração contratual, não uma app React/Vite.
- `FRONTEND_CONTRACT.md` admite isso.
- `ARCHITECTURE.md` e `C4_CONTAINERS.md` não preservam essa distinção com clareza suficiente.

5. **Baseline de ambiente está inconsistente**
- `config/settings.py` declara stack Django + PostgreSQL e opera localmente em porta `5433`.
- `infra/docker-compose.yml` usa `postgres:12`.
- `ARCHITECTURE.md` declara PostgreSQL 16 como baseline e também traz referências conflitantes a Python 3.11.9 e `postgres15`.

6. **Observabilidade documentada não está materializada**
- `ARCHITECTURE.md` e `ADR-013` tratam `X-Flow-ID` como propagado end-to-end.
- Não foi encontrada implementação de middleware/propagação em `config/` ou `src/`.
- O que existe é apenas suporte pontual a `correlation_id` no módulo `audit`.

7. **Health check documentado não existe**
- `DEPLOY_PIPELINE.md` e workflow de deploy esperam `GET /health`.
- Não há rota `/health` no código.

8. **ADR numbering conflict**
- `docs/_canon/decisions/ADR-031-backend-framework.md`
- `docs/_canon/decisions/ADR-034-scope-boundary-validation.md`
- Isso torna referências a `ADR-031` semanticamente ambíguas.

9. **`CODE_ARCHITECTURE.md` está parcialmente alinhado, mas não totalmente**
- O gate `CODE_ARCHITECTURE_GATE` já aparece como `PASS` no relatório canônico.
- O documento ainda se descreve como `SKIP_NOT_APPLICABLE até primeira implementação`.

### Drift positivo

Nem tudo é drift negativo:

- Os módulos reais quase não têm imports cross-module diretos; isso sugere que o código atual **não está violando** as fronteiras documentadas de forma evidente.
- A taxonomia dos 17 módulos em `SYSTEM_SCOPE.md`/`MODULE_MAP.md` está aderente ao diretório `src/`.
- Há lastro contratual assíncrono em `contracts/asyncapi/`, mesmo que o runtime de workers ainda não esteja materializado.

---

## PARTE 5 — Gaps arquiteturais

Para que a documentação arquitetural cumpra a função que deveria cumprir, ainda faltam:

1. **Separação explícita entre `estado atual` e `target-state`**
- Hoje isso está implícito e distribuído.
- É a principal causa de ambiguidades.

2. **Um artefato de runtime atual**
- Falta um documento curto e factual, algo como `RUNTIME_CURRENT_STATE.md`, para responder:
  - o que existe hoje;
  - o que é só contrato;
  - o que é só roadmap;
  - o que ainda está congelado.

3. **C4 de componentes**
- Não existe `C4_COMPONENTS` ou equivalente para o backend.
- Isso deixa um buraco entre `C4_CONTAINERS` e `CODE_ARCHITECTURE.md`.

4. **Arquitetura de integrações e fluxos críticos**
- Faltam flows claros para:
  - autenticação/sessão;
  - treinamento → wellness → analytics → reports;
  - notificações;
  - ingestão/IA;
  - eventos de vídeo e scout.

5. **Fonte factual única para stack e versões**
- Hoje o mesmo assunto aparece em vários lugares sem mecanismo de sincronização.

6. **Política de supersession e unicidade de ADR**
- O conflito de `ADR-031` mostra que a governança de decisões não está blindada.

7. **Validação automática de drift arquitetural**
- A documentação ainda depende demais de revisão manual.
- Falta um checker automatizado que compare claims arquiteturais com:
  - `src/`
  - `config/`
  - `infra/`
  - `package.json`
  - endpoints reais
  - assets de deploy

8. **Clarificação do papel dos artefatos de governança vs artefatos de arquitetura**
- `MODULE_SOURCE_AUTHORITY_MATRIX` e `SCOPE_BOUNDARY_POLICY` são úteis, mas não substituem documentação de estrutura e runtime.

9. **Aderência entre lifecycle documental e lifecycle real**
- `MODULE_REGISTRY.yaml` precisa refletir o estágio real dos módulos.

---

## PARTE 6 — Recomendação final

### Respostas objetivas

- **Os arquivos de arquitetura cumprem seus objetivos?** parcialmente
- **Quais cumprem melhor?**
  - `docs/_canon/CODE_ARCHITECTURE.md`
  - `docs/_canon/SYSTEM_SCOPE.md`
  - `docs/_canon/MODULE_MAP.md`
  - `docs/_canon/decisions/ADR-030-frontend-strategy.md`
- **Quais falham mais?**
  - `docs/_canon/C4_CONTEXT.md`
  - `docs/_canon/C4_CONTAINERS.md`
  - `docs/_canon/MODULE_REGISTRY.yaml`
  - `docs/_canon/decisions/ADR-034-scope-boundary-validation.md`
  - `docs/_canon/decisions/ADR-026-code-architecture.md`
- **O conjunto atual é suficiente para sustentar evolução segura do sistema?** não
- **O que deve ser corrigido, consolidado, removido ou criado?**
  - corrigir a separação current-state vs target-state;
  - consolidar stack/runtime em uma fonte factual única;
  - consertar a rastreabilidade de ADRs;
  - reescrever os C4 com aderência ao sistema real;
  - alinhar `MODULE_REGISTRY` e `MODULE_MAP` ao runtime;
  - criar artefatos faltantes de componentes, flows e runtime atual;
  - automatizar validação de drift arquitetural.

### Plano de correções em ordem de execução

#### Fase 1 — Higienização de governança e rastreabilidade

**Objetivo**: eliminar ambiguidades que contaminam o restante da documentação.

Checklist:
- [X] Renumerar `docs/_canon/decisions/ADR-031-scope-boundary-validation.md` para o próximo número livre.
- [X] Atualizar todas as referências a essa ADR em `docs/_canon/`, `.contract_driven/`, regras e gates.
- [X] Marcar explicitamente ADR-026 como superseded no front matter e no topo do arquivo.
- [X] Revisar ADR-031-backend-framework para deixar claro o que é decisão aceita e o que ainda é target-state não implementado.
- [X] Adicionar um campo explícito de semântica de estado (`current-state`, `target-state`, `governance`) nos artefatos arquiteturais principais.

Impacto esperado:
- elimina ambiguidade de decisão;
- evita leitura errada de referências cruzadas;
- cria base limpa para reescrever arquitetura sem contradições.

Validação da fase:
- [X] Não existe mais ADR duplicada por ID.
- [X] Todo artefato arquitetural principal declara semântica de estado.
- [X] `ADR-026`, `ADR-030`, ADR renumerada de boundary e `ADR-031-backend-framework` têm relação de supersession explícita e não ambígua.

#### Fase 2 — Reescrita da visão macro e dos C4

**Objetivo**: fazer a documentação macro refletir o sistema atual sem apagar o target-state.

Checklist:
- [X] Reescrever `docs/_canon/ARCHITECTURE.md` com duas seções distintas:
  - `Estado atual comprovado`
  - `Target-state aprovado`
- [X] Corrigir a seção de ambiente para bater com `config/settings.py` e `infra/docker-compose.yml`, ou marcar explicitamente como target-state.
- [X] Reescrever `docs/_canon/C4_CONTEXT.md` com atores e sistemas externos reais ou explicitamente planejados.
- [X] Reescrever `docs/_canon/C4_CONTAINERS.md` separando:
  - containers atuais;
  - containers planejados;
  - dependências externas.
- [X] Harmonizar `ARCHITECTURE.md`, `C4_CONTAINERS.md` e `SYSTEM_SCOPE.md` sobre storage externo, frontend inexistente e runtime atual.

Impacto esperado:
- reduz ambiguidade para onboarding técnico;
- evita decisões de deploy e integração baseadas em diagramas fictícios;
- torna os C4 úteis de fato.

Validação da fase:
- [X] Nenhum C4 descreve container inexistente como ativo sem marcar target-state.
- [X] `ARCHITECTURE.md`, `SYSTEM_SCOPE.md` e `C4_CONTAINERS.md` concordam sobre frontend, workers, storage e ambiente.
- [X] A visão macro pode ser conferida diretamente contra `src/`, `config/`, `infra/` e `package.json`.

#### Fase 3 — Alinhamento da arquitetura de código e do lifecycle de módulos

**Objetivo**: alinhar estrutura documental com backend real.

Checklist:
- [X] Atualizar `docs/_canon/CODE_ARCHITECTURE.md` para refletir a arquitetura efetiva:
  - `Interface / API`
  - `Application / Use Cases`
  - `Domain`
  - `Infrastructure`
- [X] Trocar a narrativa de `Service` por `Application Use Cases`, ou explicar formalmente que os use cases são a service layer.
- [X] Corrigir paths de testes para refletir `src/<module>/tests/`.
- [X] Remover ou marcar como target-state referências a `config/celery.py`, `tasks.py`, `shared_task`, WebSocket e afins enquanto não existirem.
- [X] Atualizar `MODULE_MAP.md` separando:
  - responsabilidade do módulo;
  - superfícies contratuais existentes;
  - runtime atual;
  - target-state.
- [X] Atualizar `MODULE_REGISTRY.yaml` para o status real dos módulos que já têm código, migrations e testes.

Impacto esperado:
- transforma a documentação de código em guia navegável real;
- reduz ambiguidade entre arquitetura conceitual e estrutura concreta;
- melhora readiness e priorização.

Validação da fase:
- [X] O `CODE_ARCHITECTURE.md` descreve paths e camadas que existem no repo.
- [X] `MODULE_MAP.md` não marca worker/UI como runtime atual quando eles não existem.
- [X] `MODULE_REGISTRY.yaml` reflete o lifecycle real dos módulos presentes em `src/`.

#### Fase 4 — Criação dos artefatos que faltam

**Objetivo**: fechar os buracos entre visão macro, código e operação.

Checklist:
- [X] Criar `docs/_canon/C4_COMPONENTS_BACKEND.md` ou equivalente.
- [X] Criar `docs/_canon/RUNTIME_CURRENT_STATE.md`.
- [X] Criar `docs/_canon/INTEGRATION_FLOWS.md` com pelo menos:
  - auth/session;
  - training → wellness → analytics → reports;
  - notifications;
  - video/scout;
  - ai_ingestion.
- [X] Criar um artefato de observabilidade real apenas se houver implementação correspondente; caso contrário, reduzir a claim em `ARCHITECTURE.md`. _(X-Flow-ID não possui middleware; claim reduzida/explicitada em ARCHITECTURE.md §5 itens 6 e 7; `correlation_id` pontual do módulo `audit` documentado em RUNTIME_CURRENT_STATE.md.)_
- [X] Criar um índice de decisões arquiteturais com status, superseded_by e tema.

Impacto esperado:
- fecha a lacuna entre C4 e código;
- melhora decisão técnica sobre integrações e evolução;
- reduz dependência de interpretação humana tácita.

Validação da fase:
- [X] Existe um artefato de componentes navegável.
- [X] Existe um documento factual de runtime atual.
- [X] Os principais fluxos críticos têm diagrama/descrição de ponta a ponta.
- [X] Todas as ADRs podem ser resolvidas a partir de um índice único e não ambíguo.

#### Fase 5 — Automação de validação de drift arquitetural

**Objetivo**: impedir que a documentação volte a divergir silenciosamente do sistema.

Checklist:
- [X] Criar um checker automatizado de arquitetura, por exemplo `scripts/audit/check_architecture_docs.py`.
- [X] Validar automaticamente, no mínimo:
  - unicidade de `adr_id`;
  - consistência de versões de Python/PostgreSQL entre docs e infra;
  - ausência de claims de frontend atual se `frontend/` não existir;
  - ausência de claims de Celery/Channels/WebSocket como runtime atual se não houver código correspondente;
  - coerência de `MODULE_REGISTRY.yaml` com a existência de `src/<module>/`, migrations e testes;
  - existência de `/health` antes de tratar deploy como operacional.
- [X] Integrar o checker ao pipeline CI.
- [X] Criar testes de regressão para o checker.

Impacto esperado:
- reduz drift manual;
- transforma arquitetura em artefato verificável;
- preserva valor dos documentos ao longo da evolução do sistema.

Validação da fase:
- [X] O checker falha quando uma claim arquitetural diverge do repo.
- [X] O checker passa quando docs e código estão coerentes.
- [X] O pipeline CI executa esse checker como parte do baseline.

#### Fase 6 — Validação final do pacote arquitetural corrigido

**Objetivo**: garantir que os arquivos ajustados realmente cumprem sua função após a correção.

Checklist:
- [X] Validar coerência cruzada entre `ARCHITECTURE.md`, `C4_CONTEXT.md`, `C4_CONTAINERS.md`, `CODE_ARCHITECTURE.md`, `SYSTEM_SCOPE.md`, `MODULE_MAP.md`, `MODULE_REGISTRY.yaml`.
- [X] Rodar checker de drift arquitetural.
- [X] Rodar `python3 manage.py check`.
- [X] Rodar a suíte relevante de testes.
- [X] Rodar `python3 scripts/contracts/validate/validate_contracts.py --profile ci`.
- [X] Confirmar que nenhum documento macro descreve como atual algo que o repositório ainda não implementa.

### Validação adicional — alinhamento com `.contract_driven`

Resultado da revalidação após as correções executadas:

- [X] `ARCHITECTURE.md`, `SYSTEM_SCOPE.md`, `C4_CONTEXT.md` e `C4_CONTAINERS.md` agora cumprem o papel de docs globais de governança sem sobrepor `RULES`, `LAYOUT`, contratos técnicos ou `MODULE_REGISTRY`.
- [X] `CODE_ARCHITECTURE.md` agora cumpre o objetivo operacional esperado por `.contract_driven/agent_prompts/generate_code.prompt.md`: orientar implementação a partir de paths, camadas e ausências reais do backend.
- [X] `MODULE_MAP.md` deixou de usar booleans genéricos de UI/workers como se fossem runtime atual e passou a separar responsabilidade, contratos existentes e runtime comprovado.
- [X] `MODULE_REGISTRY.yaml` e `FEATURE_REGISTRY.yaml` agora refletem o lifecycle materializado no repo (`src/`, migrations, testes e features implementadas), reduzindo conflito com `CONTRACT_PIPELINE.md`.
- [X] A leitura correta de `current-state` versus `target-state` ficou explícita nos artefatos macro, eliminando a ambiguidade que antes entrava em conflito com a regra de "bloquear em vez de inferir" de `.contract_driven/CONTRACT_SYSTEM_RULES.md`.

Evidências executadas:

- [X] `.venv/bin/python manage.py check` → `System check identified no issues (0 silenced).`
- [X] `.venv/bin/pytest tests/pipeline_gates/ -q` → `67 passed, 1 skipped`
- [X] `python3 scripts/audit/check_architecture_docs.py --json` → `PASS 6/6`
- [X] `timeout 120 .venv/bin/python scripts/contracts/validate/validate_contracts.py --profile ci` → `STATUS: PASS` (47 PASS, 3 SKIP_NOT_APPLICABLE, 0 FAIL)

Correções aplicadas durante FASE 6:
- [X] `C4_COMPONENTS_BACKEND.md`, `INTEGRATION_FLOWS.md`, `RUNTIME_CURRENT_STATE.md` e `ADR_INDEX.md` registrados em `docs/_canon/README.md` e no `TOPLEVEL_ALLOWLIST` do gate `CANON_ALLOWLIST_GATE`.
- [X] `ADR_INDEX.md` movido de `docs/_canon/decisions/` para `docs/_canon/` (arquivo é índice, não ADR — segue formato correto agora).
- [X] Referência em `ARCHITECTURE.md` §7 atualizada para novo path.

Resultado esperado ao final do plano:
- a documentação passa a separar claramente estado atual de target-state;
- os C4 passam a ser úteis para decisão técnica;
- a arquitetura de código fica aderente ao backend real;
- lifecycle e boundaries deixam de conflitar com a implementação;
- o conjunto passa a sustentar evolução segura com menor risco de drift.
