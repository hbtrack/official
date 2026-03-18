# DTO_VIEWMODEL_BOUNDARY_RULES.md

version: 1.0.0
status: PROPOSTO
decision_type: politica_de_limite_de_interface
scope: hb_track
owners:
  - arquitetura
  - backend
  - frontend
  - analytics
related_decisions:
  - HB_TRACK_ARCHITECTURE_DECISION.md
  - HB_TRACK_PERSISTENCE_POLICY.md
  - INGESTION_PROVIDER_CONTRACT.md
related_modules:
  - frontend
  - backend
  - api
  - analytics
  - video
  - training
  - matches
  - reports
  - dashboard
related_artifacts:
  - docs/_ssot/openapi.json
  - docs/_ssot/schema.sql
  - docs/_canon/MANUAL_BACKEND_CANONICO.md
  - docs/_canon/REGRAS_SISTEMAS.md

---

## 1. Objetivo

Definir as regras canônicas de limite entre:

- Modelo de Domínio
- DTO de API
- ViewModel
- Props de Componente de UI

Este contrato existe para prevenir:

- acoplamento do frontend com internos do backend
- acoplamento da UI com payloads de provedores
- vazamento de persistência em contratos de API
- inflação de DTO de API para satisfazer telas
- uso indevido de ViewModel como verdade de domínio
- deriva acidental entre camadas

---

## 2. Decisão Principal

O HB Track DEVE manter separação estrita entre:

- Modelo de Domínio
- Contrato de DTO de API
- Contrato de ViewModel
- Props de Componente de UI

Essas camadas não são intercambiáveis.

Nenhuma camada pode ser usada como atalho em substituição a outra apenas por conveniência, velocidade ou reuso de código.

---

## 3. Definições Canônicas das Camadas

### 3.1 Modelo de Domínio

Definição:
O modelo de domínio expressa significado de negócio, invariantes, transições de estado, identidades e regras.

Exemplos:
- Agregado TrainingSession
- Fato MatchEvent
- Entidade Athlete
- Tentativa de entrega de Notification
- Fato de marcação de Attendance

O modelo de domínio:
- pode ser mais rico do que os contratos de API
- pode conter invariantes internas
- pode conter IDs internos e metadados operacionais
- não deve ser moldado por necessidades de renderização de UI
- não deve ser moldado por particularidades de payload bruto de provedores

---

### 3.2 DTO de API

Definição:
DTO de API é o contrato de transporte exposto pelos endpoints de backend.

Propósito:
- limite de transporte estável
- esquema explícito de entrada/saída
- contrato público versionável
- intercâmbio entre backend e frontend

DTO de API:
- não é uma entidade de domínio
- não é uma entidade de banco de dados
- não é um modelo de tela específico de UI
- pode ser mais estreito ou mais amplo que o modelo de domínio dependendo do propósito do endpoint
- deve ser projetado intencionalmente

---

### 3.3 ViewModel

Definição:
Um ViewModel é um modelo de composição orientado ao frontend, otimizado para uma tela, seção, fluxo de interação ou visualização.

Propósito:
- agregar dados para uma visão
- adaptar dados de transporte para formato amigável à renderização
- localizar decisões de formatação e composição
- proteger componentes de UI da rotatividade da API

ViewModel:
- não é fonte de verdade
- não é um contrato de backend
- pode unir múltiplos DTOs
- pode incluir campos de exibição derivados
- pode incluir estruturas amigáveis ao estado da UI
- não deve se tornar verdade canônica de negócio

---

### 3.4 Props de Componente de UI

Definição:
Props são o menor limite, específico à composição de componente.

Props:
- podem ser mais estreitas do que ViewModels
- devem ser mínimas para a responsabilidade do componente
- não devem forçar conhecimento de DTOs não relacionados no componente

---

## 4. Fluxo Canônico de Dados

Fluxo canônico preferido:

```
Provedor/Entrada
-> Contrato de Ingestão
-> Lógica de Domínio
-> DTO de API
-> ViewModel
-> Props de Componente de UI
-> UI Renderizada
```

Este fluxo pode ser simplificado apenas quando a camada ignorada realmente não existe como uma preocupação separada.

Exemplo:
Para uma página de configurações estáticas trivial:
Domínio -> DTO -> Props

