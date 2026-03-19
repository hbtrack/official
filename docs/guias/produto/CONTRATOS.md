# Auditoria de Contratos Finais — HB Track API
**Data:** 2026-03-19
**Auditor:** Claude (postura: auditor sênior de contratos, sem benefício da dúvida)
**Escopo:** Contratos finais gerados — `contracts/openapi/openapi.yaml` + `contracts/openapi/paths/*.yaml` + `contracts/openapi/components/schemas/*`
**Questão central:** Este contrato é fonte de verdade real para geração downstream de API, módulos e componentes?

---

## PARTE 1 — Veredito Geral

**contrato parcialmente robusto** — com falhas estruturais que impedem uso como SSOT confiável

Os path contracts (`paths/*.yaml`) são funcionalmente densos: referenciam domain rules, invariantes, ADRs, enums e regras OWASP com precisão razoável. Módulos como `training`, `users` e `identity_access` mostram intenção normativa real.

O problema é sistêmico e inviabiliza o veredito "robusto de verdade": **a maioria dos schemas referenciados nos paths são stubs de 3 a 5 campos**, enquanto os schemas canônicos completos existem em `contracts/schemas/` mas não são $ref'd no OpenAPI. Um implementador que gere código a partir do contrato OpenAPI obtém modelos de resposta amputados. Além disso, 58 operações referenciam um security scheme (`bearerAuth`) que não está definido no `openapi.yaml` raiz — tornando a autenticação tecnicamente quebrada no contrato. Há dois schemas de erro paralelos incompatíveis. Um role não canônico (`match_operator`) aparece no contrato de vídeo sem definição RBAC. Endpoints críticos têm `security: [{}]` como placeholder.

O contrato parece forte na leitura superficial. Falha na derivação real.

---

## PARTE 2 — Score de Robustez

| Critério | Nota | Justificativa objetiva |
|---------|------|------------------------|
| Capacidade de governar geração downstream | **42** | Os paths têm intenção normativa, mas a maioria dos schemas referenciados são stubs. `match.yaml` tem 4 campos; o schema canônico tem 15+. Geração de código a partir do OpenAPI produz modelos incompletos para matches, medical, scout, analytics, audit, sessões de auth. Apenas training e users têm schemas completos no OpenAPI. |
| Clareza normativa | **61** | Regras de domínio (DR-XXX), invariantes (INV-XXX), ADRs e OWASP são citados consistentemente. Porém, "medical access", "owner or admin/coordinator" e "dentro da organização" são normativos apenas em prosa, sem encoding verificável. |
| Determinismo | **38** | State machines (match statusLabel, training status) estão em prose descriptions. Cross-field constraints (homeTeamId ≠ awayTeamId, startedAt ≤ endedAt) declaradas mas não verificáveis pelo schema. Paginação mista (cursor vs offset) sem política declarada. `filterExpression` em analytics é free-text sem DSL. |
| Ausência de ambiguidade | **44** | `match_operator` aparece em vídeo mas não está no RBAC canônico. "Team staff with medical access" não mapeia para nenhum dos 5 roles. "Coordinator dentro da organização" não tem organizationId como parâmetro na operação. `bearerAuth` indefinido. Dois schemas de erro com estruturas diferentes coexistem. |
| Acionabilidade | **48** | Modules como training são acionáveis (schema rico, regras detalhadas). Para matches, medical, scout, analytics — o schema retornado pelo endpoint é um stub. Implementador deve inferir o shape real de `contracts/schemas/` ou da descrição em prosa dos paths. |
| Verificabilidade | **35** | `security: [{}]` em 4 operações de users = contrato não verificável para autenticação nessas rotas. `bearerAuth` indefinido = 58 operações com security schema quebrado. Cross-field constraints não verificáveis em schema. Regras de acesso RBAC em texto, não em machine-readable policy. |
| Cobertura de cenários | **55** | Happy path bem coberto. Cenários de erro parciais (400/401/403/404 presentes em maioria). Sem nenhum 500 definido. Sem 409 em vários módulos que deveriam ter (ex: criar partida duplicada). Deleção de medical record sem definição do comportamento após soft-delete em leituras subsequentes. |
| Tratamento de exceções | **40** | Ausência total de 500 em todos os módulos. Conflito de constraint (INV-MED-002: returnToPlay implies returnToTraining) mapeado para 400 mas sem body especificando qual constraint violada. `completeScoutSession` em partida cancelada não tem resposta definida. Remoção de atleta de lineup durante overtime não coberta. |
| Consistência interna | **33** | Duas error schemas (`common/error.yaml` e `shared/problem.yaml`) com estruturas incompatíveis usadas em módulos diferentes. Dois security schemes (`bearerAuth` e `HTTPBearer`) onde um não está definido. Paginação cursor-based (users, identity_access, training) vs offset-based (matches, teams, seasons) sem política. |
| Resistência a interpretação frouxa | **40** | RBAC rules em texto livre permitem interpretações divergentes. `filterExpression` sem DSL. `eventLabel` sem enum (apesar de referir taxonomia canônica). State machine como prose. `match_operator` como role não canônico abre espaço para invenção. |
| Capacidade de servir como fonte de verdade | **39** | Para gerar código somente do OpenAPI: schemas de resposta de 7+ módulos estão incompletos. Security scheme quebrado em 10 módulos. Error schema inconsistente. O contrato não é auto-suficiente — requer leitura de `contracts/schemas/`, `CONTRACT_SYSTEM_RULES.md`, ADRs e domain docs para fechar os gaps. |
| Robustez real vs qualidade aparente | **32** | Esta é a divergência mais crítica. Leitura superficial: paths ricos, muitas referências normativas, OWASP citado, invariantes nomeados. Leitura técnica: schemas amputados, security quebrado, inconsistências estruturais, regras acionáveis apenas por humano. Aparência > substância. |