Mas a simplificação deve ser justificada, não assumida.

---

## 5. Responsabilidades das Camadas

| Camada | Responsabilidade | Não deve fazer |
|---|---|---|
| Modelo de Domínio | significado de negócio, invariantes, ciclo de vida, semânticas de fonte de verdade | adaptar-se a conveniências de renderização de tela |
| DTO de API | limite de transporte e versionamento de contrato | expor entidades de BD ou artefatos de renderização de UI diretamente |
| ViewModel | agregação e transformação específicas de tela | tornar-se contrato de API pública ou fonte de verdade |
| Props de Componente | contrato de renderização do componente | carregar bagagem de transporte/domínio não relacionada |

---

## 6. Regras de Separação

### 6.1 Domínio != DTO
Um modelo de domínio não deve ser exposto diretamente como output de transporte.

Razão:
- invariantes internas podem vazar
- refatorações futuras de domínio quebrariam clientes
- detalhes de persistência e operacionais podem vazar para o frontend

---

### 6.2 DTO != ViewModel
Um DTO de API não deve ser tratado como o modelo de tela final por padrão.

Razão:
- telas frequentemente precisam de composição de múltiplos endpoints
- formatação e agrupamento são preocupações de UI
- necessidades de tela mudam mais rápido do que contratos de API

---

### 6.3 ViewModel != Domínio
Um ViewModel nunca deve ser usado como verdade de negócio.

Razão:
- pode conter strings formatadas
- pode colapsar conceitos distintos por conveniência de UX
- pode omitir invariantes obrigatórios
- pode mesclar campos de múltiplas fontes

---

### 6.4 Entidade de BD != DTO
Entidades de persistência não devem ser retornadas diretamente de endpoints públicos.

Razão:
- vazamento de esquema
- exposição acidental de colunas internas
- acoplamento firme a migrações
- clientes frágeis

---

### 6.5 Payload de Provedor != DTO/ViewModel
Payloads brutos de provedores nunca devem ser expostos diretamente como DTOs ou ViewModels, a menos que um endpoint explícito de revisão/interno exista para ferramental operacional.

Razão:
- lock-in de provedor
- instabilidade de esquema
- inconsistência semântica
- superfície não controlada

---

## 7. Regras de Design de DTO de API

### 7.1 DTOs são contratos de endpoint
Cada DTO deve existir porque um endpoint precisa de um formato de transporte, não porque uma tabela de banco de dados ou componente de frontend existe.

### 7.2 DTOs devem ser explícitos
Cada DTO deve ter:
- nome explícito
- propósito explícito
- semântica de campos explícita
- propriedade estável de esquema

### 7.3 DTOs devem evitar formatação de UI
DTOs devem carregar valores semânticos, não strings de apresentação, a menos que a string de apresentação em si seja um requisito de produto.

Preferido:
- `started_at: datetime`
- `duration_seconds: integer`

Evitar:
- `started_at_label: "Ontem às 18:30"`
- `duration_label: "1h 25min"`

Estes pertencem ao ViewModel ou à camada de formatação.

### 7.4 DTOs podem expor resumos intencionalmente
DTOs podem expor campos de resumo quando esses resumos fazem parte do caso de uso da API.

Exemplo:
- `current_score`
- `attendance_rate`
- `last_notification_status`

Mas tais resumos devem ser explícitos, não vazamento acidental de projeções internas.

### 7.5 DTOs não devem expor semânticas brutas de persistência a menos que intencional
Evitar vazar:
- estrutura de tabelas de junção
- nomenclatura de chave estrangeira interna
- formato bruto de armazenamento do event store
- colunas internas de soft-delete
- artefatos de migração

---

## 8. Regras de Design de ViewModel

### 8.1 ViewModels são orientados à tela
Um ViewModel pode ser criado por:
- página
- widget de dashboard
- linha de lista
- painel de detalhes
- seção de linha do tempo
- adaptador de gráfico
- modal
- inicializador de estado de formulário

### 8.2 ViewModels podem combinar múltiplos DTOs
Isso é permitido e esperado.

Exemplos:
- Cabeçalho de sessão de treino + resumo de presença + estado de notificação
- Metadados de partida + linha do tempo de eventos + links de clipes de vídeo
- Perfil de atleta + tendência de performance + banner de aviso de bem-estar

### 8.3 ViewModels podem incluir campos de exibição derivados
Exemplos permitidos:
- `statusBadge`
- `formattedDate`
- `chartSeries`
- `groupedTimeline`
- `ctaState`
- `emptyStateMessage`

Estes não são campos de DTO por padrão.

### 8.4 ViewModels podem achatar estruturas de transporte aninhadas
Permitido quando melhora a ergonomia da UI.

Exemplo:
DTO da API:
```json
{
  "athlete": { "id": "a1", "name": "Maria" },
  "team": { "id": "t1", "name": "Sub-16" }
}
```
ViewModel:
```json
{
  "athleteId": "a1",
  "athleteName": "Maria",
  "teamName": "Sub-16"
}
```

### 8.5 ViewModels não devem ocultar ambiguidade semântica
Não colapse distinções de domínio distintas em um único campo de exibição se a UI ainda precisar da distinção.

Exemplo ruim:
`status: "active"`

Quando distinções de backend importam:
- scheduled
- in_progress
- completed
- suspended
- archived

Se a UI precisa apenas de um badge, derive-o conscientemente, mas não perca distinções canônicas upstream.

---

## 9. Regras de Mapeamento

### 9.1 Todos os mapeamentos não triviais devem ser explícitos
Transformações entre camadas devem ser intencionais e revisáveis.

Mapeamentos devem ser explícitos para:
- Domínio -> DTO
- DTO -> ViewModel
- ViewModel -> Estado de Formulário
- Payload normalizado de ingestão -> Comando/fato de domínio

### 9.2 Código de mapeamento é parte da arquitetura
Código de mapeamento não é cola para ser ignorada.
É um limite controlado de anti-acoplamento.

### 9.3 Propriedade do mapeamento
Propriedade recomendada:
- backend possui mapeamento Domínio -> DTO
- frontend possui mapeamento DTO -> ViewModel
- backend possui mapeamento Ingestão -> promoção de Domínio

### 9.4 Sem adaptação de transporte oculta em componentes folha de UI
Componentes folha não devem receber DTOs brutos e mapeá-los silenciosamente internamente, a menos que o componente seja explicitamente um adaptador de limite.

---

## 10. Regras Canônicas de Nomenclatura

### 10.1 Nomenclatura de DTO
Use nomes orientados a transporte.

Exemplos:
- `TrainingSessionResponseDto`
- `TrainingSessionListItemDto`
- `MatchTimelineEventDto`
- `AthleteProfileDto`
- `NotificationDeliveryAttemptDto`

Evitar:
- `TrainingSessionModel`
- `AthleteEntity`
- `MatchData`

### 10.2 Nomenclatura de ViewModel
Use nomes orientados a tela/caso de uso.

Exemplos:
- `TrainingSessionCardViewModel`
- `TrainingAgendaDayViewModel`
- `MatchTimelineViewModel`
- `AthleteDashboardViewModel`
- `WellbeingAlertBannerViewModel`

Evitar:
- `AthleteDtoView`
- `MatchEntityView`
- `SessionData`

### 10.3 Nomenclatura de Props
Use nomes orientados a componente.

Exemplos:
- `SessionCardProps`
- `TimelineRowProps`
- `AttendanceChipProps`

---

## 11. Regras de Composição de Telas

### 11.1 Endpoints de API atendem casos de uso, não tabelas
Endpoints devem expor formatos de transporte alinhados com casos de uso de produto.

### 11.2 ViewModels absorvem a volatilidade de composição
Quando telas mudam frequentemente, a volatilidade pertence principalmente à composição do ViewModel, não ao redesenho do modelo de domínio.

### 11.3 Telas de dashboard são naturalmente ricas em ViewModel
Para dashboards, painéis de analytics, linhas do tempo e interfaces de vídeo, ViewModels são esperados ser mais ricos e mais específicos para a tela.

### 11.4 Formulários podem requerer modelos separados de entrada/saída
Um formulário pode usar:
- esquema de DTO de entrada da API
- ViewModel/estado local do formulário
- DTO de submissão de volta para a API

Estes são artefatos separados.

---

## 12. Regras Canônicas de Anti-Acoplamento

### 12.1 Backend não deve emitir strings exclusivas de UI por padrão
Evitar incorporar:
- frases localizadas
- rótulos de badge
- tokens orientados a CSS
- marcadores de agrupamento específicos de visão