**Nota final consolidada: 42 / 100**

**Por que não merece 100/100:** Há cinco falhas que isoladamente cada uma impediria nota acima de 60: (1) schemas de resposta são stubs para a maioria dos módulos; (2) 58 operações têm security scheme inválido (`bearerAuth` indefinido); (3) dois schemas de erro incompatíveis sem política; (4) role `match_operator` sem definição RBAC; (5) múltiplas regras normativas codificadas apenas em prosa, incluindo state machines, autorização granular e constraints cross-field.

---

## PARTE 3 — Sinais de "Contrato Bonito"

| Trecho/ponto | Por que parece forte | Por que é fraco na prática | Impacto downstream | Severidade |
|-------------|----------------------|----------------------------|--------------------|------------|
| Citações de DR-XXX, INV-XXX, HBR-XXX em descriptions | Transmite que há sistema normativo por trás; impressiona pela rastreabilidade | São referências a documentos externos. O contrato em si não incorpora as regras — apenas as nomeia. Implementador precisa buscar o documento referenciado para saber o que a regra diz. | Duas implementações podem interpretar DR-MATCH-003 de formas diferentes sem violar o contrato textualmente | ALTA |
| `additionalProperties: false` em requestBodies | Parece proteção contra BOPLA (OWASP API3) | Não tem efeito normativo quando o schema de response (`match.yaml`, `auth_session.yaml`) não reflete o shape real — implementador que gera cliente a partir do response schema obtém objeto com 3–4 campos | Cliente gerado ignora campos reais da resposta | ALTA |
| OWASP API Security Top 10 (2023) citado em descriptions | Transmite rigor de segurança | Citações são documentais. `security: [{}]` em 4 rotas de users + `bearerAuth` indefinido em 58 operações significa que o contrato não impõe o OWASP que anuncia | Gerador de middleware/SDK produz endpoints sem autenticação ou com security scheme inválido | CRÍTICA |
| Enum de statusLabel com 9 fases HBR-013 em matches | Parece machine-verifiable e completo | State machine de transições (forward-only, sem retroceder) está apenas em description prose. Não há encoding de qual estado sucede qual. Contrato aceita `PATCH statusLabel: scheduled` numa partida `completed` | Dois implementadores: um bloqueia transições inválidas, outro não — ambos conformes ao contrato | ALTA |
| Referência à "CANONICAL_EVENT_TAXONOMY_SCOUT.yaml" para eventLabel | Transmite controle vocabular rigoroso | `eventLabel` no schema é `type: string, maxLength: 120` — sem enum. A taxonomia não é incorporada. Qualquer string de até 120 chars é válida pelo schema | Scout aceita eventLabel "GOLO_QUALQUER" sem violação de contrato | ALTA |
| `x-semantic-id` annotations em campos UUID | Transmite tipagem semântica sofisticada | São extensões sem spec formal; nenhum toolchain os interpreta de forma padronizada. Gerador de código os ignora. Dois campos `type: string, format: uuid` com x-semantic-ids diferentes são indistinguíveis no schema gerado | Gerador produz `string` para todos os IDs — perde semântica de domínio | MÉDIA |
| Referências a ADR-007 (RS256), ADR-008 (RBAC) em descriptions | Decisões arquiteturais parecem formalizadas no contrato | Os ADRs não estão inline — são ponteiros. Contrato não define duração do JWT, algoritmo de chave, claims obrigatórios no token (além de menção em prose) | Implementador de auth lê "RS256" e infere o resto; dois implementadores produzem JWTs diferentes | ALTA |
| `minProperties: 1` em PATCH requestBodies | Parece proteção contra PATCH vazio | Não substitui validação de que o PATCH realmente altera algo válido. PATCH com `{"displayName": ""}` viola `minLength: 1` mas sem mensagem específica | Erros de validação parcialmente cobertos mas sem especificação de error body distinguível | BAIXA |
| Invariante INV-IAM-001 citada na description de `/auth/me` | Parece que a sessão retornada sempre terá id, principalUserId, sessionScopeLabel | `auth_session.yaml` schema tem somente: sessionId, token, expiresAt. Os campos citados na invariante não existem no schema referenciado | Contrato de resposta diverge da invariante que anuncia cumprir | CRÍTICA |
| Descrição de "soft-delete" em medical com audit trail | Parece comportamento definido e rastreável | Nenhuma definição de como registros deletados aparecem em GET `/medical/records` — response body contém `deletedAt`? São filtrados? São retornados com flag? | Dois implementadores: um oculta, outro expõe registros deletados — ambos conformes | ALTA |

---

## PARTE 4 — Fragilidades Reais

| Falha | Tipo | Impacto no sistema gerado | Severidade | Correção necessária |
|------|------|----------------------------|------------|--------------------|
| `contracts/openapi/components/schemas/matches/match.yaml` tem 4 campos (matchId, homeTeam, awayTeam, date). O schema canônico em `contracts/schemas/matches/match.schema.json` tem 15+ campos. O OpenAPI $ref aponta para o stub. | fonte de verdade insuficiente | Qualquer SDK/cliente gerado a partir do OpenAPI produz Match com 4 campos. statusLabel, scores, lineup, timestamps e incidentes ficam fora do contrato de API. | CRÍTICA | Substituir stub por $ref ao schema canônico ou copiar campos do JSON Schema completo |
| `auth_session.yaml` tem 3 campos (sessionId, token, expiresAt). INV-IAM-001 exige principalUserId e sessionScopeLabel obrigatórios. Esses campos não existem no schema. | conflito | Schema de resposta de `/auth/me`, `/auth/sessions`, `/auth/login` não contém os campos que a invariante declara obrigatórios. Contrato interno contraditório. | CRÍTICA | Schema deve incluir id, principalUserId, sessionScopeLabel, roleLabels, issuedAt, revokedAt, mfaSatisfied |
| `medical_record.yaml` tem 3 campos (recordId, athleteId, date). Path contract define 9 campos no requestBody incluindo returnToTrainingAuthorized, returnToPlayAuthorized, clinicalNotes. Response schema não reflete esses campos. | fonte de verdade insuficiente | Cliente que gera model do response não sabe da invariante INV-MED-002. POST com returnToPlayAuthorized=true retorna objeto sem esse campo. | CRÍTICA | Schema precisa refletir todos os campos do domínio médico |
| `scout_event.yaml` tem 3 campos (eventId, type, timestamp). DR-SCOUT-001 define soberania sobre tags, coding schema, clipes. INV-SCOUT-001 exige matchId e eventLabel obrigatórios. Nenhum desses campos está no schema. | fonte de verdade insuficiente | SDK gerado não conhece matchId, eventLabel, tagLabels, clipAssetRefs, athleteUserId. Integração com módulo de vídeo (clipAssetRefs) impossível a partir do schema. | CRÍTICA | Schema precisa incluir todos os campos de INV-SCOUT-001..004 |
| `analytics_snapshot.yaml` schema não tem sourceModuleLabels, timeWindowLabel, granularityLabel, refreshModeLabel — todos obrigatórios no requestBody de POST. | conflito | Response de createAnalyticsSnapshot não inclui os campos que foram enviados no request. Contrato POST→response é inconsistente. | ALTA | Schema de response deve espelhar os campos obrigatórios definidos no POST |
| 10 módulos (video, matches, competitions, ai_ingestion, teams, seasons, wellness, audit, notifications, scout) usam `security: - bearerAuth: []`. `bearerAuth` não está definido em `components/securitySchemes` do `openapi.yaml` raiz (que define apenas `HTTPBearer`). | ambiguidade | OpenAPI inválido por spec. Validator rejeitará o documento. SDK generators produzirão erro ou ignorarão security. 58 operações ficam sem enforcement de auth no artefato. | CRÍTICA | Definir `bearerAuth` em securitySchemes ou migrar todos para `HTTPBearer` |
| Endpoints em `users.yaml`: listUsers, createUser, getUser, patchUser têm `security: [{}]` com comentário "define quando identity_access estiver contratado". São placeholder, não contrato. | lacuna | Essas 4 rotas de users são tecnicamente públicas/anônimas no contrato atual. Qualquer gerador produzirá endpoints sem autenticação. | ALTA | Substituir `{}` por security scheme real antes de usar como SSOT |
| `common/error.yaml` (código+message) coexiste com `shared/problem.yaml` (RFC7807 type+title+status+detail). 7 módulos usam o primeiro, 9 o segundo. Root openapi.yaml diz RFC 7807 é canônico. | conflito | Cliente que consome errors de matches recebe `{code, message}`. Cliente que consome de users recebe `{type, title, status, detail}`. Tratamento de erro unificado impossível. | ALTA | Eliminar `common/error.yaml`; migrar todos os 7 módulos para `shared/problem.yaml` |
| `video.yaml` referencia role `match_operator` (admin, coordinator ou match_operator). ADR-008 define 5 roles canônicos: admin, coordinator, coach, athlete, member. `match_operator` não existe no RBAC canônico. | ambiguidade | Implementador de identity_access não sabe o que é `match_operator`. Como é atribuído? Quais operações protege além de vídeo? Ou é `coordinator` com restrição? | ALTA | Mapear para role canônico ou abrir ADR para 6º role |
| Match state machine ("Transição forward — nunca retroceder fases") está exclusivamente em description prose no PATCH. Nenhuma representação estrutural de transições válidas. | determinismo fraco | Implementador A bloqueia qualquer transição backward no servidor. Implementador B implementa apenas no cliente. Ambos conformes ao contrato. | ALTA | Adicionar `x-state-machine` ou equivalente, ou separar endpoint de transição de estado |
| INV-MED-002 (returnToPlayAuthorized=true implica returnToTrainingAuthorized=true) é cross-field constraint não verificável por JSON Schema. | determinismo fraco | Validadores de schema não detectam violação. Contrato descreve mas não impõe. | MÉDIA | Documentar validação server-side obrigatória como rule explícita na description; adicionar exemplo negativo no contract test |
| `lineupUserIds` em matches: HBR-008 diz máximo 16 jogadores por equipe. Nenhuma das schemas (stub ou canônica em contracts/schemas) tem `maxItems: 16`. | lacuna | Limite de 16 jogadores não é verificável a partir do contrato. | MÉDIA | Adicionar `maxItems: 16` ao array lineupUserIds |
| `/analytics/query` response: `data: items: {additionalProperties: true}`. Shape de cada row é completamente aberto. | determinismo fraco | Qualquer objeto é válido como row de resultado. Cliente não pode gerar tipos. Impossível validar conformidade. | ALTA | Definir union type ou pelo menos campos esperados por combinação de sourceModules+metricNames |
| `filterExpression` em `/analytics/query` é `type: string, maxLength: 500` com exemplo "team=X, athlete=Y". Sem DSL formal. | ambiguidade | Dois implementadores produzirão parsers incompatíveis. "team=X" pode significar teamId UUID, teamLabel string ou team index. | ALTA | Definir DSL mínimo ou substituir por filtros tipados como campos individuais |
| "Team staff with medical access" em medical.yaml não mapeia para nenhum dos 5 roles canônicos. | lacuna | Implementador cria sub-role ad hoc ou mapeia arbitrariamente para coach/coordinator. Duas implementações terão ACL diferentes para dados médicos sensíveis (PHI). | ALTA | Definir qual role canônico (ou combinação) representa "medical access" |
| "Coordinator pode atribuir roles dentro da organização" em identity_access — mas operação POST `/auth/users/{userId}/roles` não tem organizationId como parâmetro. | lacuna | Restrição de escopo da organização não é derivável do contrato. Server precisa inferir organização do JWT — comportamento não especificado no contrato. | MÉDIA | Adicionar parâmetro ou documetar que organizationId é extraído do JWT claim |
| Nenhum módulo define resposta 500 (Internal Server Error). | exceção ausente | Operação real do sistema produz 500s. Clientes gerados não sabem como tratar. Monitoramento não sabe o schema do error payload em falha interna. | MÉDIA | Adicionar 500 com `$ref: shared/problem.yaml` como default em todos os módulos |
| Comportamento de GET após DELETE (soft-delete) em medical não especificado. | lacuna | Implementador A oculta registros deletados (404). Implementador B os retorna com flag `deletedAt`. Nenhuma opção viola o contrato. | MÉDIA | Especificar se soft-deleted records aparecem em listagem (com filtro? omitidos? 410?) |
| Paginação mista: `matches.yaml` usa `page/pageSize/total` (offset). `users.yaml`, `identity_access.yaml`, `training.yaml` usam `nextPageToken` (cursor). Sem policy explícita no root. | ambiguidade | Cliente que implementa paginação genérica precisa de lógica bifurcada. Inconsistência com `api_rules.yaml` que referencia Google AIP cursor-based como canônico. | MÉDIA | Definir paginação canônica no root openapi.yaml e migrar matches para cursor-based ou documentar exceção |
| `auth_session.yaml` não define campo `revokedAt`. INV-IAM-003 (revokedAt >= issuedAt) é citada em `/auth/logout` e `/auth/sessions/{sessionId}`. | conflito | Schema de sessão não tem o campo que a invariante anuncia como verificável. Validação de invariante temporal não é derivável do contrato. | ALTA | Adicionar revokedAt (nullable), issuedAt ao schema de auth_session |