a menos que explicitamente requerido pelo contrato de produto.

### 12.2 Frontend não deve depender de nomes de apresentação de enums do backend
Frontend deve depender de códigos semânticos estáveis, depois mapear para rótulos localizados/tokens de tema localmente.

Preferido:
- DTO: `status = "in_progress"`
- ViewModel/UI: `statusLabel = "Em andamento"`

### 12.3 Frontend não deve inferir regras de domínio ocultas a partir de acidentes de DTO
Se uma tela depende de semânticas de negócio, essas semânticas devem ser explícitas no DTO ou na documentação, não adivinhadas a partir de campos incidentais.

### 12.4 ViewModels não devem espelhar DTOs de backend 1:1 sem razão
Se um "ViewModel" é apenas um clone de DTO, é provavelmente cerimônia inútil.
Ou:
- use DTO diretamente para esse caso trivial, ou
- crie um modelo de tela real

---

## 13. Regras Especiais para Analytics, Vídeo e Linhas do Tempo

### 13.1 DTOs de analytics devem permanecer semânticos
DTOs de analytics devem expor:
- medidas
- dimensões
- períodos
- identificadores
- unidades
- proveniência se necessário

Evitar DTOs que já contêm estrutura específica de biblioteca de gráficos, a menos que o endpoint seja explicitamente uma API de gráficos.

### 13.2 Dados de gráficos geralmente pertencem ao ViewModel
Exemplos:
- rótulos de eixo
- rótulos de cor
- agrupamento de séries de gráfico
- texto de tooltip
- estrutura de legenda

Estas são preocupações de UI, a menos que a API seja intencionalmente uma API de gráficos.

### 13.3 Telas de linha do tempo de vídeo requerem forte adaptação de ViewModel
Interfaces de vídeo e linha do tempo de eventos frequentemente precisam de:
- clipes agrupados
- rótulos sincronizados
- flags de interação
- fatias mescladas de evento+vídeo

Esta composição pertence ao ViewModel ou à camada de adaptador dedicada de frontend, não em objetos de domínio brutos.

---

## 14. Regras Especiais para Domínios Sensíveis

### 14.1 Campos sensíveis não devem ser espalhados por conveniência
Campos de bem-estar / psicológicos / saúde adjacentes devem aparecer apenas em DTOs que explicitamente os requerem.

### 14.2 ViewModels devem preservar limites de acesso
Composição de frontend não deve mesclar dados sensíveis restritos em dashboards genéricos de atletas, a menos que o endpoint e a política de acesso explicitamente permitam.

### 14.3 Mascaramento/redação pode diferir por DTO
Diferentes DTOs podem expor:
- valor completo
- valor redigido
- apenas flag booleana
- apenas status de resumo

Isso é legítimo e esperado em domínios sensíveis.

---

## 15. Padrões Proibidos

Os seguintes padrões são proibidos.

### 15.1 Retornar objetos ORM/modelo diretamente da API
Isso vaza persistência e remove controle de contrato.

### 15.2 Projetar DTOs para satisfazer o formato de props de um único componente para sempre
Isso cria acoplamento frágil entre transporte de backend e detalhe de implementação de frontend.

### 15.3 Tratar esquemas OpenAPI como ViewModels
OpenAPI descreve transporte, não composição de tela.

### 15.4 Usar ViewModels em lógica de negócio de backend
Um ViewModel não tem autoridade em decisões de domínio.

### 15.5 Duplicar regras de negócio apenas em ViewModels de frontend
Regras de negócio pertencem ao backend/domínio, a menos que seja claramente apenas de apresentação.

### 15.6 Usar rótulos formatados como semânticas canônicas
Rótulos mudam com locale e política de UI; semânticas devem permanecer estáveis.

### 15.7 Deixar payload normalizado de ingestão se tornar DTO público por acidente
A camada de ingestão é uma camada interna anti-corrupção, não uma superfície de API pública.

---

## 16. Checklist de Revisão para Novos Endpoints

Todo novo endpoint deve responder:
- Qual é o caso de uso do endpoint?
- Qual DTO é exposto?
- Por que este DTO não é um objeto direto de domínio/persistência?
- Quais telas de frontend irão consumi-lo?
- A tela precisa de um ViewModel?
- Quais campos são semânticos vs orientados a apresentação?
- Este endpoint expõe dados sensíveis?
- Este DTO poderia acidentalmente prender a UI nos internos atuais do backend?

Se essas respostas não estiverem claras, o contrato do endpoint não está maduro.

---

## 17. Checklist de Revisão para Novas Telas

Toda nova tela deve responder:
- Quais DTOs ela consome?
- Ela precisa de um ViewModel dedicado?
- Quais transformações são apenas de apresentação?
- Quais campos são derivados?
- Algum campo sensível está sendo combinado com dados não sensíveis?
- As props de componente são mínimas e locais?
- Algum componente está dependendo de complexidade de DTO bruto de que não precisa?

Se não, a arquitetura de tela provavelmente está sub-especificada.

---

## 18. Exemplos de Padrões

### 18.1 Bom padrão — Card de treino

DTO do Backend:
```json
{
  "sessionId": "ts_1",
  "title": "Treino técnico ofensivo",
  "status": "scheduled",
  "scheduledStart": "2026-03-11T18:30:00Z",
  "athleteCount": 18
}
```

ViewModel do Frontend:
```json
{
  "id": "ts_1",
  "title": "Treino técnico ofensivo",
  "statusCode": "scheduled",
  "statusLabel": "Agendado",
  "startsAtLabel": "Hoje, 18:30",
  "subtitle": "18 atletas previstas",
  "isLateRisk": false
}
```

Props do Componente:
```json
{
  "title": "Treino técnico ofensivo",
  "statusLabel": "Agendado",
  "subtitle": "18 atletas previstas"
}
```

---

### 18.2 Bom padrão — Linha do tempo de partida

DTO do Backend:
```json
{
  "matchId": "m_1",
  "events": [
    {
      "eventId": "e_1",
      "eventType": "goal",
      "occurredAt": "2026-03-11T19:02:10Z",
      "athleteId": "a_7",
      "teamSide": "home"
    }
  ]
}
```

ViewModel do Frontend:
```json
{
  "matchId": "m_1",
  "timelineGroups": [
    {
      "minuteLabel": "02'",
      "items": [
        {
          "id": "e_1",
          "icon": "goal",
          "label": "Gol de Ana",
          "side": "home"
        }
      ]
    }
  ]
}
```

Isso está correto porque agrupamento de linha do tempo e formatação de rótulos são preocupações de UI.

---

### 18.3 Padrão ruim — Vazamento de provedor

DTO ruim:
```json
{
  "sr_match_id": "sr:match:123",
  "sport_event_status": { "match_status": "live" },
  "competitors": [...]
}
```

Por que é ruim:
- nomes de campos nativos do provedor vazaram
- contrato de transporte vinculado ao esquema upstream
- UI/domínio interno se acoplará à estrutura do provedor

Abordagem correta:
normalize primeiro, depois emita campos de DTO estáveis.

---

## 19. Política de Implementação Recomendada

### 19.1 Backend
Backend deve expor esquemas de DTO via OpenAPI e manter mapeadores/adaptadores explícitos.

### 19.2 Frontend
Frontend deve manter uma camada de adaptador dedicada para:
- DTO -> ViewModel
- DTO -> Estado Inicial de Formulário
- Coleção de DTO -> linhas de tabela / gráficos / cards / linhas do tempo

### 19.3 Tipos compartilhados
Tipos compartilhados são permitidos apenas para contratos semânticos estáveis, não como atalho para apagar limites de camadas.

### 19.4 Clientes de API gerados
Clientes gerados são clientes de transporte.
Eles não removem a necessidade de composição de ViewModel.

---

## 20. Definição de Pronto

Esta política está PRONTA apenas quando:
- endpoints não expõem diretamente entidades ORM/persistência
- DTOs são modelados explicitamente como contratos de transporte
- telas não triviais definem ViewModels ou justificativa explícita para não precisar deles
- telas de analytics/vídeo/linha do tempo usam adaptação de ViewModel orientada a apresentação
- campos sensíveis são expostos apenas em DTOs explícitos
- payloads nativos de provedores não vazam para contratos de API pública
- componentes de frontend não estão fortemente acoplados à complexidade de DTO bruto
- OpenAPI é tratado como contrato de transporte, não contrato de tela