---

## PARTE 5 — Teste de Derivação

### API (rotas, métodos, parâmetros)
**Parcialmente** — a estrutura de paths é completa e bem-formada (17 módulos, rotas coerentes). Operationids são únicos. Parâmetros de query razoavelmente definidos. **Falha:** 58 operações com security scheme inválido impedem geração de SDK seguro. Paginação inconsistente entre módulos.

**O que falta:** Definição de `bearerAuth` em securitySchemes, política de paginação uniforme, remoção dos `security: [{}]` placeholders.

### Módulos (shapes de dados, campos obrigatórios, tipos)
**Não** para a maioria dos módulos — os schemas de response são stubs. Para gerar um `Match` completo, `AuthSession` completo, `MedicalRecord` completo, `ScoutEvent` completo, o contrato OpenAPI é insuficiente. O implementador precisa buscar `contracts/schemas/` que não está linkado formalmente no OpenAPI.

**O que falta:** Os $refs nos paths devem apontar para schemas completos que reflitam os campos declarados no requestBody e nas invariantes citadas.

### Regras principais (RBAC, invariantes, domain rules)
**Parcialmente** — as regras são nomeadas (DR-XXX, INV-XXX). Um implementador humano que rastreia as referências pode encontrá-las. Mas não há encoding machine-readable das regras nos schemas. State machines, cross-field constraints e RBAC estão em prosa.

**O que falta:** State machine formal para statusLabel transitions, cross-field rules como assertions ou x-extensions, RBAC policy inline ou referenciada formalmente.

### Interfaces (contratos de request/response completos)
**Não** — o contrato de interface é assimétrico: requestBody está frequentemente completo (ex: POST /matches tem todos os campos), mas o response schema é um stub (match.yaml retorna 4 campos). Um cliente gerado a partir do OpenAPI não sabe que a resposta contém statusLabel, scores, lineup.

**O que falta:** Schemas de response que reflitam o shape real de cada agregado de domínio.

### Restrições relevantes (validação, limites, unicidade)
**Parcialmente** — alguns constraints estão no schema (maxLength, minimum, uniqueItems, enum). Cross-field constraints (homeTeamId ≠ awayTeamId, INV-MED-002) não são deriváveis do schema. maxItems: 16 para lineup está ausente.

**O que falta:** Constraints cross-field documentados como assertions ou regras server-side explícitas; maxItems em arrays com limites de domínio.

---

## PARTE 6 — Teste Adversarial

| Cenário | Trecho causador | Divergência possível | Consequência | Severidade |
|--------|------------------|----------------------|--------------|------------|
| **Geração de cliente para GET /matches/{matchId}** | `$ref: "../components/schemas/matches/match.yaml"` aponta para stub de 4 campos | Implementador A usa stub → cliente só conhece matchId, homeTeam, awayTeam, date. Implementador B busca `contracts/schemas/matches/match.schema.json` → cliente conhece statusLabel, scores, lineup. | Dois clientes incompatíveis para o mesmo endpoint. Integrações com scout e analytics que dependem de statusLabel falham no cliente A. | CRÍTICA |
| **Implementação de autenticação em /scout/events** | `security: - bearerAuth: []` onde `bearerAuth` não está definido no securitySchemes | Implementador A trata bearerAuth como sinônimo de HTTPBearer (Bearer JWT). Implementador B rejeita o spec como inválido e cria seu próprio scheme. Implementador C usa o default do framework. | Três implementações de autenticação distintas para o mesmo endpoint. | CRÍTICA |
| **Tratamento de erro em POST /teams** | `$ref: "../components/schemas/common/error.yaml"` (structure: code+message) vs outros módulos que usam `shared/problem.yaml` (RFC7807: type+title+status+detail) | Middleware de tratamento de erro global espera RFC7807. POST /teams retorna `{code, message}`. Middleware falha ao parsear. Frontend que espera `detail` recebe `message`. | Error handling inconsistente na plataforma. Logging/alerting que parseia erros falha para os 7 módulos com `common/error`. | ALTA |
| **Atribuição de role no módulo video: `match_operator`** | "Papel RBAC insuficiente — requer admin, coordinator ou match_operator" em video.yaml | Implementador A cria um 6º role `match_operator` no banco de dados e no sistema de auth. Implementador B mapeia `match_operator` para `coordinator` (mais próximo). Implementador C trata como `coach`. | Três implementações com ACL diferentes para funções de vídeo. Usuário com role `coordinator` pode ou não gerenciar vídeo dependendo da implementação. | ALTA |
| **Transição de status em matches: cancelled → scheduled** | "Transição forward — nunca retroceder fases" em description do PATCH. Sem encoding formal de máquina de estados. | Implementador A bloqueia qualquer transição backward (scheduled < cancelled na ordem do enum). Implementador B permite qualquer transição que o enum aceite (incluindo completed → scheduled para reagendar). Implementador C só bloqueia se o estado atual for `completed`. | Partida cancelada pode ou não ser reaberta dependendo da implementação. Impacto em registros de scout e analytics vinculados. | ALTA |
| **Acesso de atleta a dados médicos próprios** | Medical: "team staff with medical access" pode criar/ler records. Não há definição de se athlete tem acesso read-only aos seus próprios records. | Implementador A: 403 para qualquer athlete (só staff médico acessa). Implementador B: athlete lê somente seus records. Implementador C: athlete lê e edita. Contrato não define nenhuma dessas opções. | Atleta pode ou não ver seus próprios dados clínicos dependendo da implementação. Impacto direto em privacidade (PHI) e conformidade. | CRÍTICA |
| **Paginação de GET /matches** | `page/pageSize/total` em matches vs `items/nextPageToken` em users. Frontend que implementa paginação genérica baseada no padrão do contrato. | Frontend que usa nextPageToken para navegar matches falha (campo não existe). Frontend que usa `page` para navegar users falha (campo não existe). SDK gerado produz dois modelos de paginação incompatíveis. | Implementação de UI de lista quebrada em pelo menos um dos módulos. | MÉDIA |
| **Validação de returnToPlayAuthorized=true quando returnToTrainingAuthorized=false** | INV-MED-002 em description. Não encodado no schema. | Implementador A valida server-side e retorna 400. Implementador B não implementa a validação (schema não força). Implementador C valida no frontend. | Dados clínicos clinicamente incoerentes podem ser persistidos em implementações que não leram o INV-MED-002 no texto. Impacto em decisões médicas de retorno ao treino. | ALTA |

---

## PARTE 7 — Veredito Final

**Este contrato é fonte de verdade real?** — **Não**
Para training e users, parcialmente sim. Para matches, medical, scout, analytics, identity_access (auth_session), audit, notificações — o schema de response referenciado no contrato OpenAPI não reflete o shape real. O contrato não é auto-suficiente.

**Ele é suficientemente determinístico para geração downstream?** — **Não**
58 operações com security scheme inválido, schemas de response stub, state machines em prosa, roles não canônicos, error schemas divergentes e constraints cross-field não encodados produzem divergência garantida entre implementações independentes.

**Ele está em nível 100/100?** — **Não**
Nota final consolidada: 42/100. Falhas estruturais, não de estilo.

**Ele governa comportamento real ou só aparenta governar?**
Aparenta. A densidade de referências normativas (DR-XXX, INV-XXX, OWASP) cria a aparência de rigor. Mas as referências são ornamentais na maior parte dos casos: as regras ficam nos documentos referenciados, não no contrato. O schema — que é a única parte machine-verifiable do contrato OpenAPI — está incompleto ou contraditório na maioria dos módulos. Um contrato que precisa de documentos externos para ser interpretado não é SSOT.

**O que falta para deixar de ser "bonito" e passar a ser "forte":**

1. **Imediato / bloqueante:** Corrigir `bearerAuth` → definir em `securitySchemes` ou migrar todos para `HTTPBearer`. Eliminar `security: [{}]` de rotas críticas.

2. **Imediato / integridade:** Substituir schemas stub (`match.yaml`, `auth_session.yaml`, `medical_record.yaml`, `scout_event.yaml`, `analytics_snapshot.yaml`, `audit_entry.yaml`) pelos schemas canônicos completos de `contracts/schemas/` ou equivalente.

3. **Alta prioridade:** Eliminar `common/error.yaml`; unificar em `shared/problem.yaml` (RFC7807). Definir `match_operator` ou remover e mapear para role canônico. Tornar state machines machine-readable.

4. **Médio prazo:** Unificar modelo de paginação. Definir "medical access" no RBAC canônico. Especificar comportamento de soft-delete em leituras. Definir DSL formal para `filterExpression` ou substituir por campos tipados. Adicionar 500 responses. Adicionar `maxItems: 16` ao lineup.

5. **Estrutural:** Garantir que o OpenAPI seja a SSOT completa — não apenas um índice de paths que delega substance para documentos referenciados. Contrato forte é lido de cima a baixo, sem saltos.

---

*Auditoria produzida em 2026-03-19. Escopo: contratos finais gerados. Não inclui avaliação de pipeline, templates ou ecossistema.*
